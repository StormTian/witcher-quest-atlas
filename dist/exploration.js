'use strict';
window.ExplorationLayers = {
  create({data, map, state, regionMeta, placeName, esc, questCount, onSelect, onApply}) {
    const markers = L.layerGroup().addTo(map);
    const byId = Object.fromEntries(data.points.map(point => [point.id, point]));
    const categories = Object.fromEntries(data.categories.map(category => [category.id, category]));
    const options = document.querySelector('#layer-options');
    const keys = ['quests', 'landmarks', ...data.categories.map(category => category.id)];
    const get = key => key === 'landmarks' ? state.landmarks : state.layers[key];
    const set = (key, value) => key === 'landmarks' ? state.landmarks = value : state.layers[key] = value;
    let previous = null;
    options.innerHTML = [
      {id: 'quests', name: '任务标记', symbol: '◇'},
      {id: 'landmarks', name: '路标与地名', symbol: '•'},
      ...data.categories,
    ].map(category => `<label class="layer-option"><input type="checkbox" data-layer="${category.id}" checked><span class="layer-symbol ${category.id}" aria-hidden="true">${category.symbol}</span><span>${esc(category.name)}</span><span class="layer-count" data-count-for="${category.id}"></span></label>`).join('');

    function visible() {
      return data.points.filter(point => point.region === state.region && state.layers[point.type]);
    }
    function sync() {
      document.querySelector('#layers-region').textContent = regionMeta().title + ' · 当前地区数量';
      for (const input of options.querySelectorAll('[data-layer]')) input.checked = get(input.dataset.layer);
      document.querySelector('[data-count-for="quests"]').textContent = questCount();
      document.querySelector('[data-count-for="landmarks"]').textContent = window.atlas.DATA.landmarks.filter(point => point.region === state.region).length;
      for (const category of data.categories) {
        document.querySelector(`[data-count-for="${category.id}"]`).textContent = data.points.filter(point => point.region === state.region && point.type === category.id).length;
      }
      document.querySelector('#hide-layers').disabled = !keys.some(get);
      document.querySelector('#restore-layers').disabled = previous === null;
      const total = data.points.filter(point => point.region === state.region).length;
      document.querySelector('#exploration-count').textContent = total ? `探索点 ${visible().length} / ${total}` : '';
    }
    function render() {
      markers.clearLayers();
      for (const point of visible()) {
        const category = categories[point.type];
        const title = point.title + ' · ' + placeName(point.nearbyLandmark) + '附近';
        const marker = L.marker(point.latlng, {
          title, keyboard: true, zIndexOffset: 500,
          icon: L.divIcon({
            className: 'exploration-marker',
            html: `<span class="exploration-pin ${point.type}${state.selectedPoint === point.id ? ' chosen' : ''}" data-point="${esc(point.id)}"><span aria-hidden="true">${category.symbol}</span></span>`,
            iconSize: [30, 30], iconAnchor: [15, 15],
          }),
        });
        marker.bindTooltip(esc(title), {direction: 'top', offset: [0, -13]});
        marker.on('click', () => onSelect(point.id));
        marker.addTo(markers);
        L.DomEvent.on(marker.getElement(), 'keydown', event => {
          if (event.key !== 'Enter' && event.key !== ' ') return;
          L.DomEvent.stop(event);
          onSelect(point.id);
        });
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
    const dialog = document.querySelector('#layers-dialog');
    document.querySelector('#layers-toggle').onclick = () => { sync(); dialog.showModal(); };
    document.querySelector('#close-layers').onclick = () => dialog.close();
    dialog.onclick = event => {
      if (event.target !== dialog) return;
      const rect = dialog.getBoundingClientRect();
      if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close();
    };
    return {data, markers, byId, categories, render, sync, visible};
  },
};
