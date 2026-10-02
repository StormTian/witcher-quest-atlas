# 狩魔手记 · 巫师3任务与抉择地图

中文互动地图，覆盖本体、《石之心》和《血与酒》。按地区、任务类型、资料片、名称、人物及地点查找任务；查看接取说明、前置线索、进度门槛，以及已整理的关键决策。后果默认隐藏，可逐任务展开。

## 使用

网站：https://witcher-quest-atlas.stormberich.chatgpt.site （默认仅拥有者可访问）。

手机底部可切换地图、任务索引和详情。右上角“资料与验证”提供实际检查结果、攻略链接、地图样例和下载。

地图默认显示 227 个快速旅行路标的位置，并显示视野内可容纳的地名。主要城镇优先显示，密集处避让后以细线指回路标。放大可以看清更多附近地名；右侧“地名”按钮可以开关，任务筛选不会隐藏路标。

## 当前覆盖与正确性

- 267 个目录条目：87 主线、180 支线；149 个地图定位。
- 40 个关键任务有已核对分支：45 节点、101 个选项。
- 希里与血与酒结局可按选择组合演算。
- 地图社区坐标、地标近似定位和无独立接取点的流程任务明确区分。
- 未整理的分支明确标为未收录；不表示该任务没有决策或后果。

详见 [验证报告](dist/validation-report.md) 和 [可检查结果](dist/validation.json)。资料核对、网页测试与游戏实机验证是不同层次，本项目没有执行逐任务实机验证。随机遭遇、狩魔委托和寻宝不在目录范围。

## 本地运行与修改

这是无构建依赖的静态网站，不需要安装前端框架。

```sh
python3 -m http.server 8765 --bind 127.0.0.1 --directory dist
```

打开 http://127.0.0.1:8765/ 。浏览器直接打开 HTML 文件可能无法读取 JSON，请使用本地服务。

```sh
python3 scripts/build-data.py
python3 scripts/enrich-data.py
node scripts/validate.cjs
node scripts/browser-validate.cjs
node scripts/validate-landmarks.cjs
python3 scripts/build-report.py
node scripts/validate-assets.cjs
python3 scripts/build-report.py
```

浏览器检查使用 Codex 随附 Playwright 和 macOS 上已安装的 Google Chrome，路径在检查脚本顶部；在其他机器上可替换为自己的 Playwright 与浏览器路径。先启动上述本地服务。`validate-assets.cjs` 检查最终报告、下载与页面资源。不得在检查未执行或失败时生成通过报告。

## 文件职责

- `dist/`：可部署网站、地图切片、任务数据、检查结果。
- `scripts/build-data.py`：从冻结的社区 XML 生成基础目录与坐标。
- `scripts/enrich-data.py`：资料修正、中文摘要、来源和决策规则。
- `dist/logic.js`：两个主干结局的组合规则。
- `evidence/`：冻结输入、地图校准、实际测试结果与验收画面。
- `.openai/hosting.json`：已注册 Sites 身份及静态目录，请保留项目 ID。

资料修改后先检查名称、任务 ID、坐标精度和来源，再重跑相关检查。不要把任务目标点冒充接取点，也不要把社区数据结构检查称为游戏实机正确性证明。

## 来源与版权

地图与基础坐标：Witcher3MapViewer commit `fb674dbff7df087d0a45f9b3938ba6d5317295af`；任务目录与攻略交叉对照见网站报告。Leaflet 1.9.4 使用 BSD-2-Clause。游戏资产 © CD PROJEKT RED。此非官方个人研究工具没有将游戏地图授予新许可。
