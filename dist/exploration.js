'use strict';
window.ExplorationLayers = {
  create({data, map, state, regionMeta, placeName, esc, questCount, onSelect, onGroup, onApply, isEligible = () => true, isDone = () => false}) {
    const markers = L.layerGroup().addTo(map);
    const byId = Object.fromEntries(data.points.map(point => [point.id, point]));
    const categories = Object.fromEntries(data.categories.map(category => [category.id, category]));
    const options = document.querySelector('#layer-options');
    const keys = ['quests', 'landmarks', ...data.categories.map(category => category.id)];
    const get = key => key === 'landmarks' ? state.landmarks : state.layers[key];
    const set = (key, value) => key === 'landmarks' ? state.landmarks = value : state.layers[key] = value;
    let previous = null;
    let renderedPositions = [];
    options.innerHTML = [
      {id: 'quests', name: '任务标记', symbol: '◇'},
      {id: 'landmarks', name: '路标与地名', symbol: '•'},
      ...data.categories,
    ].map(category => `<label class="layer-option"><input type="checkbox" data-layer="${category.id}" checked><span class="layer-symbol ${category.id}" aria-hidden="true">${category.symbol}</span><span>${esc(category.name)}</span><span class="layer-count" data-count-for="${category.id}"></span></label>`).join('');

    function visible() {
      return data.points.filter(point => point.region === state.region && state.layers[point.type] && isEligible(point));
    }
    function sync() {
      document.querySelector('#layers-region').textContent = regionMeta().title + ' · 当前地区数量';
      for (const input of options.querySelectorAll('[data-layer]')) input.checked = get(input.dataset.layer);
      document.querySelector('[data-count-for="quests"]').textContent = questCount();
      document.querySelector('[data-count-for="landmarks"]').textContent = window.atlas.DATA.landmarks.filter(point => point.region === state.region).length;
      for (const category of data.categories) {
        document.querySelector(`[data-count-for="${category.id}"]`).textContent = data.points.filter(point => point.region === state.region && point.type === category.id && isEligible(point)).length;
      }
      document.querySelector('#hide-layers').disabled = !keys.some(get);
      document.querySelector('#restore-layers').disabled = previous === null;
      const total = data.points.filter(point => point.region === state.region && isEligible(point)).length;
      document.querySelector('#exploration-count').textContent = total ? `探索点 ${visible().length} / ${total}` : '';
    }
    function render() {
      if (!markers._map || !Number.isFinite(map.getZoom())) return;
      markers.clearLayers();
      const grouped = new Map();
      for (const point of visible()) {
        const p = map.latLngToContainerPoint(point.latlng);
        const key = map.getZoom() < 3.5 && !['power','board','stash'].includes(point.type) && state.selectedPoint !== point.id ? `${Math.floor(p.x/64)},${Math.floor(p.y/64)}` : point.id;
        if (!grouped.has(key)) grouped.set(key, []);
        grouped.get(key).push(point);
      }
      renderedPositions = [];
      for (const group of grouped.values()) {
        const point = group[0];
        const category = categories[point.type];
        const title = group.length > 1 ? `${group.length} 个探索点 · 点击选择` : point.title + ' · ' + placeName(point.nearbyLandmark) + '附近';
        const position = group.length > 1 ? group.reduce((sum,p)=>sum.map((n,i)=>n+p.latlng[i]/group.length),[0,0]) : point.latlng;
        renderedPositions.push(position);
        const select = () => group.length > 1 ? onGroup(group) : onSelect(point.id);
        const marker = L.marker(position, {
          title, keyboard: true, zIndexOffset: 500,
          icon: L.divIcon({
            className: 'exploration-marker',
            html: `<span class="exploration-pin ${point.type}${group.length>1 ? ' cluster' : ''}${isDone(point) && group.length===1 ? ' completed' : ''}${state.selectedPoint === point.id ? ' chosen' : ''}" ${group.length===1 ? `data-point="${esc(point.id)}"` : `data-point-group="${group.length}"`}><span aria-hidden="true">${group.length>1 ? group.length : category.symbol}</span></span>`,
            iconSize: [30, 30], iconAnchor: [15, 15],
          }),
        });
        marker.bindTooltip(esc(title), {direction: 'top', offset: [0, -13]});
        marker.on('click', select);
        marker.on('add', () => {
          L.DomEvent.on(marker.getElement(), 'keydown', event => {
            if (event.key !== 'Enter' && event.key !== ' ') return;
            L.DomEvent.stop(event);
            select();
          });
        });
        marker.addTo(markers);
      }
      sync();
    }
    options.onchange = event => {
      const input = event.target.closest('[data-layer]');
      if (!input) return;
      set(input.dataset.layer, input.checked);
      render();
      onApply();
    };
    document.querySelector('#hide-layers').onclick = () => {
      previous = Object.fromEntries(keys.map(key => [key, get(key)]));
      for (const key of keys) set(key, false);
      render();
      onApply();
    };
    document.querySelector('#restore-layers').onclick = () => {
      if (!previous) return;
      for (const key of keys) set(key, previous[key]);
      previous = null;
      render();
      onApply();
    };
    document.querySelector('#select-layers').onclick = () => {
      for (const key of keys) set(key, true);
      render(); onApply();
    };
    document.querySelector('#layer-search').oninput = event => {
      const needle = event.target.value.trim();
      for (const label of options.querySelectorAll('.layer-option')) label.hidden = !label.textContent.includes(needle);
    };
    const dialog = document.querySelector('#layers-dialog');
    document.querySelector('#layers-toggle').onclick = () => { sync(); dialog.showModal(); };
    document.querySelector('#close-layers').onclick = () => dialog.close();
    dialog.onclick = event => {
      if (event.target !== dialog) return;
      const rect = dialog.getBoundingClientRect();
      if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close();
    };
    map.on('zoomend moveend', render);
    return {data, markers, byId, categories, render, sync, visible, positions: () => renderedPositions};
  },
};
