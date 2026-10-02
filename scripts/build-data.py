import xml.etree.ElementTree as ET,json,math,re,pathlib,hashlib,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1]
REF=ROOT/'evidence/upstream'
x=ET.parse(REF/'Witcher3MapViewer/Quests.xml'); p=ET.parse(REF/'Witcher3MapViewer/MapPins.xml')
settings={'WO':(.000038,60,19.2),'NO':(.000114,968.6,706.4),'SK':(.000164,209.9,305.7),'KM':(.0000568,10.1,244.2),'TO':(.0000897,-153.3,-717.7)}
region={'WO':'white-orchard','VE':'velen','NO':'velen','SK':'skellige','KM':'kaer-morhen','TO':'toussaint','VI':'vizima'}
def transform(world,x,y):
 world='NO' if world=='VE' else world
 s,xi,yi=settings[world];X=(float(x)-xi)/s;Y=(float(y)-yi)/s
 return [math.degrees(2*math.atan(math.exp(Y/6378137))-math.pi/2),math.degrees(X/6378137)]
pins=[]
for w in p.findall('world'):
 for n in w.findall('mappin'):
  a=n.find('position');
  if a is not None:
   pins.append({'world':w.get('code'),'name':n.findtext('name',''),'type':n.get('type'),'xy':[float(a.get('x')),float(a.get('y'))]})
def anchor(world,name):
 a=next((p for p in pins if (p['world']==world or set([p['world'],world])=={'VE','NO'}) and p['name'].lower()==name.lower()),None)
 return a
cn='''2|凯尔莫罕
3|丁香与醋栗
44|白果园的野兽
39|白果园事件
19|失踪的兄弟
20|干净的平底锅
36|珍贵的货物
37|扭曲的纵火犯
42|临终之前
40|觐见皇帝
12|昆特牌：威伦大玩家
22|星空下的真相
45|火葬堆
49|危险货物
68|狗的一生
82|里尔顿家的衰败
83|往日的幽灵
84|愚人金
88|暴民
89|贪婪的神
93|狂野之心
119|冒牌狩魔猎人
118|信仰守护者
120|爱情的残酷陷阱
121|烈火下的亡魂
130|愤怒之拳：威伦
139|血缘关系
268|猫与狼共舞
267|拿走你想要的
60|尼弗迦德的线人
65|狩猎女巫
73|伸手不见五指
78|魔法灯
79|凯拉·梅兹的邀约
80|老鼠之塔
81|拔刀相助
99|以知识进步为名
75|血腥男爵
61|希里：狼之王
69|希里的房间
74|家家有本难念的经
63|公主落难
64|希里：赛马
62|希里：天机泄漏
76|林中夫人
67|呢喃山丘
66|希里：逃离泥沼
91|祖灵前夜
105|最后的仪式
107|重回驼背泥沼
90|禁止通行
106|假证件
104|苦涩的收获
206|前往史凯利杰
41|矮人文件的困境
13|昆特牌：酒馆老板
21|空空的鸡舍
24|老朋友的讯息
77|嘿，要看看我的东西吗
97|尼弗迦德的隐藏讯息
98|诺维格瑞的热情好客
103|乳酪与黑暗
122|粗暴的街区
129|一谷仓的麻烦
138|受惊的马
142|码头散步
157|志愿者
161|埋葬的书籍
162|仓库之灾
198|小红帽
252|愤怒之拳：诺维格瑞
263|宝剑与饺子
310|杳无音信
311|税务官来了
312|注魔：启动资金
431|注魔：品质有价
14|昆特牌：大城玩家
324|使节与酒差
117|诺维格瑞之火
87|诺维格瑞的白日梦
92|鬼屋
125|破碎之花
143|剑术训练
147|危险游戏
136|打倒二世
109|诺维格瑞的黑帮
101|希里：拜访二世
137|卢文伯爵的宝藏
145|生死交关
131|诺维格瑞，封闭的城市 I
132|诺维格瑞，封闭的城市 II
186|致命阴谋
148|以眼还眼
127|戏剧是关键
156|诗人落难
126|希里：狂奔
180|贵族雕像
179|士兵雕像
185|歌舞厅
182|逃出生天
208|肉体之罪
108|盗贼的仁义
102|拉多维德的恩惠
146|瑞达尼亚的头号要犯
181|滚出去
308|恶魔的第一次接触
316|鲜红战场上的蔷薇
315|死者的派对
317|午夜之光
320|芝麻开门
321|芝麻开门：狩魔猎人的调味料
322|芝麻开门：入室盗窃
323|芝麻开门：保险箱高手
325|狂热收藏家
332|婚姻回忆
361|种什么因，得什么果
277|大赌局
16|昆特牌：史凯利杰牌风
23|勇敢的傻瓜死得早
133|人口贩卖
141|循线追查
140|神圣的号角
160|黑珍珠
158|来自遥远的国度
159|自由精神
177|诅咒之角
178|荣誉的代价
193|家传宝剑
194|吟游诗人的情人
195|名誉与荣耀
196|武装突袭
207|战士之路
184|异乡人
183|梦之洞窟
197|未偿还的债
218|罪与罚
233|钢铁处女
240|艰难时刻
258|拾取者
259|废弃的伐木场
260|休克疗法
262|高等炼金术实习
269|被打扰的安宁
270|少女被掳
275|格罗斯巴特兄弟的悲惨故事
303|愤怒之拳：史凯利杰
128|竞技场大师
176|愤怒之拳：冠军中的冠军
304|凭空出现的塔
205|国王已死，浩气长存
212|往昔的回声
192|失踪人口
175|无名之人
174|暴风雨前的平静
200|最后的愿望
199|披着狼皮
213|乌德维克之王
256|护甲大师
214|附身
219|国王的赌局
220|加冕典礼
236|乌鸦的盛宴
15|昆特牌：老友记
17|昆特牌：与塔勒对决
251|堡垒
276|怪物杀手
280|贝连迦尔的剑
281|温室效应
302|狩魔猎人的熔炉
229|丑陋的婴儿
231|最后的试炼
228|引诱叉尾龙
4|扰动
232|没有比家更好的地方
230|瓦·费尔，伊莲
245|并肩作战：尼弗迦德
246|并肩作战：史凯利杰
247|并肩作战：威伦
248|并肩作战：诺维格瑞
249|迷雾之岛
257|凯尔莫罕之战
235|战场上的鲜血
273|光头山
144|最后的善举
6|最后的准备
274|穿越时空
288|偿还
287|显而易见
289|胜利大逃亡
301|为祖国
25|三人探戈
285|战斗准备
283|薇歌之歌
306|长者之血的子嗣
284|太阳石
286|史凯裘的坟墓
296|如履薄冰
297|泰德·戴尔瑞，终结时代
298|结束与开始
10|忠诚的朋友
333|陶森特的野兽
336|血流成河
366|愚人之笼
387|孩童的玩具，成年人的劳苦
388|葡萄酒是神圣的
392|来自辛特拉的男人
403|攻下城堡
405|长牙之夜
404|血色简单
406|看不见的世界
407|童话世界
415|泰沙姆穆那
416|盛典
417|无论何处都是家
418|麻布是新的潮流
419|牢狱之灾
408|鸭鸭鹅
389|饥饿游戏
367|磨坊里的故事
1|家园装修
334|面对改变
335|骑士的恋爱故事
396|理发与狩魔猎人
337|愤怒之拳：陶森特
371|怒狼
338|至死不渝
339|纸追钱
18|昆特牌：史凯利杰风云
362|昆特牌：翻转再翻转
340|天哪，伟大的石像之球
345|父亲知道最糟
374|大脚板的补缺
346|大脚板：第一组
347|大脚板：第二组
348|大脚板：第三组
349|大脚板：第四组
350|大脚板：第五组
351|酒商委托：里维卡姆仓库
352|葡萄酒大战：贝尔迦德
353|葡萄酒大战：科罗纳塔
354|葡萄酒大战：佛蒙提诺
390|葡萄酒大战：机械中的神
378|葡萄酒大战：联合
369|受雇骑士
370|酒商委托：敦·泰恩山坡
377|酒商委托：喋喋洞窟
393|酒商委托：清理难以触及的地方
394|酒商委托：葡萄藤中的狮鹫
372|骑士的故事
373|极限角色扮演
375|先知的话语刻在石棺上
376|大师中的大师
395|狩魔猎人的老年肖像
401|陶森特的野生王国
424|唯有一人'''
cn={str(a):b for a,b in (line.split('|',1) for line in cn.splitlines())}
loccn={'Woesong bridge':'哀歌桥','Nilfgaardian Garrison':'尼弗迦德驻军','White Orchard':'白果园','Blackbough':'Blackbough（黑树村）','Crow\'s Perch':'乌鸦窝','Midcopse':'米德考普斯','Fyke Isle':'费克岛','Ancient Oak':'古老橡树','Downwarren':'下瓦伦','Devil\'s Pit':'恶魔之坑','Inn at the Crossroads':'十字路口旅店','Seven Cats Inn':'七只猫旅馆','Kaer Trolde Harbor':'凯尔卓港','Bridge to Kaer Trolde':'凯尔卓城堡桥','Larvik':'拉尔维克','Lofoten':'罗弗敦','Gedyneith':'盖迪尼斯','Kaer Morhen':'凯尔莫罕','Corvo Bianco Vineyard':'白鸦葡萄园','Tesham Mutna Ruins':'泰沙姆穆那遗迹','Plegmund\'s Bridge':'普雷格蒙德桥','Stonecutters\' Settlement':'采石场聚落','Gran\'place':'大广场','Tourney Grounds':'比武场','Garin Estate':'加林庄园','Oxenfurt Harbor':'奥森弗特港','Oxenfurt Gate':'奥森弗特城门','Novigrad Gate':'诺维格瑞城门'}
# These are correction facts, not a claim that all community data is game-tested.
exclude={'363','452','453','454','455','456','447','448','299','300','368'}
namepatch={'297':'Tedd Deireadh, The Final Age','83':'Ghosts of the Past','361':'Whatsoever a Man Soweth...','417':'Be It Ever So Humble...','298':'Something Ends, Something Begins','321':'Open Sesame: Witcher Seasonings','322':'Open Sesame: Breaking and Entering','323':'Open Sesame: The Safecracker','352':'Wine Wars: Belgaard','394':"Vintner's Contract: Cleaning Those Hard-to-Reach Places?"}
namepatch['394']="Vintner's Contract: Griffin-in-the-Vines"
for i,g in enumerate(['First','Second','Third','Fourth','Fifth'],346):namepatch[str(i)]='Big Feet to Fill: The '+g+' Group'
worldpatch={'2':'KM','40':'VI','229':'VE','245':'VI','248':'NO','274':'NO','289':'NO','285':'NO','324':'VE'}
hos={'308','315','320','321','322','323','332','361','310','311','312','431','316','317','325','309'}
cn.update({'35':'值得信任','8':'赛马：乌鸦窝','9':'伊拉斯谟·威吉布德纪念德比','309':'赛马：快如西风','420':'英雄追逐：费隆德','421':'英雄追逐：费尔斯达','422':'英雄追逐：凯尔卓','423':'英雄追逐：为了女神的荣耀'})
auto_links={e.findtext('GUID'):e for e in x.findall('.//quest') if e.findtext('GUID')}
obj_links={e.findtext('GUID'):e.findtext('name') for e in x.findall('.//objective') if e.findtext('GUID')}
quests=[]
for e in x.findall('.//quest'):
 id=e.get('id');typ=e.get('type')
 if id in exclude or (typ not in ['main','side','dlcmain','endgame','race'] and id!='35'):continue
 w=worldpatch.get(id,e.get('world'));name=namepatch.get(id,e.findtext('name'))
 typ='main' if typ in ['main','dlcmain','endgame'] else 'side'
 if id=='109':typ='side'
 if id in ['144','25']:typ='main'
 xy=e.find('discoverprompt/XY');info=e.findtext('discoverprompt/info','')
 q={'id':'q'+id,'name':name,'title':cn.get(id,name),'type':typ,'region':region[w],'expansion':'hos' if id in hos else ('baw' if w=='TO' or id=='324' else 'base'),'level':int(e.get('level','0')) or None,'trigger':'','point':None,'location':'','precision':'flow','predecessors':[],'requirements':[],'decisions':[],'sources':[{'label':'社区任务数据','url':'https://github.com/reubengann/Witcher3MapViewer/blob/'+'fb674dbff7df087d0a45f9b3938ba6d5317295af'+'/Witcher3MapViewer/Quests.xml'},{'label':'任务攻略（英文）','url':'https://witcher.fandom.com/wiki/'+name.replace(' ','_')}],'reviewed':False}
 if xy is not None:
  pw=xy.get('world');gx,gy=float(xy.get('X')),float(xy.get('Y'))
  q['point']={'world':pw,'xy':[gx,gy],'latlng':transform(pw,gx,gy)};q['region']=region[pw];q['precision']='community'
  near=sorted([a for a in pins if a['type']=='RoadSign' and region.get(a['world'])==region[pw]],key=lambda a:(a['xy'][0]-gx)**2+(a['xy'][1]-gy)**2)
  if near:q['location']='接取点附近：'+loccn.get(near[0]['name'],near[0]['name'])
 if 'Notice board' in info:q['trigger']='阅读当地告示板上的相关告示。标记对应社区数据记录的接取告示板。'
 elif '! sign' in info or '! symbol' in info:q['trigger']='到标记处寻找头顶带感叹号的角色，靠近或对话接取；部分任务还需推进前置流程。'
 elif 'Automatically' in info or 'automatically' in info or 'Given' in info or not info:q['trigger']='由前序任务或剧情对话开启；先查看下方前置线索。'
 elif 'Talk' in info:q['trigger']='到标记附近与相关角色交谈接取。'
 else:q['trigger']='满足相关剧情条件后，在标记附近探索或交谈。具体条件请对照任务攻略。'
 for group,mode in [('available','any'),('oneofabsolutelyrequired','any-required'),('strict','all')]:
  for g in e.findall(group+'/GUID'):
   v=g.text;state=g.get('state','active-or-complete');node=auto_links.get(v)
   if node is not None and node.get('id') not in exclude:
    pid='q'+node.get('id');q['requirements'].append({'questId':pid,'state':state,'mode':mode})
    if state=='JS_Success' and pid!=q['id'] and pid not in q['predecessors']:q['predecessors'].append(pid)
 if q['point'] is None:q['location']='剧情流程；没有独立接取点'
 quests.append(q)
# Supplement missing registered quests and 4.0 addition; catalog comparison is stored separately.
extras=[('eternal',"In the Eternal Fire's Shadow",'永恒之火的阴影','velen','base',15),('ciri',"In Ciri's Footsteps",'追寻希里的踪迹','velen','base',None),('collect',"Gwent: Collect 'Em All",'昆特牌：收集所有卡牌','white-orchard','base',None),('mysterious','The Mysterious Passenger','神秘乘客','skellige','base',None),('derby','The Great Erasmus Vegelbud Memorial Derby','伊拉斯谟·威吉布德纪念德比','velen','base',None),('swift','Races: Swift as the Western Winds','赛马：快如西风','velen','hos',32)]
for id,name,title,reg,exp,level in extras:
 if id in ['derby','swift']:continue
 quests.append({'id':id,'name':name,'title':title,'type':'main' if id=='ciri' else 'side','region':reg,'expansion':exp,'level':level,'trigger':'参照任务攻略确认接取流程。','location':'尚未校准接取坐标','precision':'unmapped','point':None,'predecessors':[],'requirements':[],'decisions':[],'reviewed':False,'sources':[{'label':'任务攻略（英文）','url':'https://witcher.fandom.com/wiki/'+name.replace(' ','_')} ]})
by={q['id']:q for q in quests}
# Landmark pins are explicitly approximate, never passed off as quest-giver coordinates.
def patch(id,trigger,landmark=None,world=None,loc=None,pre=None,cutoff=None,url=None):
 q=by[id];q['trigger']=trigger
 if loc:q['location']=loc
 if pre is not None:q['predecessors']=pre
 if cutoff:q['cutoff']=cutoff
 if url:q['sources'].append({'label':'地点／前置核对','url':url})
 if landmark:
  a=anchor(world,landmark)
  if a:
   q['point']={'world':world,'xy':a['xy'],'latlng':transform(world,*a['xy'])};q['precision']='landmark';q['region']=region[world];q['location']=loc or (loccn.get(landmark,landmark)+'附近（地标定位）')
patch('q44','到尼弗迦德驻军与队长彼得·萨尔·格温勒夫交谈；这是寻找叶奈法的主线环节。','Nilfgaardian Garrison','WO',pre=['q3'])
patch('q3','凯尔莫罕梦境结束后，随维瑟米尔进入白果园并寻找叶奈法。',pre=['q2'])
patch('q39','完成狮鹫委托后，回白果园酒馆与维瑟米尔交谈。',pre=['q44'])
patch('q40','离开白果园后，由剧情自动前往维吉玛王宫。',pre=['q39'])
patch('q60','在威伦十字路口旅店寻找汉崔克的情报。','Inn at the Crossroads','VE',pre=['q40'])
patch('q65','前往米德考普斯打听女巫，也可直接寻找凯拉的住处。','Midcopse','VE',pre=['q60'])
patch('q75','到乌鸦窝与男爵会面。','Crow\'s Perch','VE',pre=['q60'])
patch('q74','与男爵交谈后，调查乌鸦窝中安娜和塔玛拉的房间。','Crow\'s Perch','VE',pre=['q75'])
patch('q76','凯拉的线索指向驼背泥沼；沿糖果小径前往孤儿所在的村落。',pre=['q73'])
patch('q67','通常在“林中夫人”中受下瓦伦长老委托前往古老橡树；也能提前探索山丘。','Ancient Oak','VE',pre=['q76'])
patch('q80','接受凯拉的请求后前往费克岛；地图标记是岛上地标，不是一个新的任务发布者。','Fyke Isle','VE',pre=['q79'])
patch('q99','完成“拔刀相助”后开启，到费克岛高塔找凯拉。','Fyke Isle','VE',pre=['q81'],cutoff='进入“迷雾之岛”前完成')
patch('q107','完成男爵的相关调查后，答应陪他返回驼背泥沼。','Crow\'s Perch','VE',pre=['q74'])
patch('q117','进入诺维格瑞后，在教主广场一带寻找特莉丝的线索。',pre=['q40'])
patch('q141','诺维格瑞告示板上的“比特区的怪物”委托会引向兰伯特。',cutoff='推进至七只猫旅馆与兰伯特交谈，将使“人口贩卖”不可接取')
patch('q182','完成“生死交关”后，回特莉丝的住处，处理法师撤离。',pre=['q145'],cutoff='进入“迷雾之岛”前完成')
patch('q208','完成“歌舞厅”后由剧情开启，在医院开始调查。',pre=['q185'])
patch('q200','完成希里在史凯利杰的线索后，到拉尔维克的战士大厅与叶奈法会面。','Larvik','SK',pre=['q174'],cutoff='在“丑陋的婴儿”中从乌鸦窝领走乌马前完成',url='https://witcher.fandom.com/wiki/The_Last_Wish_(quest)')
patch('q219','完成“附身”和“乌德维克之王”后返回凯尔卓，参加克拉奇的宴会。','Bridge to Kaer Trolde','SK',pre=['q214','q213'],cutoff='进入“迷雾之岛”前完成')
patch('q229','调查三个地区的希里线索后，到乌鸦窝领走乌马。','Crow\'s Perch','VE',pre=['q74','q174','q156'])
patch('q249','完成乌马的诅咒调查后，从史凯利杰乘船跟随萤火虫进入迷雾。',pre=['q230'],cutoff='进入时出现不可逆进度警告；先完成相关人物支线')
patch('q235','凯尔莫罕之战结束后自动开启。',pre=['q257'])
patch('q6','光头山剧情后回诺维格瑞，准备与狂猎的最终对抗。',pre=['q273'])
patch('q287','“最后的准备”期间，在变色龙酒馆与特莉丝交谈。',pre=['q6'])
patch('q301','先完成“致命阴谋”“以眼还眼”“瑞达尼亚的头号要犯”，再在“显而易见”结尾对迪科斯彻采用外交方式。',pre=['q186','q148','q146','q287'],cutoff='在“如履薄冰”前完成')
patch('q298','完成“泰德·戴尔瑞，终结时代”后自动开始；地点取决于已达成的结局。',pre=['q297'])
patch('q308','安装《石之心》后，到七只猫旅馆告示板接取怪物委托。','Seven Cats Inn','NO',loc='七只猫旅馆告示板（地标定位）')
patch('q361','完成“婚姻回忆”后到奥森弗特炼金旅馆；最终选择前可去找夏妮与教授。',pre=['q332'])
patch('q324','安装《血与酒》，且完成“诗人落难”后，阅读陶森特骑士的告示，再前往威伦采石场聚落。','Stonecutters\' Settlement','VE',pre=['q156'])
patch('q333','答应陪陶森特骑士南行后，在公国入口由剧情继续。',pre=['q324'])
patch('q366','完成“血流成河”后与雷吉斯会合，随后调查特拉斯塔马拉庄园。',pre=['q336'])
patch('q405','完成“攻下城堡”后，长牙之夜开始。',pre=['q403'])
patch('q407','在“长牙之夜”选择寻找席安娜，再通过儿童房中的书进入童话世界。',pre=['q405'])
patch('q406','选择暗影长者路线；“血色简单”之后可反悔，真正进入长者洞穴才锁定路线。',pre=['q404'])
patch('q415','根据“长牙之夜”的路线与前序选择，在泰沙姆穆那与狄拉夫见面。','Tesham Mutna Ruins','TO',pre=['q407','q406'])
patch('q416','席安娜在泰沙姆穆那存活后继续这一收尾主线。',pre=['q415'])
patch('q417','《血与酒》结局结束后，返回白鸦葡萄园。','Corvo Bianco Vineyard','TO')
patch('eternal','4.0 次世代版新增：在恶魔之坑入口与永恒之火牧师交谈。','Devil\'s Pit','VE',url='https://witcher.fandom.com/wiki/In_the_Eternal_Fire%27s_Shadow')
patch('collect','在白果园酒馆首次与学者打昆特牌时开启；这是跨地区收集任务，没有单一接取地点。')
patch('ciri','完成觐见后开启的调查总任务，包含威伦、诺维格瑞和史凯利杰三条线索。',pre=['q40'])
patch('q309','在《石之心》的上磨坊寻找欧菲尔商人，参加赛马。')
# Fix task titles which collide between base game and expansion.
by['q232']['title']='没有比家更好的地方（本体）';by['q1']['title']='没有比家更好的地方（家园装修）'
for q in quests:
 q['predecessors']=[i for i in q['predecessors'] if i in by and i!=q['id']]
 q['requirements']=[i for i in q['requirements'] if i['questId'] in by and i['questId']!=q['id']]
# Map-backed context labels for nearby landmarks.
landmarks=[{'name':loccn.get(a['name'],a['name']),'region':region[a['world']],'latlng':transform(a['world'],*a['xy'])} for a in pins if a['type']=='RoadSign']
meta={'date':'2026-10-02','catalogVersion':'1.0','scope':'本体 + 石之心 + 血与酒；主线、支线与登记为支线的昆特／竞赛任务。非完整随机遭遇百科。','sources':[{'label':'地图与接取坐标：Witcher3MapViewer','url':'https://github.com/reubengann/Witcher3MapViewer'},{'label':'任务目录交叉对照：Gercius','url':'https://github.com/Gercius/witcher3-quest-manager'},{'label':'本体主线目录','url':'https://witcher.fandom.com/wiki/The_Witcher_3_main_quests'},{'label':'本体支线目录','url':'https://witcher.fandom.com/wiki/The_Witcher_3_secondary_quests'},{'label':'石之心目录','url':'https://witcher.fandom.com/wiki/Hearts_of_Stone_quests'},{'label':'血与酒目录','url':'https://witcher.fandom.com/wiki/Blood_and_Wine_quests'}],'corrections':['移除 5 条购书步骤、2 条主线目标和 1 条误归类寻宝任务。','合并本体结局的 3 个条目；合并贝尔迦德任务的两个阶段。','纠正凯尔莫罕教学、觐见皇帝、丑陋的婴儿、使节与酒差、并肩作战与数条最终章任务的起始地区。','纠正诺维格瑞黑帮、三人探戈与最后的善举的分类；补充 4.0 新任务、总任务与竞赛条目。'],'limitations':['社区坐标没有逐个在游戏中复测；移动角色位置与版本变化可能影响接取。','地标标记只定位相关地点，不代表 NPC 的精确站位。','没有坐标的流程任务仍在目录中，不会被随机放在地图上。','决策树集中于已核对的关键分支；未收录分支不代表任务没有后果。','中文名用于检索，保留英文原名以便对照不同汉化版本。']}
(ROOT/'dist/data.json').write_text(json.dumps({'meta':meta,'quests':quests,'landmarks':landmarks},ensure_ascii=False,indent=2))
print(json.dumps({'quests':len(quests),'main':sum(q['type']=='main' for q in quests),'side':sum(q['type']=='side' for q in quests),'mapped':sum(q['point'] is not None for q in quests)},ensure_ascii=False))
