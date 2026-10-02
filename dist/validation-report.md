# 狩魔手记：互动地图验证报告

资料与验证日期：2026-10-02。目录版本：1.0。

本报告证明所列资料检查与网页交互检查已经执行并通过。它不等于游戏实机全量验收，也不是官方任务完整性证明。

## 覆盖

- 267 个任务条目：87 个主线、180 个支线。本体 195、石之心 16、血与酒 56。
- 149 个地图定位：133 个社区接取坐标、16 个相关地标。另 118 个流程／未知坐标条目保留在索引中。
- 五个真实地区地图：白果园、威伦／诺维格瑞、史凯利杰、凯尔莫罕、陶森特。维吉玛王宫仅显示室内剧情任务。
- 40 个重点任务的 45 个决策节点、101 个选项；尚未整理分支的任务有明确提示。
- 支线范围含竞赛和昆特任务；随机遭遇、狩魔委托、寻宝不在目录范围内。

## 验证结果

| 范围 | 实际检查 | 结果 |
| --- | --- | --- |
| 任务数据与规则 | 25/25 项；任务引用、地图资源、结局条件、流程前置 | 通过 |
| 网页实际交互 | 19/19 项；五区地图、筛选、101 个选项、剧透与手机操作 | 通过 |
| 中文地名与缩放体验 | 11/11 项；227 个中文地名、滚轮锚点、连续点击、概览与双指手势 | 通过 |
| 地名与路标显示 | 8/8 项；五区 227 个路标、默认地名、缩放拖动和手机 | 通过 |
| 报告与资源交付 | 3/3 项；报告、下载与资源加载 | 通过 |
| 攻略事实核对 | 16 项重点核对；40 个任务／45 个节点附攻略依据 | 资料核对完成 |
| 地图位置抽样 | 4 个独立坐标样例及地图裁切，校准社区坐标转换 | 抽样一致 |
| 实机游戏验证 | 没有读取游戏存档或逐任务运行游戏 | 未执行 |

### 数据与结局规则

[逐项结果](checks/data-logic.json)：25/25 项通过。

- 目录唯一性与范围：267 unique quests; 87 main, 180 side。
- 任务与决策引用完整性：45 nodes / 101 options, all referenced task IDs resolve。
- 坐标与流程分类：149 positioned tasks, 118 flow/unmapped entries; no invented coordinates。
- 独立接取点校准样例：4 independent numeric fixtures; corresponding XYZ map tiles present。
- 地图资源完整性：5 regions / 5721 native map tiles; full z4 and z5 coverage for the larger regions。
- 目录交叉覆盖：261 normalized catalog entries matched (split phases merged); this is not an official completeness proof。
- 希里条件：未觐见，四项全积极：witcher。
- 希里条件：未觐见，二比二边界：witcher。
- 希里条件：未觐见，仅一次积极：tragedy。
- 希里条件：觐见，收钱但其余全积极：empress。
- 希里条件：觐见，二项积极并拒绝酬金：empress。
- 希里条件：觐见，二项积极并收钱：tragedy。
- 希里条件：觐见，迪科斯彻获胜：witcher。
- 希里条件：觐见，拉多维德获胜：witcher。
- 未发生的酬金节点不计分：16 combinations checked。
- 血与酒条件：完整条件：reconcile。
- 血与酒条件：缺缎带：syanna-dies。
- 血与酒条件：只有缎带，缺第五人调查：both-die。
- 血与酒条件：缺日记：both-die。
- 血与酒条件：缺席安娜故事：both-die。
- 血与酒条件：劝解失败：both-die。
- 血与酒条件：暗影长者不能和解：both-die。
- 无效输入被拒绝：invalid enums and types rejected。
- 关键来源边界未丢失：6 high-risk facts plus correct DLC starting region and palace。
- 流程前置与失败例外的独立核对：12 source-derived predecessor fixtures and 3 timing/failure boundaries。

### 浏览器实际操作

[逐项结果](checks/browser.json)：19/19 项通过。在 Google Chrome 中实际加载页面并执行操作。

- 桌面初始状态与剧透保护：通过。
- 五个地区地图实际加载：通过。
- 王宫不显示虚构地图：通过。
- 点击真实地图标记打开任务：通过。
- 缩放、拖动与地区复位：通过。
- 中文、英文和人物跨地区搜索：通过。
- 主线、支线、资料片与分支筛选：通过。
- 仅展开本任务剧透，其他任务仍隐藏：通过。
- 条件分支随前序选项解锁或清空：通过。
- 全部101个分支选项实际点击：通过。
- 希里结局演算的关键边界：通过。
- 血与酒结局演算不会把缎带当作和解：通过。
- 关闭全局剧透清空所有局部展开：通过。
- 键盘访问与快捷搜索：通过。
- 1280 × 720 与200%文字放大：通过。
- 手机首屏与地图：通过。
- 手机任务索引、详情与关闭：通过。
- 验证窗口、资料来源与可检查地图证据：通过。
- 页面运行与资源错误检查：通过。

验收画面：[桌面](checks/desktop-final.png)、[手机](checks/mobile-final.png)、[分支展开](checks/decision-final.png)、[验证窗口](checks/mobile-audit.png)、[200% 文字](checks/text-200.png)。

WebMCP 在验收浏览器中不可用，因此未计入通过项目。普通页面功能不依赖它。

### 地图校准

地图与坐标采用同一个 Witcher3MapViewer 来源版本，未混用不同投影的社区地图。MBTiles 的 TMS 行号转换为 XYZ；游戏 XY 经各地区校准后转为 Leaflet 使用的合成坐标，不是现实地理经纬度。

| 独立样例 | 核对内容 | 证据 |
| --- | --- | --- |
| 失踪的兄弟 | 白果园洗劫村庄的接取点 | [裁切](assets/check-19.jpg) |
| 扭曲的纵火犯 | 白果园铁匠附近建筑 | [裁切](assets/check-37.jpg) |
| 宝剑与饺子 | 诺维格瑞铁匠街区 | [裁切](assets/check-263.jpg) |
| 唯有一人 | 鲍克兰告示板，不是湖上试炼目标 | [裁切](assets/check-424.jpg) |

数值样例用于检查坐标转换；裁切用于建筑与地标的一致性抽样。没有验证全部 149 个点的游戏内 NPC 站位。


### 本次地名更新验收

[逐项结果](checks/landmarks.json)：8/8 项通过。227 个原有快速旅行路标现在默认显示名称，密集处的主要地名避让后用细线指回路标；可用“地名”按钮开关。

- 地名默认显示且主城可辨认：no hover needed; Novigrad, Crow’s Perch and major landmarks labeled。
- 五区227个路标对应原有坐标：all 227 road signs use unchanged source coordinates in all 5 regions。
- 地名不相互遮挡且保留地图控件：actual text boxes avoid each other and map title, compass, tools, legend and attribution。
- 缩放拖动后仍显示对应地点：zoom to Corvo Bianco and physical pointer drag update labels correctly。
- 地名开关和任务筛选彼此独立：toggle affects only places; empty quest search still leaves orientation landmarks。
- 路标可点开且不阻挡任务标记：physical click opens a road sign popup; q37 task marker and default spoiler protection work。
- 手机首屏地名和开关可用：390 × 844; city and major place names visible immediately, toggle works and no horizontal overflow。
- 运行与资源错误：zero page exceptions or HTTP failures。

更新画面：[桌面地名](checks/landmarks-desktop.png)、[手机地名](checks/landmarks-mobile.png)。19 项完整流程也已重新验收；新增地名叠加和地图操作由上述专门检查复验。


### 中文地名与缩放更新验收

[逐项結果](checks/navigation.json)：11/11 项通过。每次加减或单次滚轮操作只改变 0.25 级；鼠标位置为缩放锚点。选任务保留倍率，返回地区保留原视野。概览亮框显示当前窗口，点击概览可平移。

- 227个地名有来源且地图无英文回退：all 227 road signs, marker titles, map labels and region subtitles display Chinese。
- 中文译名用独立样例核对：8 fixed source-derived examples; no guessed Blackbough or Cackler translation, distinct Elverum lighthouse。
- 加减按钮每次只改变四分之一档：2 → 2.25 → 2; map center drift at most 2 pixels。
- 真实滚轮缩放保持鼠标下的位置：physical mouse wheel; quarter step, cursor anchor drift 0.63 pixels。
- 大滚轮事件不会跨越多个倍率：a 3000-pixel wheel event still produces only one quarter step。
- 连续五次点击不会漏掉缩放：5 physical clicks = 1.25 levels; queued zoom survives an in-progress animation。
- 选任务保留倍率，换区回来保留视野：task focus retains 3.25 zoom; returning to Velen restores center within 3 pixels。
- 放大使用原生细节图且有上限：native z5 WebP details load; maximum 5.5 prevents unlimited blurry enlargement。
- 概览框跟随视野且点击保留倍率：overview rectangle shrinks on zoom; clicking overview moves the center without changing magnification。
- 手机小步缩放与双指手势：390 × 844; quarter-step buttons and a real two-touch pinch both work without horizontal overflow。
- 地图平移边界和运行错误：panning remains inside the map world; zero script exceptions or failed HTTP requests。

更新画面：[桌面](checks/navigation-desktop.png)、[手机双指缩放](checks/navigation-mobile.png)。

中文名称对照：[227 个逐项名称与来源](places-zh.json)、[公开中文游戏地图](https://www.tivaprojects.com/witcher3map/)。
公开游戏中文地图的中英路标对照；繁体中文逐字转简，保留原文与来源。
不是直接从官方简中语言文件导出；没有逐项实机比对。官中繁、简版本可能有不同用词。
修正原来手工译名，如 Cackler Bridge 为“嘻笑者之桥”、Blackbough 为“大黑树”、Lornruk 为“孤岩”、Tesham Mutna 为“迪沙谬那”。另修正社区中文对照把 Elverum 与 Eldberg 灯塔写成同名的问题，[艾孚鲁灯塔核对](https://witcher.huijiwiki.com/wiki/艾孚鲁灯塔)。
凯尔莫罕来源旧名通过地图相对位置对应当前路标：The Morhen Eye 为堡垒、Outpost ruins 为被毁的瞭望塔、Morhen Mine dam 为铁矿、The Lake House 为湖畔小屋。没有移动这些点的坐标。
底图继续使用同一来源版本，较大地图增加原生 4、5 级细节瓦片，以 WebP 质量 88 压缩；总计 5721 个瓦片。白果园原生上限 4，其余地区 5；最多再放大半级，避免无限拉伸。
首轮发现连续点击丢失一档，已修正动画期间的目标倍率队列。双指验收使用载入页面前就启用的触摸设备模式；桌面页面载入后切换触摸模拟不能证明手机手势正常。


### 重点事实与来源

| 核对项目 | 结论 | 依据 |
| --- | --- | --- |
| 白果园的纵火犯 | 与地图建筑对齐；不是随意插点 | [攻略](https://witcher.fandom.com/wiki/Twisted_Firestarter) |
| 失踪的兄弟 | 标记对应洗劫村庄的接取角色 | [攻略](https://witcher.fandom.com/wiki/Missing_in_Action) |
| 宝剑与饺子 | 标记对应诺维格瑞的铁匠街区 | [攻略](https://witcher.fandom.com/wiki/Of_Swords_and_Dumplings) |
| 唯有一人 | 标记是告示板，试炼在湖上 | [攻略](https://witcher.fandom.com/wiki/There_Can_Be_Only_One) |
| 最后的愿望 | 领走乌马前处理，非一律迷雾之岛门槛 | [攻略](https://witcher.fandom.com/wiki/The_Last_Wish_(quest)) |
| 呢喃山丘 | 提前释放与正常释放分开叙述 | [攻略](https://witcher.fandom.com/wiki/The_Whispering_Hillock) |
| 重回驼背泥沼 | 正确娃娃不等于安娜最终存活 | [攻略](https://witcher.fandom.com/wiki/Return_to_Crookback_Bog) |
| 以知识进步为名 | 凯拉的三种去向 | [攻略](https://witcher.fandom.com/wiki/For_the_Advancement_of_Learning) |
| 肉体之罪 | 先问清楚再行动，保留真正凶手线 | [攻略](https://witcher.fandom.com/wiki/Carnal_Sins) |
| 特莉丝恋情 | 前序亲吻＋留下＋告白 | [攻略](https://witcher.fandom.com/wiki/Now_or_Never) |
| 为祖国 | 刺杀前置与外交选择共同决定 | [攻略](https://witcher.fandom.com/wiki/The_Witcher_3_decision_checklist) |
| 石之心终章 | 教授调查是介入救人的前提 | [攻略](https://witcher.fandom.com/wiki/Whatsoever_a_Man_Soweth...) |
| 血与酒终章 | 缎带生存与姐妹和解条件分开 | [攻略](https://witcher.fandom.com/wiki/Pomp_and_Strange_Circumstance) |
| 长牙之夜 | 寻找欧丽安娜本身不锁定路线 | [攻略](https://witcher.fandom.com/wiki/The_Night_of_Long_Fangs) |
| 骑士的恋爱故事 | 守密／转移诅咒的长期后果 | [攻略](https://witcher.fandom.com/wiki/The_Warble_of_a_Smitten_Knight) |
| 葡萄酒大战 | 联合并非所有和解路线的必经任务 | [攻略](https://witcher.fandom.com/wiki/Wine_Wars:_The_Deus_in_the_Machina) |

### 已修复的资料问题

- 移除 5 条购书步骤、2 条主线目标和 1 条误归类寻宝任务。
- 合并本体结局的 3 个条目；合并贝尔迦德任务的两个阶段。
- 纠正凯尔莫罕教学、觐见皇帝、丑陋的婴儿、使节与酒差、并肩作战与数条最终章任务的起始地区。
- 纠正诺维格瑞黑帮、三人探戈与最后的善举的分类；补充 4.0 新任务、总任务与竞赛条目。
- 补全 35 项无 XML 前置链接的触发说明；修正“为祖国”前置成功／失败状态不能一概而论的问题。
- “为祖国”前置保留 Wiki 关于特定阶段失败的记录；“以眼还眼”需到薇丝战斗、“瑞达尼亚的头号要犯”需取得抛光水晶。“致命阴谋”仍须完成，并需在“显而易见”中交换恩希尔情报。[详细依据](https://witcher.fandom.com/wiki/Reason_of_State)。
- 初轮缩放检查在地图动画结束前读取状态，产生一次误报。改为等待动画完成后复测，缩放、拖动和复位均通过。失败画面保存在本地 evidence/failure-5.png。

## 可重复核验

最终任务数据 SHA-256：`2a3bb7d2b153174966ec2c4125dc2a57343b55b065884ce9ae3047f7e351faa9`。

地图／社区数据来源锁定为 Witcher3MapViewer commit `fb674dbff7df087d0a45f9b3938ba6d5317295af`。来源 XML 与地图清单在源码项目 evidence/ 中保留；可重新生成任务数据，执行数据检查，并在本地服务中重跑浏览器操作。

浏览器检查按照页面自己的选项数据逐一点击，能发现渲染、引用与条件解锁故障；它不是独立证明全部中文后果文本正确的方式。后果的事实核对依靠每节点攻略链接，两个结局规则另使用预先声明的边界样例检查。

## 边界

- 社区坐标没有逐个在游戏中复测；移动角色位置与版本变化可能影响接取。
- 地标标记只定位相关地点，不代表 NPC 的精确站位。
- 没有坐标的流程任务仍在目录中，不会被随机放在地图上。
- 决策树集中于已核对的关键分支；未收录分支不代表任务没有后果。
- 中文名用于检索，保留英文原名以便对照不同汉化版本。
- 未做逐任务实机验证，也未保证所有对话、随机遭遇和版本特例都收录；可用来源链接继续核对。
- 希里未觐见时二比二的边界按 Wiki 四项记分解释；其他攻略把跳过觐见计为第五项积极，得到相同结果。这个边界未实机复测。
- 结局演算只覆盖说明中的主干条件，不读取存档，也不推断未输入的其他游戏状态。
- 网页默认隐藏决策后果，只有主动展开或使用全局开关后才出现；验证报告自身包含剧情信息。

## 资料与版权

- [地图与接取坐标：Witcher3MapViewer](https://github.com/reubengann/Witcher3MapViewer)
- [任务目录交叉对照：Gercius](https://github.com/Gercius/witcher3-quest-manager)
- [本体主线目录](https://witcher.fandom.com/wiki/The_Witcher_3_main_quests)
- [本体支线目录](https://witcher.fandom.com/wiki/The_Witcher_3_secondary_quests)
- [石之心目录](https://witcher.fandom.com/wiki/Hearts_of_Stone_quests)
- [血与酒目录](https://witcher.fandom.com/wiki/Blood_and_Wine_quests)
- [重点结局交叉核对：PC Gamer](https://www.pcgamer.com/all-witcher-3-endings-ciri-blood-and-wine-how-many/)
- [树灵分支交叉核对：Gamer Guides](https://www.gamerguides.com/the-witcher-3-wild-hunt/guide/walkthrough/velen/the-whispering-hillock)

游戏地图与游戏内容版权归 CD PROJEKT RED 所有。本工具是非官方个人研究项目；未发现所用地图仓库的独立许可声明，因此不把游戏地图宣称为可任意再分发的开源资源。Leaflet 1.9.4 为 BSD-2-Clause。中文摘要与交互界面独立编写，来源保留供复核。
