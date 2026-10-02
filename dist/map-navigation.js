'use strict';
window.MapNavigation={create(map,getRegion){
 const views=new Map(),step=.25,reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
 let current=null,pending=null,intendedZoom=null,applying=false,wheel=0,wheelTimer,observer;
 const overview=document.querySelector('#map-overview'),box=document.querySelector('#overview-viewport');
 function bounds(r){return r.code==='WO'?[[-77.6929,-180],[76.5985,180]]:[[-85.0511,-180],[85.0511,180]]}
 function update(){
  if(!map._loaded||!current)return;
  const z=map.getZoom(),r=getRegion();
  document.querySelector('#zoom-level').textContent=(2**(z-r.zoom)).toFixed(1)+'×';
  document.querySelector('#zoom-in').disabled=z>=map.getMaxZoom();
  document.querySelector('#zoom-out').disabled=z<=map.getMinZoom();
  const b=map.getBounds(),nw=map.project(b.getNorthWest(),0),se=map.project(b.getSouthEast(),0);
  const x=Math.max(0,Math.min(256,nw.x)),y=Math.max(0,Math.min(256,nw.y));
  box.setAttribute('x',x);box.setAttribute('y',y);
  box.setAttribute('width',Math.max(1,Math.min(256,se.x)-x));
  box.setAttribute('height',Math.max(1,Math.min(256,se.y)-y));
 }
 function apply(){
  if(!pending||applying||map._animatingZoom)return;
  const next=pending;pending=null;
  if(next.zoom===map.getZoom()){intendedZoom=null;return;}
  applying=true;
  if(next.anchor)map.setZoomAround(next.anchor,next.zoom,{animate:!reduced});
  else map.setZoom(next.zoom,{animate:!reduced});
 }
 function zoomBy(delta,anchor){
  const from=intendedZoom??map.getZoom();
  intendedZoom=Math.max(map.getMinZoom(),Math.min(map.getMaxZoom(),Math.round((from+delta)/step)*step));
  pending={zoom:intendedZoom,anchor};apply();
 }
 function remember(){if(current&&map._loaded)views.set(current,{center:map.getCenter(),zoom:map.getZoom()})}
 function enter(r){
  remember();pending=null;intendedZoom=null;applying=false;wheel=0;clearTimeout(wheelTimer);current=r.id;
  map.setMaxBounds(null);
  map.setMinZoom(1);map.setMaxZoom(r.max+.5);
  const view=views.get(r.id)||{center:r.center,zoom:r.zoom};
  map.setView(view.center,view.zoom,{animate:false});
  if(r.code)map.setMaxBounds(bounds(r));
  document.querySelector('#overview-image').setAttribute('href',r.code?`assets/tiles/${r.code}/0/0/0.png`:'');
  overview.setAttribute('aria-label',r.title+'概览；点击定位，亮框是当前视野');update();
 }
 function reset(){const r=getRegion();pending=null;intendedZoom=null;applying=false;wheel=0;clearTimeout(wheelTimer);map.setView(r.center,r.zoom,{animate:false});}
 const surface=map.getContainer();
 surface.addEventListener('wheel',e=>{
  e.preventDefault();
  const pixels=e.deltaY*(e.deltaMode===1?16:e.deltaMode===2?surface.clientHeight:1);
  wheel+=pixels;
  const anchor=map.mouseEventToContainerPoint(e);
  clearTimeout(wheelTimer);
  wheelTimer=setTimeout(()=>{if(Math.abs(wheel)>1)zoomBy(wheel<0?step:-step,anchor);wheel=0;},70);
 },{passive:false});
 overview.addEventListener('click',e=>{
  const svg=overview.querySelector('svg'),rect=svg.getBoundingClientRect();
  const p=e.detail?L.point((e.clientX-rect.left)/rect.width*256,(e.clientY-rect.top)/rect.height*256):L.point(128,128);
  map.panTo(map.unproject(p,0),{animate:!reduced,duration:.2});
 });
 map.on('move zoom resize',update);
 map.on('zoomend',()=>{applying=false;update();if(pending)requestAnimationFrame(apply);else intendedZoom=null});map.on('moveend',remember);
 observer=new ResizeObserver(()=>{if(map._loaded)map.invalidateSize({animate:false,pan:true})});observer.observe(surface);
 return {enter,zoomBy,reset,update,views};
}};
