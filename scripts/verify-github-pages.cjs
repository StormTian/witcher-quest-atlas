// Exercise the actual Pages package, including its source binding and project path.
const fs = require('node:fs'), path = require('node:path'), crypto = require('node:crypto');
const assert = require('node:assert/strict'), {execFileSync} = require('node:child_process');
const {chromium, launchOptions, baseURL, provenance} = require('./browser-runtime.cjs');
const root = path.resolve(__dirname, '..');
const output = path.resolve(process.env.PAGES_EVIDENCE_DIR || '/tmp/witcher-pages-checks');
fs.mkdirSync(output, {recursive: true});
const expectedCommit = process.env.EXPECTED_SOURCE_SHA || execFileSync('git', ['rev-parse', 'HEAD'], {cwd: root, encoding: 'utf8'}).trim();
const hashes = require('./runtime-hashes.cjs')();
const checks = [], errors = [], failures = [];
let version;
async function check(name, action) {
  try { const detail = await action(); checks.push({name, status: 'pass', detail}); }
  catch (error) { checks.push({name, status: 'fail', detail: error.message}); }
}
async function request(name) {
  const response = await fetch(new URL(name, baseURL), {cache: 'no-store'});
  assert.equal(response.status, 200, name);
  return Buffer.from(await response.arrayBuffer());
}
async function waitForPublishedCommit() {
  for (let attempt = 0; attempt < 12; attempt++) {
    try {
      const response = await fetch(new URL('version.json', baseURL), {cache: 'no-store'});
      if (response.ok && (await response.json()).sourceCommit === expectedCommit) return;
    } catch {}
    await new Promise(resolve => setTimeout(resolve, 5000));
  }
  throw new Error(`Pages did not serve the expected source commit ${expectedCommit} within 60 seconds`);
}

(async () => {
  await waitForPublishedCommit();
  await check('发布版本对应精确源码提交及已验证运行文件', async () => {
    version = JSON.parse(await request('version.json'));
    assert.equal(version.sourceCommit, expectedCommit);
    assert.equal(version.sourceURL, `https://github.com/${version.repository}/commit/${expectedCommit}`);
    assert.deepEqual(version.runtimeInputHashes, hashes);
    assert.equal(version.verification.status, 'pass');
    assert.ok(version.verification.passed >= 137);
    const report = await request('validation.json');
    assert.equal(crypto.createHash('sha256').update(report).digest('hex'), version.verification.reportSha256);
    return `${expectedCommit}; ${version.verification.passed} checked results`;
  });
  await check('实际发布的运行资源与源码逐个一致', async () => {
    for (const [name, hash] of Object.entries(hashes)) {
      const bytes = await request(name);
      assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'), hash, name);
    }
    await request('.nojekyll');
    return `${Object.keys(hashes).length} runtime files and static hosting marker`;
  });
  const browser = await chromium.launch(launchOptions);
  try {
    for (const viewport of [{width: 1440, height: 900}, {width: 390, height: 844}]) {
      const context = await browser.newContext({viewport});
      const page = await context.newPage();
      page.setDefaultTimeout(15000);
      page.on('pageerror', error => errors.push(error.message));
      page.on('response', response => {if (response.status() >= 400) failures.push({url: response.url(), status: response.status()});});
      await check(`${viewport.width}px：地图、分享定位和默认剧透保护`, async () => {
        await page.goto(new URL('?region=white-orchard&quest=q37', baseURL).href);
        await page.waitForFunction(() => window.atlas?.progress);
        assert.equal(await page.evaluate(() => atlas.state.selected), 'q37');
        assert.equal(await page.evaluate(() => atlas.state.region), 'white-orchard');
        assert.equal(await page.evaluate(() => atlas.state.spoilers), false);
        assert.equal(await page.locator('.decision-choice').count(), 0);
        await page.waitForFunction(() => [...document.querySelectorAll('.leaflet-tile-loaded')].some(image => image.complete && image.naturalWidth === 256));
        await page.locator('[data-share="quest"]').click();
        const share = new URL(await page.locator('.share-url').inputValue());
        assert.equal(share.pathname, new URL(baseURL).pathname);
        assert.deepEqual([...share.searchParams.keys()].sort(), ['quest', 'region']);
        assert.equal(share.searchParams.get('quest'), 'q37');
        await page.screenshot({path: path.join(output, `map-${viewport.width}.png`)});
        return 'Native tiles load; the share link retains the complete Pages project path';
      });
      await check(`${viewport.width}px：版本入口与源码提交链接`, async () => {
        if (viewport.width < 700) await page.locator('#mobile-map').click();
        await page.locator('#verification').click();
        const link = page.locator('a[href="version.html"]');
        await link.waitFor({state: 'visible'});
        assert.equal(await link.count(), 1);
        await page.goto(new URL(await link.getAttribute('href'), baseURL).href);
        await page.waitForSelector('#version:not([hidden])');
        assert.equal(await page.locator('#commit code').textContent(), expectedCommit);
        assert.equal(await page.locator('#commit').getAttribute('href'), version.sourceURL);
        assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1), false);
        await page.screenshot({path: path.join(output, `version-${viewport.width}.png`)});
        await page.locator('a[href="./"]').click();
        await page.waitForFunction(() => window.atlas?.DATA);
        assert.equal(new URL(page.url()).pathname, new URL(baseURL).pathname);
        return 'The version page shows the deployed commit and returns to the same project path';
      });
      await context.close();
    }
    await check('桌面与手机没有脚本或资源错误', async () => {
      assert.deepEqual(errors, []); assert.deepEqual(failures, []);
      return 'Zero browser errors and HTTP failures';
    });
  } finally { await browser.close(); }
  const result = {...provenance, executedAt: new Date().toISOString(), baseURL,
    sourceCommit: expectedCommit, runtimeInputHashes: hashes,
    status: checks.every(check => check.status === 'pass') ? 'pass' : 'fail',
    passed: checks.filter(check => check.status === 'pass').length, total: checks.length,
    checks, pageErrors: errors, httpFailures: failures};
  fs.writeFileSync(path.join(output, 'pages-validation.json'), JSON.stringify(result, null, 2) + '\n');
  console.log(JSON.stringify(result));
  if (result.status !== 'pass') process.exitCode = 1;
})().catch(error => {console.error(error); process.exitCode = 1;});
