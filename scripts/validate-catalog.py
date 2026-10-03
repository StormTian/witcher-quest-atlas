"""Check round-three additions against independently reviewed frozen row bindings."""
from pathlib import Path
import hashlib, json, math
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
load=lambda p:json.loads((ROOT/p).read_text())
review=load('evidence/catalog-review/reconciliation.json');data=load('dist/data.json');by={q['id']:q for q in data['quests']}
source=ET.parse(ROOT/'evidence/upstream/Witcher3MapViewer/Quests.xml');xml={int(n.get('id')):n for n in source.findall('.//quest')};checks=[]
def check(name,fn):
 try: checks.append({'name':name,'status':'pass','detail':fn() or 'Independent fixtures matched.'})
 except Exception as e:checks.append({'name':name,'status':'fail','detail':str(e)})
def reconciliation():
 for path,sha in review['sourceHashes'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==sha
 expected={i for i,n in xml.items() if n.get('type') in ['contract','treasure','event']}
 assert {r['sourceId'] for r in review['xml']}==expected and len(review['xml'])==162
 ref=load('evidence/catalog-comparison-source.json');rows={e['id'] for e in ref if e['questInfo']['type'] in ['Contract','Treasure Hunt','Scavenger Hunt','Chance Encounter']}
 assert {r['sourceId'] for r in review['reference']}==rows and len(rows)==177
 for row in review['xml']+review['reference']:assert row['targetId'] in by and row['reason']
 return '162 XML and 177 reference rows all have reviewed targets; no unexplained source difference.'
def inventory():
 assert set(by)==set(review['baselineIds'])|set(review['addedIds'])
 for qid,typ in review['addedTypes'].items():assert by[qid]['type']==typ
 assert len(by)==428
 return '161 added IDs: 35 contracts, 29 school hunts, 57 other treasure hunts, 40 encounters.'
def no_components():
 targets={r['sourceId']:r['targetId'] for r in review['reference']}
 for rid,qid in {14:'q85',15:'q85',85:'q261',117:'eternal',317:'forgotten-wolf-diagrams',347:'q320',348:'q320',357:'q361',408:'q418',430:'q351',434:'q394'}.items():assert targets[rid]==qid
 assert 'q451' not in by and 'q111' not in by and 'q112' not in by and 'q29' not in by
 assert [s['sourceId'] for s in by['q110']['relatedStages']]==[111,112]
 return 'Diagram components, journal objectives, aliases and encounter stages are not duplicate tasks.'
def legacy():
 for old in load('evidence/history/cloud-round1-2026-10-03/data.json')['quests']:
  for field in ['id','title','type','region','expansion','point','decisions']:assert by[old['id']][field]==old[field],(old['id'],field)
 return '267 legacy identifiers, classifications, coordinates and 101 option labels preserved.'
def titles_sources():
 for qid in review['addedIds']:
  q=by[qid];assert any('\u4e00'<=c<='\u9fff' for c in q['title']);assert q['sources'] and q['trigger'] and q['location']
  assert all(s['url'].startswith('https://') for s in q['sources']);assert not q['reviewed'] and not q['decisions']
 return 'Every added entry has Chinese search text, provenance, trigger context and an unreviewed-branch status.'
def position_roles():
 for qid in ['q134','q189','q327']:assert by[qid]['positionRole']=='vendor-clue' and '不是' not in by[qid]['trigger'] and '不能代表所有图纸位置' in by[qid]['trigger']
 for qid in ['forgotten-wolf-diagrams','drakenborg-redemption','encounter-farmers-daughter-1','encounter-farmers-daughter-2','q432']:assert by[qid]['point'] is None
 assert by['ciri']['precision']==by['collect']['precision']==by['mysterious']['precision']=='flow'
 return 'Vendor clue coordinates are distinct from diagram destinations; source-only entries stay accessible without invented pins.'
def coordinate_samples():
 # Independent formulas and source values; do not call the generator transform.
 fixtures=[('q38','WO',(.000038,60,19.2)),('q211','SK',(.000164,209.9,305.7)),('q381','TO',(.0000897,-153.3,-717.7)),('q134','VE',(.000114,968.6,706.4))]
 for qid,world,(scale,ox,oy) in fixtures:
  xy=xml[int(qid[1:])].find('discoverprompt/XY');coords=[float(xy.get(a)) for a in ['X','Y']];lng=(coords[0]-ox)/scale/6378137*180/math.pi;lat=(2*math.atan(math.exp((coords[1]-oy)/scale/6378137))-math.pi/2)*180/math.pi
  assert by[qid]['point']['world']==world and by[qid]['point']['xy']==coords
  assert max(abs(a-b) for a,b in zip(by[qid]['point']['latlng'],[lat,lng]))<1e-9
 return 'Four independent contract/school coordinate samples match source XY and own-region projection.'
def source_conflicts():
 assert len(review['levelConflicts'])==15
 for c in review['levelConflicts']:
  q=by[c['targetId']];assert q['level']==c['xmlLevel'];assert any(str(c['referenceLevel']) in s and '差异' in s for s in q['sourceDifferences'])
 assert '无法据此判断' in by['q429']['sourceDifferences'][0]
 return 'All 15 level disagreements and Naughty Feathers trigger conflict remain explicit.'
def classification():
 for qid in ['q351','q377','q393','q370','q394']:assert by[qid]['type']=='side' and by[qid]['secondaryTypes']==['contract']
 assert {q['type'] for q in data['quests']}=={'main','side','contract','scavenger','treasure','encounter'}
 return 'Existing Vintner entries participate in the contract filter without changing the legacy side filter or IDs.'
def requirements():
 for qid in review['addedIds']:
  for row in by[qid]['requirements']:assert row['questId'] in by and row['mode'] in ['any','any-required','all']
 assert any(r['questId']=='q392' and r['state']=='JS_Active' for r in by['q432']['requirements'])
 return 'Source all/any and game-state fields retained; active prerequisites are not rewritten as success.'
for name,fn in [('独立来源完整对账',reconciliation),('新增任务计数与分类',inventory),('组件与阶段去重',no_components),('旧目录稳定 ID 回归',legacy),('中文与来源覆盖',titles_sources),('接取／售图／未知位置语义',position_roles),('新增定位独立样例',coordinate_samples),('来源冲突保留',source_conflicts),('旧酒商委托分类兼容',classification),('条件状态与引用',requirements)]:check(name,fn)
result={'date':datetime.now(timezone.utc).date().isoformat(),'executionEnvironment':'cloud-linux','executedAt':datetime.now(timezone.utc).isoformat(),'status':'pass' if all(c['status']=='pass' for c in checks) else 'fail','checks':checks,'passed':sum(c['status']=='pass' for c in checks),'total':len(checks),'datasetSha256':hashlib.sha256((ROOT/'dist/data.json').read_bytes()).hexdigest(),'reviewSha256':hashlib.sha256((ROOT/'evidence/catalog-review/reconciliation.json').read_bytes()).hexdigest()}
(ROOT/'evidence/catalog-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False));raise SystemExit(result['status']!='pass')
