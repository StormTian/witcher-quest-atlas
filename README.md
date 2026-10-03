# 狩魔手记 · 巫师3任务与抉择地图

中文互动地图，覆盖本体、《石之心》和《血与酒》。按地区、任务类型、资料片、名称、人物及地点查找任务；查看接取说明、前置线索、进度门槛，以及已整理的关键决策。后果默认隐藏，可逐任务展开。

## 使用

网站：https://witcher-quest-atlas.stormberich.chatgpt.site （保持现有公开访问权限）。

手机底部可切换地图、任务索引和详情。右上角“资料与验证”提供实际检查结果、攻略链接、地图样例和下载。

地图默认显示 227 个快速旅行路标的位置，并显示视野内可容纳的地名。主要城镇优先显示，密集处避让后以细线指回路标。放大可以看清更多附近地名；右侧“地名”按钮可以开关，任务筛选不会隐藏路标。

现有 615 个探索点，含原 70 个基础设施点以及商人、工匠、昆特、资源和洞穴入口。右侧“图层”可搜索、全选和分别开关，显示当前地区数量，支持全隐藏并恢复。新增分类默认关闭，密集点可聚合选择。点击探索点查看方位、用途和来源。探索点整理与开放条件的边界保存在 `dist/exploration.json`。

地图路标现在全部显示中文，按照公开游戏中文地图的中英对照核对，并修正“大黑树”“嘻笑者之桥”“孤岩”等先前的手工译名。部分来源为繁体官中，逐字转简；没有逐项对照官方简中语言文件。逐项来源和边界保存在 `dist/places-zh.json`。

缩放按钮与每次滚轮操作只改变 0.25 级，滚轮保持鼠标下的位置。选任务保留当前倍率，换区回来保留原有视野。左下地区概览用亮框显示当前窗口，点击可以重新定位；手机可用双指缩放。较大地图增加原生 4、5 级细节图片，最大仅允许再放大半级。

完成状态和收藏可在任务／探索点详情中记录，任务索引支持“我的收藏”“已完成”和隐藏已完成。进度、筛选、地图视野与决策保存在当前浏览器；每次加载仍隐藏剧透。“进度与备份”可导出个人 JSON，选择备份后先检查并预览，再恢复；不提供账号云同步。

“分享定位”只带地区与对象 ID，可直达任务或探索点，并支持浏览器前进／后退。公共任务数据下载和个人进度备份为不同入口。

## 当前覆盖与正确性

- 428 个目录条目：保留 87 主线、180 支线；新增 35 委托、29 套装搜集、57 其他寻宝、40 遭遇。304 个定位为发现／接取线索或关联地标。
- 615 个探索点、13 类，使用独立稳定 ID；617 条候选合并重复 1 条、暂缓独立场景 1 条。16 条共用或空白源键有显式 ID 映射。
- 40 个关键任务有已核对分支：45 节点、101 个选项。
- 希里与血与酒结局可按选择组合演算。
- 地图社区坐标、地标近似定位和无独立接取点的流程任务明确区分。
- 未整理的分支明确标为未收录；不表示该任务没有决策或后果。

详见 [验证报告](dist/validation-report.md) 和 [可检查结果](dist/validation.json)。资料核对、网页测试与游戏实机验证是不同层次，本项目没有执行逐任务实机验证。第三轮按冻结 XML 和参考目录逐条归并，不把装备组件、阶段或资源点当作独立任务。详见 evidence/catalog-review/reconciliation.json。

## 云端维护与验证

这是无构建依赖的静态网站，不需要安装前端框架。

```sh
python3 -m http.server 8765 --bind 127.0.0.1 --directory dist
```

打开 http://127.0.0.1:8765/ 。浏览器直接打开 HTML 文件可能无法读取 JSON，请使用云端测试服务。

```sh
python3 scripts/build-data.py
python3 scripts/enrich-data.py
python3 scripts/expand-catalog.py
python3 scripts/build-places.py
python3 scripts/build-exploration.py
node scripts/validate.cjs
python3 scripts/validate-exploration.py
python3 scripts/validate-catalog.py
node scripts/browser-validate.cjs
node scripts/validate-landmarks.cjs
node scripts/validate-navigation.cjs
node scripts/validate-exploration.cjs
node scripts/validate-progress.cjs
node scripts/validate-catalog.cjs
python3 scripts/build-report.py
node scripts/validate-assets.cjs
python3 scripts/build-report.py
```

后续修改、检查、提交和发布只在云端执行，不依赖用户电脑在线，不使用远程 Mac 或 Local computer access。此会话是云端接续入口。用 Sites 官方 Site workflow 恢复完整源码到云端空目录，复用 `.openai/hosting.json` 中项目 ID；短期凭证只经隐藏标准输入传递，禁止写入文件或日志。

浏览器脚本自动使用云端 Node 的 Playwright 或 `CODEX_PRIMARY_RUNTIME_NODE_MODULES` 中的 Playwright，默认使用其 Chromium。可通过 `PLAYWRIGHT_MODULE_PATH`、`CHROMIUM_EXECUTABLE_PATH`、`ATLAS_BASE_URL` 配置。先在云端启动上述静态测试服务，回环地址仅指云端容器。缺少工具时记录阻碍，不回落到用户电脑。`validate-assets.cjs` 检查最终报告、下载与页面资源。不得在检查未执行或失败时生成通过报告。

中文地名生成使用 `evidence/localization/tiva/` 中冻结的中英对照和繁转简副本，不依赖在线接口。新增细节图片可用 Pillow 重新导出：`python3 scripts/export-detail-tiles.py --source /path/to/Witcher3MapViewer/Witcher3MapViewer/Maps`。来源必须为上述固定版本，脚本核对 MBTiles 文件指纹后才导出。

## 文件职责

- `dist/`：可部署网站、地图切片、任务数据、检查结果。
- `scripts/build-data.py`：从冻结的社区 XML 生成基础目录与坐标。
- `scripts/build-exploration.py`：逐条整理冻结探索点，保留稳定来源键、重复／暂缓账目与位置精度。
- `dist/exploration.js`、`dist/exploration.css`：探索图层、分类控制与样式。
- `scripts/validate-exploration.py`、`scripts/validate-exploration.cjs`：独立来源清单、坐标样例和实际桌面／手机图层操作。
- `docs/map-iteration-plan.md`：BWIKI 对照盘点、分轮范围与验收门槛。
- `scripts/enrich-data.py`：资料修正、中文摘要、来源和决策规则。
- `dist/logic.js`：两个主干结局的组合规则。
- `evidence/`：冻结输入、地图校准、实际测试结果与验收画面。
- `.openai/hosting.json`：已注册 Sites 身份及静态目录，请保留项目 ID。

资料修改后先检查名称、任务 ID、坐标精度和来源，再重跑相关检查。不要把任务目标点冒充接取点，也不要把社区数据结构检查称为游戏实机正确性证明。

## 来源与版权

地图与基础坐标：Witcher3MapViewer commit `fb674dbff7df087d0a45f9b3938ba6d5317295af`；任务目录与攻略交叉对照见网站报告。Leaflet 1.9.4 使用 BSD-2-Clause。游戏资产 © CD PROJEKT RED。此非官方个人研究工具没有将游戏地图授予新许可。

原始云端恢复基线：`341b240bbb598db2f5f37e4c548953b046178b4f`，5,822 个版本管理文件。历史本地验收已保存在 `evidence/history/local-2026-10-02/`；本次及后续云端结果必须明确执行环境与时间，不能把历史本地 66 项通过写为本次云端结果。

历史迁移曾因 Chromium 缺失而未完成浏览器验收，阻碍记录保留在 `evidence/cloud-migration.json`、`evidence/cloud-logs/`。2026-10-03 已在本云环境使用 Chromium 151 完成基线与第一轮浏览器检查，第二轮 93/93，第三轮 113/113 项通过，当前结果见 `dist/validation.json`；历史阻碍不再代表当前状态。地图原始 MBTiles 数据库不在版本管理源码中；现有全部图块已恢复，新导出图块须另行取得指定版本的原始数据库。
