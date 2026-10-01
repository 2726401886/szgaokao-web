# -*- coding: utf-8 -*-
"""生成 4 套新卷（v07-v10）：试卷 md + 音频脚本与生词表 md + 追加 szgaokao-web/data/quiz.json。
数据单一来源，md 与 JSON 同源渲染，保证一致性。
用法：python tools/gen_new_volumes.py
"""
import os, json, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))          # szgaokao-web
DATA = os.path.join(ROOT, 'data')
MD_DIR = os.path.join(os.path.dirname(ROOT), 'english-edu-company', '03交付素材库', '听说试卷包')
JSON_DIR = os.path.join(os.path.dirname(ROOT), 'english-edu-company', '题库导入JSON', '分卷')
os.makedirs(MD_DIR, exist_ok=True)
os.makedirs(JSON_DIR, exist_ok=True)

def A(qid, word, options, ans, level, ipa, cn, pos='n.'):
    return {"id": qid, "word": word, "options": options, "answer": ans, "level": level,
            "ipa": ipa, "cn": cn, "pos": pos}

def B(qid, sent, options, ans):
    return {"id": qid, "sent": sent, "options": options, "answer": ans}

def C(qid, turns, q, options, ans, trap, analysis):
    return {"id": qid, "turns": turns, "q": q, "options": options, "answer": ans,
            "trap": trap, "analysis": analysis}

VOLS = []

# ============ 卷07 家庭与朋友 ============
VOLS.append({
  "vid": "v07", "title": "试卷07（家庭与朋友）", "topic": "家庭与朋友", "mainTrap": "数字计算+人物关系",
  "A": [
    A("v07A01","family",["工厂","家庭","农场"],1,"课标","/ˈfæməli/","家庭"),
    A("v07A02","parents",["礼物","父母","公园"],1,"课标","/ˈpeərənts/","父母"),
    A("v07A03","cousin",["厨师","堂（表）兄弟姐妹","顾客"],1,"课标","/ˈkʌzn/","堂（表）兄弟姐妹"),
    A("v07A04","friendly",["友好的","可怕的","拥挤的"],0,"课标","/ˈfrendli/","友好的",'adj.'),
    A("v07A05","trust",["尝试","交通","信任"],2,"课标","/trʌst/","信任",'v./n.'),
    A("v07A06","share",["分享","剪切","闪耀"],0,"课标","/ʃeə(r)/","分享",'v.'),
    A("v07A07","respect",["报告","尊重","重复"],1,"课标","/rɪˈspekt/","尊重",'v./n.'),
    A("v07A08","relative",["亲戚","休息","关系"],0,"课标","/ˈrelətɪv/","亲戚"),
    A("v07A09","generation",["一代人","发电机","感谢"],0,"拓展","/ˌdʒenəˈreɪʃn/","一代人"),
    A("v07A10","elder",["电梯","年长的","选举"],1,"课标","/ˈeldə(r)/","年长的",'adj.'),
  ],
  "B": [
    B("v07B01","How many people are there in your family?",["I like them.","Four people.","On weekends."],1),
    B("v07B02","What does your mother do?",["She is fine.","She is at home.","She is a nurse."],2),
    B("v07B03","Would you like to play basketball with us?",["It's Monday.","Sure, I'd love to.","Here you are."],1),
    B("v07B04","Happy birthday, my friend!",["The same to you.","I don't think so.","Thank you very much."],2),
    B("v07B05","How do you get along with your classmates?",["Very well, we help each other.","Twice a week.","By bike."],0),
  ],
  "C": [
    C("v07C01",["M: My sister Mary plays the piano very well.","W: And my brother Tom plays the guitar."],
      "What does Mary play?",["The guitar","The piano","The violin"],1,"张冠李戴",
      "问的是 Mary，答案在男生的话里（Mary plays the piano）；女生说的是自己的弟弟 Tom。"),
    C("v07C02",["M: How old is your father?","W: He is 40. And my brother is only 10."],
      "How much older is the father than the brother?",["40","10","30"],2,"数字计算",
      "40-10=30，需计算年龄差，录音不念结果。"),
    C("v07C03",["W: We planned a picnic with our friends, but it rained, so we played board games at home."],
      "What did they do?",["Had a picnic","Played board games","Went shopping"],1,"转折后取义",
      "but 之后才是真实发生的事。"),
    C("v07C04",["M: I'm so happy that my best friend moved back to our city!","W: Great! Now you can play together again."],
      "How does the boy feel?",["Sad","Angry","Happy"],2,"态度推断",
      "so happy + best friend moved back → 高兴。"),
    C("v07C05",["W: Look at this photo. We were at my grandmother's birthday dinner.","M: Wow, the cake looks great!"],
      "Where were they?",["At a restaurant","At grandmother's home","At school"],1,"地点身份",
      "birthday dinner at grandmother's + 家庭照片 → 在奶奶家。"),
  ],
  "D": {
    "passage": ("Hello, I'm Emma. I live with my parents and my little sister Lucy. My father is a doctor, "
      "and my mother is a teacher. We have breakfast at 7:00. My father leaves home at 7:30, and my mother "
      "takes me to school at 7:50. My sister is only 6 years old. She goes to a kindergarten. On weekends, "
      "we often visit my grandparents. My grandfather likes telling stories, and my grandmother cooks "
      "delicious food. I love my family very much."),
    "qs": [
      ("v07D01","Who is a doctor?",["My father","My mother","My grandfather"],0),
      ("v07D02","What time do they have breakfast?",["7:30","7:00","7:50"],1),
      ("v07D03","How old is Lucy?",["6","7","8"],0),
      ("v07D04","What does the grandfather like doing?",["Cooking","Singing","Telling stories"],2),
      ("v07D05","How does Emma feel about her family?",["She loves her family","She is bored","She is angry"],0),
    ],
  },
  "E": {
    "read": ("My family always has dinner together on Friday evenings.",
             "always has /ˈɔːlweɪz hæz/；together on /təˈɡeðər ɒn/ 弱读。"),
    "answer": ["How many people are there in your family?","What do your parents do?",
               "What do you like to do with your friends?"],
    "describe": ("Describe your best friend.",
      "My best friend is Li Hua. He is friendly and always ready to help others. We have known each other "
      "for three years. He likes playing basketball, and I often watch his games. When I am in trouble, "
      "he always gives me good advice. I am happy to have such a good friend."),
  },
  "words_extra": [
    ("piano","/piˈænəʊ/","n.","钢琴","C1","课标"),
    ("guitar","/ɡɪˈtɑː(r)/","n.","吉他","C1","课标"),
    ("board game","/ˈbɔːd ɡeɪm/","n.","桌游","C3","拓展"),
  ],
})

# ============ 卷08 科技与媒体 ============
VOLS.append({
  "vid": "v08", "title": "试卷08（科技与媒体）", "topic": "科技与媒体", "mainTrap": "态度推断",
  "A": [
    A("v08A01","computer",["计算机","计算器","摄像机"],0,"课标","/kəmˈpjuːtə(r)/","计算机"),
    A("v08A02","internet",["互联网","国际","内部"],0,"课标","/ˈɪntənet/","互联网"),
    A("v08A03","phone",["照片","电话","面条"],1,"课标","/fəʊn/","电话"),
    A("v08A04","message",["消息","按摩","婚礼"],0,"课标","/ˈmesɪdʒ/","消息"),
    A("v08A05","screen",["尖叫","屏幕","曲线"],1,"课标","/skriːn/","屏幕"),
    A("v08A06","download",["上传","下载","播放"],1,"课标","/ˌdaʊnˈləʊd/","下载",'v.'),
    A("v08A07","video",["音频","视频","无线电"],1,"课标","/ˈvɪdiəʊ/","视频"),
    A("v08A08","keyboard",["键盘","黑板","橱柜"],0,"课标","/ˈkiːbɔːd/","键盘"),
    A("v08A09","technology",["科技","传统","温度"],0,"课标","/tekˈnɒlədʒi/","科技"),
    A("v08A10","online",["在线的","关机的","旧式的"],0,"拓展","/ˌɒnˈlaɪn/","在线的",'adj.'),
  ],
  "B": [
    B("v08B01","How do you usually keep in touch with your friends?",["It's sunny.","By phone messages.","I'm fine."],1),
    B("v08B02","Can I use your computer for a moment?",["No, I don't.","Sure, go ahead.","Thank you."],1),
    B("v08B03","How often do you play computer games?",["It's interesting.","Never, I prefer reading.","On the computer."],1),
    B("v08B04","Do you like watching videos online?",["Yes, I watch them every day.","No, they are books.","Yes, I'm a video."],0),
    B("v08B05","What do you think of the new phone?",["I'm a student.","Here you are.","It's cool and fast."],2),
  ],
  "C": [
    C("v08C01",["W: My brother likes playing online games.","M: My sister likes watching cartoons on TV."],
      "What does the girl's brother like?",["Watching cartoons","Playing online games","Reading books"],1,"张冠李戴",
      "问女生的哥哥，答案在她的话里（brother likes playing online games）；男生说的是自己的妹妹。"),
    C("v08C02",["M: The computer costs 4,000 yuan now, and it is 500 yuan cheaper than before.","W: So what was the old price?"],
      "What was the original price of the computer?",["4,000","3,500","4,500"],2,"数字计算",
      "现价 4000，比原价便宜 500，原价 = 4000+500 = 4500，需逆向计算。"),
    C("v08C03",["W: I wanted to watch a movie online, but the internet was down, so I read a book instead."],
      "What did the girl do?",["Watched a movie","Read a book","Played games"],1,"转折后取义",
      "but 之后才是真实发生的事。"),
    C("v08C04",["M: This phone game is really boring. I keep losing!","W: Let's play something else."],
      "How does the boy feel about the game?",["Excited","Happy","Bored"],2,"态度推断",
      "really boring + keep losing → 觉得无聊、不耐烦。"),
    C("v08C05",["W: Excuse me, which floor is the electronic section on?","M: It's on the third floor, next to the book area."],
      "Where are they?",["In a library","In a shop","In a cinema"],1,"地点身份",
      "electronic section + 楼层 + book area → 商场/书店。"),
  ],
  "D": {
    "passage": ("Last month, my father bought me a new tablet. I use it to watch English videos and listen to "
      "music. My teacher says we can use the internet to learn, but we should not spend too much time on games. "
      "I often study online for one hour after dinner. My parents limit my screen time to two hours a day. "
      "I think technology is helpful, but I must use it wisely."),
    "qs": [
      ("v08D01","What did the father buy?",["A phone","A tablet","A computer"],1),
      ("v08D02","What does she use the tablet to do?",["Play games","Watch English videos","Chat with friends"],1),
      ("v08D03","How long does she study online after dinner?",["One hour","Two hours","Half an hour"],0),
      ("v08D04","How many hours of screen time do her parents allow a day?",["One hour","Two hours","Three hours"],1),
      ("v08D05","What does she think of technology?",["Useless","Bad for students","Helpful if used wisely"],2),
    ],
  },
  "E": {
    "read": ("I often search for information on the internet.",
             "search for /ˈsɜːtʃ fə/ 弱读；on the /ɒn ðə/ 弱读。"),
    "answer": ["What do you usually do on the computer?",
               "Do you think students should use phones at school? Why?",
               "How do you usually contact your friends?"],
    "describe": ("Describe how technology helps you study.",
      "Technology helps me a lot in my study. I use the computer to search for information and watch English "
      "videos. I also take notes on my tablet. When I don't understand a word, I look it up online. My parents "
      "control my screen time, so I can study and rest well. I think technology is a good helper if we use it wisely."),
  },
  "words_extra": [
    ("tablet","/ˈtæblət/","n.","平板电脑","D","课标"),
    ("cartoon","/kɑːˈtuːn/","n.","动画片","C1","课标"),
    ("wisely","/ˈwaɪzli/","adv.","明智地","D","课标"),
  ],
})

# ============ 卷09 动物与自然 ============
VOLS.append({
  "vid": "v09", "title": "试卷09（动物与自然）", "topic": "动物与自然", "mainTrap": "地点身份",
  "A": [
    A("v09A01","animal",["动物","动画","蔬菜"],0,"课标","/ˈænɪml/","动物"),
    A("v09A02","panda",["熊猫","斑马","鹦鹉"],0,"课标","/ˈpændə/","熊猫"),
    A("v09A03","forest",["森林","家具","节日"],0,"课标","/ˈfɒrɪst/","森林"),
    A("v09A04","river",["米饭","河流","邮递员"],1,"课标","/ˈrɪvə(r)/","河流"),
    A("v09A05","environment",["环境","娱乐","信封"],0,"课标","/ɪnˈvaɪrənmənt/","环境"),
    A("v09A06","protect",["保护","抗议","项目"],0,"课标","/prəˈtekt/","保护",'v.'),
    A("v09A07","nature",["自然","名字","营养"],0,"课标","/ˈneɪtʃə(r)/","自然"),
    A("v09A08","pollution",["污染","人口","流行"],0,"课标","/pəˈluːʃn/","污染"),
    A("v09A09","wild",["温和的","野生的","世界"],1,"课标","/waɪld/","野生的",'adj.'),
    A("v09A10","recycle",["回收利用","骑车","记录"],0,"拓展","/ˌriːˈsaɪkl/","回收利用",'v.'),
  ],
  "B": [
    B("v09B01","What animals do you like best?",["It's a panda.","I like pandas best.","In the zoo."],1),
    B("v09B02","Have you ever seen a real panda?",["No, but I want to.","Yes, I'm a panda.","It's cute."],0),
    B("v09B03","Why do we protect wild animals?",["Because they are our friends.","They are cute.","In the forest."],0),
    B("v09B04","How can we protect the environment?",["We can save water and plant trees.","It's sunny.","Let's go."],0),
    B("v09B05","Where can we see wild animals?",["On Monday.","By bus.","In the forest or the zoo."],2),
  ],
  "C": [
    C("v09C01",["M: Tom likes dogs, and Lily likes cats.","W: I like rabbits best."],
      "What does Lily like?",["Dogs","Cats","Rabbits"],1,"张冠李戴",
      "问 Lily，答案在男生的话里（Lily likes cats），不要被女生说的 rabbits 干扰。"),
    C("v09C02",["W: There were 50 trees in our school. We planted 20 more this year."],
      "How many trees are there now?",["50","70","20"],1,"数字计算",
      "50+20=70，需做加法。"),
    C("v09C03",["M: We wanted to go to the forest park, but the weather was bad, so we visited the science museum instead."],
      "Where did they go?",["The forest park","The science museum","The zoo"],1,"转折后取义",
      "but 之后才是真实去的地方。"),
    C("v09C04",["W: I'm really worried about the pollution in the river. The fish are dying!","M: We should do something to help."],
      "How does the girl feel?",["Worried","Happy","Bored"],0,"态度推断",
      "really worried + fish are dying → 担忧。"),
    C("v09C05",["M: Welcome to our zoo! Please keep quiet near the panda area.","W: OK, we will."],
      "Where are they?",["In a zoo","In a park","In a school"],0,"地点身份",
      "zoo + panda area + keep quiet → 动物园。"),
  ],
  "D": {
    "passage": ("There is a small forest near my home. Many birds and rabbits live there. Last year, people cut "
      "down some trees, and the birds lost their homes. My classmates and I decided to help. We planted 30 new "
      "trees. We also put up signs to tell people not to throw rubbish in the forest. Now the forest is green "
      "again, and the birds are back. I hope people can protect nature together."),
    "qs": [
      ("v09D01","What animals live in the forest?",["Birds and rabbits","Cats and dogs","Fish and ducks"],0),
      ("v09D02","What happened last year?",["People planted trees","People cut down trees","People moved away"],1),
      ("v09D03","How many new trees did they plant?",["13","30","50"],1),
      ("v09D04","What do the signs tell people?",["To throw rubbish in the forest","Not to throw rubbish in the forest","To cut more trees"],1),
      ("v09D05","How does the speaker feel now?",["Sad and tired","Angry with people","Hopeful and happy"],2),
    ],
  },
  "E": {
    "read": ("We should protect wild animals and keep the forest clean.",
             "protect wild /prəˈtekt waɪld/；and keep /ən kiːp/ 弱读。"),
    "answer": ["What is your favorite animal? Why?",
               "How do you usually protect the environment?",
               "Have you ever been to a zoo? What did you see?"],
    "describe": ("Describe a time you did something for the environment.",
      "Last month I joined a tree-planting activity with my classmates. We planted 20 small trees near the "
      "river. We also picked up rubbish in the park. My teacher said the environment needs everyone's help. "
      "I was tired but very happy. I want to do it again next year."),
  },
  "words_extra": [
    ("rabbit","/ˈræbɪt/","n.","兔子","C1/D","课标"),
    ("rubbish","/ˈrʌbɪʃ/","n.","垃圾","D","课标"),
    ("sign","/saɪn/","n.","标牌","D","课标"),
  ],
})

# ============ 卷10 职业与梦想 ============
VOLS.append({
  "vid": "v10", "title": "试卷10（职业与梦想）", "topic": "职业与梦想", "mainTrap": "转折后取义",
  "A": [
    A("v10A01","engineer",["引擎","工程师","能量"],1,"课标","/ˌendʒɪˈnɪə(r)/","工程师"),
    A("v10A02","pilot",["飞行员","枕头","邮局"],0,"课标","/ˈpaɪlət/","飞行员"),
    A("v10A03","artist",["演员","助手","艺术家"],2,"课标","/ˈɑːtɪst/","艺术家"),
    A("v10A04","scientist",["场景","科学家","剪刀"],1,"课标","/ˈsaɪəntɪst/","科学家"),
    A("v10A05","dream",["梦想","戏剧","鼓"],0,"课标","/driːm/","梦想"),
    A("v10A06","future",["家具","未来","水果"],1,"课标","/ˈfjuːtʃə(r)/","未来"),
    A("v10A07","job",["工作","跳跃","珠宝"],0,"课标","/dʒɒb/","工作"),
    A("v10A08","goal",["黄金","目标","山羊"],1,"课标","/ɡəʊl/","目标"),
    A("v10A09","firefighter",["农民","渔民","消防员"],2,"课标","/ˈfaɪəfaɪtə(r)/","消防员"),
    A("v10A10","astronaut",["宇航员","天文学","宇宙"],0,"拓展","/ˈæstrənɔːt/","宇航员"),
  ],
  "B": [
    B("v10B01","What do you want to be in the future?",["I'm a student.","I want to be a scientist.","It's nice."],1),
    B("v10B02","Why do you want to be a teacher?",["I'm a teacher.","On weekends.","Because I like helping children."],2),
    B("v10B03","What does your father do?",["He is an engineer.","He is fine.","He is 40."],0),
    B("v10B04","Is your dream to be a pilot?",["Yes, I fly.","No, I want to be an artist.","I like planes."],1),
    B("v10B05","How will you make your dream come true?",["It's hard.","Next year.","I will study hard and never give up."],2),
  ],
  "C": [
    C("v10C01",["M: My uncle is a pilot.","W: My aunt is a nurse."],
      "What does the boy's uncle do?",["A pilot","A nurse","A teacher"],0,"张冠李戴",
      "问男生的叔叔，答案在他自己的话里（uncle is a pilot）。"),
    C("v10C02",["W: A doctor works 8 hours a day. A nurse works 2 hours more."],
      "How many hours does the nurse work a day?",["8","10","6"],1,"数字计算",
      "8+2=10，需做加法。"),
    C("v10C03",["M: I wanted to be a singer, but I found I was not good at singing. Now I want to be a music teacher."],
      "What does the boy want to be now?",["A singer","A music teacher","A doctor"],1,"转折后取义",
      "but 之后才是现在的目标，答案取转折后。"),
    C("v10C04",["W: I'm proud of my son. He became a firefighter and saved three people!","M: He is really a hero!"],
      "How does the mother feel?",["Proud","Angry","Worried"],0,"态度推断",
      "proud of + saved people → 自豪。"),
    C("v10C05",["M: Welcome to our hospital. The doctor will see you soon.","W: Thank you. I have a bad headache."],
      "Where are they?",["At school","In a hospital","In a police station"],1,"地点身份",
      "hospital + doctor will see you → 医院。"),
  ],
  "D": {
    "passage": ("Hello, I'm Jack. I am 15 years old, and I want to be a scientist in the future. My dream started "
      "when I read a book about space. I study math and science very hard. After school, I often watch "
      "documentaries about rockets. Last month, I joined the school science club. We do small experiments "
      "together. My teacher says I should also practice English, because scientists need to read English papers. "
      "I believe if I keep working hard, my dream will come true."),
    "qs": [
      ("v10D01","What does Jack want to be?",["A doctor","A scientist","A pilot"],1),
      ("v10D02","When did his dream start?",["When he watched a movie","When he visited a lab","When he read a book about space"],2),
      ("v10D03","What does he do after school?",["Watch documentaries about rockets","Play computer games","Play basketball"],0),
      ("v10D04","What club did he join?",["Science club","Music club","Basketball club"],0),
      ("v10D05","Why does he practice English?",["To pass exams","To travel abroad","To read English papers"],2),
    ],
  },
  "E": {
    "read": ("I will study hard to make my dream come true.",
             "study hard /ˈstʌdi hɑːd/；come true /kʌm truː/。"),
    "answer": ["What do you want to be in the future? Why?",
               "What should a student do to reach his or her dream?",
               "Which job do you think is the most useful? Why?"],
    "describe": ("Describe your dream job.",
      "I want to be a scientist when I grow up. I am interested in space and rockets. I will study math and "
      "science hard. I also need to practice English to read papers. My teacher tells me that only hard work "
      "makes dreams come true. I will never give up."),
  },
  "words_extra": [
    ("rocket","/ˈrɒkɪt/","n.","火箭","D","课标"),
    ("documentary","/ˌdɒkjuˈmentri/","n.","纪录片","D","拓展"),
    ("experiment","/ɪkˈsperɪmənt/","n.","实验","D","课标"),
  ],
})

# ============ 卷11 节日与庆祝 ============
VOLS.append({
  "vid": "v11", "title": "试卷11（节日与庆祝）", "topic": "节日与庆祝", "mainTrap": "张冠李戴",
  "A": [
    A("v11A01","festival",["工厂","节日","宴会"],1,"课标","/ˈfestɪvl/","节日"),
    A("v11A02","celebrate",["称呼","冷静","庆祝"],2,"课标","/ˈselɪbreɪt/","庆祝",'v.'),
    A("v11A03","lantern",["午餐","灯笼","柠檬"],1,"课标","/ˈlæntən/","灯笼"),
    A("v11A04","dumpling",["饺子","哑铃","鼓"],0,"课标","/ˈdʌmplɪŋ/","饺子"),
    A("v11A05","firework",["消防员","烟花","篝火"],1,"课标","/ˈfaɪəwɜːk/","烟花"),
    A("v11A06","culture",["农业","文化","颜色"],1,"课标","/ˈkʌltʃə(r)/","文化"),
    A("v11A07","traditional",["临时的","贸易","传统的"],2,"课标","/trəˈdɪʃənl/","传统的",'adj.'),
    A("v11A08","lucky",["幸运的","滑稽的","美味的"],0,"课标","/ˈlʌki/","幸运的",'adj.'),
    A("v11A09","reunion",["团聚","联合","原因"],0,"拓展","/ˌriːˈjuːniən/","团聚"),
    A("v11A10","decorate",["决定","装饰","奉献"],1,"拓展","/ˈdekəreɪt/","装饰",'v.'),
  ],
  "B": [
    B("v11B01","What festival do you like best?",["It's a festival.","I like the Spring Festival best.","On Monday."],1),
    B("v11B02","When is the Mid-Autumn Festival?",["It's usually in September.","It's delicious.","By plane."],0),
    B("v11B03","What do people eat on the Lantern Festival?",["Rice dumplings.","Tangyuan, sweet dumplings.","Cakes."],1),
    B("v11B04","Did you enjoy the Spring Festival?",["Yes, it was great fun.","It's cold.","Thank you."],0),
    B("v11B05","What do you do during the festival?",["I'm fine.","We visit relatives and eat together.","Next week."],1),
  ],
  "C": [
    C("v11C01",["W: My family eats dumplings on the Spring Festival.","M: My family has hotpot instead."],
      "What does the girl's family eat on the Spring Festival?",["Hotpot","Dumplings","Noodles"],1,"张冠李戴",
      "问女生家，答案在她的话里（dumplings）；男生家是 hotpot。"),
    C("v11C02",["M: The festival lasts 3 days. We have already spent 2 days.","W: So how many days are left?"],
      "How many days are left?",["3","2","1"],2,"数字计算",
      "3-2=1，需做减法。"),
    C("v11C03",["W: I planned to go to the lantern show, but it rained, so we watched it online."],
      "What did the girl do?",["Went to the show","Watched the lantern show online","Stayed home doing nothing"],1,"转折后取义",
      "but 之后才是真实发生的。"),
    C("v11C04",["M: I can't wait for the New Year! I love the big family dinner and red envelopes!","W: Me too!"],
      "How does the boy feel about the New Year?",["Bored","Excited","Angry"],1,"态度推断",
      "can't wait + love → 期待兴奋。"),
    C("v11C05",["M: Excuse me, where can I watch the dragon dance?","W: It's in the town square, starting at 3 p.m."],
      "Where is the dragon dance?",["In the town square","In a restaurant","At school"],0,"地点身份",
      "town square + dragon dance → 广场。"),
  ],
  "D": {
    "passage": ("Last week was the Mid-Autumn Festival. My family got together at my grandparents' home. We had "
      "a big dinner with fish, chicken and vegetables. After dinner, we went to the balcony and watched the "
      "full moon. We ate mooncakes and told stories about Chang'e. My little sister was so happy. She said the "
      "moon looked like a big round cake. We stayed together until 10 p.m. It was a warm and happy night."),
    "qs": [
      ("v11D01","Where did the family get together?",["At a restaurant","At grandparents' home","In a park"],1),
      ("v11D02","What did they do after dinner?",["Played games","Went shopping","Watched the full moon"],2),
      ("v11D03","What did they eat?",["Mooncakes","Dumplings","Cakes"],0),
      ("v11D04","What did the sister say the moon looked like?",["A ball","A plate","A big round cake"],2),
      ("v11D05","How was the night?",["Warm and happy","Boring","Tiring"],0),
    ],
  },
  "E": {
    "read": ("We watched the full moon and ate mooncakes together.",
             "watched the /wɒtʃt ðə/；and ate /ən eɪt/ 弱读。"),
    "answer": ["Which festival do you like best? Why?",
               "What do you usually do during the Spring Festival?",
               "What traditional food does your family eat on festivals?"],
    "describe": ("Describe your favorite festival.",
      "My favorite festival is the Spring Festival. My family gets together and has a big dinner. We eat "
      "dumplings and watch TV. My grandparents give me red envelopes. We visit relatives and say happy new "
      "year to them. I love this festival because everyone is happy."),
  },
  "words_extra": [
    ("mooncake","/ˈmuːnkeɪk/","n.","月饼","D","课标"),
    ("red envelope","/ˌred ˈenvələʊp/","n.","红包","C4/D","课标"),
    ("dragon dance","/ˈdræɡən dɑːns/","n.","舞龙","C5","拓展"),
  ],
})

# ============ 卷12 交通与出行 ============
VOLS.append({
  "vid": "v12", "title": "试卷12（交通与出行）", "topic": "交通与出行", "mainTrap": "数字计算",
  "A": [
    A("v12A01","traffic",["交通","火车","贸易"],0,"课标","/ˈtræfɪk/","交通"),
    A("v12A02","bus",["出租车","公共汽车","火车"],1,"课标","/bʌs/","公共汽车"),
    A("v12A03","subway",["潜艇","地铁","郊外"],1,"课标","/ˈsʌbweɪ/","地铁"),
    A("v12A04","direction",["导演","数字","方向"],2,"课标","/dəˈrekʃn/","方向"),
    A("v12A05","passenger",["护照","乘客","段落"],1,"课标","/ˈpæsɪndʒə(r)/","乘客"),
    A("v12A06","fare",["公平","害怕","车费"],2,"课标","/feə(r)/","车费"),
    A("v12A07","turn",["转弯","调音","隧道"],0,"课标","/tɜːn/","转弯",'v./n.'),
    A("v12A08","cross",["课程","王冠","穿过"],2,"课标","/krɒs/","穿过",'v.'),
    A("v12A09","straight",["奇怪的","径直的","强壮的"],1,"课标","/streɪt/","径直的",'adj./adv.'),
    A("v12A10","traffic light",["路灯","灯塔","交通灯"],2,"拓展","/ˈtræfɪk laɪt/","交通灯"),
  ],
  "B": [
    B("v12B01","Excuse me, how can I get to the train station?",["It's far away.","Go straight and turn left.","Thank you."],1),
    B("v12B02","How do you usually go to school?",["By bike.","It's near.","I like it."],0),
    B("v12B03","How long does it take to get to the airport?",["About half an hour.","It's expensive.","On the bus."],0),
    B("v12B04","Which bus goes to the museum?",["It's blue.","In the morning.","The No. 5 bus."],2),
    B("v12B05","Is the park far from here?",["No, it's just around the corner.","Yes, I am.","It's closed."],0),
  ],
  "C": [
    C("v12C01",["M: I take the subway to school.","W: My sister takes the bus."],
      "How does the girl's sister go to school?",["By subway","By bus","On foot"],1,"张冠李戴",
      "问女生的妹妹，答案在她的话里（sister takes the bus）。"),
    C("v12C02",["W: The bus fare is 2 yuan. I take it twice a day."],
      "How much does she spend on the bus every day?",["2 yuan","4 yuan","8 yuan"],1,"数字计算",
      "2×2=4，需做乘法。"),
    C("v12C03",["M: We planned to ride bikes to the park, but it started raining, so we took a taxi instead."],
      "How did they go to the park?",["By bike","By taxi","On foot"],1,"转折后取义",
      "but 之后才是真实方式。"),
    C("v12C04",["W: I hate waiting for the bus in the rain!","M: Don't worry, it's coming."],
      "How does the girl feel?",["Happy","Angry / annoyed","Excited"],1,"态度推断",
      "hate waiting in the rain → 烦躁、生气。"),
    C("v12C05",["M: Next stop is the Central Library. Please get ready.","W: OK, let's move to the door."],
      "Where are they?",["On a bus","In a library","In a car"],0,"地点身份",
      "next stop + get ready → 在公交车/地铁上。"),
  ],
  "D": {
    "passage": ("Every day I go to school by bus. The bus stop is near my home, so I walk there in about five "
      "minutes. The bus ride takes twenty minutes. I usually get on the bus at 7:15 and arrive at school at "
      "7:35. Sometimes the traffic is heavy, and I am late. Last week, I missed the bus, so I took the subway "
      "instead. It was faster. Now I always leave home ten minutes earlier."),
    "qs": [
      ("v12D01","How does he go to school every day?",["By subway","By bus","On foot"],1),
      ("v12D02","How long does he walk to the bus stop?",["Twenty minutes","Five minutes","Ten minutes"],1),
      ("v12D03","What time does he arrive at school?",["7:15","7:35","7:50"],1),
      ("v12D04","What happened last week?",["He was ill","He walked to school","He missed the bus and took the subway"],2),
      ("v12D05","What does he do now?",["Take the subway every day","Leave home ten minutes earlier","Ride a bike"],1),
    ],
  },
  "E": {
    "read": ("Go straight ahead and turn right at the second crossing.",
             "turn right /tɜːn raɪt/；at the /æt ðə/ 弱读。"),
    "answer": ["How do you usually go to school?",
               "Can you tell me the way to your school?",
               "Do you like taking the subway or the bus? Why?"],
    "describe": ("Describe your way to school.",
      "I go to school by bus every day. I walk to the bus stop in five minutes. The bus ride takes about "
      "twenty minutes. I usually leave home at 7:00. I like taking the bus because I can read on the way. "
      "Sometimes the traffic is heavy, but I am never late."),
  },
  "words_extra": [
    ("crossing","/ˈkrɒsɪŋ/","n.","十字路口","E1","课标"),
    ("airport","/ˈeəpɔːt/","n.","机场","B3","课标"),
    ("taxi","/ˈtæksi/","n.","出租车","C3","课标"),
  ],
})

# ============ 卷13 运动与文娱 ============
VOLS.append({
  "vid": "v13", "title": "试卷13（运动与文娱）", "topic": "运动与文娱", "mainTrap": "态度推断",
  "A": [
    A("v13A01","sport",["港口","运动","支持"],1,"课标","/spɔːt/","运动"),
    A("v13A02","team",["茶叶","团队","汤"],1,"课标","/tiːm/","团队"),
    A("v13A03","match",["手表","比赛","数学"],1,"课标","/mætʃ/","比赛"),
    A("v13A04","win",["赢","风","翅膀"],0,"课标","/wɪn/","赢",'v.'),
    A("v13A05","lose",["放松","灯笼","输/丢失"],2,"课标","/luːz/","输；丢失",'v.'),
    A("v13A06","player",["选手","平原","祈祷"],0,"课标","/ˈpleɪə(r)/","选手"),
    A("v13A07","cinema",["相机","电影院","厨房"],1,"课标","/ˈsɪnəmə/","电影院"),
    A("v13A08","stage",["舞台","状态","车站"],0,"课标","/steɪdʒ/","舞台"),
    A("v13A09","drama",["梦想","戏剧","相机"],1,"拓展","/ˈdrɑːmə/","戏剧"),
    A("v13A10","audience",["观众","音频","作者"],0,"拓展","/ˈɔːdiəns/","观众"),
  ],
  "B": [
    B("v13B01","What sport do you like?",["It's Monday.","I like playing basketball.","I'm fine."],1),
    B("v13B02","Did you watch the football match last night?",["Yes, it was exciting.","It's late.","No, I'm a player."],0),
    B("v13B03","How often do you play sports?",["For two hours.","Twice a week.","In the park."],1),
    B("v13B04","Would you like to go to the cinema with me?",["Sure, I'd love to.","It's a film.","Here you are."],0),
    B("v13B05","How was the concert?",["It's a concert.","At 8 p.m.","It was wonderful."],2),
  ],
  "C": [
    C("v13C01",["M: Tom plays basketball on Mondays.","W: I play tennis on Wednesdays."],
      "What does Tom play on Mondays?",["Tennis","Basketball","Football"],1,"张冠李戴",
      "问 Tom，答案在男生的话里（basketball），女生说的是自己。"),
    C("v13C02",["W: The basketball team scored 60 points. The other team scored 45."],
      "How many more points did their team score?",["60","45","15"],2,"数字计算",
      "60-45=15，需做减法。"),
    C("v13C03",["M: I wanted to go to the concert, but the tickets were sold out, so I watched a live show online."],
      "What did the boy do?",["Went to the concert","Watched a live show online","Stayed at home"],1,"转折后取义",
      "but 之后才是真实发生的。"),
    C("v13C04",["W: I'm so proud of our team! We won the final match!","M: Great job!"],
      "How does the girl feel?",["Proud and excited","Sad","Bored"],0,"态度推断",
      "proud + won the final → 自豪兴奋。"),
    C("v13C05",["M: Please show me your ticket. Your seat is in Row 8.","W: OK, thank you."],
      "Where are they?",["In a cinema / theatre","In a library","At a bus stop"],0,"地点身份",
      "ticket + seat + Row → 影院/剧院。"),
  ],
  "D": {
    "passage": ("My favorite sport is swimming. I started swimming three years ago. I go to the swimming pool "
      "twice a week, on Tuesday and Friday. My coach says I swim very fast. Last month, our school held a "
      "swimming match. I took part in it and won the second prize. I was very happy. My parents were proud of "
      "me. I think doing sports is good for our health, and I will keep swimming."),
    "qs": [
      ("v13D01","What is the speaker's favorite sport?",["Running","Swimming","Basketball"],1),
      ("v13D02","How often does he swim?",["Every day","Twice a week","Once a week"],1),
      ("v13D03","What prize did he win?",["First prize","Third prize","Second prize"],2),
      ("v13D04","How did his parents feel?",["Angry","Worried","Proud"],2),
      ("v13D05","What does he think of doing sports?",["Good for health","A waste of time","Too tiring"],0),
    ],
  },
  "E": {
    "read": ("Doing sports every day is good for our health.",
             "every day /ˈevri deɪ/；good for /ɡʊd fə/ 弱读。"),
    "answer": ["What sport do you like best? Why?",
               "How often do you do sports?",
               "Do you prefer watching matches or playing sports? Why?"],
    "describe": ("Describe a sports match or show you watched.",
      "Last week I watched a basketball match between our school team and another school. The game was "
      "exciting. Our team scored 60 points and won. The players ran very fast. Everyone shouted and cheered. "
      "I felt very proud of our team. I hope we can watch more matches."),
  },
  "words_extra": [
    ("coach","/kəʊtʃ/","n.","教练","D","课标"),
    ("prize","/praɪz/","n.","奖品","D","课标"),
    ("cheer","/tʃɪə(r)/","v.","欢呼","E3","课标"),
  ],
})

# ============ 卷14 安全与救护 ============
VOLS.append({
  "vid": "v14", "title": "试卷14（安全与救护）", "topic": "安全与救护", "mainTrap": "地点身份",
  "A": [
    A("v14A01","safety",["盐","安全","悲伤"],1,"课标","/ˈseɪfti/","安全"),
    A("v14A02","danger",["舞蹈","危险","晚餐"],1,"课标","/ˈdeɪndʒə(r)/","危险"),
    A("v14A03","careful",["照看","胡萝卜","小心的"],2,"课标","/ˈkeəfl/","小心的",'adj.'),
    A("v14A04","accident",["账户","事故","祖先"],1,"课标","/ˈæksɪdənt/","事故"),
    A("v14A05","fire",["远处","寓言","火"],2,"课标","/ˈfaɪə(r)/","火"),
    A("v14A06","rescue",["营救","资源","结果"],0,"课标","/ˈreskjuː/","营救",'v./n.'),
    A("v14A07","ambulance",["大使","墓穴","救护车"],2,"拓展","/ˈæmbjələns/","救护车"),
    A("v14A08","emergency",["出现","紧急情况","娱乐"],1,"拓展","/iˈmɜːdʒənsi/","紧急情况"),
    A("v14A09","helmet",["帮助","头盔","蜂蜜"],1,"课标","/ˈhelmɪt/","头盔"),
    A("v14A10","rule",["尺子","规则","角色"],1,"课标","/ruːl/","规则"),
  ],
  "B": [
    B("v14B01","What should we do in a fire?",["It's hot.","Call 119 and leave quickly.","Go to sleep."],1),
    B("v14B02","Be careful! The floor is wet.",["It's wet.","Thank you for telling me.","I'm fine."],1),
    B("v14B03","How can we keep safe on the road?",["Follow the traffic rules.","By bus.","It's safe."],0),
    B("v14B04","What happened to him?",["He is a student.","It's OK.","He fell down and hurt his leg."],2),
    B("v14B05","Should we wear a helmet when riding a bike?",["No, we won't.","Yes, we should.","It's a helmet."],1),
  ],
  "C": [
    C("v14C01",["W: Tom broke his arm.","M: And Lily cut her finger."],
      "What happened to Tom?",["He broke his arm","She cut her finger","He is fine"],0,"张冠李戴",
      "问 Tom，答案在女生的话里（Tom broke his arm）。"),
    C("v14C02",["M: The medicine is 15 yuan. The bandage is 5 yuan."],
      "How much do they cost in total?",["15 yuan","5 yuan","20 yuan"],2,"数字计算",
      "15+5=20，需做加法。"),
    C("v14C03",["W: I wanted to cross the road, but the light was red, so I waited."],
      "What did the girl do?",["Crossed the road","Waited for the green light","Ran across"],1,"转折后取义",
      "but 之后才是真实做法。"),
    C("v14C04",["M: Thank you so much for helping me when I fell!","W: That's what friends are for."],
      "How does the boy feel?",["Thankful","Angry","Sad"],0,"态度推断",
      "thank you so much → 感激。"),
    C("v14C05",["M: Quick! Take him to the emergency room! He is bleeding!","W: OK, this way!"],
      "Where are they?",["In a hospital","At school","In a shop"],0,"地点身份",
      "emergency room + bleeding → 医院。"),
  ],
  "D": {
    "passage": ("Yesterday afternoon, I saw an accident on my way home. A boy fell off his bike at the crossing. "
      "He hurt his knee and it was bleeding. I stopped and called 120. A few minutes later, an ambulance came. "
      "The doctors took him to the hospital. I waited with him until his parents arrived. His parents thanked "
      "me a lot. I was a little scared, but I was happy that I helped him."),
    "qs": [
      ("v14D01","When did the speaker see the accident?",["Last night","Yesterday afternoon","This morning"],1),
      ("v14D02","What happened to the boy?",["He was hit by a car","He fell off his bike","He felt ill"],1),
      ("v14D03","What number did the speaker call?",["110","120","119"],1),
      ("v14D04","Who came to help?",["Doctors in an ambulance","His teacher","The police"],0),
      ("v14D05","How did the speaker feel?",["Angry","Bored","Scared but happy"],2),
    ],
  },
  "E": {
    "read": ("If you see an accident, call 120 and wait for help.",
             "If you /ɪf ju/ 弱读；wait for /weɪt fə/ 弱读。"),
    "answer": ["What should we do when we see a fire?",
               "How do you keep safe when crossing the road?",
               "Have you ever helped someone in danger? What did you do?"],
    "describe": ("Describe what you do to keep safe at school or on the road.",
      "I always follow the traffic rules. When I cross the road, I wait for the green light and look left and "
      "right. At school, I don't run in the hallway. If I see an accident, I call 120 or ask an adult for "
      "help. Safety is very important, so we should be careful every day."),
  },
  "words_extra": [
    ("bandage","/ˈbændɪdʒ/","n.","绷带","C2","课标"),
    ("bleed","/bliːd/","v.","流血","D","课标"),
    ("knee","/niː/","n.","膝盖","D","课标"),
  ],
})

# ============ 卷15 社区与居住 ============
VOLS.append({
  "vid": "v15", "title": "试卷15（社区与居住）", "topic": "社区与居住", "mainTrap": "转折后取义",
  "A": [
    A("v15A01","community",["委员会","社区","通信"],1,"课标","/kəˈmjuːnəti/","社区"),
    A("v15A02","building",["桥","楼房","篮子"],1,"课标","/ˈbɪldɪŋ/","楼房"),
    A("v15A03","street",["邮票","力量","街道"],2,"课标","/striːt/","街道"),
    A("v15A04","elevator",["电梯","生命","离开"],0,"课标","/ˈelɪveɪtə(r)/","电梯"),
    A("v15A05","quiet",["报价","安静的","快速的"],1,"课标","/ˈkwaɪət/","安静的",'adj.'),
    A("v15A06","convenient",["会议","方便的","内容"],1,"课标","/kənˈviːniənt/","方便的",'adj.'),
    A("v15A07","service",["服务","服务器","努力"],0,"课标","/ˈsɜːvɪs/","服务"),
    A("v15A08","post",["海报","位置","邮政/邮寄"],2,"课标","/pəʊst/","邮政；邮寄",'v./n.'),
    A("v15A09","market",["标记","音乐","市场"],2,"课标","/ˈmɑːkɪt/","市场"),
    A("v15A10","neighborhood",["邻居","噪音","街坊/社区"],2,"拓展","/ˈneɪbəhʊd/","街坊；社区"),
  ],
  "B": [
    B("v15B01","Where do you live?",["I'm at home.","I live in a tall building near the park.","It's small."],1),
    B("v15B02","Is there a supermarket near your home?",["No, I'm not.","Yes, it's just around the corner.","It's open."],1),
    B("v15B03","How long have you lived here?",["Five kilometers.","At five o'clock.","For five years."],2),
    B("v15B04","Do you like your neighborhood?",["Yes, it's quiet and convenient.","It's a neighborhood.","I live here."],0),
    B("v15B05","What can we do for our community?",["It's nice.","We can clean the park together.","Next door."],1),
  ],
  "C": [
    C("v15C01",["W: Mr. Li lives on the third floor.","M: And Mrs. Wang lives on the fifth floor."],
      "Who lives on the third floor?",["Mrs. Wang","Mr. Li","Nobody"],1,"张冠李戴",
      "问谁住三楼，答案在女生的话里（Mr. Li）。"),
    C("v15C02",["M: There are 6 buildings in our community. Each has 10 floors."],
      "How many floors are there in total?",["6","10","60"],2,"数字计算",
      "6×10=60，需做乘法。"),
    C("v15C03",["W: I wanted to live in the city center, but it was too noisy, so I moved to the quiet suburb."],
      "Where does the girl live now?",["In the city center","In the quiet suburb","In a village"],1,"转折后取义",
      "but 之后才是真实选择。"),
    C("v15C04",["M: Our community is getting better! We now have a new library and a garden.","W: Yes, I really enjoy living here!"],
      "How do they feel about the community?",["Satisfied and happy","Angry","Bored"],0,"态度推断",
      "getting better + enjoy living here → 满意高兴。"),
    C("v15C05",["W: I'd like to post this letter, please.","M: Sure, it will arrive in about three days."],
      "Where are they?",["At the post office","At school","In a bank"],0,"地点身份",
      "post this letter + arrive in three days → 邮局。"),
  ],
  "D": {
    "passage": ("I live in a small community called Sunny Garden. There are five buildings and a big garden in "
      "the middle. My home is on the fourth floor of Building 2. The community is very quiet and clean. Near "
      "my home, there is a supermarket, a post office and a bus stop. It takes me only ten minutes to walk to "
      "school. My neighbors are very friendly. Sometimes we have parties in the garden. I love my community "
      "very much."),
    "qs": [
      ("v15D01","What is the name of the community?",["Green Park","Sunny Garden","Happy Home"],1),
      ("v15D02","Where is the speaker's home?",["Building 5, fourth floor","Building 2, second floor","Building 2, fourth floor"],2),
      ("v15D03","How long does it take to walk to school?",["Twenty minutes","Ten minutes","Five minutes"],1),
      ("v15D04","What do the neighbors do sometimes?",["Travel together","Have parties in the garden","Go shopping"],1),
      ("v15D05","How does the speaker feel about the community?",["Wants to move","Is bored","Loves it"],2),
    ],
  },
  "E": {
    "read": ("My neighborhood is quiet and convenient for shopping.",
             "convenient for /kənˈviːniənt fə/；for shopping /fə ˈʃɒpɪŋ/ 弱读。"),
    "answer": ["Where do you live?",
               "What is your neighborhood like?",
               "What do you like most about your community?"],
    "describe": ("Describe your home or neighborhood.",
      "I live in a tall building near a big park. My neighborhood is quiet and clean. There is a supermarket "
      "and a bus stop near my home. My neighbors are friendly. We often help each other. On weekends, I walk "
      "in the park with my family. I like my neighborhood very much."),
  },
  "words_extra": [
    ("suburb","/ˈsʌbɜːb/","n.","郊区","C3","拓展"),
    ("noisy","/ˈnɔɪzi/","adj.","吵闹的","C3","课标"),
    ("post office","/ˈpəʊst ɒfɪs/","n.","邮局","C5/D","课标"),
  ],
})

# ============ 卷16 学习与考试 ============
VOLS.append({
  "vid": "v16", "title": "试卷16（学习与考试）", "topic": "学习与考试", "mainTrap": "全陷阱混编",
  "A": [
    A("v16A01","study",["学生","学习","站立"],1,"课标","/ˈstʌdi/","学习",'v./n.'),
    A("v16A02","quiz",["测验","困惑","安静"],0,"课标","/kwɪz/","小测验"),
    A("v16A03","review",["反转","复习","评论"],1,"课标","/rɪˈvjuː/","复习",'v./n.'),
    A("v16A04","knowledge",["知道","刀","知识"],2,"课标","/ˈnɒlɪdʒ/","知识"),
    A("v16A05","lesson",["少","课程","课桌"],1,"课标","/ˈlesn/","课程"),
    A("v16A06","notebook",["注意","面条","笔记本"],2,"课标","/ˈnəʊtbʊk/","笔记本"),
    A("v16A07","improve",["证明","进口","提高"],2,"课标","/ɪmˈpruːv/","提高",'v.'),
    A("v16A08","practice",["奖品","练习","骄傲"],1,"课标","/ˈpræktɪs/","练习",'v./n.'),
    A("v16A09","score",["楼梯","商店","分数"],2,"课标","/skɔː(r)/","分数"),
    A("v16A10","progress",["项目","进步","过程"],1,"拓展","/ˈprəʊɡres/","进步"),
  ],
  "B": [
    B("v16B01","How was your English exam?",["It's an exam.","Not bad, I did well.","I'm a student."],1),
    B("v16B02","What do you usually do after class?",["I'm tired.","I review the lessons and do homework.","It's late."],1),
    B("v16B03","Can I borrow your dictionary?",["Sure, here you are.","Yes, I am.","It's a book."],0),
    B("v16B04","Do you like studying English?",["Yes, but it takes time.","No, I don't study.","It's English."],0),
    B("v16B05","How can I improve my spoken English?",["Read a book.","Practice speaking every day.","It's hard."],1),
  ],
  "C": [
    C("v16C01",["M: Lily got 95 in math.","W: Tom got 90 in English."],
      "What score did Lily get in math?",["90","95","85"],1,"张冠李戴",
      "问 Lily 的数学分，答案在男生的话里（Lily got 95）。"),
    C("v16C02",["W: I spent 2 hours on homework and 1 hour on review last night."],
      "How many hours did she study in total?",["2 hours","1 hour","3 hours"],2,"数字计算",
      "2+1=3，需做加法。"),
    C("v16C03",["M: I planned to study for the exam, but my friend asked me to play, so I studied early this morning instead."],
      "What did the boy do this morning?",["Played with his friend","Studied for the exam","Slept late"],1,"转折后取义",
      "but 之后才是真实安排（今天早上补学）。"),
    C("v16C04",["W: I'm really nervous about tomorrow's math exam.","M: Take it easy, you have prepared well."],
      "How does the girl feel?",["Nervous","Excited","Bored"],0,"态度推断",
      "really nervous → 紧张。"),
    C("v16C05",["M: Please open your books to page 20 and read after me.","W: OK, teacher."],
      "Where are they?",["In a classroom","In a library","At home"],0,"地点身份",
      "open your books + read after me + teacher → 教室。"),
  ],
  "D": {
    "passage": ("English is my favorite subject. I have studied it for five years. To improve my English, I do "
      "three things every day. First, I read English for twenty minutes in the morning. Second, I listen to "
      "English songs on my way to school. Third, I write a short diary in English every night. Last month, I "
      "got 92 in the English test, the highest score in my class. My teacher praised me in front of the class. "
      "I was very happy. I will keep working hard."),
    "qs": [
      ("v16D01","How long has he studied English?",["Three years","Five years","One year"],1),
      ("v16D02","What does he do in the morning?",["Listen to songs","Write a diary","Read English"],2),
      ("v16D03","What did he get in the English test?",["90","82","92"],2),
      ("v16D04","Who praised him?",["His parents","His teacher","His friends"],1),
      ("v16D05","How does he feel?",["Sad","Happy","Tired"],1),
    ],
  },
  "E": {
    "read": ("I practice speaking English with my classmates every day.",
             "practice speaking /ˈpræktɪs ˈspiːkɪŋ/；with my /wɪð maɪ/ 弱读。"),
    "answer": ["What is your favorite subject? Why?",
               "How do you improve your English?",
               "What do you do before an exam?"],
    "describe": ("Describe your way of learning English.",
      "I learn English in many ways. I read English books for twenty minutes every morning. I listen to English "
      "songs and watch English cartoons. I write new words in my notebook and review them every weekend. My "
      "teacher says practice makes perfect. I will keep learning and never give up."),
  },
  "words_extra": [
    ("praise","/preɪz/","v.","表扬","D","课标"),
    ("diary","/ˈdaɪəri/","n.","日记","D","课标"),
    ("perfect","/ˈpɜːfɪkt/","adj.","完美的","E3","课标"),
  ],
})

TRAP_ORDER = ["张冠李戴", "数字计算", "转折后取义", "态度推断", "地点身份"]

# ---------- 渲染：试卷 md ----------
def render_paper(v):
    no = v["vid"][1:]
    L = []
    L.append(f"# 中考听说专项 · 试卷{no}（{v['topic']}）\n")
    L.append("> 产出岗位：3号｜内容交付专员")
    L.append("> 依据方案：02产品方案库/听说题库方案/中考英语听说专项题库方案.md")
    L.append(f"> 话题：{v['topic']}　主攻陷阱：{v['mainTrap']}")
    L.append("> 日期：2026-09-27")
    L.append("> ⚠️ **待创始人人工校对**：AI 生成英语内容存在出错概率，以下答案/拼写/考点请逐题复核。\n")
    L.append("---\n")
    L.append("## Part A　单词听力（10 题 × 1 分）")
    L.append("*听录音，选出你所听到单词的正确中文意思。*\n")
    for i, a in enumerate(v["A"], 1):
        opts = "　".join(f"{chr(65+j)}. {o}" for j, o in enumerate(a["options"]))
        L.append(f"{i}. {a['word']}　{opts}")
    ext = [a for a in v["A"] if a["level"] == "拓展"]
    if ext:
        L.append("")
        L.append("> 解析：" + "、".join(f"{i+1}" for i, a in enumerate(v["A"]) if a["level"] == "拓展")
                 + " 为略难词，建议在生词表标「拓展」并附释义。")
    L.append("\n---\n")
    L.append("## Part B　短句听力（5 题 × 1 分）")
    L.append("*听录音，选出最合适的应答语。*\n")
    for i, b in enumerate(v["B"], 1):
        opts = "　".join(f"{chr(65+j)}. {o}" for j, o in enumerate(b["options"]))
        L.append(f"{i}. — {b['sent']}")
        L.append(f"　{opts}")
    L.append("\n---\n")
    L.append("## Part C　对话听力（5 组 × 2 分）★核心陷阱题")
    L.append("*听对话，选择正确答案。每题对应一种设题陷阱。*\n")
    for i, c in enumerate(v["C"], 1):
        L.append(f"**【陷阱{i}·{c['trap']}】**")
        for t in c["turns"]:
            L.append(t)
        L.append(f"Q: {c['q']}")
        opts = "　".join(f"{chr(65+j)}. {o}" for j, o in enumerate(c["options"]))
        L.append(opts)
        L.append(f"*解析：{c['analysis']}*\n")
    L.append("---\n")
    L.append("## Part D　篇章听力（1 篇 / 5 题 × 2 分）")
    L.append("*听一段独白，回答问题。*\n")
    L.append("**录音文本（独白）**")
    L.append(f"\"{v['D']['passage']}\"\n")
    for i, (qid, q, opts, ans) in enumerate(v["D"]["qs"], 1):
        L.append(f"{i}. {q}")
        L.append("　" + "　".join(f"{chr(65+j)}. {o}" for j, o in enumerate(opts)))
    L.append("\n---\n")
    L.append("## Part E　口语输出（3 任务 × 5 分）")
    L.append("**Task 1　跟读（朗读下列句子，注意连读弱读）**")
    L.append(f"> \"{v['E']['read'][0]}\"")
    L.append(f"> *提示：{v['E']['read'][1]}*\n")
    L.append("**Task 2　情景问答（听问题，口头回答，每题 1 句即可）**")
    for i, q in enumerate(v["E"]["answer"], 1):
        L.append(f"{i}. {q}")
    L.append("")
    L.append("**Task 3　话题简述（准备 30 秒，说 5–6 句）**")
    L.append(f"> 话题：{v['E']['describe'][0]}")
    L.append(f"> *范例（sample）：{v['E']['describe'][1]}*")
    L.append("")
    L.append("**评分维度（rubric，各 5 分）**：内容完整 / 发音准确 / 表达流畅。\n")
    L.append("---\n")
    L.append("## 答案速查（⚠️ 创始人请逐题复核）")
    def ansline(items):
        return " ".join(f"{i}.{chr(65+ans)}" for i, (_, _, _, ans) in enumerate(items, 1))
    L.append("- Part A：" + " ".join(f"{i}.{chr(65 + a['answer'])}" for i, a in enumerate(v["A"], 1)))
    L.append("- Part B：" + " ".join(f"{i}.{chr(65 + b['answer'])}" for i, b in enumerate(v["B"], 1)))
    L.append("- Part C：" + " ".join(f"{i}.{chr(65 + c['answer'])}" for i, c in enumerate(v["C"], 1)))
    L.append(f"- Part D：{ansline(v['D']['qs'])}")
    L.append("- Part E：开放题，参考 Task3 范例与 rubric 评分。\n")
    L.append("> 内容交付专员提醒：以上英语文本、答案、拼写、数字计算均建议创始人人工校对后再上线。")
    return "\n".join(L) + "\n"

# ---------- 渲染：音频脚本与生词表 md ----------
def render_audio_md(v):
    no = v["vid"][1:]
    L = []
    L.append(f"# 中考听说专项·试卷{no} — 音频脚本册 + 生词表\n")
    L.append("> 产出岗位：3号｜内容交付专员")
    L.append(f"> 配套：中考听说专项-试卷{no}.md")
    L.append("> 用途：供 TTS / 真人录制；录制规格 44.1kHz、单声道、MP3。")
    L.append("> ⚠️ 待创始人校对英文文本与连读弱读标注。\n")
    L.append("---\n")
    L.append("## 一、音频脚本（逐题）\n")
    L.append("### Part A 单词听力（只读单词，每词间隔 3 秒）")
    L.append("| 题号 | 英文 | 连读弱读/读音提示 |")
    L.append("|---|---|---|")
    for i, a in enumerate(v["A"], 1):
        tag = " 拓展词" if a["level"] == "拓展" else ""
        L.append(f"| {i} | {a['word']} | {a['ipa']}{tag} |")
    L.append("\n### Part B 短句听力（每句读两遍）")
    hints = {"How": "How do you /ˈhaʊ də ju/ 弱读", "Can I": "Can I /kæn aɪ/ 连读", "Would": "Would you /ˈwʊdʒə/",
             "Do you": "Do you /dʒə/ 弱读", "What do you": "What do you /ˈwɒt də ju/", "Happy": "my friend /maɪ frend/ 连读",
             "Why": "Why do you /ˈwaɪ də ju/", "How often": "How often /ˈhaʊ ɒfn/", "What's": "What's /wɒts/",
             "Is your": "Is your /ɪz jɔː/ 连读"}
    for i, b in enumerate(v["B"], 1):
        key = next((k for k in hints if b["sent"].startswith(k)), None)
        hint = "；".join([hints[key]] if key else [])
        L.append(f"{i}. {b['sent']} → *{hint}*")
    L.append("\n### Part C 对话听力（男女声各一，间隔 5 秒后读题）")
    for c in v["C"]:
        L.append("- " + "  ".join(c["turns"]))
    L.append("\n### Part D 篇章听力（独白，正常语速 ~110wpm）")
    L.append(f"\"{v['D']['passage']}\"")
    L.append("\n### Part E 口语输出")
    L.append(f"- Task1 跟读句：{v['E']['read'][0]}")
    L.append("- Task2/3 为考生口述，无需录音播放，仅给题干与范例。\n")
    L.append("---\n")
    L.append("## 二、连读弱读标注汇总（教学用）")
    L.append("| 现象 | 原句 | 口语实际 |")
    L.append("|---|---|---|")
    L.append("| 弱读 you | Could you / Would you / do you | /kʊdʒə/ /wʊdʒə/ /dʒə/ |")
    L.append("| 弱读 to | want to / like to | /wɒntə/ /laɪktə/ |")
    L.append("| 弱读 the | on the / in the / of the | /ɒn ðə/ /ɪn ðə/ /əv ðə/ |")
    L.append("| 连读 | get up / has 120 | /ɡetʌp/ 两词粘连 |")
    L.append("\n---\n")
    L.append("## 三、生词表（字段：单词 / 音标 / 词性 / 中文 / 所在题号 / 级别）")
    L.append("| 单词 | 音标 | 词性 | 中文 | 题号 | 级别 |")
    L.append("|---|---|---|---|---|---|")
    for a in v["A"]:
        L.append(f"| {a['word']} | {a['ipa']} | {a['pos']} | {a['cn']} | A{v['A'].index(a)+1} | {a['level']} |")
    for w, ipa, pos, cn, qid, lv in v["words_extra"]:
        L.append(f"| {w} | {ipa} | {pos} | {cn} | {qid} | {lv} |")
    L.append("")
    L.append(f"> 提示：拓展词（{' / '.join(a['word'] for a in v['A'] if a['level'] == '拓展')}）建议在试卷中标注「拓展」并附释义，避免超纲争议。")
    return "\n".join(L) + "\n"

# ---------- 渲染：追加 quiz.json 的 volume ----------
def to_quiz_volume(v):
    parts = []
    parts.append({"part": "A", "name": "单词听力", "type": "word_listen", "questions": [
        {"id": a["id"], "part": "A", "audio": a["word"], "question": "听录音，选出单词的正确中文意思",
         "options": a["options"], "answer": a["answer"], "level": a["level"]} for a in v["A"]]})
    parts.append({"part": "B", "name": "短句听力", "type": "sentence_listen", "questions": [
        {"id": b["id"], "part": "B", "audio": b["sent"], "question": "听录音，选出最合适的应答语",
         "options": b["options"], "answer": b["answer"]} for b in v["B"]]})
    parts.append({"part": "C", "name": "对话听力（核心陷阱）", "type": "dialogue_listen", "questions": [
        {"id": c["id"], "part": "C", "audio": c["turns"], "question": c["q"], "options": c["options"],
         "answer": c["answer"], "trap": c["trap"], "analysis": c["analysis"]} for c in v["C"]]})
    parts.append({"part": "D", "name": "篇章听力", "type": "passage_listen", "audio": v["D"]["passage"],
        "questions": [
            {"id": qid, "part": "D", "audio": "", "question": q, "options": opts, "answer": ans}
            for qid, q, opts, ans in v["D"]["qs"]]})
    tasks = [
        {"id": v["vid"] + "E01", "type": "read", "content": v["E"]["read"][0], "note": v["E"]["read"][1]},
        {"id": v["vid"] + "E02", "type": "answer", "questions": v["E"]["answer"]},
        {"id": v["vid"] + "E03", "type": "describe", "topic": v["E"]["describe"][0],
         "sample": v["E"]["describe"][1], "rubric": ["内容完整", "发音准确", "表达流畅"]},
    ]
    parts.append({"part": "E", "name": "口语输出", "type": "speaking", "tasks": tasks})
    return {"id": v["vid"], "title": v["title"], "topic": v["topic"], "mainTrap": v["mainTrap"],
            "totalScore": 50, "parts": parts}

def main():
    # 1) 写 md
    for v in VOLS:
        no = v["vid"][1:]
        with open(os.path.join(MD_DIR, f"中考听说专项-试卷{no}.md"), "w", encoding="utf-8") as f:
            f.write(render_paper(v))
        with open(os.path.join(MD_DIR, f"中考听说专项-试卷{no}-音频脚本与生词表.md"), "w", encoding="utf-8") as f:
            f.write(render_audio_md(v))
    print(f"md 已写入 {MD_DIR}（{len(VOLS)*2} 个文件）")

    # 2) 写分卷 JSON（素材库）
    for v in VOLS:
        vol = to_quiz_volume(v)
        with open(os.path.join(JSON_DIR, f"中考听说专项-试卷{vol['id'][1:]}-{v['topic']}.json"), "w", encoding="utf-8") as f:
            json.dump({"product": "中考英语听说专项题库", "version": "1.0", "volumes": [vol]}, f,
                      ensure_ascii=False, indent=2)
    print(f"分卷 JSON 已写入 {JSON_DIR}")

    # 3) 追加 szgaokao-web/data/quiz.json（audio 字段为文本，等待 gen_audio.py 回填路径）
    qpath = os.path.join(DATA, "quiz.json")
    quiz = json.load(open(qpath, encoding="utf-8"))
    existing = {v["id"] for v in quiz["volumes"]}
    new_vols = [to_quiz_volume(v) for v in VOLS if v["vid"] not in existing]
    if not new_vols:
        print("quiz.json 已包含全部新卷，跳过追加")
        return
    quiz["volumes"].extend(new_vols)
    with open(qpath, "w", encoding="utf-8") as f:
        json.dump(quiz, f, ensure_ascii=False, indent=2)
    print(f"quiz.json 已追加 {len(new_vols)} 卷 → 共 {len(quiz['volumes'])} 卷")

if __name__ == "__main__":
    main()
