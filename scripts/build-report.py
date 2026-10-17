"""Package completed checks and their limits into the public audit report."""
from pathlib import Path
import hashlib, json, shutil

root=Path(__file__).resolve().parents[1]
read=lambda name:json.loads((root/name).read_text())
d=read('dist/data.json')
logic=read('evidence/data-logic-validation.json')
browser=read('evidence/browser-validation.json')
digest=hashlib.sha256((root/'dist/data.json').read_bytes()).hexdigest()
assert logic['status']=='pass' and browser['status']=='pass'
assert logic['datasetSha256']==digest
if browser.get('datasetSha256'):
 assert browser['datasetSha256']==digest
asset=read('evidence/asset-report-validation.json') if (root/'evidence/asset-report-validation.json').exists() else None
if asset and (asset.get('status')!='pass' or asset.get('datasetSha256')!=digest): asset=None
landmark=read('evidence/landmark-validation.json') if (root/'evidence/landmark-validation.json').exists() else None
if landmark:
 assert landmark['status']=='pass' and landmark['datasetSha256']==digest
 assert landmark['appSha256']==hashlib.sha256((root/'dist/app.js').read_bytes()).hexdigest()
 assert landmark['styleSha256']==hashlib.sha256((root/'dist/style.css').read_bytes()).hexdigest()
navigation=read('evidence/navigation-validation.json') if (root/'evidence/navigation-validation.json').exists() else None
if navigation:
 assert navigation['status']=='pass' and navigation['datasetSha256']==digest
 for key,filename in [('appSha256','app.js'),('navigationSha256','map-navigation.js'),('placesSha256','places-zh.json'),('styleSha256','style.css')]:
  assert navigation[key]==hashlib.sha256((root/'dist'/filename).read_bytes()).hexdigest()
cloud=read('evidence/cloud-migration.json') if (root/'evidence/cloud-migration.json').exists() else None
current_inputs={name:hashlib.sha256((root/'dist'/name).read_bytes()).hexdigest() for name in read('scripts/runtime-inputs.json')}
for result in [landmark,navigation]:
 if result: assert result.get('runtimeInputHashes')==current_inputs
assert browser.get('runtimeInputHashes')==current_inputs, 'Browser checks must match current runtime inputs'
if browser['status']=='pass' and browser.get('runtimeInputHashes')==current_inputs: cloud=None
if asset and asset.get('runtimeInputHashes')!=current_inputs: asset=None
exploration=read('dist/exploration.json')
exploration_data=read('evidence/exploration-data-validation.json')
exploration_browser=read('evidence/exploration-browser-validation.json')
assert exploration_data['status']=='pass' and exploration_browser['status']=='pass'
for result in [exploration_data,exploration_browser]:
 assert result['explorationSha256']==current_inputs['exploration.json'] and result['datasetSha256']==digest
for key,name in [('appSha256','app.js'),('explorationCodeSha256','exploration.js'),('explorationStyleSha256','exploration.css')]:
 assert exploration_browser[key]==current_inputs[name]
progress=read('evidence/progress-validation.json')
assert progress['status']=='pass'
assert progress['runtimeInputHashes']==current_inputs
for name,expected in progress['runtimeInputHashes'].items():
 assert expected==hashlib.sha256((root/'dist'/name).read_bytes()).hexdigest(), name
places=read('dist/places-zh.json')
summary=[
 {'name':'任务数据与规则','detail':f"{logic['passed']}/{logic['total']} 项；任务引用、地图资源、结局条件、流程前置",'status':'通过'},
 {'name':'网页实际交互','detail':f"{browser['passed']}/{browser['total']} 项；五区地图、筛选、{d['meta']['decisionOptions']} 个选项、剧透与手机操作",'status':'通过'},
 {'name':'攻略事实核对','detail':f"{len(d['meta']['factChecks'])} 项重点核对；{d['meta']['reviewedTasks']} 个任务／{d['meta']['decisionNodes']} 个节点附攻略依据",'status':'资料核对完成'},
 {'name':'地图位置抽样','detail':'4 个独立坐标样例及地图裁切，校准社区坐标转换','status':'抽样一致'},
 {'name':'实机游戏验证','detail':'没有读取游戏存档或逐任务运行游戏','status':'未执行'},
]
summary.insert(1,{'name':'个人进度与分享','detail':f"{progress['passed']}/{progress['total']} 项；完成、收藏、可靠导入导出、刷新恢复、分享与前进后退",'status':'通过'})
summary.insert(1,{'name':'探索图层','detail':f"{exploration_data['passed']+exploration_browser['passed']}/{exploration_data['total']+exploration_browser['total']} 项；{len(exploration['points'])} 个点位；来源对账、基础图层 32 种组合、手机操作",'status':'通过'})
if asset:summary.insert(2,{'name':'报告与资源交付','detail':f"{asset['passed']}/{asset['total']} 项；报告、下载与资源加载",'status':'通过'})
if landmark:summary.insert(2,{'name':'地名与路标显示','detail':f"{landmark['passed']}/{landmark['total']} 项；五区 227 个路标、默认地名、缩放拖动和手机",'status':'通过'})
if navigation:summary.insert(2,{'name':'中文地名与缩放体验','detail':f"{navigation['passed']}/{navigation['total']} 项；227 个中文地名、滚轮锚点、连续点击、概览与双指手势",'status':'通过'})
qa={'date':logic['date'],'executionEnvironment':logic.get('executionEnvironment','unknown'),'executedAt':logic.get('executedAt'),'status':'partial' if cloud and cloud['browserStatus']=='blocked' else 'pass','datasetSha256':digest,'summary':summary,
 'automatedChecksPassed':logic['passed']+browser['passed']+(asset['passed'] if asset else 0)+(landmark['passed'] if landmark else 0)+(navigation['passed'] if navigation else 0),
 'coverage':{'quests':len(d['quests']),'main':sum(q['type']=='main' for q in d['quests']),'side':sum(q['type']=='side' for q in d['quests']),'types':{t:sum(q['type']==t for q in d['quests']) for t in sorted({q['type'] for q in d['quests']})},'positioned':sum(bool(q['point']) for q in d['quests']),'communityCoordinates':sum(q['precision']=='community' for q in d['quests']),'landmarkAnchors':sum(q['precision']=='landmark' for q in d['quests']),'flowOrUnmapped':sum(not q['point'] for q in d['quests']),'reviewedBranchTasks':d['meta']['reviewedTasks'],'decisionNodes':d['meta']['decisionNodes'],'decisionOptions':d['meta']['decisionOptions']},
 'limits':d['meta']['limitations'],
 'evidence':{'data':'checks/data-logic.json','browser':'checks/browser.json','assets':'checks/assets.json' if asset else None},
 'webMCP':browser['webMCP']}
qa['automatedChecksPassed']+=exploration_data['passed']+exploration_browser['passed']+progress['passed']
qa['evidence']['progress']='checks/progress.json'
catalog_data=read('evidence/catalog-validation.json');catalog_browser=read('evidence/catalog-browser-validation.json')
assert catalog_data['status']==catalog_browser['status']=='pass' and catalog_data['datasetSha256']==digest
for name,expected in catalog_browser['runtimeInputHashes'].items(): assert expected==hashlib.sha256((root/'dist'/name).read_bytes()).hexdigest(), name
summary.insert(1,{'name':'扩充目录与服务点','detail':f"{catalog_data['passed']+catalog_browser['passed']}/{catalog_data['total']+catalog_browser['total']} 项；428 条目录、615 点位、来源归并、六类筛选、密集点与旧备份",'status':'通过'})
qa['automatedChecksPassed']+=catalog_data['passed']+catalog_browser['passed']
qa['evidence'].update(catalogData='checks/catalog-data.json',catalogBrowser='checks/catalog-browser.json')
guidance=read('dist/guidance.json');guidance_data=read('evidence/guidance-validation.json');guidance_browser=read('evidence/guidance-browser-validation.json')
for result in [guidance_data,guidance_browser]:
 assert result['status']=='pass' and result['runtimeInputHashes']==current_inputs
qa['automatedChecksPassed']+=guidance_data['passed']+guidance_browser['passed']
qa['evidence'].update(guidanceData='checks/guidance-data.json',guidanceBrowser='checks/guidance-browser.json')
summary.insert(1,{'name':'防漏清单与条件联动','detail':f"{guidance_data['passed']+guidance_browser['passed']}/{guidance_data['total']+guidance_browser['total']} 项；43 条阶段提醒、未知条件、失败例外、路线互斥、备份与逐任务剧透",'status':'通过'})
qa['coverage'].update(stageReminders=len(guidance['entries']),guidanceRules=len(guidance['rules']))
qa['gameStateRecords']={'storage':'device-local','default':'unknown','personalDoneIsGameSuccess':False,'backupSchemaVersion':1,'source':'guidance.json'}
qa['personalProgress']={'storage':'device-local','schemaVersion':1,'spoilersPersisted':False,'backup':'JSON with validated preview and unmatched-ID ledger','shareParameters':['region','quest or point']}
qa['runtimeInputHashes']=current_inputs
qa['coverage']['explorationPoints']=len(exploration['points'])
qa['coverage']['explorationTypes']={category['id']:category['count'] for category in exploration['categories']}
qa['exploration']={'source':'exploration.json','sourceCommit':exploration['meta']['sourceCommit'],'rawRecords':exploration['meta']['rawRecords'],'included':exploration['meta']['included'],'duplicates':exploration['meta']['duplicates'],'deferred':exploration['meta']['deferred'],'limits':exploration['meta']['limits']}
qa['evidence']['explorationData']='checks/exploration-data.json'
qa['evidence']['explorationBrowser']='checks/exploration-browser.json'
if landmark:
 qa['coverage']['roadSigns']=227
 qa['evidence']['landmarks']='checks/landmarks.json'
if navigation:qa['evidence']['navigation']='checks/navigation.json'
qa['localization']={'roadSigns':len(places['entries']),'englishFallbacks':0,'method':places['method'],'limits':places['limits'],'source':'places-zh.json'}
if cloud:
 qa['cloudMigration']=cloud
 if cloud['browserStatus']!='pass': qa['automatedChecksPassed']=logic['passed']
 for row in summary:
  if row['status']=='通过' and row['name']!='任务数据与规则' and cloud['browserStatus']!='pass': row['status']='历史本地通过；本次云端未执行'
 summary.insert(1,{'name':'本次云端资源检查','detail':f"{cloud['assetsFetched']} 个静态文件真实 HTTP 读取；{cloud['mapTiles']} 个地图图块",'status':'通过'})
 summary.insert(2,{'name':'本次云端浏览器','detail':cloud['browserBlocker'],'status':'通过' if cloud['browserStatus']=='pass' else '阻碍；未通过'})
 qa['summary']=summary
dist=root/'dist';(dist/'checks').mkdir(exist_ok=True)
for name,target in [('guidance-validation.json','guidance-data.json'),('guidance-browser-validation.json','guidance-browser.json')]: shutil.copyfile(root/'evidence'/name,dist/'checks'/target)
for name in ['guidance-checklist.png','guidance-conditions.png','guidance-flow.png','guidance-mobile.png']: shutil.copyfile(root/'evidence'/name,dist/'checks'/name)
for name,target in [('catalog-validation.json','catalog-data.json'),('catalog-browser-validation.json','catalog-browser.json')]: shutil.copyfile(root/'evidence'/name,dist/'checks'/target)
for name in ['catalog-desktop.png','catalog-mobile.png']: shutil.copyfile(root/'evidence'/name,dist/'checks'/name)
shutil.copyfile(root/'evidence/progress-validation.json',dist/'checks/progress.json')
for name in ['progress-desktop.png','progress-mobile.png','progress-mobile-detail.png']:
 shutil.copyfile(root/'evidence'/name,dist/'checks'/name)
for name,target in [('exploration-data-validation.json','exploration-data.json'),('exploration-browser-validation.json','exploration-browser.json')]:
 shutil.copyfile(root/'evidence'/name,dist/'checks'/target)
for name in ['exploration-desktop.png','exploration-map.png','exploration-mobile.png','exploration-mobile-layers.png']:
 shutil.copyfile(root/'evidence'/name,dist/'checks'/name)
for f,target in [('data-logic-validation.json','data-logic.json'),('browser-validation.json','browser.json')]:
 shutil.copyfile(root/'evidence'/f,dist/'checks'/target)
if navigation:
 shutil.copyfile(root/'evidence/navigation-validation.json',dist/'checks/navigation.json')
 for name in ['navigation-desktop.png','navigation-mobile.png']:
  shutil.copyfile(root/'evidence'/name,dist/'checks'/name)
if asset:shutil.copyfile(root/'evidence/asset-report-validation.json',dist/'checks/assets.json')
if landmark:
 shutil.copyfile(root/'evidence/landmark-validation.json',dist/'checks/landmarks.json')
 for name in ['landmarks-desktop.png','landmarks-mobile.png']:
  shutil.copyfile(root/'evidence'/name,dist/'checks'/name)
for name in ['desktop-final.png','mobile-final.png','decision-final.png','mobile-audit.png','text-200.png']:
 shutil.copyfile(root/'evidence'/name,dist/'checks'/name)
(dist/'validation.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2))
lines=[
 '# 狩魔手记：互动地图验证报告',
 '',
 f"任务资料日期：{d['meta']['date']}；本次验证日期：{logic['date']}。目录版本：{d['meta']['catalogVersion']}。",
 '',
 '本报告记录本次自动化环境中的实际数据与浏览器检查；各项结果附执行时间与文件摘要。历史本地结果独立保留。网页检查不等于游戏实机全量验收，也不是官方任务完整性证明。',
 '',
 '## 覆盖',
 '',
 f"- {len(d['quests'])} 个任务／遭遇条目。分类：" + '、'.join(f"{t} {n}" for t,n in qa['coverage']['types'].items()) + '。原有 267 个 ID 和主线／支线分类保留。',
 f"- {qa['coverage']['positioned']} 个地图定位：{qa['coverage']['communityCoordinates']} 个社区发现／接取线索、{qa['coverage']['landmarkAnchors']} 个关联地标。另 {qa['coverage']['flowOrUnmapped']} 个流程／未知坐标条目保留在索引中。",
 '- 五个真实地区地图：白果园、威伦／诺维格瑞、史凯利杰、凯尔莫罕、陶森特。维吉玛王宫仅显示室内剧情任务。',
 f"- {d['meta']['reviewedTasks']} 个重点任务的 {d['meta']['decisionNodes']} 个决策节点、{d['meta']['decisionOptions']} 个选项；尚未整理分支的任务有明确提示。",
 '- 目录包含主线／支线、狩魔委托、套装搜集、寻宝与随机遭遇；阶段、组件和探索资源点分别归类。',
 f"- {len(exploration['points'])} 个独立探索点，{len(exploration['categories'])} 类：设施、服务、昆特、资源与洞穴入口。与任务目录分开统计。",
 '',
 '## 验证结果',
 '',
 f"本次检查日期：{logic['date']}；执行环境：{logic.get('executionEnvironment','unknown')}。历史本地 66 项验收保存在源码 evidence/history/local-2026-10-02/，不计为本次通过。浏览器状态见下表。",
 '',
 '| 范围 | 实际检查 | 结果 |',
 '| --- | --- | --- |',
 ]
lines += [f"| {t['name']} | {t['detail']} | {t['status']} |" for t in summary]
lines += [
 '',
 '### 数据与结局规则',
 '',
 f"[逐项结果](checks/data-logic.json)：{logic['passed']}/{logic['total']} 项通过。",'']
lines += [f"- {c['name']}：{c['detail']}。" for c in logic['checks']]
lines += [
 '',
 '### 浏览器实际操作与来源',
 '',
 f"[逐项结果](checks/browser.json)：{browser['passed']}/{browser['total']} 项通过。执行来源：{browser.get('executionEnvironment','historical-local')}，日期：{browser['date']}。当前运行结果见上述状态。",'']
lines += [f"- {c['name']}：通过。" for c in browser['checks']]
lines += [
 '',
 '验收画面：[桌面](checks/desktop-final.png)、[手机](checks/mobile-final.png)、[分支展开](checks/decision-final.png)、[验证窗口](checks/mobile-audit.png)、[200% 文字](checks/text-200.png)。',
 '',
 'WebMCP 在验收浏览器中不可用，因此未计入通过项目。普通页面功能不依赖它。',
 '',
 '### 地图校准',
 '',
 '地图与坐标采用同一个 Witcher3MapViewer 来源版本，未混用不同投影的社区地图。MBTiles 的 TMS 行号转换为 XYZ；游戏 XY 经各地区校准后转为 Leaflet 使用的合成坐标，不是现实地理经纬度。',
 '',
 '| 独立样例 | 核对内容 | 证据 |',
 '| --- | --- | --- |',
 '| 失踪的兄弟 | 白果园洗劫村庄的接取点 | [裁切](assets/check-19.jpg) |',
 '| 扭曲的纵火犯 | 白果园铁匠附近建筑 | [裁切](assets/check-37.jpg) |',
 '| 宝剑与饺子 | 诺维格瑞铁匠街区 | [裁切](assets/check-263.jpg) |',
 '| 唯有一人 | 鲍克兰告示板，不是湖上试炼目标 | [裁切](assets/check-424.jpg) |',
 '',
 '数值样例用于检查坐标转换；裁切用于建筑与地标的一致性抽样。没有验证全部点位的游戏内 NPC 站位或开放状态。',
 '',
 ]
if landmark:
 lines += ['','### 本次云端地名更新验收','',f"[逐项结果](checks/landmarks.json)：{landmark['passed']}/{landmark['total']} 项通过。227 个原有快速旅行路标现在默认显示名称，密集处的主要地名避让后用细线指回路标；可用“地名”按钮开关。",'']
 lines += [f"- {c['name']}：{c['detail']}。" for c in landmark['checks']]
 lines += ['','更新画面：[桌面地名](checks/landmarks-desktop.png)、[手机地名](checks/landmarks-mobile.png)。19 项完整流程也已重新验收；新增地名叠加和地图操作由上述专门检查复验。','']
if navigation:
 lines += ['','### 本次云端中文地名与缩放更新验收','',f"[逐项結果](checks/navigation.json)：{navigation['passed']}/{navigation['total']} 项通过。每次加减或单次滚轮操作只改变 0.25 级；鼠标位置为缩放锚点。选任务保留倍率，返回地区保留原视野。概览亮框显示当前窗口，点击概览可平移。",'']
 lines += [f"- {c['name']}：{c['detail']}。" for c in navigation['checks']]
 lines += ['','更新画面：[桌面](checks/navigation-desktop.png)、[手机双指缩放](checks/navigation-mobile.png)。','',
 '中文名称对照：[227 个逐项名称与来源](places-zh.json)、[公开中文游戏地图](https://www.tivaprojects.com/witcher3map/)。',
 places['method'],places['limits'],
 '修正原来手工译名，如 Cackler Bridge 为“嘻笑者之桥”、Blackbough 为“大黑树”、Lornruk 为“孤岩”、Tesham Mutna 为“迪沙谬那”。另修正社区中文对照把 Elverum 与 Eldberg 灯塔写成同名的问题，[艾孚鲁灯塔核对](https://witcher.huijiwiki.com/wiki/艾孚鲁灯塔)。',
 '凯尔莫罕来源旧名通过地图相对位置对应当前路标：The Morhen Eye 为堡垒、Outpost ruins 为被毁的瞭望塔、Morhen Mine dam 为铁矿、The Lake House 为湖畔小屋。没有移动这些点的坐标。',
 '底图继续使用同一来源版本，较大地图增加原生 4、5 级细节瓦片，以 WebP 质量 88 压缩；总计 5721 个瓦片。白果园原生上限 4，其余地区 5；最多再放大半级，避免无限拉伸。',
 '首轮发现连续点击丢失一档，已修正动画期间的目标倍率队列。双指验收使用载入页面前就启用的触摸设备模式；桌面页面载入后切换触摸模拟不能证明手机手势正常。','']
lines += ['','### 基础探索点与图层验收','',f"[数据对账](checks/exploration-data.json)：{exploration_data['passed']}/{exploration_data['total']} 项；[浏览器操作](checks/exploration-browser.json)：{exploration_browser['passed']}/{exploration_browser['total']} 项。",'', '从 617 条冻结来源记录整理得到 615 个点位：合并陶森特鸡蛇旅馆告示板的一条重复记录；带童话世界独立场景标识、位于当前区域底图范围外的一条告示板暂缓展示。整理账目见 [探索点清单](exploration.json)。', '图层支持任务、路标和 13 类探索点独立开关。基础五图层的 32 种组合仍按旧独立清单回归；新增服务和资源层默认关闭，支持搜索、全选、全隐藏和恢复，密集探索点可聚合选择。点击探索点显示用途、最近参考路标和来源。', '最近路标按游戏 XY 直线距离选择，不代表可步行到达。是否开放需要结合任务阶段和游戏内状态，未逐点实机复核。', '', '验收画面：[探索地图](checks/exploration-map.png)、[点位详情](checks/exploration-desktop.png)、[手机图层](checks/exploration-mobile-layers.png)、[手机详情](checks/exploration-mobile.png)。','']
lines += [f"- {check['name']}：{check['detail']}。" for check in exploration_data['checks']+exploration_browser['checks']]
lines += ['', '### 第三轮目录与探索来源对账', '', f"[数据对账](checks/catalog-data.json)：{catalog_data['passed']}/{catalog_data['total']}；[浏览器](checks/catalog-browser.json)：{catalog_browser['passed']}/{catalog_browser['total']}。", '', '新增 161 条独立目录，保留原 267 个 ID。162 条 XML 候选和 177 条独立参考记录逐行绑定；套装组件、任务目标、重复阶段与旧酒商委托不重复计数。15 处推荐等级差异显式保留。', '[完整对照清单](catalog-review.json)包含合并依据与来源；其中可能包含剧情信息。没有可靠定位的条目继续从目录访问，套装售图线索不冒充所有图纸位置。', '探索来源的共享／空白标识使用维护的 ID 映射，坐标不进入永久 ID；服务点不宣称完整名单或工匠能力。', 'WebMCP 新类型使用注册接口夹具验证输入与返回契约，实际浏览器仍不支持原生上下文，未宣称原生功能已验证。', '', '[桌面](checks/catalog-desktop.png) · [手机](checks/catalog-mobile.png)', '']
lines += ['', '### 个人进度、备份与定位分享', '', f"[逐项结果](checks/progress.json)：{progress['passed']}/{progress['total']} 项通过。", '', '任务与探索点可完成、收藏、按个人记录筛选及隐藏已完成。记录、地区、筛选、视野和已选决策保存在当前设备浏览器；不是读取游戏存档，也没有账号云同步。', '备份恢复先预览并验证：无效 JSON、未知备份版本、非布尔标记、危险标识和过大文件不能覆盖当前记录。未知对象和决策保持在未匹配账目中，便于后续迁移。', '分享定位只包含地区、任务或探索点 ID，不夹带个人记录或决策。刷新后仍默认隐藏剧透，前进／后退可返回对应对象；未知链接显示提示。', '浏览器禁止或损坏存储时地图可使用，明确提示保存失败，并可导出本次记录。', '', '验收画面：[备份预览与恢复](checks/progress-desktop.png)、[手机记录](checks/progress-mobile-detail.png)、[手机备份](checks/progress-mobile.png)。', '']
lines += [f"- {check['name']}：通过。" for check in progress['checks']]
lines += ['', '### 第四轮防漏、条件状态与跨任务提示', '', f"[独立规则](checks/guidance-data.json)：{guidance_data['passed']}/{guidance_data['total']}；[浏览器操作](checks/guidance-browser.json)：{guidance_browser['passed']}/{guidance_browser['total']}。", '', '43 条来源明确的剧情阶段提醒；已处理记录可筛选、刷新保存并与现有个人进度共用稳定 ID。来源条件区分全部、任一和进行中，不把前序线索当成全部必须成功。任务级条件只是来源片段，未解析目标继续标明。', '个人完成标记与游戏日志成功、失败、进行中及阶段事实分开；未记录保持未知。剧情记录纳入原版本个人备份，旧备份可读取，未知故事 ID 留在迁移账目。', '刺杀线保留薇丝战斗／抛光水晶的失败阶段例外，“致命阴谋”仍须成功。教授调查与依赖节点、真正进入长者洞穴后的路线互斥、凯拉与两段恋情的条件分别核对。记录矛盾时按明确阶段事实提示，不偷偷改选择或结局演算。', '补审三个任务，共新增三个节点、七个选项，合计 43 个已审任务／48 节点／108 选项。来源包括本次成功抓取的 Gamer Guides 事实段落；Fandom 本次返回 402 的引用只沿用既有核对，不冒充重新抓取。', '已选决策的关联后果只有展开目标任务剧透后显示；无自有节点的目标也可单独展开关联提示，失效的条件节点不参与联动。', '任务／指导数据生成链两次从冻结输入重建一致；不同数学库的投影尾数允许 1e-9 度数值误差，原始 XY 和稳定 ID 严格保留。', '', '[防漏清单](checks/guidance-checklist.png) · [主线流程](checks/guidance-flow.png) · [条件记录](checks/guidance-conditions.png) · [手机](checks/guidance-mobile.png)', '']
lines += ['', '### 重点事实与来源', '', '| 核对项目 | 结论 | 依据 |', '| --- | --- | --- |']
lines += [f"| {c['claim']} | {c['result']} | [攻略]({c['source']}) |" for c in d['meta']['factChecks']]
lines += [
 '',
 '### 已修复的资料问题',
 '',
 ]+[f"- {s}" for s in d['meta']['corrections']]
lines += [
 '- “为祖国”前置保留 Wiki 关于特定阶段失败的记录；“以眼还眼”需到薇丝战斗、“瑞达尼亚的头号要犯”需取得抛光水晶。“致命阴谋”仍须完成，并需在“显而易见”中交换恩希尔情报。[详细依据](https://witcher.fandom.com/wiki/Reason_of_State)。',
 '- 初轮缩放检查在地图动画结束前读取状态，产生一次误报。改为等待动画完成后复测，缩放、拖动和复位均通过。失败画面保存在历史本地证据 evidence/history/local-2026-10-02/failure-5.png。',
 '',
 '## 可重复核验',
 '',
 f"最终任务数据 SHA-256：`{digest}`。",
 '',
 '地图／社区数据来源锁定为 Witcher3MapViewer commit `fb674dbff7df087d0a45f9b3938ba6d5317295af`。来源 XML 与地图清单在源码项目 evidence/ 中保留；可重新生成任务数据，执行数据检查，并在云端测试服务中重跑浏览器操作。',
 '',
 '浏览器检查按照页面自己的选项数据逐一点击，能发现渲染、引用与条件解锁故障；它不是独立证明全部中文后果文本正确的方式。后果的事实核对依靠每节点攻略链接，两个结局规则另使用预先声明的边界样例检查。',
 '',
 '## 边界',
 '',
 ]+[f"- {s}" for s in d['meta']['limitations']]
lines += [
 '- 希里未觐见时二比二的边界按 Wiki 四项记分解释；其他攻略把跳过觐见计为第五项积极，得到相同结果。这个边界未实机复测。',
 '- 结局演算只覆盖说明中的主干条件，不读取存档，也不推断未输入的其他游戏状态。',
 '- 网页默认隐藏决策后果，只有主动展开或使用全局开关后才出现；验证报告自身包含剧情信息。',
 '',
 '## 资料与版权',
 '',
 ]+[f"- [{s['label']}]({s['url']})" for s in d['meta']['sources']]
lines += [
 '',
 '游戏地图与游戏内容版权归 CD PROJEKT RED 所有。本工具是非官方个人研究项目；未发现所用地图仓库的独立许可声明，因此不把游戏地图宣称为可任意再分发的开源资源。Leaflet 1.9.4 为 BSD-2-Clause。中文摘要与交互界面独立编写，来源保留供复核。',
 ]
(dist/'validation-report.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'status':qa['status'],'automatedChecks':qa['automatedChecksPassed'],'datasetSha256':digest}))
