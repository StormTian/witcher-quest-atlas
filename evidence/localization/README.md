# 中文路标对照

2026-10-02 保存 https://www.tivaprojects.com/witcher3map/files/locales/{en,zh}/{w,v,s,k,t}.json。
原始中英 JSON 是公开中文游戏地图的本地化资料，保留以便重做同名键关联；`zh-simplified-*.json` 使用 macOS Foundation 的 Traditional-Simplified 变换逐字转简，没有自行音译剩余英文地名。

`scripts/build-places.py` 关联冻结 MapPins.xml 的 227 个 RoadSign 与这些资料。输出保存原名、当前中文显示名、来源键、逐项 URL 和文件 SHA-256。地图坐标及任务数据没有修改。

明确边界：这些资料不是 CD PROJEKT RED 官方简中语言文件。繁体官方版本与简体官方版本可能有不同用词；这里没有逐项实机比对。不要把“中文显示覆盖 227/227”写成“官方简中逐项验证 227/227”。

交叉核对：

- Cackler Bridge：嘻笑者之桥，https://witcher.huijiwiki.com/wiki/嘻笑者之桥。
- Blackbough：大黑树，https://jingyan.baidu.com/article/8065f87f412b93233024987d.html（游戏传送界面的图文实例）。
- Elverum Lighthouse：艾孚鲁灯塔，https://witcher.huijiwiki.com/wiki/艾孚鲁灯塔。TiVa 把此灯塔与 Eldberg 灯塔重复译名，已修正此条。
- Lofoten：罗伏藤，https://www.gamersky.com/handbook/202312/1689273_203.shtml。
- Tesham Mutna：迪沙谬那，https://www.gamersky.com/handbook/201606/761188_23.shtml。

凯尔莫罕有四个来源旧名，通过来源坐标的相对位置和另一个地图的路标对照恢复名称：西侧 The Morhen Eye 对应 Bastion（堡垒），最北 Outpost ruins 对应 Ruined Watchtower（被毁的瞭望塔），南侧 Morhen Mine dam 对应 Iron Mine（铁矿），东侧 The Lake House 对应 Lakeside Hut（湖畔小屋）。映射在生成脚本中明确列出，未将旧英文逐词翻译成新地名。

游戏名称和游戏地图 © CD PROJEKT RED；中文社区地图的贡献者来源保留。没有为游戏资产宣称新的开源许可。
