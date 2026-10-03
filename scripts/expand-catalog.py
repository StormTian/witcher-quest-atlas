"""Apply the reviewed source-ID reconciliation to the baseline catalogue."""
from pathlib import Path
import json
import re
import urllib.parse
import xml.etree.ElementTree as ET
import runpy

ROOT = Path(__file__).resolve().parents[1]
review = json.loads((ROOT / 'evidence/catalog-review/reconciliation.json').read_text())
path = ROOT / 'dist/data.json'
data = json.loads(path.read_text())
old_ids = set(review['baselineIds'])
data['quests'] = [q for q in data['quests'] if q['id'] in old_ids]
xml = ET.parse(ROOT / 'evidence/upstream/Witcher3MapViewer/Quests.xml')
nodes = {int(q.get('id')): q for q in xml.findall('.//quest')}
guid_nodes = {q.findtext('GUID'): q for q in nodes.values() if q.findtext('GUID')}
transform = runpy.run_path(str(ROOT / 'scripts/build-exploration.py'))['transform']
regions = {'WO': 'white-orchard', 'VE': 'velen', 'NO': 'velen', 'SK': 'skellige', 'KM': 'kaer-morhen', 'TO': 'toussaint'}
source_url = 'https://github.com/reubengann/Witcher3MapViewer/blob/fb674dbff7df087d0a45f9b3938ba6d5317295af/Witcher3MapViewer/Quests.xml'
titles = '''38|井边的恶魔
54|肮脏的资金
55|逃兵的黄金
56|泰莫利亚的宝藏
46|死亡交叉路口 I
47|死亡交叉路口 II
425|死亡交叉路口 III
48|拦路抢劫
30|强盗的藏匿物
43|骚扰巨魔
50|人类最好的朋友
51|沉没的宝藏
52|不幸的意外
53|遗失的货物
57|祖雷卡女王的宝藏
59|沉没的宝箱
70|商队遇袭
427|掠夺者 I：反抗的农民
428|掠夺者 II：食尸鬼的聚会
71|掠夺者 III：托德拉斯的强盗
86|失踪的巡逻队
95|与世隔绝
100|因果报应
110|敢不敢面对我
113|从油锅跳进火坑
114|死者没有防御
115|风流寡妇
116|林中女妖
135|沼泽怪物
154|人们为钱做的事
167|沉船海岸
202|别和神明开玩笑
225|代价高昂的错误
226|厄运
234|神秘的足迹
250|商道幽灵
266|霍诺顿的野兽
290|被忽视的恳求
314|失踪的弟弟
72|林中野兽
243|小道村谋杀之谜
433|乌鸦窝的争斗
96|尖叫怪
27|任人摆布
32|落难的妓女
33|可疑的勒索
34|仇恨之火
26|热情的欢迎
28|醉汉闹事
31|诺维格瑞的种族主义者 I
94|诺维格瑞的种族主义者 II
123|最最真正的蛇蜥
155|难以捉摸的小偷
163|救出莫里茨·迪芬索
165|夜里的陌生人
188|别相信孩子 I
173|蜜蜂幽灵
191|致命的快感
204|白色女妖
223|血黄金
239|战场上的战利品
237|女巫猎人的突袭
255|关门大吉
265|森林之王
272|奥森弗特的醉汉
313|嫁妆
318|工匠、猎人、士兵、间谍
319|来自欧菲尔的遥远海岸
331|奥森弗特森林里的怪物
341|被诅咒的礼拜堂
342|皇家空军
343|宝剑、饥荒与背叛
365|罗米利伯爵的秘密生活
364|意外的遗产
430|通行费
355|黑暗的遗产
58|赞美芙蕾雅
124|不止老鹰敢这样
151|尼弗迦德的宝藏
152|X 标记的位置
164|海妖的呼唤
166|我真倒霉
168|家族的财富
169|捷径
170|铁边的宝藏
171|海岸的珍珠
172|珍贵的货物（寻宝）
187|别相信孩子 II
190|遗产
201|荒野的呼唤
209|放屁巨魔
215|海姆达尔的四张面孔
271|被打扰的尤斯提安娜
203|奇怪的野兽
211|艾德堡的幽灵
217|穆雷·迪亚布伦
227|新郎来了
244|森林之心
279|失踪的矿工
282|巨龙
291|失踪的儿子
292|史凯利杰的头号要犯
307|深处的宝藏
413|厄运的宝藏
261|高地狮鹫
224|废墟、隐藏的宝藏，你懂的
149|山径的回声
432|针对狩魔猎人的委托
429|顽皮的羽毛
360|牛群的烦恼
344|大猎户
356|黑寡妇
357|钱没有臭味
358|别吃陌生人的糖果
359|塞琳娜帮的最后一次行动
379|等待戈与多
380|实用逃脱术
386|八天环游世界
391|汤匙带来的收益
397|不过除此之外，你喜欢这场戏吗
398|这到底是怎么回事
399|马之幽灵
400|双脚冰冷
402|卡纳冯的诅咒
409|三心二意的园丁
410|陶森特监狱实验
411|年轻弗朗索瓦的烦恼
412|陶佛怪物
414|菲利伯特总会还债'''
titles = dict(line.split('|', 1) for line in titles.splitlines())
schools = {'Viper': '毒蛇', 'Griffin': '狮鹫', 'Cat': '猫', 'Bear': '熊', 'Wolf': '狼', 'Manticore': '蝎尾狮', 'Ursine': '熊', 'Feline': '猫', 'Wolven': '狼'}
def translated(node):
    name = node.findtext('name')
    if 'Scavenger Hunt:' in name:
        school = next(value for key, value in schools.items() if re.search(r'\b' + key + r'\b', name))
        title = ('寻宝：师匠' if 'Grandmaster' in name else '寻宝：') + school + '学派装备'
        part = re.search(r'Part (\d+)', name)
        return title + ('升级图纸 · 第 ' + part[1] + ' 部分' if part else '')
    return titles[node.get('id')]

all_ids = old_ids | set(review['addedIds'])
target_by_source = {row['sourceId']: row['targetId'] for row in review['xml']}
def requirement_rows(node, own_id):
    rows = []
    for group, mode in [('available', 'any'), ('oneofabsolutelyrequired', 'any-required'), ('strict', 'all')]:
        for guid in node.findall(group + '/GUID'):
            found = guid_nodes.get(guid.text)
            source_id = int(found.get('id')) if found is not None else None
            target = target_by_source.get(source_id, 'q' + str(source_id))
            if target in all_ids and target != own_id:
                rows.append({'questId': target, 'state': guid.get('state', 'active-or-complete'), 'mode': mode})
    return rows

def nearby(world, xy):
    ll = transform('NO' if world == 'VE' else world, xy)
    # The nearest road sign is context, never substituted for a quest-giver coordinate.
    landmark = min((p for p in data['landmarks'] if p['region'] == regions[world]), key=lambda p: sum((a-b)**2 for a,b in zip(p['latlng'], ll)))
    return ll, landmark['name']

ref_by_target = {}
for row in review['reference']:
    ref_by_target.setdefault(row['targetId'], []).append(row)
for row in review['xml']:
    if row['action'] != 'include':
        continue
    node = nodes[row['sourceId']]
    qid = row['targetId']; name = node.findtext('name'); info = node.findtext('discoverprompt/info', '')
    world = node.get('world'); typ = review['addedTypes'][qid]
    q = {'id': qid, 'name': name, 'title': translated(node), 'type': typ, 'region': regions[world],
         'expansion': 'baw' if world == 'TO' else 'hos' if row['sourceId'] in [318,319,341,342,343,355,364,365] else 'base',
         'level': int(node.get('level', '0')) or None, 'point': None, 'precision': 'unmapped',
         'trigger': '', 'location': '来源没有独立接取坐标；可从目录查看攻略', 'predecessors': [],
         'requirements': requirement_rows(node, qid), 'decisions': [], 'reviewed': False,
         'sourceInfo': info, 'positionRole': 'discovery', 'aliases': [r['sourceName'] for r in ref_by_target.get(qid, [])],
         'sources': [{'label': '冻结社区任务记录', 'url': source_url}, {'label': '任务攻略（英文）', 'url': 'https://witcher.fandom.com/wiki/' + urllib.parse.quote(name.replace(' ', '_'), safe=':_')}],
         'catalogReview': {'xmlId': row['sourceId'], 'referenceIds': [r['sourceId'] for r in ref_by_target.get(qid, [])], 'scope': '独立命名任务／遭遇，非探索资源点'}}
    if 'Notice board' in info:
        q['trigger'] = '阅读来源标记处告示板的相关告示；图标是接取线索，不是怪物目标位置。'
    elif typ == 'scavenger' and ('Buy' in info or 'Armorer' in info):
        q['positionRole'] = 'vendor-clue'
        q['trigger'] = '向来源记录的商人／工匠购买或询问套装图纸线索；标记是售图线索，不能代表所有图纸位置。'
    elif typ == 'treasure' and 'Hidden treasure' in info:
        q['trigger'] = '前往社区记录的隐藏宝藏线索处，搜查相关信件或物品；目标宝箱可能位于别处。'
    elif typ == 'encounter':
        q['trigger'] = '靠近社区记录的遭遇位置或与现场人物交谈；有些事件需要前序任务、时间或再次路过，不能保证当前存档已开放。'
    else:
        q['trigger'] = '在社区记录的位置探索、读取线索或与相关角色交谈；请结合前置记录及所附攻略确认具体接取流程。'
    xy = node.find('discoverprompt/XY')
    if xy is not None:
        pw = xy.get('world'); coords = [float(xy.get(a)) for a in ['X', 'Y']]; ll, near = nearby(pw, coords)
        q.update(region=regions[pw], precision='community', point={'world': pw, 'xy': coords, 'latlng': ll}, location=('售图线索附近：' if q['positionRole']=='vendor-clue' else '来源接取／发现线索附近：') + near)
    q['predecessors'] = list(dict.fromkeys(r['questId'] for r in q['requirements'] if r['state']=='JS_Success'))
    for r in ref_by_target.get(qid, []):
        q['sources'].append({'label': '独立目录对照 · 记录 ' + str(r['sourceId']), 'url': r['sourceUrl']})
    conflicts = [c for c in review['levelConflicts'] if c['targetId']==qid]
    if conflicts:
        q['sourceDifferences'] = ['推荐等级差异：冻结 XML ' + str(c['xmlLevel']) + '；参考目录 ' + str(c['referenceLevel']) + '。显示沿用冻结 XML，当前游戏版本请自行确认。' for c in conflicts]
    data['quests'].append(q)
for entry in review['extras']:
    q = {**entry, 'point': None, 'precision': 'unmapped', 'positionRole': 'unknown', 'location': '没有冻结接取坐标；按攻略在游戏内确认', 'requirements': [], 'decisions': [], 'reviewed': False}
    q['sources'] = [{'label': '独立目录对照 · 记录 ' + str(row['sourceId']), 'url': row['sourceUrl']} for row in ref_by_target[q['id']]]
    q['aliases'] = [row['sourceName'] for row in ref_by_target[q['id']]]
    data['quests'].append(q)
by = {q['id']: q for q in data['quests']}
for conflict in review['levelConflicts']:
    q = by[conflict['targetId']]
    message = '推荐等级差异：冻结 XML ' + str(conflict['xmlLevel']) + '；参考目录 ' + str(conflict['referenceLevel']) + '。显示沿用冻结 XML，当前游戏版本请自行确认。'
    if message not in q.setdefault('sourceDifferences', []):
        q['sourceDifferences'].append(message)
for row in review['xml']:
    if row['action'] != 'merge-stage':
        continue
    node = nodes[row['sourceId']]; q = by[row['targetId']]; xy = node.find('discoverprompt/XY')
    related = {'sourceId': row['sourceId'], 'name': node.findtext('name'), 'note': row['reason']}
    if xy is not None:
        pw = xy.get('world'); coords = [float(xy.get(a)) for a in ['X','Y']]; ll, _ = nearby(pw, coords)
        related.update(region=regions[pw], gameXY=coords, latlng=ll)
    q.setdefault('relatedStages', [])
    q['relatedStages'] = [s for s in q['relatedStages'] if s['sourceId'] != row['sourceId']] + [related]
for qid in ['q351','q377','q393','q370','q394']:
    by[qid]['secondaryTypes'] = ['contract']
    by[qid]['aliases'] = [r['sourceName'] for r in ref_by_target[qid]]
by['q394']['sourceDifferences'] = list(dict.fromkeys(by['q394'].get('sourceDifferences', []) + ['冻结 XML 将 Duchaton Crest? 写作疑问别名，参考目录使用该别名。本目录合并入口并保留旧 ID，名称对应尚未实机核对。']))
by['ciri'].update(precision='flow', location='跨地区调查总任务，没有单一接取点')
by['collect'].update(precision='flow', location='跨地区卡牌收集总任务，没有单一接取点')
by['mysterious'].update(name='A Mysterious Passenger', aliases=['The Mysterious Passenger'], precision='flow', location='史凯利杰主线调查中的条件性对话流程；无独立接取坐标', trigger='参考目录记录的短流程：完成“暴风雨前的平静”后，与唐纳相关主线对话了解乌马。来源同时要求在“林中夫人”前进行；进度顺序影响是否出现，按所附攻略确认。', sources=[{'label':'独立目录登记的攻略','url':'https://witcher.fandom.com/wiki/A_Mysterious_Passenger'}])
by['q429']['sourceDifferences'] = ['发现说明写“骑士的恋爱故事”之后，XML 条件却写“无论何处都是家”成功。保留两个来源字段，无法据此判断当前存档可用。']
by['q432']['trigger'] = '社区记录关联“来自辛特拉的男人”进行中的流程；没有独立定位，按任务攻略确认触发。'
by['q163']['trigger'] = '来源记录：在诺维格瑞的火刑现场救出莫里茨；相关任务阶段可能改变现场，未核对当前存档是否仍可触发。'
by['q355']['trigger'] = '在“芝麻开门”的拍卖中买下鸟雕像，再请工匠拆解，读取里面的寻宝线索。错过拍卖购买可能错过该寻宝入口。'
by['q355']['cutoff'] = '“芝麻开门”拍卖阶段：先购买鸟雕像，再离开拍卖流程'
data['meta'].update(date='2026-10-03', catalogVersion='1.3', scope='本体 + 石之心 + 血与酒；保留原 267 条主线／支线，补入委托、套装搜集、寻宝与随机遭遇。按冻结来源核对，不声称全游戏完整。', catalogReview='catalog-review.json')
data['meta']['limitations'] = [s for s in data['meta']['limitations'] if not any(word in s for word in ['狩魔委托','寻宝','随机遭遇'])] + review['limits']
data['meta']['limitations'] = list(dict.fromkeys(data['meta']['limitations']))
data['meta']['corrections'] = [s for s in data['meta']['corrections'] if not s.startswith('第 3 轮')] + ['第 3 轮：套装组件、取剑目标和同一挑战者后续阶段合并；五条旧酒商委托加入关联分类而不复制。追寻希里与收集所有卡牌改为总流程语义。']
assert set(by) == old_ids | set(review['addedIds'])
path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
(ROOT / 'dist/catalog-review.json').write_text(json.dumps(review, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({'quests': len(by), 'added': len(review['addedIds'])}))
