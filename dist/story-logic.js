/* Tri-state source conditions. Personal done/starred flags are never game states. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.StoryRules=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const values=['yes','no','unknown'];
  const known=v=>values.includes(v)?v:'unknown';
  const all=xs=>xs.some(x=>x==='no')?'no':xs.every(x=>x==='yes')?'yes':'unknown';
  const any=xs=>xs.some(x=>x==='yes')?'yes':xs.every(x=>x==='no')?'no':'unknown';
  function gameState(actual,expected){
    if(!['active','success','failure','not-started'].includes(actual))return 'unknown';
    if(expected==='JS_Success')return actual==='success'?'yes':'no';
    if(expected==='JS_Active')return actual==='active'?'yes':'no';
    if(expected==='active-or-complete')return actual==='not-started'?'no':'yes';
    return 'unknown';
  }
  function sourceGroups(quest,states={}){
    return ['all','any-required','any'].flatMap(mode=>{
      const rows=(quest.requirements||[]).filter(r=>r.mode===mode).map(r=>({...r,result:gameState(states[r.questId],r.state)}));
      return rows.length?[{mode,rows,result:mode==='all'?all(rows.map(r=>r.result)):any(rows.map(r=>r.result))}]:[];
    });
  }
  const choice=(choices,key)=>Number.isInteger(choices?.[key])?choices[key]:null;
  const match=(value,wanted)=>value===null?'unknown':value===wanted?'yes':'no';
  function evaluate(rule,state){
    const story=state.story||{},facts=story.facts||{},states=story.questStates||{},choices=state.choices||{};
    const c=key=>choice(choices,key),f=key=>known(facts[key]);
    if(rule==='assassination')return all([gameState(states.q186,'JS_Success'),f('ves-battle-reached'),f('polished-crystal-found'),match(c('q287:0'),0)]);
    if(rule==='hos-rescue')return match(c('q361:0'),0);
    if(rule==='keira-aid')return match(c('q99:0'),0);
    if(rule==='yen-romance')return match(c('q200:0'),0);
    if(rule==='dual-romance')return all([match(c('q145:0'),0),match(c('q182:0'),0),match(c('q200:0'),0)]);
    if(rule==='triss-romance')return all([match(c('q145:0'),0),match(c('q182:0'),0)]);
    if(rule==='baw-fairy'){
      if(f('elder-cave-entered')==='yes')return 'no';
      const fairy=c('q404:0')===1||c('q405:0')===0;
      // An unrecorded cave visit can still contradict an earlier intended route.
      if(fairy&&f('elder-cave-entered')==='no')return 'yes';
      return 'unknown';
    }
    if(rule==='baw-elder')return f('elder-cave-entered');
    return 'unknown';
  }
  function decisionAllowed(qid,index,choices){
    if(qid==='q235'&&index===2)return choices['q235:1']===0;
    if(qid==='q361'&&index===1)return choices['q361:0']===0;
    return true;
  }
  return {all,any,gameState,sourceGroups,evaluate,decisionAllowed};
});
