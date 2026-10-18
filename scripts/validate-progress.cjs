const {catalogAction}=require('./browser-runtime.cjs');
const fs = require('node:fs'), path = require('node:path'), crypto = require('node:crypto'), assert = require('node:assert/strict');
const {chromium, launchOptions, baseURL} = require('./browser-runtime.cjs');
const root = path.resolve(__dirname, '..'), checks = [], errors = [], failed = [];
const files = require('./runtime-inputs.json');
(async () => {
  const browser = await chromium.launch(launchOptions);
  let context, page;
  async function fresh(options = {}) {
    if (context) await context.close();
    context = await browser.newContext({viewport: {width: 1440, height: 900}, acceptDownloads: true, ...options});
    page = await context.newPage(); page.setDefaultTimeout(12000);
    page.on('pageerror', error => errors.push(error.message));
    page.on('response', response => {if (response.status() >= 400) failed.push({url: response.url(), status: response.status()});});
    await page.goto(baseURL); await page.waitForFunction(() => window.atlas?.progress);
  }
  async function check(name, fn) {
    try { await fn(); checks.push({name, status: 'pass'}); console.log('PASS', name); }
    catch (error) { checks.push({name, status: 'fail', detail: error.message}); console.error(name, error.message); await page?.screenshot({path: path.join(root, 'evidence/progress-failure-' + checks.length + '.png')}).catch(() => {}); }
  }
  const flags = (kind, id) => page.evaluate(({kind, id}) => ({done: atlas.progress.flag(kind, id, 'done'), starred: atlas.progress.flag(kind, id, 'starred')}), {kind, id});
  await check('桌面与手机列表勾选完成后隐藏、刷新恢复并可撤销', async () => {
    for (const width of [1440, 390]) {
      await fresh({viewport: {width, height: width === 390 ? 844 : 900}, isMobile: width === 390, hasTouch: width === 390});
      await page.locator('[data-region="white-orchard"]').click();
      if (width === 390) await page.locator('#mobile-list').click();
      assert.equal(await page.locator('#hide-done').isChecked(), true);
      await page.locator('[data-quest-done="q37"]').click();
      assert.equal((await flags('quest', 'q37')).done, true);
      assert.equal(await page.locator('[data-quest="q37"]').count(), 0);
      assert.equal(await page.locator('.leaflet-marker-icon[title="扭曲的纵火犯"]').count(), 0);
      assert.equal(await page.evaluate(() => atlas.state.selected), null);
      assert.equal(await page.evaluate(() => atlas.state.story.questStates.q37), undefined);
      assert.match(await page.locator('#quest-progress-summary').innerText(), /已完成 1 \/ 428/);
      assert.equal(await page.locator('#quest-progress-bar').getAttribute('value'), '1');
      assert.equal(await page.evaluate(() => document.activeElement.hasAttribute('data-quest-done')), true);
      await page.reload(); await page.waitForFunction(() => window.atlas?.progress);
      if (width === 390) await page.locator('#mobile-list').click();
      assert.equal(await page.locator('#hide-done').isChecked(), true);
      assert.equal(await page.locator('[data-quest-done="q37"]').count(), 0);
      assert.match(await page.locator('#quest-progress-summary').innerText(), /已完成 1 \/ 428/);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1), false);
      await page.screenshot({path: path.join(root, `evidence/task-progress-${width === 390 ? 'mobile' : 'desktop'}.png`)});
      await catalogAction(page, '#progress-view', 'selectOption', 'done');
      assert.equal(await page.locator('#hide-done').isChecked(), false);
      assert.equal(await page.locator('[data-quest-done="q37"]').isChecked(), true);
      await page.locator('[data-quest-done="q37"]').click();
      assert.equal((await flags('quest', 'q37')).done, false);
      await catalogAction(page, '#progress-view', 'selectOption', 'all');
      assert.equal(await page.locator('[data-quest-done="q37"]').isChecked(), false);
      await page.locator('#hide-done').check();
      await page.locator('#hide-done').uncheck();
      await page.reload(); await page.waitForFunction(() => window.atlas?.progress);
      assert.equal(await page.evaluate(() => atlas.state.hideDone), false);
      if (width === 390) await page.locator('#mobile-list').click();
      await page.locator('[data-quest-done="q37"]').click();
      assert.equal(await page.locator('[data-quest-done="q37"]').isChecked(), true);
      assert.equal(await page.evaluate(() => {
        const backup = atlas.progress.snapshot(); backup.preferences = {progressView: 'done'};
        return atlas.progress.parse(backup).preferences.hideDone;
      }), false);
    }
  });
  await check('任务排序刷新、新标签页与新旧备份兼容', async () => {
    await fresh();assert.equal(await page.locator('#quest-sort').inputValue(),'main-first');await page.locator('#quest-sort').selectOption('level-desc');await page.locator('[data-record="starred"]').click();
    const backup=await page.evaluate(()=>atlas.progress.snapshot());assert.equal(backup.schemaVersion,1);assert.equal(backup.preferences.questSort,'level-desc');
    await page.reload();await page.waitForFunction(()=>window.atlas?.progress);assert.equal(await page.locator('#quest-sort').inputValue(),'level-desc');assert.equal((await flags('quest','q67')).starred,true);
    const second=await context.newPage();await second.goto(baseURL);await second.waitForFunction(()=>window.atlas?.progress);assert.equal(await second.locator('#quest-sort').inputValue(),'level-desc');await second.close();await page.reload();await page.waitForFunction(()=>window.atlas?.progress);
    const legacy=JSON.parse(JSON.stringify(backup));delete legacy.preferences.questSort;
    const parsed=await page.evaluate(v=>atlas.progress.parse(v).preferences.questSort,legacy);assert.equal(parsed,'main-first');
    for(const invalid of ['random',null,42,{}]){const bad=JSON.parse(JSON.stringify(backup));bad.preferences.questSort=invalid;assert.equal(await page.evaluate(v=>atlas.progress.parse(v).preferences.questSort,bad),'main-first')}
    await page.locator('#quest-sort').selectOption('region');
    for(const [value,before,after] of [[backup,'region','level-desc'],[legacy,'level-desc','main-first']]){
      await catalogAction(page,'#progress-toggle','click');await page.locator('#progress-import').setInputFiles({name:'sort-backup.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(value))});await page.waitForFunction(()=>!document.querySelector('#progress-apply').disabled);assert.equal(await page.evaluate(()=>atlas.state.questSort),before);await page.locator('#progress-apply').click();assert.equal(await page.evaluate(()=>atlas.state.questSort),after);await page.locator('#close-progress').click();assert.equal(await page.locator('#quest-sort').inputValue(),after);assert.equal((await flags('quest','q67')).starred,true);assert.equal(await page.evaluate(()=>atlas.state.spoilers),false);
    }
  });
  await check('任务完成与收藏在刷新、新标签页恢复', async () => {
    await fresh(); await page.locator('[data-record="done"]').click(); await page.locator('[data-record="starred"]').click();
    assert.deepEqual(await flags('quest', 'q67'), {done: true, starred: true});
    await page.reload(); await page.waitForFunction(() => window.atlas?.progress); assert.deepEqual(await flags('quest', 'q67'), {done: true, starred: true});
    const second = await context.newPage(); await second.goto(baseURL); await second.waitForFunction(() => window.atlas?.progress);
    assert.equal(await second.evaluate(() => window.atlas?.progress.flag('quest', 'q67', 'done')), true); await second.close();
    await page.locator('[data-record="done"]').click(); assert.equal((await flags('quest', 'q67')).done, false);
  });
  await check('任务与探索点的个人筛选及图层数量一致', async () => {
    await fresh(); await page.locator('[data-record="done"]').click(); await page.locator('[data-record="starred"]').click();
    await page.locator('#hide-done').check(); assert.equal(await page.locator('[data-quest="q67"]').count(), 0);
    assert.equal(await page.evaluate(() => {let n=0; atlas.map.eachLayer(l=>{if(l instanceof L.CircleMarker)n++;});return n;}), 0);
    await page.locator('#hide-done').uncheck(); await catalogAction(page, '#progress-view', 'selectOption', 'starred'); assert.equal(await page.locator('.quest-row').count(), 1);
    await page.locator('#layers-toggle').click();
    assert.equal(await page.locator('[data-count-for="landmarks"]').innerText(), '111');
    assert.equal(await page.locator('.road-sign').count(), 111);
    await page.locator('#close-layers').click();
    await catalogAction(page, '#progress-view', 'selectOption', 'all');
    const point = await page.evaluate(() => atlas.exploration.data.points.find(p => p.region === 'velen' && p.type === 'board'));
    await page.evaluate(id => atlas.selectExploration(id), point.id); await page.locator('[data-record="done"]').click();
    await page.locator('#hide-done').check(); assert.equal(await page.locator('.exploration-pin').count(), 28);
    await page.locator('#layers-toggle').click(); assert.equal(await page.locator('[data-count-for="board"]').innerText(), '18'); await page.locator('#close-layers').click();
    await page.locator('#hide-done').uncheck(); assert.equal(await page.locator('.exploration-pin').count(), 29);
  });
  await check('地区、筛选、视野与决策持久化且剧透默认隐藏', async () => {
    await fresh(); await page.evaluate(() => atlas.selectQuest('q416')); await page.locator('#reveal').click();
    await page.locator('.decision-choice').first().click(); await catalogAction(page, '#expansion', 'selectOption', 'baw');
    await page.evaluate(() => atlas.map.setView([10, 12], 3.25, {animate: false})); await page.waitForTimeout(200);
    await page.reload(); await page.waitForFunction(() => window.atlas?.progress);
    const value = await page.evaluate(() => ({region: atlas.state.region, exp: atlas.state.exp, choice: atlas.state.choices['q416:0'], spoilers: atlas.state.spoilers, revealed: atlas.state.revealed, zoom: atlas.map.getZoom(), center: atlas.map.getCenter()}));
    assert.equal(value.region, 'toussaint'); assert.equal(value.exp, 'baw'); assert.equal(value.choice, 0); assert.equal(value.spoilers, false); assert.deepEqual(value.revealed, []);
    assert.equal(value.zoom, 3.25); assert.ok(await page.evaluate(center => atlas.map.project(center, 3.25).distanceTo(atlas.map.project([10,12], 3.25)) <= 1, [value.center.lat,value.center.lng]), 'Restored view differs by more than one map pixel: '+JSON.stringify(value.center));
    assert.equal(await page.locator('.decision-choice').count(), 0);
  });
  await check('个人备份导出、清空与预览恢复等价', async () => {
    await fresh(); await page.locator('[data-record="done"]').click(); await page.locator('[data-record="starred"]').click();
    await catalogAction(page, '#progress-toggle', 'click'); const downloading = page.waitForEvent('download'); await page.locator('#progress-export').click(); const download = await downloading;
    const bytes = fs.readFileSync(await download.path()), value = JSON.parse(bytes); assert.equal(value.schemaVersion, 1); assert.equal(value.records.quest.q67.done, true); assert.equal(value.app, 'witcher-quest-atlas');
    await page.evaluate(() => localStorage.clear()); await page.reload(); await page.waitForFunction(() => window.atlas?.progress); assert.equal((await flags('quest', 'q67')).done, false);
    await catalogAction(page, '#progress-toggle', 'click'); await page.locator('#progress-import').setInputFiles({name: 'progress.json', mimeType: 'application/json', buffer: bytes});
    await page.waitForFunction(() => !document.querySelector('#progress-apply').disabled); assert.equal((await flags('quest', 'q67')).done, false);
    await page.locator('#progress-apply').click(); assert.deepEqual(await flags('quest', 'q67'), {done: true, starred: true});
    await page.screenshot({path: path.join(root, 'evidence/progress-desktop.png')});
  });
  await check('损坏、未知版本、恶意字段和超大备份不覆盖记录', async () => {
    await fresh(); await page.locator('[data-record="done"]').click(); await catalogAction(page, '#progress-toggle', 'click');
    await page.waitForFunction(() => !atlas.map._animatingZoom && !atlas.map._panAnim?._inProgress); await page.waitForTimeout(250);
    const original = await page.evaluate(() => localStorage.getItem(atlas.progress.storageKey));
    const valid = JSON.parse(original), payloads = ['{broken', JSON.stringify({...valid, schemaVersion: 99}), JSON.stringify({...valid, records: {quest: {q67: {done: 'yes', starred: false}}, point: {}}}), '{"app":"witcher-quest-atlas","schemaVersion":1,"records":{"quest":{"__proto__":{"done":true,"starred":false}},"point":{}}}', 'x'.repeat(1024*1024+1)];
    for (const text of payloads) {
      await page.locator('#progress-import').setInputFiles({name: 'bad.json', mimeType: 'application/json', buffer: Buffer.from(text)});
      await page.waitForFunction(() => document.querySelector('#import-feedback').textContent.includes('导入未执行'));
      assert.equal(await page.locator('#progress-apply').isDisabled(), true); assert.equal(await page.evaluate(() => localStorage.getItem(atlas.progress.storageKey)), original);
    }
    assert.equal(await page.evaluate(() => ({}).done), undefined);
  });
  await check('失效 ID 与数据版本变化保留迁移账目', async () => {
    await fresh(); let value = await page.evaluate(() => window.atlas?.progress.snapshot());
    value.dataVersion.catalog = 'old'; value.records.quest.q67 = {done: true, starred: true}; value.records.point['p-retired-source'] = {done: true, starred: false};
    value.choices = [{questId: 'q67', decisionId: 'retired-decision', optionLabel: 'old option'}];
    await catalogAction(page, '#progress-toggle', 'click'); await page.locator('#progress-import').setInputFiles({name: 'old.json', mimeType: 'application/json', buffer: Buffer.from(JSON.stringify(value))});
    await page.waitForFunction(() => !document.querySelector('#progress-apply').disabled); await page.locator('#progress-apply').click();
    assert.equal((await flags('quest', 'q67')).done, true); assert.match(await page.locator('#orphaned-records').innerText(), /2 条/);
    const restored = await page.evaluate(() => window.atlas?.progress.snapshot()); assert.equal(restored.orphaned.length, 2); assert.equal(restored.records.quest.q67.done, true);
    assert.equal(await page.evaluate(v => atlas.progress.parse(v).orphaned.length, restored), 2);
  });
  await check('任务与探索点深链接及未知链接提示', async () => {
    await fresh(); await page.goto(baseURL + '?region=toussaint&quest=q416'); await page.waitForFunction(() => window.atlas?.progress);
    assert.equal(await page.evaluate(() => atlas.state.selected), 'q416'); assert.equal(await page.evaluate(() => atlas.state.region), 'toussaint'); assert.equal(await page.locator('.decision-choice').count(), 0);
    const point = await page.evaluate(() => atlas.exploration.data.points.find(p => p.region === 'white-orchard' && p.type === 'stash'));
    await page.goto(baseURL + '?region=white-orchard&point=' + point.id); await page.waitForFunction(() => window.atlas?.progress); assert.equal(await page.evaluate(() => atlas.state.selectedPoint), point.id);
    await page.goto(baseURL + '?quest=no-such-quest'); await page.waitForFunction(() => window.atlas?.progress); assert.equal(await page.evaluate(() => atlas.state.selected), null); assert.match(await page.locator('#route-notice').innerText(), /未找到/);
    await page.goto(baseURL + '?region=not-real'); await page.waitForFunction(() => window.atlas?.progress); assert.match(await page.locator('#route-notice').innerText(), /地区未找到/);
  });
  await check('浏览器前进后退恢复同一对象及地区', async () => {
    await fresh(); await page.evaluate(() => atlas.selectQuest('q416')); await page.evaluate(() => atlas.selectQuest('q37'));
    await page.goBack(); await page.waitForFunction(() => atlas.state.selected === 'q416'); assert.equal(await page.evaluate(() => atlas.state.region), 'toussaint');
    await page.goBack(); await page.waitForFunction(() => atlas.state.selected === 'q67');
    await page.goForward(); await page.waitForFunction(() => atlas.state.selected === 'q416');
    await page.locator('[data-region="skellige"]').click(); assert.equal(new URL(page.url()).searchParams.get('region'), 'skellige');
    await page.goBack(); await page.waitForFunction(() => atlas.state.selected === 'q416');
  });
  await check('分享链接不泄漏完成、收藏、决策或剧透状态', async () => {
    await fresh(); await page.locator('[data-record="done"]').click(); await page.locator('#reveal').click(); await page.locator('.decision-choice').first().click();
    await page.locator('[data-share="quest"]').click(); const link = await page.locator('.share-url').inputValue(), params = [...new URL(link).searchParams.keys()].sort();
    assert.deepEqual(params, ['quest', 'region']); assert.equal(new URL(link).searchParams.get('quest'), 'q67');
    const stranger = await browser.newContext(), other = await stranger.newPage(); await other.goto(link); await other.waitForFunction(() => window.atlas?.progress);
    assert.equal(await other.evaluate(() => window.atlas?.progress.flag('quest', 'q67', 'done')), false); assert.equal(await other.locator('.decision-choice').count(), 0); await stranger.close();
  });
  await check('存储不可用与损坏存储不阻碍地图且有明确提示', async () => {
    await fresh(); await context.addInitScript(() => {Storage.prototype.getItem = () => {throw Error('blocked')}; Storage.prototype.setItem = () => {throw Error('blocked')};});
    await page.reload(); await page.waitForFunction(() => window.atlas?.progress); assert.match(await page.locator('#storage-notice').innerText(), /无法读取/); assert.equal(await page.locator('.exploration-pin').count(), 29); await page.locator('[data-record="done"]').click(); assert.equal((await flags('quest','q67')).done,true);
    await fresh(); await page.evaluate(() => localStorage.setItem(atlas.progress.storageKey, '{invalid')); await page.reload(); await page.waitForFunction(() => window.atlas?.progress); assert.equal(await page.evaluate(() => localStorage.getItem(atlas.progress.storageKey)), '{invalid'); assert.equal(await page.locator('.exploration-pin').count(), 29);
  });
  await check('手机直达、记录、备份与200%文字可操作', async () => {
    await fresh({viewport: {width: 390, height: 844}, hasTouch: true, isMobile: true}); await page.goto(baseURL + '?quest=q37'); await page.waitForFunction(() => window.atlas?.progress);
    assert.equal(await page.locator('#detail').isVisible(), true); await page.locator('[data-record="done"]').tap(); await page.locator('[data-record="starred"]').tap();
    await page.screenshot({path: path.join(root, 'evidence/progress-mobile-detail.png')});
    await page.locator('#mobile-list').tap(); await catalogAction(page, '#progress-toggle', 'tap'); assert.equal(await page.locator('#progress-dialog').isVisible(), true);
    await page.screenshot({path: path.join(root, 'evidence/progress-mobile.png')});
    await page.keyboard.press('Escape'); assert.equal(await page.locator('#progress-dialog').isVisible(), false);
    await page.addStyleTag({content:'html{font-size:32px !important}'}); await catalogAction(page, '#progress-toggle', 'tap'); assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1), false); await page.locator('#close-progress').tap();
  });
  await check('个人进度页面与资源无异常', async () => {assert.deepEqual(errors, []); assert.deepEqual(failed, []);});
  const result = {date: new Date().toISOString().slice(0,10), executionEnvironment:require('./execution-environment.cjs'), executedAt:new Date().toISOString(), status:checks.every(c=>c.status==='pass')?'pass':'fail', passed:checks.filter(c=>c.status==='pass').length, total:checks.length, checks, pageErrors:errors, httpFailures:failed, runtimeInputHashes:Object.fromEntries(files.map(f=>[f,crypto.createHash('sha256').update(fs.readFileSync(path.join(root,'dist',f))).digest('hex')]))};
  fs.writeFileSync(path.join(root,'evidence/progress-validation.json'),JSON.stringify(result,null,2)); console.log(JSON.stringify(result)); await browser.close(); if(result.status!=='pass')process.exitCode=1;
})().catch(error=>{console.error(error);process.exitCode=1});
