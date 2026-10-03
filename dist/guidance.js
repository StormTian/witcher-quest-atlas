'use strict';
window.AtlasGuidance={
  create({config,data,state,progress,esc,onQuest,onUpdate,hasSpoilers}){
    const byId=Object.fromEntries(data.quests.map(q=>[q.id,q])),dialog=document.querySelector('#checklist-dialog');
    const gameLabels={unknown:'未知', 'not-started':'未开始',active:'进行中',success:'游戏日志成功',failure:'游戏日志失败'};
    const triLabels={unknown:'未记录完整／未知',yes:'所列条件已记录满足',no:'所列条件有不满足项'};
    const options=(values,current)=>Object.entries(values).map(([v,label])=>`<option value="${v}"${v===current?' selected':''}>${esc(label)}</option>`).join('');
    state.story ||= {questStates:{},facts:{},stage:'before-isle'};
    function questState(qid){return `<label class="game-state">游戏状态 <select data-game-state="${esc(qid)}" aria-label="${esc(byId[qid]?.title)}的游戏状态">${options(gameLabels,state.story.questStates[qid]||'unknown')}</select></label>`;}
    function fact(f){return `<label class="story-fact">${esc(f.name)}<select data-story-fact="${esc(f.id)}" aria-label="${esc(f.name)}">${options({unknown:'未知',yes:'已发生',no:'未发生'},state.story.facts[f.id]||'unknown')}</select><a href="${esc(f.source)}" target="_blank" rel="noopener">依据 ↗</a></label>`;}
    function rulesFor(q){return config.rules.filter(r=>r.questId===q.id);}
    function ruleHTML(r){const value=StoryRules.evaluate(r.id,state);return `<div class="condition-result ${value}" data-rule="${r.id}" data-result="${value}"><strong>${esc(r.label)}</strong><span>${triLabels[value]}</span><p class="fine">${esc(r.note)} 所列条件满足仍需在游戏中确认触发。</p><a href="${esc(r.source)}" target="_blank" rel="noopener">条件依据 ↗</a></div>`;}
    function incoming(q){
      const rows=[];
      for(const other of data.quests)for(const [index,node] of other.decisions.entries()){
        if(!StoryRules.decisionAllowed(other.id,index,state.choices))continue;
        const option=node.options[state.choices[other.id+':'+index]];
        if(option?.links.includes(q.id))rows.push({other,node,option});
      }
      return rows;
    }
    function effects(q){
      if(!hasSpoilers(q))return '';
      const lines=incoming(q).map(({other,node,option})=>`<li><button data-guidance-quest="${esc(other.id)}">${esc(other.title)}</button> · ${esc(option.label)}<p>${esc(option.effect)}</p><a href="${esc(node.source.url)}" target="_blank" rel="noopener">后果依据 ↗</a></li>`);
      return lines.length?`<section class="detail-section decision-effects"><h3>已选决策对本任务的提示</h3><ul>${lines.join('')}</ul><p class="fine">只展示你已记录的有效节点，不自动改选项或结局演算输入。</p></section>`:'';
    }
    function detail(q){
      const groups=StoryRules.sourceGroups(q,state.story.questStates),rules=rulesFor(q);
      const rows=groups.map(g=>`<div class="source-condition-group"><h4>${{all:'来源要求全部', 'any-required':'来源任一必要项',any:'来源任一线索'}[g.mode]} · ${triLabels[g.result]}</h4>${g.rows.map(r=>`<div class="source-condition-row"><button data-guidance-quest="${esc(r.questId)}">${esc(byId[r.questId].title)}</button><span>来源状态：${r.state==='JS_Success'?'成功':r.state==='JS_Active'?'进行中':'进行中或结束'} · ${triLabels[r.result]}</span>${questState(r.questId)}</div>`).join('')}</div>`).join('');
      const facts=config.facts.filter(f=>f.questId===q.id||q.id==='q301'&&['ves-battle-reached','polished-crystal-found'].includes(f.id)||['q407','q405','q404'].includes(q.id)&&f.id==='elder-cave-entered');
      return `<section class="detail-section requirement-panel"><h3>条件与游戏阶段记录</h3><p class="fine">完成勾选是个人记录，不等于游戏日志成功。以下状态由你填写，未填写保留未知；社区条件只解析了任务级片段，不是全部接取条件。</p>${questState(q.id)}${facts.map(fact).join('')}${q.id==='q301'?questState('q186'):''}${rules.map(ruleHTML).join('')}${rows}${q.requirementsMeta?.unresolvedGuidCount?`<p class="fine">来源还含 ${q.requirementsMeta.unresolvedGuidCount} 项目标／未解析条件，不能仅凭上表判断可接取。</p>`:''}</section>`+effects(q);
    }
    function renderDialog(){
      if(!dialog.open)return;
      document.querySelector('#checklist-stage').value=state.story.stage;
      document.querySelector('#checklist-hide-done').checked=state.hideDone;
      const entries=config.entries.filter(e=>(state.story.stage==='all'||e.stage===state.story.stage)&&(!state.hideDone||!progress.flag('quest',e.questId,'done')));
      document.querySelector('#checklist-count').textContent=`${entries.length} 项已核对提醒 · 完成记录由你填写`;
      document.querySelector('#checklist-list').innerHTML=entries.map(e=>`<article class="checklist-entry" data-checklist-id="${esc(e.questId)}"><div><button data-guidance-quest="${esc(e.questId)}">${esc(byId[e.questId].title)}</button><label><input type="checkbox" data-checklist-done="${esc(e.questId)}"${progress.flag('quest',e.questId,'done')?' checked':''}>已处理</label></div><p>${esc(e.reminder)}</p><a href="${esc(e.source)}" target="_blank" rel="noopener">提醒依据 ↗</a></article>`).join('')||'<p class="fine">本阶段没有待显示的已核对提醒。</p>';
      bind();
    }
    function bind(){
      document.querySelectorAll('[data-guidance-quest]').forEach(b=>b.onclick=()=>{if(dialog.open)dialog.close();onQuest(b.dataset.guidanceQuest)});
      document.querySelectorAll('[data-game-state]').forEach(e=>e.onchange=()=>{state.story.questStates[e.dataset.gameState]=e.value;progress.save();onUpdate();renderDialog()});
      document.querySelectorAll('[data-story-fact]').forEach(e=>e.onchange=()=>{state.story.facts[e.dataset.storyFact]=e.value;progress.save();onUpdate();renderDialog()});
      document.querySelectorAll('[data-checklist-done]').forEach(e=>e.onchange=()=>{progress.setRecord('quest',e.dataset.checklistDone,'done',e.checked);renderDialog()});
    }
    document.querySelector('#checklist-stage').innerHTML=options({all:'全部阶段',...Object.fromEntries(config.stages.map(s=>[s.id,s.name]))},state.story.stage);
    document.querySelector('#checklist-toggle').onclick=()=>{dialog.showModal();renderDialog()};
    document.querySelector('#close-checklist').onclick=()=>dialog.close();
    document.querySelector('#checklist-stage').onchange=e=>{state.story.stage=e.target.value;progress.save();renderDialog()};
    document.querySelector('#checklist-hide-done').onchange=e=>{state.hideDone=e.target.checked;progress.save();onUpdate();renderDialog()};
    dialog.onclick=e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close()}};
    return {detail,bind,renderDialog,effects,config,hasEffects:q=>incoming(q).length>0};
  }
};
