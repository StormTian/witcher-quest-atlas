# 狩魔手记：互动地图验证报告

任务资料日期：2026-10-03；本次验证日期：2026-10-17。目录版本：1.4。

本报告记录本次自动化环境中的实际数据与浏览器检查；各项结果附执行时间与文件摘要。历史本地结果独立保留。网页检查不等于游戏实机全量验收，也不是官方任务完整性证明。

## 覆盖

- 428 个任务／遭遇条目。分类：contract 35、encounter 40、main 87、scavenger 29、side 180、treasure 57。原有 267 个 ID 和主线／支线分类保留。
- 304 个地图定位：288 个社区发现／接取线索、16 个关联地标。另 124 个流程／未知坐标条目保留在索引中。
- 五个真实地区地图：白果园、威伦／诺维格瑞、史凯利杰、凯尔莫罕、陶森特。维吉玛王宫仅显示室内剧情任务。
- 43 个重点任务的 48 个决策节点、108 个选项；尚未整理分支的任务有明确提示。
- 目录包含主线／支线、狩魔委托、套装搜集、寻宝与随机遭遇；阶段、组件和探索资源点分别归类。
- 615 个独立探索点，13 类：设施、服务、昆特、资源与洞穴入口。与任务目录分开统计。

## 验证结果

本次检查日期：2026-10-17；执行环境：local-macos-chromium-151.0.7922.34。历史本地 66 项验收保存在源码 evidence/history/local-2026-10-02/，不计为本次通过。浏览器状态见下表。

| 范围 | 实际检查 | 结果 |
| --- | --- | --- |
| 任务数据与规则 | 25/25 项；任务引用、地图资源、结局条件、流程前置 | 通过 |
| 防漏清单与条件联动 | 26/26 项；43 条阶段提醒、未知条件、失败例外、路线互斥、备份与逐任务剧透 | 通过 |
| 扩充目录与服务点 | 20/20 项；428 条目录、615 点位、来源归并、六类筛选、密集点与旧备份 | 通过 |
| 探索图层 | 15/15 项；615 个点位；来源对账、基础图层 32 种组合、手机操作 | 通过 |
| 中文地名与缩放体验 | 11/11 项；227 个中文地名、滚轮锚点、连续点击、概览与双指手势 | 通过 |
| 地名与路标显示 | 8/8 项；五区 227 个路标、默认地名、缩放拖动和手机 | 通过 |
| 报告与资源交付 | 3/3 项；报告、下载与资源加载 | 通过 |
| 个人进度与分享 | 13/13 项；完成、收藏、可靠导入导出、刷新恢复、分享与前进后退 | 通过 |
| 网页实际交互 | 19/19 项；五区地图、筛选、108 个选项、剧透与手机操作 | 通过 |
| 攻略事实核对 | 19 项重点核对；43 个任务／48 个节点附攻略依据 | 资料核对完成 |
| 地图位置抽样 | 4 个独立坐标样例及地图裁切，校准社区坐标转换 | 抽样一致 |
| 实机游戏验证 | 没有读取游戏存档或逐任务运行游戏 | 未执行 |

### 数据与结局规则

[逐项结果](checks/data-logic.json)：25/25 项通过。

- 目录唯一性与范围：428 unique quests; frozen source reconciliation and legacy main/side classifications match。
- 任务与决策引用完整性：48 nodes / 108 options, all task references resolve。
- 坐标与流程分类：304 positioned tasks; flow/unknown entries retained without invented coordinates。
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

### 浏览器实际操作与来源

[逐项结果](checks/browser.json)：19/19 项通过。执行来源：local-macos-chromium-151.0.7922.34，日期：2026-10-17。当前运行结果见上述状态。

- 桌面初始状态与剧透保护：通过。
- 五个地区地图实际加载：通过。
- 王宫不显示虚构地图：通过。
- 点击真实地图标记打开任务：通过。
- 缩放、拖动与地区复位：通过。
- 中文、英文和人物跨地区搜索：通过。
- 主线、支线、资料片与分支筛选：通过。
- 仅展开本任务剧透，其他任务仍隐藏：通过。
- 条件分支随前序选项解锁或清空：通过。
- 全部已整理分支选项实际点击：通过。
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

数值样例用于检查坐标转换；裁切用于建筑与地标的一致性抽样。没有验证全部点位的游戏内 NPC 站位或开放状态。


### 本次云端地名更新验收

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


### 本次云端中文地名与缩放更新验收

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


### 基础探索点与图层验收

[数据对账](checks/exploration-data.json)：7/7 项；[浏览器操作](checks/exploration-browser.json)：8/8 项。

从 617 条冻结来源记录整理得到 615 个点位：合并陶森特鸡蛇旅馆告示板的一条重复记录；带童话世界独立场景标识、位于当前区域底图范围外的一条告示板暂缓展示。整理账目见 [探索点清单](exploration.json)。
图层支持任务、路标和 13 类探索点独立开关。基础五图层的 32 种组合仍按旧独立清单回归；新增服务和资源层默认关闭，支持搜索、全选、全隐藏和恢复，密集探索点可聚合选择。点击探索点显示用途、最近参考路标和来源。
最近路标按游戏 XY 直线距离选择，不代表可步行到达。是否开放需要结合任务阶段和游戏内状态，未逐点实机复核。

验收画面：[探索地图](checks/exploration-map.png)、[点位详情](checks/exploration-desktop.png)、[手机图层](checks/exploration-mobile-layers.png)、[手机详情](checks/exploration-mobile.png)。

- 原始记录逐条对账：Locked source hash; all 617 raw records independently accounted for, with original XY retained.。
- 独立分类与地区清单：615 audited records; exact per-category counts independently declared for all five regions.。
- 重复与独立场景处理：Duplicate Cockatrice Inn board merged; separate-scene candidate withheld from Toussaint.。
- 独立坐标样例与区域边界：Five predeclared coordinate fixtures match; every point has finite coordinates in its own region.。
- 稳定标识与引用：Unique stable source identities, separate from quest IDs; all reference landmarks resolve in the same region.。
- 旧任务目录保持：All 267 legacy IDs, classifications, titles, expansion boundaries and coordinates retain their frozen baseline values.。
- 来源与精度边界：Every point retains frozen source provenance and unknown-availability limits; no in-game verification claimed.。
- 五区探索点与来源清单数量：White Orchard 8, Velen 29, Skellige 18, Toussaint 13, Kaer Morhen 2; no fabricated Vizima point.。
- 32种图层组合及任务索引独立性：All 32 combinations match independently declared Velen counts; the preserved 85-side-quest index remains available.。
- 全隐藏恢复原选择并隐藏任务高亮：Restores the prior partial selection; hidden quest layers stay hidden when a quest is opened from the index.。
- 三类点位真实点击详情与键盘操作：All three types open through real marker clicks; keyboard Enter and Space open a board; provenance and availability limits remain visible.。
- 任务筛选与探索图层互不干扰：Empty task search and DLC filtering leave exploration and road signs intact; point selection preserves filters.。
- 地图叠加与密集区渲染耗时：25 real Velen renders; p95 1.6ms on this cloud Chromium; map controls have their own stacking context.。
- 手机图层与探索详情及200%文字：390×844 touch device; layer toggles, Escape/focus return, tap-to-detail and doubled text remain usable without page overflow.。
- 探索资源与页面异常：Zero page exceptions and zero unexpected HTTP failures across the exploration interactions.。

### 第三轮目录与探索来源对账

[数据对账](checks/catalog-data.json)：10/10；[浏览器](checks/catalog-browser.json)：10/10。

新增 161 条独立目录，保留原 267 个 ID。162 条 XML 候选和 177 条独立参考记录逐行绑定；套装组件、任务目标、重复阶段与旧酒商委托不重复计数。15 处推荐等级差异显式保留。
[完整对照清单](catalog-review.json)包含合并依据与来源；其中可能包含剧情信息。没有可靠定位的条目继续从目录访问，套装售图线索不冒充所有图纸位置。
探索来源的共享／空白标识使用维护的 ID 映射，坐标不进入永久 ID；服务点不宣称完整名单或工匠能力。
WebMCP 新类型使用注册接口夹具验证输入与返回契约，实际浏览器仍不支持原生上下文，未宣称原生功能已验证。

[桌面](checks/catalog-desktop.png) · [手机](checks/catalog-mobile.png)


### 个人进度、备份与定位分享

[逐项结果](checks/progress.json)：13/13 项通过。

任务列表可直接勾选完成，顶部显示累计进度。新浏览器默认隐藏已完成，已有筛选偏好保留；列表与地图同步隐藏，选择“已完成”可查看并撤销误勾选。任务与探索点仍共用原有完成、收藏和个人筛选。记录、地区、筛选、视野和已选决策保存在当前设备浏览器；不是读取游戏存档，也没有账号云同步。
备份恢复先预览并验证：无效 JSON、未知备份版本、非布尔标记、危险标识和过大文件不能覆盖当前记录。未知对象和决策保持在未匹配账目中，便于后续迁移。
分享定位只包含地区、任务或探索点 ID，不夹带个人记录或决策。刷新后仍默认隐藏剧透，前进／后退可返回对应对象；未知链接显示提示。
浏览器禁止或损坏存储时地图可使用，明确提示保存失败，并可导出本次记录。

验收画面：[桌面列表勾选](checks/task-progress-desktop.png)、[手机列表勾选](checks/task-progress-mobile.png)、[备份预览与恢复](checks/progress-desktop.png)、[手机记录](checks/progress-mobile-detail.png)、[手机备份](checks/progress-mobile.png)。

- 桌面与手机列表勾选完成后隐藏、刷新恢复并可撤销：通过。
- 任务完成与收藏在刷新、新标签页恢复：通过。
- 任务与探索点的个人筛选及图层数量一致：通过。
- 地区、筛选、视野与决策持久化且剧透默认隐藏：通过。
- 个人备份导出、清空与预览恢复等价：通过。
- 损坏、未知版本、恶意字段和超大备份不覆盖记录：通过。
- 失效 ID 与数据版本变化保留迁移账目：通过。
- 任务与探索点深链接及未知链接提示：通过。
- 浏览器前进后退恢复同一对象及地区：通过。
- 分享链接不泄漏完成、收藏、决策或剧透状态：通过。
- 存储不可用与损坏存储不阻碍地图且有明确提示：通过。
- 手机直达、记录、备份与200%文字可操作：通过。
- 个人进度页面与资源无异常：通过。

### 第四轮防漏、条件状态与跨任务提示

[独立规则](checks/guidance-data.json)：12/12；[浏览器操作](checks/guidance-browser.json)：14/14。

43 条来源明确的剧情阶段提醒；已处理记录可筛选、刷新保存并与现有个人进度共用稳定 ID。来源条件区分全部、任一和进行中，不把前序线索当成全部必须成功。任务级条件只是来源片段，未解析目标继续标明。
个人完成标记与游戏日志成功、失败、进行中及阶段事实分开；未记录保持未知。剧情记录纳入原版本个人备份，旧备份可读取，未知故事 ID 留在迁移账目。
刺杀线保留薇丝战斗／抛光水晶的失败阶段例外，“致命阴谋”仍须成功。教授调查与依赖节点、真正进入长者洞穴后的路线互斥、凯拉与两段恋情的条件分别核对。记录矛盾时按明确阶段事实提示，不偷偷改选择或结局演算。
补审三个任务，共新增三个节点、七个选项，合计 43 个已审任务／48 节点／108 选项。来源包括本次成功抓取的 Gamer Guides 事实段落；Fandom 本次返回 402 的引用只沿用既有核对，不冒充重新抓取。
已选决策的关联后果只有展开目标任务剧透后显示；无自有节点的目标也可单独展开关联提示，失效的条件节点不参与联动。
任务／指导数据生成链两次从冻结输入重建一致；不同数学库的投影尾数允许 1e-9 度数值误差，原始 XY 和稳定 ID 严格保留。

[防漏清单](checks/guidance-checklist.png) · [主线流程](checks/guidance-flow.png) · [条件记录](checks/guidance-conditions.png) · [手机](checks/guidance-mobile.png)


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
| 以眼还眼 | 薇丝生存影响任务收尾与援军；刺杀前置另看指定战斗阶段。 | [攻略](https://www.gamerguides.com/the-witcher-3-wild-hunt/guide/secondary-quests/novigrad/an-eye-for-an-eye) |
| 瑞达尼亚的头号要犯 | 取得抛光水晶与交付对象分开，额外背景对话不改变恋情。 | [攻略](https://www.gamerguides.com/the-witcher-3-wild-hunt/guide/secondary-quests/novigrad/redanias-most-wanted) |
| 致命阴谋 | 和平或战斗均可营救塔勒，须护送并结束对话才算成功。 | [攻略](https://www.gamerguides.com/the-witcher-3-wild-hunt/guide/secondary-quests/novigrad/a-deadly-plot) |

### 已修复的资料问题

- 移除 5 条购书步骤、2 条主线目标和 1 条误归类寻宝任务。
- 合并本体结局的 3 个条目；合并贝尔迦德任务的两个阶段。
- 纠正凯尔莫罕教学、觐见皇帝、丑陋的婴儿、使节与酒差、并肩作战与数条最终章任务的起始地区。
- 纠正诺维格瑞黑帮、三人探戈与最后的善举的分类；补充 4.0 新任务、总任务与竞赛条目。
- 补全 35 项无 XML 前置链接的触发说明；修正“为祖国”前置成功／失败状态不能一概而论的问题。
- 第 3 轮：套装组件、取剑目标和同一挑战者后续阶段合并；五条旧酒商委托加入关联分类而不复制。追寻希里与收集所有卡牌改为总流程语义。
- “为祖国”前置保留 Wiki 关于特定阶段失败的记录；“以眼还眼”需到薇丝战斗、“瑞达尼亚的头号要犯”需取得抛光水晶。“致命阴谋”仍须完成，并需在“显而易见”中交换恩希尔情报。[详细依据](https://witcher.fandom.com/wiki/Reason_of_State)。
- 初轮缩放检查在地图动画结束前读取状态，产生一次误报。改为等待动画完成后复测，缩放、拖动和复位均通过。失败画面保存在历史本地证据 evidence/history/local-2026-10-02/failure-5.png。

## 可重复核验

最终任务数据 SHA-256：`80c2bc7810177855ecfe437b31c46dbdf9fbfd6fe4f3075c22b915378ebcd246`。

地图／社区数据来源锁定为 Witcher3MapViewer commit `fb674dbff7df087d0a45f9b3938ba6d5317295af`。来源 XML 与地图清单在源码项目 evidence/ 中保留；可重新生成任务数据，执行数据检查，并在云端测试服务中重跑浏览器操作。

浏览器检查按照页面自己的选项数据逐一点击，能发现渲染、引用与条件解锁故障；它不是独立证明全部中文后果文本正确的方式。后果的事实核对依靠每节点攻略链接，两个结局规则另使用预先声明的边界样例检查。

## 边界

- 社区坐标没有逐个在游戏中复测；移动角色位置与版本变化可能影响接取。
- 地标标记只定位相关地点，不代表 NPC 的精确站位。
- 没有坐标的流程任务仍在目录中，不会被随机放在地图上。
- 决策树集中于已核对的关键分支；未收录分支不代表任务没有后果。
- 中文名用于检索，保留英文原名以便对照不同汉化版本。
- 本清单核对两套冻结社区来源，未声称全游戏任务或探索点完整。
- 中文新增标题为本项目译名，不宣称全部是游戏官方译名。
- 遗忘狼的升级装备条目归并图纸任务；Griffin-in-the-Vines 与 Duchaton Crest 的别名有 XML 问号，保留待实机核对说明。
- 来源无法读取的网页链接保留为引用，不冒充本次抓取验证。
- 来源支持关键条件与动作影响，未建立所有任务、人物和存档状态的完整模拟。
- 个人完成标记不等于游戏日志成功；游戏状态和阶段事实需要单独记录。
- 条件未知时不推断可接取；来源任务条件片段不等于全部游戏触发条件。
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
