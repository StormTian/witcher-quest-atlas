'use strict';
window.AtlasProgress = {
  create({state, data, points, regions, navigation, esc, onUpdate, onNavigate, onRegion}) {
    const storageKey = 'witcher-atlas-progress-v1';
    const known = {quest: new Map(data.quests.map(q => [q.id, q])), point: new Map(points.points.map(p => [p.id, p]))};
    let records = {quest: {}, point: {}}, orphaned = [], pendingImport = null, timer, ready = false, routing = false, loadBlocked = false, lastRaw;
    const dialog = document.querySelector('#progress-dialog');
    const notify = (text, failed = false) => {
      const node = document.querySelector('#progress-status');
      node.textContent = text; node.classList.toggle('save-error', failed);
      document.querySelector('#storage-notice').textContent = failed ? text : '';
    };
    const flag = (kind, id, name) => Boolean(records[kind]?.[id]?.[name]);
    const allows = (kind, id) => (!state.hideDone || !flag(kind, id, 'done')) &&
      (state.progressView === 'all' || flag(kind, id, state.progressView === 'done' ? 'done' : 'starred'));
    const isObject = value => value !== null && typeof value === 'object' && !Array.isArray(value);
    const identifier = value => typeof value === 'string' && /^[a-zA-Z0-9_-]{1,100}$/.test(value) && !['__proto__', 'prototype', 'constructor'].includes(value);
    const defaults = {region: 'velen', type: 'all', exp: 'all', query: '', global: false, branch: false, landmarks: true, layers: {quests: true, ...Object.fromEntries(points.categories.map(c => [c.id, c.defaultEnabled === true]))}, hideDone: false, progressView: 'all'};
    function parse(value) {
      if (!isObject(value) || value.app !== 'witcher-quest-atlas' || value.schemaVersion !== 1 || !isObject(value.records)) throw Error('不是支持的巫师3地图备份，或备份版本不受支持。');
      const result = {records: {quest: Object.create(null), point: Object.create(null)}, orphaned: [], preferences: {...defaults, layers: {...defaults.layers}}, choices: {}, views: {}, selected: null, sim: {}, baw: {}};
      const addRecord = (kind, id, flags) => {
        if (!['quest', 'point'].includes(kind) || !identifier(id) || !isObject(flags) || typeof flags.done !== 'boolean' || typeof flags.starred !== 'boolean') throw Error('备份中的完成或收藏记录格式不正确。');
        if (known[kind].has(id)) result.records[kind][id] = {done: flags.done, starred: flags.starred};
        else result.orphaned.push({kind, id, done: flags.done, starred: flags.starred});
      };
      for (const kind of ['quest', 'point']) {
        if (!isObject(value.records[kind])) throw Error('备份缺少任务或探索点记录。');
        for (const [id, flags] of Object.entries(value.records[kind])) addRecord(kind, id, flags);
      }
      if (value.orphaned !== undefined && !Array.isArray(value.orphaned)) throw Error('未匹配记录格式不正确。');
      for (const item of value.orphaned || []) {
        if (item.kind === 'decision') {
          if (!identifier(item.questId) || !identifier(item.decisionId) || typeof item.optionLabel !== 'string' || item.optionLabel.length > 300) throw Error('未匹配决策格式不正确。');
          result.orphaned.push({...item});
        } else addRecord(item.kind, item.id, item);
      }
      const pref = value.preferences || {};
      if (!isObject(pref)) throw Error('筛选偏好格式不正确。');
      if (regions.some(r => r.id === pref.region)) result.preferences.region = pref.region;
      if (['all', ...new Set(data.quests.map(q => q.type))].includes(pref.type)) result.preferences.type = pref.type;
      if (['all', 'base', 'hos', 'baw'].includes(pref.exp)) result.preferences.exp = pref.exp;
      if (typeof pref.query === 'string' && pref.query.length <= 300) result.preferences.query = pref.query;
      for (const key of ['global', 'branch', 'landmarks', 'hideDone']) if (typeof pref[key] === 'boolean') result.preferences[key] = pref[key];
      if (['all', 'done', 'starred'].includes(pref.progressView)) result.preferences.progressView = pref.progressView;
      if (isObject(pref.layers)) for (const key of ['quests', ...points.categories.map(c => c.id)]) if (typeof pref.layers[key] === 'boolean') result.preferences.layers[key] = pref.layers[key];
      if (value.choices !== undefined && !Array.isArray(value.choices)) throw Error('决策记录格式不正确。');
      for (const choice of value.choices || []) {
        if (!isObject(choice) || !identifier(choice.questId) || !identifier(choice.decisionId) || typeof choice.optionLabel !== 'string' || choice.optionLabel.length > 300) throw Error('决策记录格式不正确。');
        const q = known.quest.get(choice.questId), index = q?.decisions.findIndex(d => d.id === choice.decisionId) ?? -1;
        const option = index >= 0 ? q.decisions[index].options.findIndex(o => o.label === choice.optionLabel) : -1;
        if (option >= 0) result.choices[q.id + ':' + index] = option;
        else result.orphaned.push({kind: 'decision', ...choice});
      }
      for (const [kind, target] of [['sim', state.sim], ['baw', state.baw]]) {
        if (!isObject(value[kind])) continue;
        for (const [key, fallback] of Object.entries(target)) {
          const candidate = value[kind][key];
          if (typeof fallback === 'boolean' && typeof candidate === 'boolean') result[kind][key] = candidate;
          else if (kind === 'sim' && key === 'war' && ['nilfgaard', 'dijkstra', 'radovid'].includes(candidate)) result[kind][key] = candidate;
          else if (kind === 'baw' && key === 'route' && ['fairy', 'elder'].includes(candidate)) result[kind][key] = candidate;
        }
      }
      if (isObject(value.views)) for (const region of regions) {
        const view = value.views[region.id];
        if (isObject(view) && Array.isArray(view.center) && view.center.length === 2 && view.center.every(Number.isFinite) && Math.abs(view.center[0]) <= 85.0512 && Math.abs(view.center[1]) <= 180 && Number.isFinite(view.zoom) && view.zoom >= 1 && view.zoom <= region.max + .5) result.views[region.id] = {center: view.center, zoom: view.zoom};
      }
      if (isObject(value.selected) && ['quest', 'point'].includes(value.selected.kind) && known[value.selected.kind].has(value.selected.id)) result.selected = value.selected;
      return result;
    }
    function snapshot() {
      const preferences = Object.fromEntries(Object.keys(defaults).map(key => [key, state[key]]));
      const choices = [];
      for (const [key, optionIndex] of Object.entries(state.choices)) {
        const split = key.lastIndexOf(':'), q = known.quest.get(key.slice(0, split)), decision = q?.decisions[Number(key.slice(split + 1))], option = decision?.options[optionIndex];
        if (option) choices.push({questId: q.id, decisionId: decision.id, optionLabel: option.label});
      }
      const views = {};
      for (const [id, view] of navigation.views) views[id] = {center: Array.isArray(view.center) ? view.center : [view.center.lat, view.center.lng], zoom: view.zoom};
      return {app: 'witcher-quest-atlas', schemaVersion: 1, dataVersion: {catalog: data.meta.catalogVersion, exploration: points.meta.schemaVersion, source: points.meta.sourceCommit}, savedAt: new Date().toISOString(), records, orphaned, preferences, choices, views, sim: state.sim, baw: state.baw, selected: state.selected ? {kind: 'quest', id: state.selected} : state.selectedPoint ? {kind: 'point', id: state.selectedPoint} : null};
    }
    function save() {
      if (!ready || loadBlocked) return;
      clearTimeout(timer);
      try {
        const current = localStorage.getItem(storageKey);
        if (lastRaw !== undefined && current !== lastRaw) {
          loadBlocked = true;
          notify('本地记录已在页面外更改，已停止覆盖。请刷新读取最新记录，或导出当前记录。', true);
          return;
        }
        lastRaw = JSON.stringify(snapshot());
        localStorage.setItem(storageKey, lastRaw);
        notify('已保存在此浏览器。可导出备份后转移到其他设备。');
      }
      catch { notify('此浏览器无法保存进度，当前记录仅在本次页面中有效。请导出备份。', true); }
    }
    const touch = () => { if (ready) { clearTimeout(timer); timer = setTimeout(save, 100); } };
    function install(parsed) {
      loadBlocked = false; records = parsed.records; orphaned = parsed.orphaned;
      Object.assign(state, parsed.preferences); state.choices = parsed.choices;
      Object.assign(state.sim, parsed.sim); Object.assign(state.baw, parsed.baw);
      state.spoilers = false; state.revealed = [];
      navigation.views.clear();
      for (const [id, view] of Object.entries(parsed.views)) navigation.views.set(id, view);
    }
    function initial() {
      Object.assign(state, defaults, {layers: {...defaults.layers}});
      let saved = null;
      try { const raw = localStorage.getItem(storageKey); lastRaw = raw; if (raw) { saved = parse(JSON.parse(raw)); install(saved); } }
      catch { loadBlocked = true; notify('无法读取本地进度；地图仍可使用。原有记录没有被覆盖，请保留备份。', true); }
      return saved;
    }
    function shareURL(kind, id, region = state.region) {
      const url = new URL(location.pathname, location.origin);
      url.searchParams.set('region', region);
      if (kind && id) url.searchParams.set(kind, id);
      return url.href;
    }
    function selected(kind, id) {
      if (ready && !routing) {
        const href = shareURL(kind, id);
        if (location.href !== href) history.pushState({atlas: true}, '', href);
        save();
      }
    }
    function applyRoute(saved = null, first = false) {
      routing = true;
      try {
        const params = new URL(location.href).searchParams;
        const provided = params.has('region') || params.has('quest') || params.has('point');
        let region = params.get('region'), kind = params.has('quest') ? 'quest' : params.has('point') ? 'point' : null, id = kind ? params.get(kind) : null;
        let message = '';
        if (params.has('quest') && params.has('point')) { kind = null; message = '链接同时指定了任务和探索点，请使用单个对象的分享链接。'; }
        if (region && !regions.some(r => r.id === region)) { region = null; message = '链接中的地区未找到，已显示可用地图。'; }
        if (kind && !known[kind].has(id)) { kind = null; message = '链接中的任务或探索点未找到，已显示地区地图。'; }
        if (!provided && first && saved?.selected) { kind = saved.selected.kind; id = saved.selected.id; }
        if (!provided && first && !saved) { kind = 'quest'; id = 'q67'; }
        const restoringSelection = first && saved?.selected?.kind === kind && saved.selected.id === id && (!region || region === saved.preferences.region);
        if (kind) onNavigate(kind, id, !first || (provided && !restoringSelection));
        else onRegion(region || state.region);
        const notice = document.querySelector('#route-notice'); notice.textContent = message; notice.hidden = !message;
        if (first) history.replaceState({atlas: true}, '', shareURL(kind, kind ? id : null));
      } finally { routing = false; }
      ready = true; save();
    }
    function actions(kind, id) {
      return `<div class="record-actions"><button data-record="done" data-kind="${kind}" data-id="${esc(id)}" aria-pressed="${flag(kind, id, 'done')}">${flag(kind, id, 'done') ? '✓ 已完成 · 取消' : '标为完成'}</button><button data-record="starred" data-kind="${kind}" data-id="${esc(id)}" aria-pressed="${flag(kind, id, 'starred')}">${flag(kind, id, 'starred') ? '★ 已收藏 · 取消' : '☆ 收藏'}</button><button data-share="${kind}" data-id="${esc(id)}">分享定位</button></div><div class="share-output" hidden><label>定位链接<input class="share-url" readonly></label><span class="fine" role="status"></span></div>`;
    }
    function bindActions() {
      for (const button of document.querySelectorAll('[data-record]')) button.onclick = () => {
        const {kind, id, record} = button.dataset, flags = records[kind][id] || {done: false, starred: false};
        records[kind][id] = {...flags, [record]: !flags[record]}; save(); onUpdate(); render(); document.querySelector(`[data-record="${record}"][data-id="${id}"]`)?.focus({preventScroll:true});
      };
      for (const button of document.querySelectorAll('[data-share]')) button.onclick = async () => {
        const output = button.closest('.detail-top').querySelector('.share-output'), input = output.querySelector('input'), status = output.querySelector('[role="status"]');
        input.value = shareURL(button.dataset.share, button.dataset.id); output.hidden = false;
        try { await navigator.clipboard.writeText(input.value); status.textContent = '定位链接已复制。链接不包含个人进度或决策。'; }
        catch { input.focus(); input.select(); status.textContent = '请复制上面的链接。链接不包含个人进度或决策。'; }
      };
    }
    function render() {
      for (const [kind, label] of [['quest', '任务'], ['point', '探索点']]) {
        const list = [...known[kind].keys()], done = list.filter(id => flag(kind, id, 'done')).length, starred = list.filter(id => flag(kind, id, 'starred')).length;
        document.querySelector(`[data-progress-stat="${kind}"]`).textContent = `${label}：已完成 ${done} / ${list.length} · 收藏 ${starred}`;
      }
      document.querySelector('#orphaned-records').hidden = orphaned.length === 0;
      document.querySelector('#orphaned-records').textContent = orphaned.length ? `${orphaned.length} 条记录暂未匹配到当前数据，仍保留在备份中：` + orphaned.map(item => item.id || item.decisionId).join('、') : '';
      document.querySelector('#progress-view').value = state.progressView;
      document.querySelector('#hide-done').checked = state.hideDone;
    }
    document.querySelector('#progress-toggle').onclick = () => { render(); dialog.showModal(); };
    document.querySelector('#close-progress').onclick = () => dialog.close();
    document.querySelector('#progress-view').onchange = event => { state.progressView = event.target.value; onUpdate(); save(); };
    document.querySelector('#hide-done').onchange = event => { state.hideDone = event.target.checked; onUpdate(); save(); };
    document.querySelector('#progress-export').onclick = () => {
      const blob = new Blob([JSON.stringify(snapshot(), null, 2)], {type: 'application/json'}), url = URL.createObjectURL(blob), link = document.createElement('a');
      link.href = url; link.download = 'witcher3-personal-progress-' + new Date().toISOString().slice(0, 10) + '.json'; link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
    };
    document.querySelector('#progress-import').onchange = async event => {
      pendingImport = null; document.querySelector('#progress-apply').disabled = true;
      const feedback = document.querySelector('#import-feedback'), file = event.target.files[0]; if (!file) return;
      try {
        if (file.size > 1024 * 1024) throw Error('备份文件超过 1 MB，请选择个人进度 JSON。');
        pendingImport = parse(JSON.parse(await file.text()));
        const count = Object.keys(pendingImport.records.quest).length + Object.keys(pendingImport.records.point).length;
        feedback.textContent = `备份检查通过：${count} 个对象记录，${Object.keys(pendingImport.choices).length} 项决策，${pendingImport.orphaned.length} 条未匹配记录。点击“恢复此备份”后替换当前记录。`;
        document.querySelector('#progress-apply').disabled = false;
      } catch (error) { feedback.textContent = '导入未执行：' + error.message + ' 当前记录保持不变。'; }
    };
    document.querySelector('#progress-apply').onclick = () => {
      if (!pendingImport) return;
      try { lastRaw = localStorage.getItem(storageKey); } catch { lastRaw = undefined; }
      const saved = pendingImport; pendingImport = null; install(saved); routing = true;
      try { onRegion(state.region); if (saved.selected) onNavigate(saved.selected.kind, saved.selected.id, false); onUpdate(); }
      finally { routing = false; }
      history.replaceState({atlas: true}, '', shareURL(state.selected ? 'quest' : state.selectedPoint ? 'point' : null, state.selected || state.selectedPoint));
      document.querySelector('#progress-apply').disabled = true;
      document.querySelector('#import-feedback').textContent = '备份已恢复；未匹配记录继续保留。'; render(); save();
    };
    window.addEventListener('popstate', () => applyRoute());
    window.addEventListener('storage', event => {
      if (event.key !== storageKey) return;
      try {
        if (event.newValue === null) { lastRaw = null; loadBlocked = true; notify('本地记录已在其他标签页清空，请刷新后继续。', true); return; }
        const parsed = parse(JSON.parse(event.newValue));
        records = parsed.records; orphaned = parsed.orphaned; state.choices = parsed.choices;
        lastRaw = event.newValue; loadBlocked = false; onUpdate(); render();
      } catch { loadBlocked = true; notify('其他标签页的记录无法读取，已停止覆盖。请导出备份。', true); }
    });
    window.addEventListener('pagehide', save);
    navigation.onViewChange = touch;
    return {initial, applyRoute, allows, flag, actions, bindActions, render, touch, save, selected, snapshot, parse, storageKey};
  },
};
