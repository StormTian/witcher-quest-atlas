/* Independently authored guide logic; source and game-test limits appear in the interface. */
(function(root){
  function ciriEnding({snow,lodge,lab,grave,visit,payment,war}){
    for(const [k,v] of Object.entries({snow,lodge,lab,grave,visit,payment}))if(typeof v!=='boolean')throw new TypeError(k+' must be boolean');
    if(!['nilfgaard','dijkstra','radovid'].includes(war))throw new TypeError('Unknown war result');
    const total=visit?5:4,positive=[snow,lodge,lab,grave].filter(Boolean).length+(visit&&payment?1:0),negative=total-positive;
    const outcome=positive<negative?'tragedy':visit&&war==='nilfgaard'?'empress':'witcher';
    return {outcome,positive,negative,total,boundary:!visit&&positive===2};
  }
  function bloodWineEnding({route,ribbon,diary,story,fifth,forgive}){
    if(!['fairy','elder'].includes(route))throw new TypeError('Unknown route');
    for(const [k,v] of Object.entries({ribbon,diary,story,fifth,forgive}))if(typeof v!=='boolean')throw new TypeError(k+' must be boolean');
    if(route==='elder')return {outcome:'both-die',reason:'elder-lock'};
    if(!ribbon)return {outcome:'syanna-dies',reason:'no-ribbon'};
    return {outcome:diary&&story&&fifth&&forgive?'reconcile':'both-die',reason:diary&&story&&fifth&&forgive?'all-conditions':'missing-condition'};
  }
  const api={ciriEnding,bloodWineEnding};root.QuestLogic=api;if(typeof module!=='undefined')module.exports=api;
})(typeof window!=='undefined'?window:globalThis);
