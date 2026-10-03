# GitHub 仓库与 Pages

源码仓库：https://github.com/StormTian/witcher-quest-atlas

Pages 地址：https://stormtian.github.io/witcher-quest-atlas/

仓库保留完整项目与 Git 历史。`origin` 仍指向原 Sites 源码仓库，`github` 指向 GitHub；这两个远端分别维护。`.openai/hosting.json` 保留原 Sites 身份。

## 发布

在仓库 Settings → Pages 中将 Source 设为 **GitHub Actions**。推送 `main` 会触发 `.github/workflows/pages.yml`，也可在 Actions 中手动运行。工作流没有定时任务。

发布使用已核对的 `dist/`，不在发布过程中重新生成任务数据。`scripts/prepare-github-pages.py` 要求源码已提交，核对公开报告的运行文件摘要与实际文件一致，并检查各项公开验证结果通过；过期或失败的报告会阻止打包。

工作流将完整 `dist/` 复制到临时 `_site/`，加上 `.nojekyll` 和 `version.json`，再上传并发布到 Pages。`_site/` 不加入源码版本管理。`version.json` 包含精确源码提交、运行文件摘要、静态目录摘要、检查记录摘要及 Actions 发布记录。地图的“资料与验证”提供“网站版本与源码”入口。

源码预览没有发布时生成的 `version.json`，版本页面会明确说明预览状态。打包可以在云端手动执行：

```sh
python3 scripts/prepare-github-pages.py --repository StormTian/witcher-quest-atlas --output /tmp/witcher-pages-release
```

输出目录必须不存在。发布不需要用户电脑或额外前端构建依赖。

## 切换站点与进度

Sites 与 GitHub Pages 使用不同网址，浏览器的个人进度分别保存。切换前在原站“进度与备份”导出 JSON，再在新站选择备份、预览并恢复。公共分享链接只包含地区和对象 ID，个人记录不会上传到仓库或 Pages。
