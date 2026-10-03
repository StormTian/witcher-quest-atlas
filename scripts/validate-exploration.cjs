const fs = require('node:fs'), path = require('node:path'), assert = require('node:assert/strict'), crypto = require('node:crypto');
const {chromium, launchOptions, baseURL} = require('./browser-runtime.cjs');
const root = path.resolve(__dirname, '..'), checks = [], errors = [], httpFailures = [];
const sha = name => crypto.createHash('sha256').update(fs.readFileSync(path.join(root, name))).digest('hex');
const fixtures = {'white-orchard': [6, 1, 1], velen: [8, 19, 2], skellige: [9, 8, 1], toussaint: [5, 7, 1], 'kaer-morhen': [1, 0, 1]};

(async () => {
  const browser = await chromium.launch(launchOptions);
  let page = await browser.newPage({viewport: {width: 1440, height: 900}});
  function observe(p) {
    p.on('pageerror', error => errors.push(error.message));
    p.on('response', response => { if (response.status() >= 400) httpFailures.push({url: response.url(), status: response.status()}); });
  }
  observe(page);
  async function fresh() { await page.goto(baseURL); await page.waitForFunction(() => window.atlas?.exploration); }
  async function check(name, fn) {
    try { checks.push({name, status: 'pass', detail: await fn()}); }
    catch (error) {
      checks.push({name, status: 'fail', detail: error.message});
      console.error(name, error.message);
      await page.screenshot({path: path.join(root, 'evidence', 'exploration-failure-' + checks.length + '.png')}).catch(() => {});
    }
  }
  async function centerPoint(point) { await page.evaluate(p => atlas.map.setView(p.latlng, 3, {animate: false}), point); await page.waitForTimeout(250); }
  function pointMarker(point) { return page.locator(`.exploration-marker:has([data-point="${point.id}"])`); }

  await fresh();
  await check('五区探索点与来源清单数量', async () => {
    for (const [region, expected] of Object.entries(fixtures)) {
      await page.locator(`[data-region="${region}"]`).click();
      for (const [index, type] of ['power', 'board', 'stash'].entries()) assert.equal(await page.locator('.exploration-pin.' + type).count(), expected[index], region + '/' + type);
      assert.equal(await page.evaluate(() => atlas.exploration.markers.getLayers().length), expected.reduce((a, b) => a + b, 0));
    }
    await page.locator('[data-region="vizima"]').click();
    assert.equal(await page.locator('.exploration-pin').count(), 0);
    return 'White Orchard 8, Velen 29, Skellige 18, Toussaint 13, Kaer Morhen 2; no fabricated Vizima point.';
  });
  await check('32种图层组合及任务索引独立性', async () => {
    await fresh(); await page.locator('#layers-toggle').click();
    const keys = ['quests', 'landmarks', 'power', 'board', 'stash'];
    for (let mask = 0; mask < 32; mask++) {
      for (let index = 0; index < keys.length; index++) await page.locator(`[data-layer="${keys[index]}"]`).setChecked(Boolean(mask & (1 << index)));
      assert.equal(await page.locator('.map-pin').count(), mask & 1 ? 64 : 0);
      assert.equal(await page.locator('.road-sign').count(), mask & 2 ? 111 : 0);
      assert.equal(await page.locator('.exploration-pin').count(), (mask & 4 ? 8 : 0) + (mask & 8 ? 19 : 0) + (mask & 16 ? 2 : 0));
      assert.equal(await page.locator('.quest-row').count(), 131);
    }
    await page.locator('#close-layers').click();
    return 'All 32 combinations match independently declared Velen counts; the 131-quest index remains available.';
  });
  await check('全隐藏恢复原选择并隐藏任务高亮', async () => {
    await fresh(); await page.evaluate(() => atlas.selectQuest('q67'));
    await page.locator('#layers-toggle').click();
    await page.locator('[data-layer="power"]').uncheck(); await page.locator('[data-layer="stash"]').uncheck();
    await page.locator('#hide-layers').click();
    assert.equal(await page.locator('.map-pin,.road-sign,.exploration-pin').count(), 0);
    assert.equal(await page.evaluate(() => {let n = 0; atlas.map.eachLayer(layer => {if (layer instanceof L.CircleMarker) n++;}); return n;}), 0);
    await page.locator('#restore-layers').click();
    assert.equal(await page.locator('.exploration-pin').count(), 19);
    assert.equal(await page.locator('[data-layer="power"]').isChecked(), false);
    assert.equal(await page.locator('[data-layer="stash"]').isChecked(), false);
    await page.locator('[data-layer="quests"]').uncheck(); await page.locator('#close-layers').click();
    await page.locator('[data-quest="q67"]').click();
    assert.equal(await page.locator('.map-pin').count(), 0);
    assert.equal(await page.evaluate(() => {let n = 0; atlas.map.eachLayer(layer => {if (layer instanceof L.CircleMarker) n++;}); return n;}), 0);
    return 'Restores the prior partial selection; hidden quest layers stay hidden when a quest is opened from the index.';
  });
  await check('三类点位真实点击详情与键盘操作', async () => {
    await fresh(); await page.locator('[data-region="white-orchard"]').click();
    for (const type of ['power', 'board', 'stash']) {
      const point = await page.evaluate(t => atlas.exploration.data.points.find(p => p.region === 'white-orchard' && p.type === t), type);
      await centerPoint(point); await pointMarker(point).click();
      assert.equal(await page.evaluate(() => atlas.state.selectedPoint), point.id, 'selected exploration point: ' + point.type);
      assert.equal(await page.locator('#detail h2').innerText(), point.title);
      assert.match(await page.locator('#detail').innerText(), /社区位置/);
      assert.match(await page.locator('#detail').innerText(), /尚未逐点实机/);
      assert.equal(await page.locator('#reveal,.decision-choice').count(), 0);
      assert.ok((await page.locator('#detail .source-list a').first().getAttribute('href')).includes('fb674dbff7df087d0a45f9b3938ba6d5317295af'));
      await page.locator('#detail-close').click();
    }
    const point = await page.evaluate(() => atlas.exploration.data.points.find(p => p.region === 'white-orchard' && p.type === 'board'));
    await centerPoint(point); await pointMarker(point).focus(); await page.keyboard.press('Enter');
    assert.equal(await page.evaluate(() => atlas.state.selectedPoint), point.id, 'selected exploration point: ' + point.type);
    await page.locator('#detail-close').click();
    await centerPoint(point); await pointMarker(point).focus(); await page.keyboard.press('Space');
    assert.equal(await page.evaluate(() => atlas.state.selectedPoint), point.id, 'Space activates focused marker');
    await page.screenshot({path: path.join(root, 'evidence/exploration-desktop.png')});
    return 'All three types open through real marker clicks; keyboard Enter and Space open a board; provenance and availability limits remain visible.';
  });
  await check('任务筛选与探索图层互不干扰', async () => {
    await fresh(); await page.locator('#search').fill('no such quest xyz'); await page.locator('#expansion').selectOption('hos');
    assert.equal(await page.locator('.quest-row').count(), 0);
    assert.equal(await page.locator('.exploration-pin').count(), 29);
    assert.equal(await page.locator('.road-sign').count(), 111);
    const point = await page.evaluate(() => atlas.exploration.data.points.find(p => p.region === 'velen' && p.type === 'stash'));
    await centerPoint(point); await pointMarker(point).click();
    assert.equal(await page.locator('#search').inputValue(), 'no such quest xyz');
    assert.equal(await page.locator('#expansion').inputValue(), 'hos');
    await page.locator('#spoiler').click();
    assert.equal(await page.locator('#detail h2').innerText(), '储藏箱');
    assert.equal(await page.locator('.decision-choice').count(), 0);
    return 'Empty task search and DLC filtering leave exploration and road signs intact; point selection preserves filters.';
  });
  await check('地图叠加与密集区渲染耗时', async () => {
    await fresh();
    const timings = await page.evaluate(() => {const times = []; for (let i = 0; i < 25; i++) {const start = performance.now(); atlas.exploration.render(); times.push(performance.now() - start);} return times.sort((a, b) => a - b);});
    const p95 = timings[Math.ceil(timings.length * .95) - 1]; assert.ok(p95 < 250, '29-point render exceeded 250ms');
    assert.ok(await page.locator('#map').evaluate(element => getComputedStyle(element).zIndex === '0'));
    await page.screenshot({path: path.join(root, 'evidence/exploration-map.png')});
    return `25 real Velen renders; p95 ${p95.toFixed(1)}ms on this cloud Chromium; map controls have their own stacking context.`;
  });
  await check('手机图层与探索详情及200%文字', async () => {
    await page.close(); page = await browser.newPage({viewport: {width: 390, height: 844}, hasTouch: true, isMobile: true}); observe(page);
    await fresh(); await page.locator('#layers-toggle').click();
    assert.equal(await page.locator('#layers-dialog').isVisible(), true);
    await page.locator('[data-layer="board"]').uncheck(); assert.equal(await page.locator('.exploration-pin.board').count(), 0);
    await page.locator('[data-layer="board"]').check();
    await page.screenshot({path: path.join(root, 'evidence/exploration-mobile-layers.png')});
    await page.keyboard.press('Escape'); assert.equal(await page.locator('#layers-dialog').isVisible(), false);
    assert.equal(await page.locator('#layers-toggle').evaluate(element => document.activeElement === element), true);
    const point = await page.evaluate(() => atlas.exploration.data.points.find(p => p.region === 'velen' && p.type === 'board'));
    await centerPoint(point); await pointMarker(point).tap();
    assert.equal(await page.locator('#detail').isVisible(), true); assert.equal(await page.locator('#catalog').isVisible(), false);
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1), false);
    await page.screenshot({path: path.join(root, 'evidence/exploration-mobile.png')});
    await page.locator('#detail-close').click();
    await page.addStyleTag({content: 'html {font-size:32px !important}'});
    await page.locator('#layers-toggle').click();
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1), false);
    await page.locator('#close-layers').click();
    return '390×844 touch device; layer toggles, Escape/focus return, tap-to-detail and doubled text remain usable without page overflow.';
  });
  await check('探索资源与页面异常', async () => {
    assert.deepEqual(errors, []); assert.deepEqual(httpFailures, []);
    return 'Zero page exceptions and zero unexpected HTTP failures across the exploration interactions.';
  });
  const output = {date: new Date().toISOString().slice(0, 10), executionEnvironment: 'cloud-linux', executedAt: new Date().toISOString(), status: checks.every(check => check.status === 'pass') ? 'pass' : 'fail', checks, passed: checks.filter(check => check.status === 'pass').length, total: checks.length, pageErrors: errors, httpFailures, datasetSha256: sha('dist/data.json'), explorationSha256: sha('dist/exploration.json'), appSha256: sha('dist/app.js'), explorationCodeSha256: sha('dist/exploration.js'), explorationStyleSha256: sha('dist/exploration.css')};
  fs.writeFileSync(path.join(root, 'evidence/exploration-browser-validation.json'), JSON.stringify(output, null, 2));
  console.log(JSON.stringify(output)); await browser.close(); if (output.status !== 'pass') process.exitCode = 1;
})().catch(error => {console.error(error); process.exitCode = 1;});
