"""Author sourced stage reminders and extend three reviewed decision nodes."""
from pathlib import Path
import json
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'dist/data.json';data=json.loads(path.read_text());by={q['id']:q for q in data['quests']}
review=json.loads((ROOT/'evidence/guidance-review/review.json').read_text());sources={s['name']:s['url'] for s in review['sources']}
def add(qid,title,options,source,note):
 q=by[qid];d={'id':qid+'-d1','title':title,'options':[{'label':label,'effect':effect,'links':links} for label,effect,links in options],'source':{'label':'本次文档核对：Gamer Guides','url':sources[source]},'note':note}
 q['decisions']=[d];q['reviewed']=True
 q['sources']=[s for s in q['sources'] if s['label']!='本次分支交叉核对']+[{'label':'本次分支交叉核对','url':sources[source]}]
add('q148','战斗中是否保住薇丝',[
 ('救下薇丝，并完成战斗','保住薇丝可以成功收尾，并保留罗契与薇丝赴凯尔莫罕助战的机会；还需完成招募对话。',['q248','q257']),
 ('薇丝在战斗中死亡','这项任务失败，并失去罗契的正常援军路线。刺杀线另按已到达的战斗阶段判断，不能只凭失败标签断定关闭。',['q248','q301'])],
 'an-eye-for-an-eye','薇丝血条出现是“为祖国”的阶段记录之一；不等同于任务成功。战后对孤立士兵的杀／放选择，来源明确不改变后续，本节点不把它描述成新的结局条件。')
add('q146','取得抛光水晶后：交给谁',[
 ('交给藏身处外的女巫猎人','避免这场战斗；猎人向拉多维德抢功，报告时失去正常金钱报酬，也无法再用这枚水晶询问女术士。',['q301']),
 ('保留水晶，先向特莉丝或叶奈法询问','可得到额外背景对话；不改变恋情或后续主线结果。角色是否有空取决于当前任务阶段；交出水晶与只展示它也不同。',['q182','q200']),
 ('保留水晶，向拉多维德报告并交付','通常可得到金钱报酬；可先向女术士展示后再交付。取得水晶的阶段事实与最后交付对象、任务成功标签应分别记录。',['q301'])],
 'redanias-most-wanted','本节点从取得抛光水晶之后开始。攻略记录女术士对话可能在日志中产生红叉，不应把所有红叉都解释成刺杀线失效。此处不是完整对话枚举。')
add('q186','如何带走塔勒',[
 ('说服巨魔让塔勒离开','可以和平救出塔勒；仍需护送回车旁并结束对话，才算完成“致命阴谋”。随后可与他打昆特牌。',['q17','q301']),
 ('与巨魔战斗，救出塔勒','需要击败巨魔后护送塔勒并结束对话；这条路线也能成功完成任务。取得巨魔材料不额外改变刺杀前置。',['q17','q301'])],
 'a-deadly-plot','“为祖国”要求本任务成功完成；只选择营救方式不代表已完成。塔勒的昆特对战应单独记录。')
by['q148']['people']='弗农·罗契 薇丝 Vernon Roche Ves'
by['q146']['people']='菲丽芭 特莉丝 叶奈法 拉多维德 Philippa Triss Yennefer Radovid'
by['q186']['people']='塔勒 迪科斯彻 Thaler Dijkstra'
by['q17']['cutoff']='推进“为祖国”之前，先完成塔勒的昆特对战'
by['mysterious']['trigger']='参考目录记录：完成“暴风雨前的平静”后，参与有关乌马的短对话流程。来源同时要求在“林中夫人”前进行；先后顺序影响是否出现，按所附攻略核对。'
by['q211']['cutoff']='想保留“异乡人／梦之洞窟”支线时，留意“国王的赌局”之前的委托顺序；延后会改变相关遭遇链'
stages=[{'id':'white-orchard','name':'离开白果园前'},{'id':'uma','name':'领走乌马前'},{'id':'before-isle','name':'进入迷雾之岛前'},{'id':'before-finale','name':'本体最终准备期间'},{'id':'hos-finale','name':'石之心终章之前'},{'id':'baw-route','name':'血与酒袭击与路线选择前'},{'id':'local','name':'特定对话／拍卖／活动前'}]
stage_override={'q19':'white-orchard','q37':'white-orchard','q141':'uma','q200':'uma','q17':'before-finale','q301':'before-finale','q335':'baw-route','q133':'local','q184':'local','q317':'local','q355':'local','q211':'local'}
entries=[]
for q in data['quests']:
 if not q.get('cutoff'):continue
 entries.append({'questId':q['id'],'stage':stage_override.get(q['id'],'before-isle'),'reminder':q['cutoff'],'source':q['sources'][-1]['url'],'kind':'source-cutoff'})
for qid,stage,note,source in [
 ('q361','hos-finale','在最终会面前完成夏妮与教授调查；后续介入选项依赖这段调查。','https://witcher.fandom.com/wiki/Whatsoever_a_Man_Soweth...'),
 ('q405','baw-route','先了解两条调查路线；寻找欧丽安娜这一步仍允许改主意。','https://witcher.fandom.com/wiki/The_Night_of_Long_Fangs'),
 ('q406','baw-route','真正进入长者洞穴后锁定路线。游戏阶段应单独记录，完成勾选不代表已进入。','https://witcher.fandom.com/wiki/What_Lies_Unseen'),
 ('q407','baw-route','童话路线的关键调查与物品各自有条件；具体影响保留在本任务剧透区。','https://witcher.fandom.com/wiki/Beyond_Hill_and_Dale...'),
 ('q418','local','监狱内的昆特活动要在下去洗衣之前处理；这是主线内的活动，不另建任务。','https://witcher.fandom.com/wiki/Burlap_is_the_New_Stripe')]:
 entries.append({'questId':qid,'stage':stage,'reminder':note,'source':source,'kind':'reviewed-stage'})
facts=[{'id':'ves-battle-reached','name':'“以眼还眼”中薇丝的血条已出现','questId':'q148','source':'https://witcher.fandom.com/wiki/Reason_of_State'}, {'id':'polished-crystal-found','name':'已取得抛光水晶','questId':'q146','source':'https://witcher.fandom.com/wiki/Reason_of_State'}, {'id':'elder-cave-entered','name':'已真正进入暗影长者洞穴','questId':'q406','source':'https://witcher.fandom.com/wiki/What_Lies_Unseen'}]
rules=[{'id':'assassination','questId':'q301','label':'刺杀线的关键条件','source':'https://witcher.fandom.com/wiki/Reason_of_State','note':'致命阴谋须成功；另外两任务看阶段事实，之后失败不自动关闭这条线。还需在“显而易见”交换情报，并及时推进后续任务。'}, {'id':'hos-rescue','questId':'q361','label':'教授调查与介入选项','source':'https://witcher.fandom.com/wiki/Whatsoever_a_Man_Soweth...','note':'按已经记录的调查选择核对后续选项；未选择时保留未知。'}, {'id':'baw-fairy','questId':'q407','label':'童话路线与长者洞穴锁定','source':'https://witcher.fandom.com/wiki/What_Lies_Unseen','note':'真正进入长者洞穴会排除童话路线；先前调查方向仍可能改变。'}, {'id':'baw-elder','questId':'q406','label':'长者路线阶段记录','source':'https://witcher.fandom.com/wiki/What_Lies_Unseen','note':'只选择去找欧丽安娜不能当作已经进入洞穴。'}, {'id':'keira-aid','questId':'q247','label':'凯拉路线的援军条件','source':'https://witcher.fandom.com/wiki/For_the_Advancement_of_Learning','note':'这里只核对去向选择；仍需结合任务阶段和招募对话。'}, {'id':'triss-romance','questId':'q182','label':'特莉丝恋情的前序选择','source':'https://witcher.fandom.com/wiki/Now_or_Never','note':'前序亲吻与留下／告白要分别满足；单个选项不代替完整游戏流程。'}]
rules += [{'id':'yen-romance','questId':'q200','label':'叶奈法的表白记录','source':'https://witcher.fandom.com/wiki/The_Last_Wish_(quest)','note':'只记录本任务的表白选择；同时追求两位角色的影响另在“三人探戈”核对。'},{'id':'dual-romance','questId':'q25','label':'两段恋情的选择组合','source':'https://witcher.fandom.com/wiki/It_Takes_Three_to_Tango','note':'特莉丝的前序亲吻、留下告白，以及叶奈法表白共同核对；未记录项仍为未知，人物结局只在剧透区展示。'}]
guidance={'meta':{'schemaVersion':1,'date':'2026-10-03','scope':'已核对的剧情提醒与关键条件；不是全部游戏任务或存档模拟。','limits':review['limits']},'stages':stages,'entries':entries,'facts':facts,'rules':rules,'sources':review['sources']}
xml=ET.parse(ROOT/'evidence/upstream/Witcher3MapViewer/Quests.xml');nodes={q.get('id'):q for q in xml.findall('.//quest')};known_guids={q.findtext('GUID') for q in nodes.values() if q.findtext('GUID')}
catalog_review=json.loads((ROOT/'evidence/catalog-review/reconciliation.json').read_text())
added=set(catalog_review['addedIds']);targets={str(r['sourceId']):r['targetId'] for r in catalog_review['xml']}
guid_targets={q.findtext('GUID'):targets.get(q.get('id'),'q'+q.get('id')) for q in nodes.values() if q.findtext('GUID')}
restored=0
for q in data['quests']:
 node=nodes.get(q['id'][1:]) if q['id'].startswith('q') else None
 if node is not None:
  # Baseline generation filtered references to then-excluded contracts/hunts. Restore
  # those now-present entities without overwriting the existing curated conditions.
  for group,mode in [('available','any'),('oneofabsolutelyrequired','any-required'),('strict','all')]:
   for g in node.findall(group+'/GUID'):
    target=guid_targets.get(g.text);clause={'questId':target,'state':g.get('state','active-or-complete'),'mode':mode}
    if target in added and target!=q['id'] and clause not in q['requirements']:
     q['requirements'].append(clause);restored+=1
     if clause['state']=='JS_Success' and target not in q['predecessors']:q['predecessors'].append(target)
  q['requirementsMeta']={'taskLevelOnly':True,'unresolvedGuidCount':sum(guid_targets.get(g.text) not in by for group in ['available','oneofabsolutelyrequired','strict'] for g in node.findall(group+'/GUID')),'source':q['sources'][0]['url']}
data['meta'].update(catalogVersion='1.4',date='2026-10-03',reviewedTasks=sum(q['reviewed'] for q in data['quests']),decisionNodes=sum(len(q['decisions']) for q in data['quests']),decisionOptions=sum(len(d['options']) for q in data['quests'] for d in q['decisions']))
facts_check=[{'category':'阶段／分支','claim':by[qid]['title'],'questId':qid,'result':description,'source':sources[name]} for qid,name,description in [('q148','an-eye-for-an-eye','薇丝生存影响任务收尾与援军；刺杀前置另看指定战斗阶段。'),('q146','redanias-most-wanted','取得抛光水晶与交付对象分开，额外背景对话不改变恋情。'),('q186','a-deadly-plot','和平或战斗均可营救塔勒，须护送并结束对话才算成功。')]]
data['meta']['factChecks']=[f for f in data['meta']['factChecks'] if f['questId'] not in review['branchAdditions']]+facts_check
for s in review['limits']:
 if s not in data['meta']['limitations']:data['meta']['limitations'].append(s)
for file,obj in [(path,data),(ROOT/'dist/guidance.json',guidance),(ROOT/'dist/fact-checks.json',data['meta']['factChecks'])]:file.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
(ROOT/'dist/catalog-review.json').write_text((ROOT/'evidence/catalog-review/reconciliation.json').read_text())
print(json.dumps({'stageEntries':len(entries),'restoredSourceReferences':restored,'reviewedTasks':data['meta']['reviewedTasks'],'decisionNodes':data['meta']['decisionNodes'],'decisionOptions':data['meta']['decisionOptions']}))
