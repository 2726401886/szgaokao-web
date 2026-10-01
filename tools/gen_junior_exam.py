# -*- coding: utf-8 -*-
"""生成初中英语题库 data/junior_exam.json。
题型以中考笔试真题格式为原型（原创练习，非真实真题）：
  choice  单项选择
  cloze   完形填空（带选项）
  reading 阅读理解（篇章+选择题）
  vocab   词汇运用（form: 适当形式填空 / blank: 首字母或句意填词）
  grammar 语法填空（篇章+带选项空）
  task    任务型阅读（篇章+问答/填表）
  writing 书面表达
每题字段：id, grade(7/8/9), type, book(7a/7b/8a/8b/9), unit(可选), topic, difficulty(1-3)
以及题型专属内容。组卷引擎在前端/后端按 grade/type/book/unit/difficulty 过滤并切片。
"""
import json, os

OUT = os.path.join(os.path.dirname(__file__), '..', 'data', 'junior_exam.json')

def mk(qid, grade, typ, book, topic, diff, unit='', **body):
    d = {"id": qid, "grade": grade, "type": typ, "book": book,
         "unit": unit, "topic": topic, "difficulty": diff}
    d.update(body)
    return d

def choice(grade, book, unit, topic, diff, stem, options, answer, analysis):
    assert 0 <= answer < len(options), f"answer越界 {qid}"
    return mk('', grade, 'choice', book, topic, diff, unit=unit,
              stem=stem, options=options, answer=answer, analysis=analysis)

BANK = []

# ========================= 七年级（grade 7） =========================
# —— 单项选择 ——
BANK += [
choice(7,'7a','7a01','基础语法',1,
  "— ___ is that boy? — He is my cousin.", ["What","Who","Where","How"], 1,
  "问人用 Who；问物用 What，问地点用 Where，问方式用 How。"),
choice(7,'7a','7a02','代词',1,
  "This is ___ apple. ___ apple is red.", ["a; The","an; The","the; An","an; A"], 1,
  "apple 以元音音素开头，用 an；第二次提到用 the 特指。"),
choice(7,'7a','7a03','名词复数',1,
  "There are two ___ on the desk.", ["box","boxs","boxes","boxies"], 2,
  "以 x 结尾的名词复数加 -es，box→boxes。"),
choice(7,'7a','7a04','be动词',1,
  "I ___ a student. My friends ___ teachers.", ["am; are","is; am","am; is","are; am"], 0,
  "I 后用 am；复数 friends 后用 are。"),
choice(7,'7a','7a05','情态动词',2,
  "You ___ smoke here. It's not allowed.", ["must","can","mustn't","need"], 2,
  "禁止做某事用 mustn't（千万别/不许）。"),
choice(7,'7a','7a06','冠词',1,
  "She plays ___ piano very well.", ["a","an","the","/"], 2,
  "乐器前加 the：play the piano。"),
choice(7,'7a','7a07','介词',2,
  "The book is ___ the desk ___ the floor.", ["on; on","in; under","on; under","under; on"], 2,
  "书在桌上用 on，地板用 under 表示在桌子下方的地板上。"),
choice(7,'7b','7b01','时态-一般现在',2,
  "Tom often ___ to school by bike.", ["go","goes","going","went"], 1,
  "主语第三人称单数，一般现在时动词加 -es：go→goes。"),
choice(7,'7b','7b02','疑问词',2,
  "— ___ do you go to bed? — At nine o'clock.", ["What","When","Why","Where"], 1,
  "问时间用 When；答语是时间点。"),
choice(7,'7b','7b03','物主代词',1,
  "This isn't my pen. It's ___.", ["your","yours","you","your's"], 1,
  "名物代 yours = your pen，省略名词。"),
]
# —— 完形填空 7a ——
BANK.append(mk('c7a01',7,'cloze','7a','记叙-校园',2,unit='7a06',
  title="My First Day at School",
  passage="It was my first day at a new school. I was very (1)___. A girl came to me and said, 'Hi! I am Lily. (2)___ name is Lily.' She (3)___ me to the classroom. The teacher was (4)___ and kind. We had (5)___ classes in the morning. At noon we ate (6)___ in the dining hall. I made (7)___ new friends. After school I went (8)___ happily.",
  blanks=[
    {"options":["happy","nervous","angry","tired"],"answer":1,"analysis":"第一次去新学校感到紧张最合理。"},
    {"options":["Her","His","My","Your"],"answer":0,"analysis":"Lily 是女生，用 Her。"},
    {"options":["took","takes","taking","take"],"answer":0,"analysis":"过去时 took。"},
    {"options":["strict","tall","nice","young"],"answer":2,"analysis":"and kind 并列，选 nice 友善。"},
    {"options":["little","few","some","much"],"answer":2,"analysis":"几节课用 some classes。"},
    {"options":["breakfast","lunch","dinner","supper"],"answer":1,"analysis":"中午吃 lunch。"},
    {"options":["any","some","much","a"],"answer":1,"analysis":"肯定句用 some 修饰可数复数 friends。"},
    {"options":["home","to home","school","to school"],"answer":0,"analysis":"go home 回家，home 前无 to。"},
  ]))
# —— 阅读理解 7a ——
BANK.append(mk('r7a01',7,'reading','7a','说明-健康',2,unit='7a08',
  title="Healthy Eating",
  passage="Tom is a middle school student. He likes eating hamburgers and drinking cola. He seldom eats vegetables. One day he felt ill and went to see the doctor. The doctor said, 'You should eat more fruit and vegetables, and drink more water. Don't eat too much fast food.' Tom listened and now he is healthy.",
  questions=[
    {"stem":"What does Tom like eating?","options":["Vegetables","Hamburgers","Fruit","Rice"],"answer":1,"analysis":"原文 likes eating hamburgers。"},
    {"stem":"Why did Tom see the doctor?","options":["He was ill.","He was happy.","He was hungry.","He was late."],"answer":0,"analysis":"felt ill 所以看医生。"},
    {"stem":"What did the doctor advise?","options":["Eat more fast food.","Drink more cola.","Eat more vegetables.","Sleep more."],"answer":2,"analysis":"建议多吃蔬菜水果。"},
  ]))
BANK.append(mk('r7a02',7,'reading','7b','记叙-节日',2,unit='7b05',
  title="Spring Festival",
  passage="Spring Festival is the most important festival in China. Before it, people clean their houses and buy food. On New Year's Eve, families get together and have a big dinner. Children get red packets with money. They watch TV and let off fireworks. Everyone is happy.",
  questions=[
    {"stem":"When do families have a big dinner?","options":["On New Year's Day","On New Year's Eve","On Christmas","On Mid-autumn Day"],"answer":1,"analysis":"新年前夜吃团圆饭。"},
    {"stem":"What do children get?","options":["Gifts","Red packets","Books","Cakes"],"answer":1,"analysis":"孩子得到红包 red packets。"},
    {"stem":"How do people feel?","options":["Sad","Angry","Happy","Tired"],"answer":2,"analysis":"Everyone is happy。"},
  ]))
# —— 词汇运用 7a ——
BANK += [
mk('v7a01',7,'vocab','7a','词形-名词',1,unit='7a03',mode='form',stem="There are three ___ (tomato) on the table.",word="tomato",answer="tomatoes",analysis="以 o 结尾表有生命物加 -es。"),
mk('v7a02',7,'vocab','7a','词形-动词',1,unit='7b01',mode='form',stem="She ___ (study) English every day.",word="study",answer="studies",analysis="第三人称单数 study→studies。"),
mk('v7a03',7,'vocab','7a','句意填词',2,unit='7a04',mode='blank',stem="My father is a doctor. He works in a h___.",answer="hospital",analysis="在医院工作填 hospital。"),
mk('v7a04',7,'vocab','7a','句意填词',2,unit='7b02',mode='blank',stem="It's cold outside. Please put on your c___.",answer="coat",analysis="天冷穿外套 coat。"),
mk('v7a05',7,'vocab','7b','词形-形容词',1,unit='7b06',mode='form',stem="This book is ___ (interest) than that one.",word="interest",answer="more interesting",analysis="多音节形容词比较级加 more。"),
mk('v7a06',7,'vocab','7b','词形-副词',2,unit='7b07',mode='form',stem="He runs ___ (quick) than me.",word="quick",answer="more quickly",analysis="副词 quick→quickly，比较级 more quickly。"),
mk('v7a07',7,'vocab','7a','句意填词',2,unit='7a07',mode='blank',stem="We have lunch at 12:00 at n___.",answer="noon",analysis="中午 at noon。"),
mk('v7a08',7,'vocab','7b','词形-名词',1,unit='7b08',mode='form',stem="My ___ (friend) and I play basketball.",word="friend",answer="friends",analysis="与 I 并列用复数 friends。"),
]
# —— 语法填空 7a（带选项）——
BANK.append(mk('g7a01',7,'grammar','7a','时态综合',2,unit='7b01',
  title="Grammar Fill-in",
  passage="Look! The boy (1)___ (play) basketball. He (2)___ (like) sports very much. Yesterday he (3)___ (win) a game. Now he (4)___ (be) happy. His father (5)___ (watch) him.",
  blanks=[
    {"options":["plays","is playing","played","play"],"answer":1,"analysis":"Look! 提示现在进行时 is playing。"},
    {"options":["like","likes","liked","liking"],"answer":1,"analysis":"第三人称单数 likes。"},
    {"options":["wins","won","win","winning"],"answer":1,"analysis":"Yesterday 用过去时 won。"},
    {"options":["is","was","are","be"],"answer":0,"analysis":"Now 现在时 is。"},
    {"options":["watch","watches","watched","watching"],"answer":1,"analysis":"父亲第三人称单数 watches。"},
  ]))
# —— 任务型阅读 7b ——
BANK.append(mk('t7b01',7,'task','7b','任务-表格',2,unit='7b09',
  title="My School Life",
  passage="My name is Lucy. I am in Class 3, Grade 7. I have six classes a day. My favorite subject is English. I join the art club after school. I go to the library on Friday.",
  questions=[
    {"stem":"What class is Lucy in?","answer":"Class 3, Grade 7","analysis":"直接提取信息。","kind":"answer"},
    {"stem":"What is her favorite subject?","answer":"English","analysis":"原文 favorite subject is English。","kind":"answer"},
    {"stem":"When does she go to the library?","answer":"On Friday","analysis":"on Friday 去图书馆。","kind":"answer"},
  ]))
# —— 书面表达 7b ——
BANK.append(mk('w7b01',7,'writing','7b','话题-我的朋友',2,unit='7b10',
  title="My Best Friend",
  prompt="请以 'My Best Friend' 为题写一篇不少于 60 词的英语短文，介绍你最好朋友的姓名、年龄、外貌、爱好及你们常做的事。",
  requirements=["包含姓名与年龄","描述外貌","介绍爱好","说明共同活动"],
  points=["用一般现在时","注意第三人称单数","语句连贯"],
  wordLimit=60,
  sample="My best friend is Li Hua. He is 13 years old. He is tall and has short black hair. He likes playing basketball and reading. After school we often play basketball together. He is kind and helps me with English. I am happy to have such a good friend."))

# ========================= 八年级（grade 8） =========================
BANK += [
choice(8,'8a','8a01','时态-过去',2,
  "We ___ a picnic last Sunday.", ["have","has","had","having"], 2,
  "last Sunday 过去时，have→had。"),
choice(8,'8a','8a02','比较级',2,
  "This box is ___ than that one.", ["heavy","heavier","heaviest","more heavy"], 1,
  "than 用比较级；heavy→heavier。"),
choice(8,'8a','8a03','连词',2,
  "Hurry up, ___ you will be late.", ["and","but","or","so"], 2,
  "祈使句 + or 表示否则。"),
choice(8,'8a','8a04','情态动词',2,
  "— Must I finish it now? — No, you ___.", ["mustn't","needn't","can't","may not"], 1,
  "Must 否定回答用 needn't（不必）。"),
choice(8,'8a','8a05','被动语态',3,
  "English ___ in many countries.", ["speaks","is spoken","spoke","was spoken"], 1,
  "一般现在被动 is spoken。"),
choice(8,'8a','8a06','定语从句',3,
  "The boy ___ is standing there is my brother.", ["which","who","whom","whose"], 1,
  "指人作主语用 who。"),
choice(8,'8b','8b01','现在完成时',3,
  "I ___ already ___ my homework.", ["have; finish","has; finished","have; finished","had; finished"], 2,
  "现在完成时 have/has + done；I 用 have。"),
choice(8,'8b','8b02','宾语从句',3,
  "Could you tell me ___ the station is?", ["where","what","how","when"], 0,
  "宾语从句问地点用 where，语序用陈述句。"),
choice(8,'8b','8b03','状语从句',2,
  "I will call you ___ I arrive.", ["as soon as","because","though","unless"], 0,
  "as soon as 一…就…，主将从现。"),
choice(8,'8b','8b04','非谓语',3,
  "It's difficult ___ the problem.", ["solve","to solve","solving","solved"], 1,
  "It's + adj. + to do 固定结构。"),
]
BANK.append(mk('c8a01',8,'cloze','8a','记叙-帮助',3,unit='8a07',
  title="A Good Deed",
  passage="Yesterday I (1)___ the bus to school. An old woman (2)___ on the bus. She had no seat. I (3)___ my seat to her. She (4)___ me and said thanks. I felt (5)___. Helping others makes me (6)___. After that I (7)___ to help more people. It was a (8)___ day.",
  blanks=[
    {"options":["take","took","taking","takes"],"answer":1,"analysis":"过去时 took。"},
    {"options":["get","gets","got","getting"],"answer":2,"analysis":"过去时 got on 上车。"},
    {"options":["give","gave","giving","gives"],"answer":1,"analysis":"过去时 gave。"},
    {"options":["smile","smiled","smiling","smiles"],"answer":1,"analysis":"过去时 smiled。"},
    {"options":["sad","happy","tired","bored"],"answer":1,"analysis":"帮助人感到 happy。"},
    {"options":["sad","angry","happy","tired"],"answer":2,"analysis":"make sb + adj. happy。"},
    {"options":["decide","decided","deciding","decides"],"answer":1,"analysis":"过去时 decided。"},
    {"options":["bad","good","cold","busy"],"answer":1,"analysis":"好人好事 a good day。"},
  ]))
BANK.append(mk('r8a01',8,'reading','8a','说明-环保',3,unit='8a09',
  title="Save the Earth",
  passage="Our earth is in danger. People cut down too many trees and pollute rivers. We should plant more trees and save water. We can also ride bikes instead of driving cars. If we work together, the earth will be better.",
  questions=[
    {"stem":"What is in danger?","options":["The trees","The earth","The rivers","The animals"],"answer":1,"analysis":"Our earth is in danger。"},
    {"stem":"What should we do?","options":["Cut trees","Plant trees","Drive cars","Pollute water"],"answer":1,"analysis":"应 plant more trees。"},
    {"stem":"What can we do instead of driving?","options":["Take a bus","Ride bikes","Walk far","Fly"],"answer":1,"analysis":"ride bikes 代替开车。"},
  ]))
BANK.append(mk('r8b01',8,'reading','8b','议论-网络',3,unit='8b05',
  title="The Internet",
  passage="The Internet is useful. We can study and shop online. But some students play games too much and forget homework. We should use the Internet in a right way. Parents and teachers should help students.",
  questions=[
    {"stem":"What can we do online?","options":["Only play games","Study and shop","Nothing","Only watch"],"answer":1,"analysis":"can study and shop online。"},
    {"stem":"What problem do some students have?","options":["They study hard.","They play games too much.","They sleep.","They read books."],"answer":1,"analysis":"玩太多游戏忘记作业。"},
    {"stem":"Who should help students?","options":["Doctors","Parents and teachers","Workers","Strangers"],"answer":1,"analysis":"家长和教师应帮助。"},
  ]))
BANK += [
mk('v8a01',8,'vocab','8a','词形-比较级',2,unit='8a02',mode='form',stem="This problem is ___ (easy) than that one.",word="easy",answer="easier",analysis="辅音+y 变 i+er：easy→easier。"),
mk('v8a02',8,'vocab','8a','词形-过去式',2,unit='8a01',mode='form',stem="They ___ (build) a library last year.",word="build",answer="built",analysis="build 过去式 built。"),
mk('v8a03',8,'vocab','8a','句意填词',3,unit='8a03',mode='blank',stem="If you don't hurry, you'll m___ the bus.",answer="miss",analysis="错过 miss 公交车。"),
mk('v8a04',8,'vocab','8a','句意填词',3,unit='8a04',mode='blank',stem="You n___ to practice more to improve.",answer="need",analysis="需要 need。"),
mk('v8b01',8,'vocab','8b','词形-完成时',3,unit='8b01',mode='form',stem="She ___ (live) here since 2010.",word="live",answer="has lived",analysis="since+过去时间用现在完成时 has lived。"),
mk('v8b02',8,'vocab','8b','词形-名词',2,unit='8b06',mode='form',stem="The ___ (invent) of the phone changed the world.",word="invent",answer="invention",analysis="invent→invention 名词。"),
mk('v8b03',8,'vocab','8b','句意填词',3,unit='8b07',mode='blank',stem="He is a___ from Japan and can't speak Chinese well.",answer="foreigner",analysis="外国人 foreigner。"),
mk('v8b04',8,'vocab','8b','词形-副词',3,unit='8b08',mode='form',stem="He drove ___ (careful) and arrived safely.",word="careful",answer="carefully",analysis="副词 carefully 修饰 drove。"),
]
BANK.append(mk('g8a01',8,'grammar','8a','被动语+时态',3,unit='8a05',
  title="Grammar Fill-in",
  passage="The bridge (1)___ (build) in 1990. It (2)___ (use) by many people every day. A new one (3)___ (build) next year. The road (4)___ (clean) now. Cars (5)___ (not allow) to park here.",
  blanks=[
    {"options":["built","was built","is built","builds"],"answer":1,"analysis":"1990 过去被动 was built。"},
    {"options":["uses","is used","used","was used"],"answer":1,"analysis":"每天用，现在被动 is used。"},
    {"options":["will build","will be built","builds","is built"],"answer":1,"analysis":"next year 将来被动 will be built。"},
    {"options":["cleaned","is cleaned","cleans","clean"],"answer":1,"analysis":"now 现在被动 is cleaned。"},
    {"options":["are not allowed","don't allow","not allow","isn't allowed"],"answer":0,"analysis":"复数 cars 现在被动否定 are not allowed。"},
  ]))
BANK.append(mk('t8b01',8,'task','8b','任务-问答',3,unit='8b09',
  title="Reading Habits",
  passage="Jack reads for 30 minutes before sleep. He likes science books. He borrows books from the school library. He thinks reading makes him smart.",
  questions=[
    {"stem":"How long does Jack read before sleep?","answer":"30 minutes","analysis":"30 minutes 提取。","kind":"answer"},
    {"stem":"What kind of books does he like?","answer":"Science books","analysis":"science books。"},
    {"stem":"Where does he borrow books?","answer":"From the school library","analysis":"学校图书馆借书。"},
  ]))
BANK.append(mk('w8b01',8,'writing','8b','话题-网络利弊',3,unit='8b05',
  title="The Internet",
  prompt="请以 'The Internet' 为题写一篇不少于 80 词的短文，谈谈网络的优点、存在的问题以及你的建议。",
  requirements=["说明优点","指出问题","给出建议","表明态度"],
  points=["使用连接词","现在时为主","观点明确"],
  wordLimit=80,
  sample="The Internet is important in our life. We can study and shop online. However, some students play games too much and hurt their eyes. In my opinion, we should use the Internet wisely. Parents and teachers should guide us. If we use it well, it will help us a lot."))

# ========================= 九年级（grade 9 / 中考冲刺） =========================
BANK += [
choice(9,'9','9a01','宾语从句',3,
  "I don't know ___ he will come tomorrow.", ["if","that","what","不填"], 0,
  "是否来用 if 引导宾语从句。"),
choice(9,'9','9a02','定语从句',3,
  "This is the book ___ I bought yesterday.", ["who","whom","which","whose"], 2,
  "指物作宾语用 which/that。"),
choice(9,'9','9a03','倒装',3,
  "— He likes music. — ___.", ["So do I","So I do","Neither do I","So am I"], 0,
  "So + 助动词 + 主语 表示前者情况也适用于后者。"),
choice(9,'9','9a04','虚拟语气',3,
  "If I ___ you, I would take the job.", ["am","was","were","be"], 2,
  "与现在事实相反，be 用 were。"),
choice(9,'9','9a05','非谓语',3,
  "He made us ___ the room.", ["clean","to clean","cleaning","cleaned"], 0,
  "make sb do sth 用动词原形。"),
choice(9,'9','9a06','时态',3,
  "By the time he came, we ___ the work.", ["finish","finished","had finished","have finished"], 2,
  "过去的过去用过去完成时 had finished。"),
choice(9,'9','9a07','词汇辨析',3,
  "The ___ of the match made him sad.", ["lose","loss","lost","losing"], 1,
  "the + 名词 loss（失败）。"),
choice(9,'9','9a08','连词',3,
  "___ it was raining, we went on working.", ["Though","Because","If","Unless"], 0,
  "尽管下雨仍继续，用 Though 让步。"),
choice(9,'9','9a09','情态动词',3,
  "The book ___ be Lily's. Her name is on it.", ["can","must","may","could"], 1,
  "有名字肯定推测用 must。"),
choice(9,'9','9a10','介词',3,
  "He is good ___ math but weak ___ English.", ["at; in","in; at","at; at","in; in"], 0,
  "be good at 擅长；weak in 在…弱。"),
]
BANK.append(mk('c9a01',9,'cloze','9','记叙-成长',3,unit='9a05',
  title="Never Give Up",
  passage="Tom failed the exam. He felt (1)___ and wanted to give up. His teacher (2)___ him, 'Failure is the mother of success.' Tom (3)___ hard from then on. He asked teachers for (4)___. Finally he (5)___ the next exam. He learned that (6)___ is important. We should (7)___ our best and never (8)___ up.",
  blanks=[
    {"options":["happy","sad","excited","proud"],"answer":1,"analysis":"考试失败感到 sad。"},
    {"options":["told","said","spoke","talked"],"answer":0,"analysis":"tell sb + 话语，用 told。"},
    {"options":["works","worked","working","work"],"answer":1,"analysis":"过去时 worked。"},
    {"options":["help","helps","helping","helped"],"answer":0,"analysis":"for help 求助。"},
    {"options":["pass","passed","past","passes"],"answer":1,"analysis":"过去时 passed。"},
    {"options":["give up","hard work","luck","money"],"answer":1,"analysis":"努力工作重要。"},
    {"options":["try","tries","tried","trying"],"answer":0,"analysis":"should 后动词原形 try。"},
    {"options":["give","gave","giving","gives"],"answer":0,"analysis":"never give up 永不放弃。"},
  ]))
BANK.append(mk('r9a01',9,'reading','9','说明-科技',3,unit='9a07',
  title="AI in Our Life",
  passage="AI is changing our life. It helps doctors find illness early. Self-driving cars may reduce accidents. But AI also brings problems, like job loss. We should learn to use AI well and make rules for it.",
  questions=[
    {"stem":"How does AI help doctors?","options":["Drive cars","Find illness early","Make rules","Lose jobs"],"answer":1,"analysis":"帮助早诊疾病。"},
    {"stem":"What problem may AI bring?","options":["Fewer accidents","Job loss","More illness","Better study"],"answer":1,"analysis":"带来失业问题。"},
    {"stem":"What should we do?","options":["Stop AI","Use it well and make rules","Ignore it","Buy more"],"answer":1,"analysis":"用好并立规矩。"},
  ]))
BANK.append(mk('r9a02',9,'reading','9','议论-环保',3,unit='9a08',
  title="Plastic Pollution",
  passage="Plastic pollution is serious. Millions of plastic bottles go into the sea each day. Animals eat them by mistake. We should use reusable bags and bottles. Small actions can make a big difference.",
  questions=[
    {"stem":"Where do plastic bottles go?","options":["Into the sea","Into the sky","Into the bank","Into the school"],"answer":0,"analysis":"流入海洋。"},
    {"stem":"Why are animals in danger?","options":["They swim.","They eat plastic.","They sleep.","They fly."],"answer":1,"analysis":"误食塑料。"},
    {"stem":"What should we use?","options":["Reusable bags","Plastic bags","More bottles","Paper only"],"answer":0,"analysis":"用可重复使用的袋子。"},
  ]))
BANK += [
mk('v9a01',9,'vocab','9','词形-名词',3,unit='9a03',mode='form',stem="His ___ (suggest) is very useful.",word="suggest",answer="suggestion",analysis="suggest→suggestion 名词。"),
mk('v9a02',9,'vocab','9','词形-比较级',3,unit='9a01',mode='form',stem="This problem is the ___ (difficult) of the three.",word="difficult",answer="most difficult",analysis="三者及以上用最高级 most difficult。"),
mk('v9a03',9,'vocab','9','句意填词',3,unit='9a04',mode='blank',stem="The government should take a___ to protect the environment.",answer="action",analysis="take action 采取行动。"),
mk('v9a04',9,'vocab','9','句意填词',3,unit='9a06',mode='blank',stem="We should r___ the old things instead of throwing them.",answer="reuse",analysis="重复使用 reuse。"),
mk('v9a05',9,'vocab','9','词形-被动',3,unit='9a07',mode='form',stem="The letter ___ (write) by him yesterday.",word="write",answer="was written",analysis="过去被动 was written。"),
mk('v9a06',9,'vocab','9','词形-副词',3,unit='9a08',mode='form',stem="He solved the problem ___ (success).",word="success",answer="successfully",analysis="副词 successfully 修饰动词。"),
mk('v9a07',9,'vocab','9','句意填词',3,unit='9a09',mode='blank',stem="It's our d___ to protect nature.",answer="duty",analysis="责任 duty。"),
mk('v9a08',9,'vocab','9','词形-名词',3,unit='9a10',mode='form',stem="We need more ___ (volunteer) for the event.",word="volunteer",answer="volunteers",analysis="volunteer 复数 volunteers。"),
]
BANK.append(mk('g9a01',9,'grammar','9','综合语法填空',3,unit='9a02',
  title="Grammar Fill-in",
  passage="If I (1)___ (be) a bird, I (2)___ (fly) high. He (3)___ (work) here since 2015. The letter (4)___ (write) by Mary. We (5)___ (tell) to keep quiet just now.",
  blanks=[
    {"options":["am","was","were","be"],"answer":2,"analysis":"虚拟语气用 were。"},
    {"options":["fly","would fly","flew","flying"],"answer":1,"analysis":"与现在相反主句 would fly。"},
    {"options":["works","worked","has worked","is working"],"answer":2,"analysis":"since 2015 现在完成时 has worked。"},
    {"options":["writes","wrote","was written","is writing"],"answer":2,"analysis":"过去被动 was written。"},
    {"options":["tell","told","were told","are told"],"answer":2,"analysis":"just now 过去被动 were told。"},
  ]))
BANK.append(mk('t9a01',9,'task','9','任务-观点',3,unit='9a07',
  title="Opinion Task",
  passage="Some schools start classes at 8:30 a.m. Students say they can sleep more and study better. Teachers say it is good for health. Parents worry about traffic.",
  questions=[
    {"stem":"What time do some schools start?","answer":"8:30 a.m.","analysis":"8:30 上课。"},
    {"stem":"Why do students like it?","answer":"They can sleep more and study better","analysis":"多睡且学得更好。"},
    {"stem":"What do parents worry about?","answer":"Traffic","analysis":"家长担心交通。"},
  ]))
BANK.append(mk('w9a01',9,'writing','9','话题-环保',3,unit='9a08',
  title="How to Protect the Environment",
  prompt="请以 'How to Protect the Environment' 为题写一篇不少于 100 词的短文，提出至少三条环保建议并说明意义。",
  requirements=["三条建议","说明意义","条理清晰","呼吁行动"],
  points=["使用 first/second/third","情态动词 should","现在时为主"],
  wordLimit=100,
  sample="It is our duty to protect the environment. First, we should reduce plastic use and take reusable bags. Second, we must save water and electricity. Third, planting more trees can make the air cleaner. If everyone takes action, the earth will be more beautiful. Let's start from small things now."))

# 分配唯一 id
seen = {}
for i, q in enumerate(BANK):
    if not q['id'] or q['id'] in seen:
        q['id'] = f"je{str(i+1).zfill(4)}"
    seen[q['id']] = True

data = {
  "product": "初中英语题库（中考笔试真题格式原型·原创练习）",
  "version": "1.0",
  "schema_version": "1.0",
  "note": "题型：choice 单选 / cloze 完形 / reading 阅读 / vocab 词汇运用 / grammar 语法填空 / task 任务型阅读 / writing 书面表达；grade 7/8/9；book 7a~9；difficulty 1-3。组卷按 grade/type/book/unit/difficulty 过滤切片。",
  "questions": BANK,
}

# 校验
from collections import Counter
c = Counter((q['grade'], q['type']) for q in BANK)
errs = 0
for q in BANK:
    t = q['type']
    if t == 'choice':
        if not (0 <= q['answer'] < len(q['options'])): errs += 1; print('ERR answer', q['id'])
    elif t in ('cloze','grammar'):
        for b in q['blanks']:
            if not (0 <= b['answer'] < len(b['options'])): errs += 1; print('ERR blank', q['id'])
    elif t == 'reading':
        for qn in q['questions']:
            if not (0 <= qn['answer'] < len(qn['options'])): errs += 1; print('ERR rq', q['id'])
print("总题项（含子题）:", len(BANK), "| 答案越界错误:", errs)
print("分布(年级/题型):")
for k in sorted(c): print("  ", k, c[k])

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=1)
print("写入:", os.path.abspath(OUT))
