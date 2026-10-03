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
if asset:
 assert asset['status']=='pass' and asset['datasetSha256']==digest
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
current_inputs={name:hashlib.sha256((root/'dist'/name).read_bytes()).hexdigest() for name in ['app.js','index.html','style.css','exploration.js','exploration.css','exploration.json','progress.js','progress.css']}
assert browser.get('runtimeInputHashes')==current_inputs, 'Browser checks must match current runtime inputs'
if browser.get('executionEnvironment')=='cloud-linux' and browser.get('runtimeInputHashes')==current_inputs: cloud=None
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
for name,expected in progress['runtimeInputHashes'].items():
 assert expected==hashlib.sha256((root/'dist'/name).read_bytes()).hexdigest(), name
places=read('dist/places-zh.json')
summary=[
 {'name':'任务数据与规则','detail':f"{logic['passed']}/{logic['total']} 项；任务引用、地图资源、结局条件、流程前置",'status':'通过'},
 {'name':'网页实际交互','detail':f"{browser['passed']}/{browser['total']} 项；五区地图、筛选、101 个选项、剧透与手机操作",'status':'通过'},
 {'name':'攻略事实核对','detail':'16 项重点核对；40 个任务／45 个节点附攻略依据','status':'资料核对完成'},
 {'name':'地图位置抽样','detail':'4 个独立坐标样例及地图裁切，校准社区坐标转换','status':'抽样一致'},
 {'name':'实机游戏验证','detail':'没有读取游戏存档或逐任务运行游戏','status':'未执行'},
]
summary.insert(1,{'name':'个人进度与分享','detail':f"{progress['passed']}/{progress['total']} 项；完成、收藏、可靠导入导出、刷新恢复、分享与前进后退",'status':'通过'})
summary.insert(1,{'name':'基础探索图层','detail':f"{exploration_data['passed']+exploration_browser['passed']}/{exploration_data['total']+exploration_browser['total']} 项；70 个点位（29 魔力之所、35 告示板、6 储藏箱），来源对账、32 种图层组合、手机操作",'status':'通过'})
if asset:summary.insert(2,{'name':'报告与资源交付','detail':f"{asset['passed']}/{asset['total']} 项；报告、下载与资源加载",'status':'通过'})
if landmark:summary.insert(2,{'name':'地名与路标显示','detail':f"{landmark['passed']}/{landmark['total']} 项；五区 227 个路标、默认地名、缩放拖动和手机",'status':'通过'})
if navigation:summary.insert(2,{'name':'中文地名与缩放体验','detail':f"{navigation['passed']}/{navigation['total']} 项；227 个中文地名、滚轮锚点、连续点击、概览与双指手势",'status':'通过'})
qa={'date':logic['date'],'executionEnvironment':'cloud-linux','executedAt':logic.get('executedAt'),'status':'partial' if cloud and cloud['browserStatus']=='blocked' else 'pass','datasetSha256':digest,'summary':summary,
 'automatedChecksPassed':logic['passed']+browser['passed']+(asset['passed'] if asset else 0)+(landmark['passed'] if landmark else 0)+(navigation['passed'] if navigation else 0),
 'coverage':{'quests':len(d['quests']),'main':87,'side':180,'positioned':149,'communityCoordinates':133,'landmarkAnchors':16,'flowOrUnmapped':118,'reviewedBranchTasks':40,'decisionNodes':45,'decisionOptions':101},
 'limits':d['meta']['limitations'],
 'evidence':{'data':'checks/data-logic.json','browser':'checks/browser.json','assets':'checks/assets.json' if asset else None},
 'webMCP':browser['webMCP']}
qa['automatedChecksPassed']+=exploration_data['passed']+exploration_browser['passed']+progress['passed']
qa['evidence']['progress']='checks/progress.json'
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
 '本报告记录本次云端实际数据与浏览器检查；各项结果附执行时间与文件摘要。历史本地结果独立保留。网页检查不等于游戏实机全量验收，也不是官方任务完整性证明。',
 '',
 '## 覆盖',
 '',
 '- 267 个任务条目：87 个主线、180 个支线。本体 195、石之心 16、血与酒 56。',
 '- 149 个地图定位：133 个社区接取坐标、16 个相关地标。另 118 个流程／未知坐标条目保留在索引中。',
 '- 五个真实地区地图：白果园、威伦／诺维格瑞、史凯利杰、凯尔莫罕、陶森特。维吉玛王宫仅显示室内剧情任务。',
 '- 40 个重点任务的 45 个决策节点、101 个选项；尚未整理分支的任务有明确提示。',
 '- 支线范围含竞赛和昆特任务；随机遭遇、狩魔委托、寻宝不在目录范围内。',
 '- 70 个独立探索点：29 魔力之所、35 告示板、6 储藏箱。与任务目录分开统计。',
 '',
 '## 验证结果',
 '',
 f"本次云端检查日期：{logic['date']}。历史本地 66 项验收保存在源码 evidence/history/local-2026-10-02/，不计为本次云端通过。云端浏览器状态见下表。",
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
 f"[逐项结果](checks/browser.json)：{browser['passed']}/{browser['total']} 项通过。执行来源：{browser.get('executionEnvironment','historical-local')}，日期：{browser['date']}。本次云端是否通过见上述状态。",'']
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
 '数值样例用于检查坐标转换；裁切用于建筑与地标的一致性抽样。没有验证全部 149 个点的游戏内 NPC 站位。',
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
lines += ['','### 基础探索点与图层验收','',f"[数据对账](checks/exploration-data.json)：{exploration_data['passed']}/{exploration_data['total']} 项；[浏览器操作](checks/exploration-browser.json)：{exploration_browser['passed']}/{exploration_browser['total']} 项。",'', '从 72 条冻结来源记录整理得到 70 个点位：合并陶森特鸡蛇旅馆告示板的一条重复记录；带童话世界独立场景标识、位于当前区域底图范围外的一条告示板暂缓展示。整理账目见 [探索点清单](exploration.json)。', '图层支持任务、路标和三类探索点独立开关，32 种组合均按独立地区清单检查；全隐藏后恢复先前选择。点击探索点显示用途、最近参考路标和来源。', '最近路标按游戏 XY 直线距离选择，不代表可步行到达。是否开放需要结合任务阶段和游戏内状态，未逐点实机复核。', '', '验收画面：[探索地图](checks/exploration-map.png)、[点位详情](checks/exploration-desktop.png)、[手机图层](checks/exploration-mobile-layers.png)、[手机详情](checks/exploration-mobile.png)。','']
lines += [f"- {check['name']}：{check['detail']}。" for check in exploration_data['checks']+exploration_browser['checks']]
lines += ['', '### 个人进度、备份与定位分享', '', f"[逐项结果](checks/progress.json)：{progress['passed']}/{progress['total']} 项通过。", '', '任务与探索点可完成、收藏、按个人记录筛选及隐藏已完成。记录、地区、筛选、视野和已选决策保存在当前设备浏览器；不是读取游戏存档，也没有账号云同步。', '备份恢复先预览并验证：无效 JSON、未知备份版本、非布尔标记、危险标识和过大文件不能覆盖当前记录。未知对象和决策保持在未匹配账目中，便于后续迁移。', '分享定位只包含地区、任务或探索点 ID，不夹带个人记录或决策。刷新后仍默认隐藏剧透，前进／后退可返回对应对象；未知链接显示提示。', '浏览器禁止或损坏存储时地图可使用，明确提示保存失败，并可导出本次记录。', '', '验收画面：[备份预览与恢复](checks/progress-desktop.png)、[手机记录](checks/progress-mobile-detail.png)、[手机备份](checks/progress-mobile.png)。', '']
lines += [f"- {check['name']}：通过。" for check in progress['checks']]
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
