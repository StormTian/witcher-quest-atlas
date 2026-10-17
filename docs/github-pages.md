# GitHub 仓库与 Pages

源码仓库：https://github.com/StormTian/witcher-quest-atlas

Pages 地址：https://stormtian.github.io/witcher-quest-atlas/

仓库保留完整项目、Git 提交历史和标签，`origin` 指向上述 GitHub 仓库。源码恢复使用标准 `git clone`，发布使用 GitHub Actions。

## 发布

在仓库 Settings → Pages 中将 Source 设为 **GitHub Actions**。推送 `main` 会触发 `.github/workflows/pages.yml`，也可在 Actions 中手动运行。工作流没有定时任务。

发布前，工作流会在 GitHub Actions 的 Ubuntu runner 上启动 `dist/` 的本地 HTTP 预览，安装锁定版本的 Playwright Chromium，并运行数据、页面、进度、目录、地图、剧情提示和资源检查。随后 `scripts/build-report.py` 根据本次检查结果生成 `dist/validation.json`、`dist/validation-report.md` 及逐项证据。打包器只允许这些明确的 CI 检查输出处于未提交状态；源码、冻结输入和运行文件仍须来自工作流触发的精确提交。

`scripts/prepare-github-pages.py` 核对发布报告的运行文件摘要与实际文件一致，并检查被引用的验证结果全部通过；过期或失败的报告会阻止打包。

工作流将完整 `dist/` 复制到临时 `_site/`，加上 `.nojekyll` 和 `version.json`，再上传并发布到 Pages。`_site/` 不加入源码版本管理。`version.json` 包含精确源码提交、运行文件摘要、静态目录摘要、检查记录摘要及 Actions 发布记录。部署后，工作流再次启动 Chromium 访问正式 Pages，核对 `version.json.sourceCommit`、逐个运行资源摘要、桌面与手机视口、任务深链接、默认剧透保护、版本页和页面错误；验证截图与结果作为 Actions artifact 保留。地图的“资料与验证”提供“网站版本与源码”入口。

源码预览没有发布时生成的 `version.json`，版本页面会明确说明预览状态。打包也可以在本地或 CI 环境手动执行：

```sh
python3 scripts/prepare-github-pages.py --repository StormTian/witcher-quest-atlas --output /tmp/witcher-pages-release
```

输出目录必须不存在。正式发布由 GitHub Actions 执行，不需要额外前端构建依赖。

## 切换站点与进度

个人进度保存在当前浏览器和网址下。更换网址或浏览器前，在“进度与备份”导出 JSON，再在目标浏览器选择备份、预览并恢复。公共分享链接只包含地区和对象 ID，个人记录不会上传到仓库或 Pages。
