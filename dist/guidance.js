'use strict';
window.AtlasGuidance={
  create({config,data,state,progress,esc,onQuest,onUpdate,hasSpoilers}){
    const byId=Object.fromEntries(data.quests.map(q=>[q.id,q])),dialog=document.querySelector('#checklist-dialog'),flowDialog=document.querySelector('#flow-dialog');
    const flowSuccessors=new Map(data.quests.map(q=>[q.id,[]])),flowOpen=new Set();
    for(const q of data.quests)for(const predecessor of new Set(q.predecessors||[]))flowSuccessors.get(predecessor)?.push(q);
    const typeNames={main:'主线',side:'支线',contract:'委托',scavenger:'套装',treasure:'寻宝',encounter:'遭遇'},expansionNames={base:'游戏本体',hos:'石之心',baw:'血与酒'},regionNames={'white-orchard':'白果园',velen:'威伦',skellige:'史凯利杰','kaer-morhen':'凯尔莫罕',toussaint:'陶森特',vizima:'维吉玛王宫'};
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
    function possibleIncoming(q){
      const rows=[];
      for(const other of data.quests)for(const [index,node] of other.decisions.entries()){
        if(!StoryRules.decisionAllowed(other.id,index,state.choices))continue;
        for(const option of node.options)if(option.links.includes(q.id))rows.push({other,node,option});
      }
      return rows;
    }
    function effects(q){
      const possible=possibleIncoming(q);
      if(!hasSpoilers(q)&&possible.length)return '';
      const selected=incoming(q);
      if(selected.length){
        const lines=selected.map(({other,node,option})=>`<li><button data-guidance-quest="${esc(other.id)}">${esc(other.title)}</button> · ${esc(option.label)}<p>${esc(option.effect)}</p><a href="${esc(node.source.url)}" target="_blank" rel="noopener">后果依据 ↗</a></li>`);
        return `<section class="detail-section decision-effects"><h3>已选决策对本任务的提示</h3><ul>${lines.join('')}</ul><p class="fine">只展示你已记录的有效选择；其他未记录的分支不会在这里展开。</p></section>`;
      }
      const message=possible.length
        ?`当前没有可展示的已选决策报告。目录中有 ${possible.length} 条已整理选项关联到本任务；请在对应任务详情中记录实际选择后查看结果。`
        :'当前目录没有已整理、指向本任务的决策关系。这里暂无报告不代表任务没有影响。';
      return `<section class="detail-section decision-effects decision-effects-empty"><h3>其他任务对本任务的影响</h3><p>${message}</p></section>`;
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
    function renderFlowDialog(){
      if(!flowDialog.open)return;
      const mainCount=data.quests.filter(q=>q.type==='main').length;
      const linkedCount=data.quests.filter(q=>(q.predecessors||[]).length>0).length;
      const relationTotal=data.quests.filter(q=>q.type==='main').reduce((sum,q)=>sum+(flowSuccessors.get(q.id)||[]).length,0);
      document.querySelector('#flow-metrics').innerHTML=`<div class="flow-metric"><strong>${mainCount}</strong><span>目录中的主线节点</span></div><div class="flow-metric"><strong>${linkedCount}</strong><span>有已记录前置线索的任务</span></div><div class="flow-metric"><strong>${relationTotal}</strong><span>主线节点直连的后续任务</span></div>`;
      const query=document.querySelector('#flow-search').value.trim().toLocaleLowerCase();
      const expansion=document.querySelector('#flow-expansion').value;
      const type=document.querySelector('#flow-type').value;
      document.querySelectorAll('#flow-list .flow-group[open]').forEach(group=>flowOpen.add(group.dataset.flowQuest));
      const matches=(q,text)=>!query||`${q.title} ${q.name} ${Array.isArray(q.aliases)?q.aliases.join(' '):q.aliases||''} ${q.people||''} ${text}`.toLocaleLowerCase().includes(query);
      const mains=data.quests.filter(q=>q.type==='main'&&(expansion==='all'||q.expansion===expansion)).map(main=>{
        let children=(flowSuccessors.get(main.id)||[]).filter(q=>expansion==='all'||q.expansion===expansion).filter(q=>type==='all'||q.type===type);
        const mainMatches=matches(main,'');
        if(query&&!mainMatches)children=children.filter(q=>matches(q,''));
        if(query&&!mainMatches&&!children.length)return null;
        return {main,children,mainMatches};
      }).filter(Boolean);
      const relationCount=mains.reduce((sum,row)=>sum+row.children.length,0);
      document.querySelector('#flow-count').textContent=`${mains.length} 条主线节点 · ${relationCount} 条已记录的直接关系`;
      document.querySelector('#flow-list').innerHTML=mains.map(({main,children,mainMatches})=>{
        const open=flowOpen.has(main.id)||(query&&!mainMatches);
        const childRows=children.map(child=>{
          const clauses=(child.requirements||[]).filter(r=>r.questId===main.id);
          const relation=clauses.length?[...new Set(clauses.map(r=>{
            const status=r.state==='JS_Success'?'需要任务成功':r.state==='JS_Active'?'需要任务进行中':'需要任务进行中或已完成';
            const mode=r.mode==='all'?'全部条件':r.mode==='any-required'?'任一必要条件':'任一开放条件';
            return `${status} · ${mode}`;
          }))].join('；'):'前置线索';
          return `<article class="flow-row"><div class="flow-row-main"><span class="flow-type flow-type-${esc(child.type)}">${esc(typeNames[child.type]||'任务')}</span><button data-guidance-quest="${esc(child.id)}">${esc(child.title)}</button><span class="flow-expansion">${esc(expansionNames[child.expansion]||'资料片未知')}</span></div><p>${esc(relation)} <span>· ${esc(regionNames[child.region]||'地区待核对')} · ${child.point?'有地图定位':'流程／无独立定位'}</span></p></article>`;
        }).join('');
        return `<details class="flow-group" data-flow-quest="${esc(main.id)}"${open?' open':''}><summary><span class="flow-group-title">${esc(main.title)}</span><span class="flow-group-count">${children.length} 项关联</span><span class="flow-group-meta">${esc(expansionNames[main.expansion]||'资料片未知')} · ${esc(regionNames[main.region]||'地区待核对')}</span></summary><div class="flow-group-body"><div class="flow-anchor"><span class="flow-type flow-type-main">主线节点</span><button data-guidance-quest="${esc(main.id)}">打开任务详情</button></div>${childRows||'<p class="fine">当前筛选下没有已记录的直接后续任务。</p>'}</div></details>`;
      }).join('')||'<p class="fine">没有符合筛选条件的主线流程。</p>';
      for(const group of document.querySelectorAll('#flow-list .flow-group'))group.addEventListener('toggle',()=>{if(group.open)flowOpen.add(group.dataset.flowQuest);else flowOpen.delete(group.dataset.flowQuest)});
      bind();
    }
    function bind(){
      document.querySelectorAll('[data-guidance-quest]').forEach(b=>b.onclick=()=>{if(dialog.open)dialog.close();if(flowDialog.open)flowDialog.close();onQuest(b.dataset.guidanceQuest)});
      document.querySelectorAll('[data-game-state]').forEach(e=>e.onchange=()=>{state.story.questStates[e.dataset.gameState]=e.value;progress.save();onUpdate();renderDialog()});
      document.querySelectorAll('[data-story-fact]').forEach(e=>e.onchange=()=>{state.story.facts[e.dataset.storyFact]=e.value;progress.save();onUpdate();renderDialog()});
      document.querySelectorAll('[data-checklist-done]').forEach(e=>e.onchange=()=>{progress.setRecord('quest',e.dataset.checklistDone,'done',e.checked);renderDialog()});
    }
    document.querySelector('#checklist-stage').innerHTML=options({all:'全部阶段',...Object.fromEntries(config.stages.map(s=>[s.id,s.name]))},state.story.stage);
    document.querySelector('#checklist-toggle').onclick=()=>{dialog.showModal();renderDialog()};
    document.querySelector('#flow-toggle').onclick=()=>{flowDialog.showModal();renderFlowDialog()};
    document.querySelector('#close-checklist').onclick=()=>dialog.close();
    document.querySelector('#close-flow').onclick=()=>flowDialog.close();
    document.querySelector('#flow-search').oninput=renderFlowDialog;
    document.querySelector('#flow-expansion').onchange=renderFlowDialog;
    document.querySelector('#flow-type').onchange=renderFlowDialog;
    document.querySelector('#checklist-stage').onchange=e=>{state.story.stage=e.target.value;progress.save();renderDialog()};
    document.querySelector('#checklist-hide-done').onchange=e=>{state.hideDone=e.target.checked;progress.save();onUpdate();renderDialog()};
    dialog.onclick=e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close()}};
    flowDialog.onclick=e=>{if(e.target===flowDialog){const r=flowDialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)flowDialog.close()}};
    return {detail,bind,renderDialog,renderFlowDialog,effects,config,hasEffects:q=>incoming(q).length>0,hasPotentialEffects:q=>possibleIncoming(q).length>0};
  }
};
