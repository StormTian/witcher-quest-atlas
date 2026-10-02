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
summary=[
 {'name':'任务数据与规则','detail':f"{logic['passed']}/{logic['total']} 项；任务引用、地图资源、结局条件、流程前置",'status':'通过'},
 {'name':'网页实际交互','detail':f"{browser['passed']}/{browser['total']} 项；五区地图、筛选、101 个选项、剧透与手机操作",'status':'通过'},
 {'name':'攻略事实核对','detail':'16 项重点核对；40 个任务／45 个节点附攻略依据','status':'资料核对完成'},
 {'name':'地图位置抽样','detail':'4 个独立坐标样例及地图裁切，校准社区坐标转换','status':'抽样一致'},
 {'name':'实机游戏验证','detail':'没有读取游戏存档或逐任务运行游戏','status':'未执行'},
]
if asset:summary.insert(2,{'name':'报告与资源交付','detail':f"{asset['passed']}/{asset['total']} 项；报告、下载与资源加载",'status':'通过'})
if landmark:summary.insert(2,{'name':'地名与路标显示','detail':f"{landmark['passed']}/{landmark['total']} 项；五区 227 个路标、默认地名、缩放拖动和手机",'status':'通过'})
qa={'date':d['meta']['date'],'status':'pass','datasetSha256':digest,'summary':summary,
 'automatedChecksPassed':logic['passed']+browser['passed']+(asset['passed'] if asset else 0)+(landmark['passed'] if landmark else 0),
 'coverage':{'quests':len(d['quests']),'main':87,'side':180,'positioned':149,'communityCoordinates':133,'landmarkAnchors':16,'flowOrUnmapped':118,'reviewedBranchTasks':40,'decisionNodes':45,'decisionOptions':101},
 'limits':d['meta']['limitations'],
 'evidence':{'data':'checks/data-logic.json','browser':'checks/browser.json','assets':'checks/assets.json' if asset else None},
 'webMCP':browser['webMCP']}
if landmark:
 qa['coverage']['roadSigns']=227
 qa['evidence']['landmarks']='checks/landmarks.json'
dist=root/'dist';(dist/'checks').mkdir(exist_ok=True)
for f,target in [('data-logic-validation.json','data-logic.json'),('browser-validation.json','browser.json')]:
 shutil.copyfile(root/'evidence'/f,dist/'checks'/target)
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
 f"资料与验证日期：{d['meta']['date']}。目录版本：{d['meta']['catalogVersion']}。",
 '',
 '本报告证明所列资料检查与网页交互检查已经执行并通过。它不等于游戏实机全量验收，也不是官方任务完整性证明。',
 '',
 '## 覆盖',
 '',
 '- 267 个任务条目：87 个主线、180 个支线。本体 195、石之心 16、血与酒 56。',
 '- 149 个地图定位：133 个社区接取坐标、16 个相关地标。另 118 个流程／未知坐标条目保留在索引中。',
 '- 五个真实地区地图：白果园、威伦／诺维格瑞、史凯利杰、凯尔莫罕、陶森特。维吉玛王宫仅显示室内剧情任务。',
 '- 40 个重点任务的 45 个决策节点、101 个选项；尚未整理分支的任务有明确提示。',
 '- 支线范围含竞赛和昆特任务；随机遭遇、狩魔委托、寻宝不在目录范围内。',
 '',
 '## 验证结果',
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
 '### 浏览器实际操作',
 '',
 f"[逐项结果](checks/browser.json)：{browser['passed']}/{browser['total']} 项通过。在 Google Chrome 中实际加载页面并执行操作。",'']
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
 lines += ['','### 本次地名更新验收','',f"[逐项结果](checks/landmarks.json)：{landmark['passed']}/{landmark['total']} 项通过。227 个原有快速旅行路标现在默认显示名称，密集处的主要地名避让后用细线指回路标；可用“地名”按钮开关。",'']
 lines += [f"- {c['name']}：{c['detail']}。" for c in landmark['checks']]
 lines += ['','更新画面：[桌面地名](checks/landmarks-desktop.png)、[手机地名](checks/landmarks-mobile.png)。原有 19 项完整流程验收保留；本次新增地名叠加和地图操作由上述专门检查复验。','']
lines += ['', '### 重点事实与来源', '', '| 核对项目 | 结论 | 依据 |', '| --- | --- | --- |']
lines += [f"| {c['claim']} | {c['result']} | [攻略]({c['source']}) |" for c in d['meta']['factChecks']]
lines += [
 '',
 '### 已修复的资料问题',
 '',
 ]+[f"- {s}" for s in d['meta']['corrections']]
lines += [
 '- “为祖国”前置保留 Wiki 关于特定阶段失败的记录；“以眼还眼”需到薇丝战斗、“瑞达尼亚的头号要犯”需取得抛光水晶。“致命阴谋”仍须完成，并需在“显而易见”中交换恩希尔情报。[详细依据](https://witcher.fandom.com/wiki/Reason_of_State)。',
 '- 初轮缩放检查在地图动画结束前读取状态，产生一次误报。改为等待动画完成后复测，缩放、拖动和复位均通过。失败画面保存在本地 evidence/failure-5.png。',
 '',
 '## 可重复核验',
 '',
 f"最终任务数据 SHA-256：`{digest}`。",
 '',
 '地图／社区数据来源锁定为 Witcher3MapViewer commit `fb674dbff7df087d0a45f9b3938ba6d5317295af`。来源 XML 与地图清单在源码项目 evidence/ 中保留；可重新生成任务数据，执行数据检查，并在本地服务中重跑浏览器操作。',
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
print(json.dumps({'status':'pass','automatedChecks':qa['automatedChecksPassed'],'datasetSha256':digest}))
