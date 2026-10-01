# -*- coding: utf-8 -*-
# PET 听说模拟练习（剑桥 B1 Preliminary）4 卷 × 12 题，五大题型
# 音频命名 /audio/px/px{vol}-{no}.mp3；题 id px1a01...
import json, os, subprocess, re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
AUD = os.path.join(BASE, "public", "audio", "px")

def Q(vol, no, qtype, q, audio_text, options, answer, tip, subs=None):
    d = {"id": "%s%02d" % (vol, no), "type": qtype, "q": q, "audio": "/audio/px/%s%02d.mp3" % (vol, no),
         "audio_text": audio_text, "options": options, "answer": answer, "tip": tip}
    if subs:
        d["questions"] = subs
    return d

def build_volumes():
    vols = []
    # —— 卷一：教育与社会 ——
    v = {"id": "px1a", "title": "PET 模拟卷一 · 教育与社会", "topic": "教育 · 社会 · 公共事务", "questions": [
        Q("px1a", 1, "word", "听单词，选出正确的中文意思", "environment", ["环境", "政府", "教育"], 0, "environment = 环境，注意重音在第二个音节。"),
        Q("px1a", 2, "word", "听单词，选出正确的中文意思", "opportunity", ["机会", "困难", "责任"], 0, "opportunity = 机会，复数 opportunities。"),
        Q("px1a", 3, "sentence", "听短句，选出正确的翻译", "Education plays an important role in modern society.", ["教育在现代社会中起着重要作用", "教育在现代社会中越来越昂贵", "教育在现代社会中受到限制"], 0, "play a role in = 在……中起作用。"),
        Q("px1a", 4, "sentence", "听短句，选出正确的翻译", "The government has decided to build more public libraries.", ["政府决定拆除更多公共图书馆", "政府决定修建更多公共图书馆", "政府决定关闭更多公共图书馆"], 1, "decide to do = 决定做某事。"),
        Q("px1a", 5, "dialogue", "听对话，选择正确的答案", "A: Have you applied for the university scholarship? B: Not yet. I'm still preparing my application documents.", ["还没申请，正在准备材料", "已经申请成功", "决定放弃申请"], 0, "apply for = 申请；scholarship = 奖学金。"),
        Q("px1a", 6, "dialogue", "听对话，选择正确的答案", "A: Why do you think online courses are popular? B: Because they are flexible and you can study at your own pace.", ["因为课程便宜", "因为灵活，可以按自己的节奏学习", "因为老师更好"], 1, "at your own pace = 按自己的节奏。"),
        Q("px1a", 7, "dialogue", "听对话，选择正确的答案", "A: Would you like to donate books to the school library? B: Of course. I have many books that I no longer need.", ["拒绝捐书", "愿意捐出不再需要的书", "建议卖书"], 1, "donate = 捐赠；no longer = 不再。"),
        Q("px1a", 8, "passage", "听短文，回答问题", "Volunteering has become a popular activity among young people. Many students spend their weekends helping in community centres, teaching children or cleaning public parks. Research shows that volunteers not only help others but also develop important skills such as communication and teamwork. Some schools even include volunteer work in their graduation requirements.",
            None, 0, "", [
            {"id": "px1a08a", "q": "What do many students do at weekends?", "options": ["Work part-time", "Volunteer in the community", "Stay at home"], "answer": 1, "tip": "Many students spend their weekends helping in community centres."},
            {"id": "px1a08b", "q": "What skills can volunteers develop?", "options": ["Cooking and driving", "Communication and teamwork", "Painting and singing"], "answer": 1, "tip": "They develop important skills such as communication and teamwork."},
            {"id": "px1a08c", "q": "What do some schools do about volunteer work?", "options": ["Include it in graduation requirements", "Forbid students from volunteering", "Pay students for volunteering"], "answer": 0, "tip": "Some schools include volunteer work in their graduation requirements."},
        ]),
        Q("px1a", 9, "speaking", "跟读下列句子（口语题）", "In my opinion, young people should take part in more social activities to broaden their horizons.", ["✅ 点击播放并跟读"], 0, "注意 broaden 的 oa 音，horizons 的重音在第一个音节。"),
        Q("px1a", 10, "dialogue", "听对话，选择正确的答案", "A: Have you heard about the community garden project? B: Yes. Neighbours plant vegetables together and share the harvest. I've already signed up to join.", ["邻居们一起种菜分享收成，已报名参加", "项目已取消", "只有老年人可以参加"], 0, "sign up = 报名；community garden = 社区菜园。"),
        Q("px1a", 11, "passage", "听短文，回答问题", "Lifelong learning has become a necessity in today's fast-changing world. Technology develops so quickly that skills from ten years ago may no longer be useful. More and more adults are taking online courses to learn new skills, such as programming and digital design. Online learning makes it possible for busy people to study at home in the evening. Experts believe that those who keep learning will have more chances to succeed in their careers.",
            None, 0, "", [
            {"id": "px1a11a", "q": "Why is lifelong learning necessary?", "options": ["Because technology develops quickly and old skills may become useless", "Because schools are closing", "Because people have too much free time"], "answer": 0, "tip": "Technology develops so quickly that old skills may no longer be useful."},
            {"id": "px1a11b", "q": "What skills are mentioned as examples of new learning?", "options": ["Cooking and cleaning", "Programming and digital design", "Driving and flying"], "answer": 1, "tip": "They learn new skills, such as programming and digital design."},
            {"id": "px1a11c", "q": "What do experts believe about continuous learning?", "options": ["It leads to more career success chances", "It wastes time", "It is only for young people"], "answer": 0, "tip": "Those who keep learning will have more chances to succeed in their careers."},
        ]),
        Q("px1a", 12, "speaking", "跟读下列句子（口语题）", "Lifelong learning has become necessary in the modern world, especially for young people.", ["✅ 点击播放并跟读"], 0, "注意 especially 的重音在第二个音节，necessary 的 ce 轻读。"),
    ]}
    vols.append(v)
    # —— 卷二：科技与媒体 ——
    v = {"id": "px1b", "title": "PET 模拟卷二 · 科技与媒体", "topic": "科技 · 网络 · 媒体", "questions": [
        Q("px1b", 1, "word", "听单词，选出正确的中文意思", "technology", ["技术", "传统", "理论"], 0, "technology = 技术，形容词 technological。"),
        Q("px1b", 2, "word", "听单词，选出正确的中文意思", "advertisement", ["广告", "娱乐", "娱乐节目"], 0, "advertisement = 广告，常缩写为 ad。"),
        Q("px1b", 3, "sentence", "听短句，选出正确的翻译", "More and more people prefer reading news online to buying newspapers.", ["越来越多的人更喜欢在网上看新闻而不是买报纸", "越来越多的人更喜欢买报纸而不是上网", "越来越多的人既不看新闻也不买报纸"], 0, "prefer A to B = 比起 B 更喜欢 A。"),
        Q("px1b", 4, "sentence", "听短句，选出正确的翻译", "This mobile app allows users to share photos instantly.", ["这款手机应用让用户无法分享照片", "这款手机应用让用户能即时分享照片", "这款手机应用让用户付费分享照片"], 1, "allow sb to do = 允许某人做某事；instantly = 即时地。"),
        Q("px1b", 5, "dialogue", "听对话，选择正确的答案", "A: I heard that some websites collect personal information without permission. B: That's true. We should always read the privacy policy before using an app.", ["下载应用前应阅读隐私政策", "应用都会保护隐私", "个人信息不重要"], 0, "privacy policy = 隐私政策；without permission = 未经许可。"),
        Q("px1b", 6, "dialogue", "听对话，选择正确的答案", "A: How do you usually keep in touch with your friends abroad? B: I use video calls. It feels like we are in the same room.", ["发邮件", "打视频电话", "寄明信片"], 1, "keep in touch with = 与……保持联系；video calls = 视频通话。"),
        Q("px1b", 7, "dialogue", "听对话，选择正确的答案", "A: Do you think artificial intelligence will replace teachers? B: I don't think so. AI can assist teaching, but it can't understand students' feelings like human teachers.", ["会完全取代老师", "AI 能辅助教学，但无法取代老师", "AI 很快会取代所有职业"], 1, "assist = 辅助；replace = 取代。"),
        Q("px1b", 8, "passage", "听短文，回答问题", "Social media has changed the way we communicate. People can share their lives with friends around the world in seconds. However, experts warn that too much time on social media may cause problems. It can make young people compare themselves with others and feel unhappy. Experts suggest that we should spend more time on outdoor activities and face-to-face communication with family and friends.",
            None, 0, "", [
            {"id": "px1b08a", "q": "What can people do on social media in seconds?", "options": ["Share their lives with friends worldwide", "Learn new languages", "Buy tickets"], "answer": 0, "tip": "People can share their lives with friends around the world in seconds."},
            {"id": "px1b08b", "q": "What problem may social media cause?", "options": ["Sleep problems", "Comparing with others and feeling unhappy", "Memory loss"], "answer": 1, "tip": "It can make young people compare themselves with others and feel unhappy."},
            {"id": "px1b08c", "q": "What do experts suggest?", "options": ["Spend more time online", "Spend more time on outdoor activities and face-to-face communication", "Delete all social media accounts"], "answer": 1, "tip": "Experts suggest spending more time on outdoor activities and face-to-face communication."},
        ]),
        Q("px1b", 9, "speaking", "跟读下列句子（口语题）", "Technology has brought us great convenience, but we should also learn to use it wisely.", ["✅ 点击播放并跟读"], 0, "注意 convenience 的重音在第二个音节，wisely 的 ly 轻读。"),
        Q("px1b", 10, "dialogue", "听对话，选择正确的答案", "A: My parents limit my screen time to two hours a day. B: That sounds reasonable. Too much screen time is bad for your eyes.", ["父母限制每天屏幕时间两小时", "父母不限制屏幕时间", "父母要求整天玩手机"], 0, "limit ... to = 把……限制在；reasonable = 合理的。"),
        Q("px1b", 11, "passage", "听短文，回答问题", "A survey among middle school students shows that most of them still prefer paper books to e-books. When asked why, many students said that reading paper books is easier on the eyes and gives them a stronger sense of achievement. Some students also mentioned that they like the feeling of turning real pages. However, e-books are still popular because they are convenient and easy to carry. Many students use e-books when travelling or waiting for buses.",
            None, 0, "", [
            {"id": "px1b11a", "q": "What do most students prefer according to the survey?", "options": ["E-books", "Paper books", "Audio books"], "answer": 1, "tip": "Most students still prefer paper books to e-books."},
            {"id": "px1b11b", "q": "Why do students like paper books?", "options": ["Easier on the eyes and a sense of achievement", "Cheaper than e-books", "Lighter to carry"], "answer": 0, "tip": "Reading paper books is easier on the eyes and gives a stronger sense of achievement."},
            {"id": "px1b11c", "q": "When do students use e-books?", "options": ["When travelling or waiting for buses", "When studying at home", "When sleeping"], "answer": 0, "tip": "Many students use e-books when travelling or waiting for buses."},
        ]),
        Q("px1b", 12, "speaking", "跟读下列句子（口语题）", "Reading paper books is still popular among students because it is good for their eyes.", ["✅ 点击播放并跟读"], 0, "注意 popular 的重音在第一个音节，among 的 ng 音。"),
    ]}
    vols.append(v)
    # —— 卷三：健康与环境 ——
    v = {"id": "px2a", "title": "PET 模拟卷三 · 健康与环境", "topic": "健康 · 运动 · 环保", "questions": [
        Q("px2a", 1, "word", "听单词，选出正确的中文意思", "nutrition", ["营养", "健康", "疾病"], 0, "nutrition = 营养，形容词 nutritious。"),
        Q("px2a", 2, "word", "听单词，选出正确的中文意思", "pollution", ["污染", "保护", "资源"], 0, "pollution = 污染，动词 pollute。"),
        Q("px2a", 3, "sentence", "听短句，选出正确的翻译", "Regular exercise is essential for keeping a healthy body.", ["规律锻炼对保持健康至关重要", "偶尔锻炼对保持健康有帮助", "锻炼对健康没有影响"], 0, "be essential for = 对……必不可少。"),
        Q("px2a", 4, "sentence", "听短句，选出正确的翻译", "We should recycle waste paper instead of throwing it away.", ["我们应该回收废纸而不是扔掉它", "我们应该把废纸卖掉", "我们应该减少废纸的使用"], 0, "instead of = 而不是。throw away = 扔掉。"),
        Q("px2a", 5, "dialogue", "听对话，选择正确的答案", "A: I've been feeling tired these days. B: Maybe you should go to bed earlier and do some exercise.", ["建议早点睡并锻炼", "建议去看心理医生", "建议多喝咖啡"], 0, "should = 应该，提建议的常用词。"),
        Q("px2a", 6, "dialogue", "听对话，选择正确的答案", "A: Have you tried the new vegetable salad at the school canteen? B: Yes. It's delicious and healthy. I have it almost every day.", ["几乎每天吃蔬菜沙拉", "觉得很难吃", "没吃过学校食堂的沙拉"], 0, "almost every day = 几乎每天。"),
        Q("px2a", 7, "dialogue", "听对话，选择正确的答案", "A: What can we do to protect the environment? B: For a start, we can bring our own bags when shopping instead of using plastic bags.", ["购物时自带袋子代替塑料袋", "尽量网购", "减少购物次数"], 0, "For a start = 首先。plastic bags = 塑料袋。"),
        Q("px2a", 8, "passage", "听短文，回答问题", "A healthy lifestyle includes a balanced diet, regular exercise and enough sleep. Doctors say that eating too much fast food can lead to serious health problems, such as obesity and heart disease. To stay healthy, teenagers should eat more fruit and vegetables, drink plenty of water and exercise at least three times a week. They should also avoid staying up late, because sleep helps the body recover.",
            None, 0, "", [
            {"id": "px2a08a", "q": "What can eating too much fast food lead to?", "options": ["Obesity and heart disease", "Better memory", "Stronger bones"], "answer": 0, "tip": "Eating too much fast food can lead to obesity and heart disease."},
            {"id": "px2a08b", "q": "How often should teenagers exercise?", "options": ["Every day", "At least three times a week", "Once a month"], "answer": 1, "tip": "They should exercise at least three times a week."},
            {"id": "px2a08c", "q": "Why should teenagers avoid staying up late?", "options": ["Because sleep helps the body recover", "Because it costs money", "Because it is boring"], "answer": 0, "tip": "Sleep helps the body recover."},
        ]),
        Q("px2a", 9, "speaking", "跟读下列句子（口语题）", "To live a healthy life, we should develop good habits and keep a positive attitude.", ["✅ 点击播放并跟读"], 0, "注意 develop 的重音在第二个音节，attitude 的重音在第一个音节。"),
        Q("px2a", 10, "dialogue", "听对话，选择正确的答案", "A: I want to join the gym, but the yearly card is quite expensive. B: Why not try the monthly card first? It's cheaper and you can decide later.", ["先办月卡试试，更便宜且灵活", "办年卡更划算", "不建议办卡"], 0, "Why not ...? = 为什么不……？提建议。"),
        Q("px2a", 11, "passage", "听短文，回答问题", "Planting trees in cities brings many benefits. Trees can lower the temperature on hot summer days because they provide shade. They also help clean the air by absorbing harmful gases. Besides, green trees make the city more beautiful and give people a peaceful place to relax. Many cities have started tree-planting programmes and encourage citizens to take part. Even planting one tree in your neighbourhood can make a difference.",
            None, 0, "", [
            {"id": "px2a11a", "q": "How do trees help on hot summer days?", "options": ["They lower the temperature by providing shade", "They make the city noisy", "They use more water"], "answer": 0, "tip": "Trees can lower the temperature because they provide shade."},
            {"id": "px2a11b", "q": "What do trees do to the air?", "options": ["They absorb harmful gases", "They produce harmful gases", "They have no effect"], "answer": 0, "tip": "They help clean the air by absorbing harmful gases."},
            {"id": "px2a11c", "q": "What do many cities encourage citizens to do?", "options": ["Take part in tree-planting programmes", "Cut down trees", "Move to the countryside"], "answer": 0, "tip": "Cities encourage citizens to take part in tree-planting programmes."},
        ]),
        Q("px2a", 12, "speaking", "跟读下列句子（口语题）", "Planting more trees in the city can improve our living environment and reduce pollution.", ["✅ 点击播放并跟读"], 0, "注意 improve 的重音在第二个音节，environment 的重音在第二个音节。"),
    ]}
    vols.append(v)
    # —— 卷四：工作与旅行 ——
    v = {"id": "px2b", "title": "PET 模拟卷四 · 工作与旅行", "topic": "职业 · 求职 · 旅行体验", "questions": [
        Q("px2b", 1, "word", "听单词，选出正确的中文意思", "interview", ["面试", "合同", "培训"], 0, "interview = 面试；job interview 求职面试。"),
        Q("px2b", 2, "word", "听单词，选出正确的中文意思", "destination", ["目的地", "护照", "航班"], 0, "destination = 目的地，travel destination 旅游目的地。"),
        Q("px2b", 3, "sentence", "听短句，选出正确的翻译", "She has gained a lot of experience since she joined the company.", ["自从加入公司以来她积累了很多经验", "她加入公司之前就有很多经验", "她因为经验丰富而被公司录取"], 0, "since + 过去时间点 = 自从……以来。gain experience = 积累经验。"),
        Q("px2b", 4, "sentence", "听短句，选出正确的翻译", "Travelling abroad can open your eyes and enrich your mind.", ["出国旅行能开阔眼界、丰富思想", "出国旅行花费很高", "出国旅行很浪费时间"], 0, "open your eyes = 开阔眼界；enrich = 丰富。"),
        Q("px2b", 5, "dialogue", "听对话，选择正确的答案", "A: Why did you apply for this position? B: Because it offers more opportunities for career development and a better working environment.", ["因为工资更高", "因为提供更多职业发展机会和更好的工作环境", "因为离家更近"], 1, "career development = 职业发展。"),
        Q("px2b", 6, "dialogue", "听对话，选择正确的答案", "A: What impressed you most during your trip to Japan? B: The local people's politeness and the cleanliness of the streets impressed me most.", ["当地美食", "当地人的礼貌和街道的整洁", "当地的气候"], 1, "impress = 给……留下深刻印象。"),
        Q("px2b", 7, "dialogue", "听对话，选择正确的答案", "A: Is it your first time to work as a tour guide? B: No, I've been working in this field for five years.", ["第一次当导游", "在这个行业工作五年了", "想转行当导游"], 1, "have been working = 现在完成进行时，表示持续至今的动作。"),
        Q("px2b", 8, "passage", "听短文，回答问题", "Choosing a career is one of the most important decisions in life. Experts suggest that young people should consider their interests, abilities and the job market before making a choice. It is also wise to gain some work experience through internships. Some people change careers several times during their lifetime, which is quite normal today. The key is to keep learning and stay open to new opportunities.",
            None, 0, "", [
            {"id": "px2b08a", "q": "What should young people consider before choosing a career?", "options": ["Their interests, abilities and the job market", "Their salary only", "Their family's opinion only"], "answer": 0, "tip": "They should consider their interests, abilities and the job market."},
            {"id": "px2b08b", "q": "What is a wise way to gain work experience?", "options": ["Changing jobs often", "Taking internships", "Retiring early"], "answer": 1, "tip": "It is wise to gain work experience through internships."},
            {"id": "px2b08c", "q": "What is the key to career success according to the passage?", "options": ["Staying in one job forever", "Keeping learning and staying open to new opportunities", "Working overtime"], "answer": 1, "tip": "The key is to keep learning and stay open to new opportunities."},
        ]),
        Q("px2b", 9, "speaking", "跟读下列句子（口语题）", "I believe that a good job is not only about the salary, but also about personal satisfaction and growth.", ["✅ 点击播放并跟读"], 0, "注意 satisfaction 的重音在第三个音节，growth 的 th 音要轻。"),
        Q("px2b", 10, "dialogue", "听对话，选择正确的答案", "A: I have a business trip to Shanghai next Monday. Could you help me book a hotel near the station? B: Sure. I'll find a comfortable one and send you the information today.", ["出差去上海，帮忙订车站附近的酒店", "去上海度假，订海边酒店", "取消出差"], 0, "business trip = 出差；book a hotel = 订酒店。"),
        Q("px2b", 11, "passage", "听短文，回答问题", "Remote work has become a new trend in recent years. Working from home saves a lot of time because people do not need to commute. It also gives employees more flexible schedules, so they can balance work and family life better. However, remote work is not perfect. Some people find it hard to concentrate at home, and others miss talking with their colleagues face to face. Experts say that the key is to make a clear plan and set a comfortable working space at home.",
            None, 0, "", [
            {"id": "px2b11a", "q": "What is one advantage of remote work?", "options": ["No need to commute and more flexible schedules", "Higher salary", "Longer holidays"], "answer": 0, "tip": "It saves time and gives employees more flexible schedules."},
            {"id": "px2b11b", "q": "What problem may remote workers face?", "options": ["Hard to concentrate at home", "Too many meetings", "No salary"], "answer": 0, "tip": "Some people find it hard to concentrate at home."},
            {"id": "px2b11c", "q": "What do experts suggest for remote workers?", "options": ["Make a clear plan and set a comfortable working space", "Work at the office every day", "Avoid using computers"], "answer": 0, "tip": "The key is to make a clear plan and set a comfortable working space at home."},
        ]),
        Q("px2b", 12, "speaking", "跟读下列句子（口语题）", "Working from home has become a new trend in recent years, and it gives people more flexibility.", ["✅ 点击播放并跟读"], 0, "注意 flexibility 的重音在第三个音节，trend 的 tr 音。"),
    ]}
    vols.append(v)
    return vols

def gen():
    os.makedirs(DATA, exist_ok=True)
    vols = build_volumes()
    payload = {"level": "PET", "name": "PET 听说模拟（B1）", "volumes": vols}
    with open(os.path.join(DATA, "pet_exam.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    md = ["# 小学英语-剑桥PET备考包-听说模拟练习（B1）", "",
          "> 内容由 AI 生成，待创始人人工校对（红线条款）", "",
          "共 4 套模拟卷 × 12 题，覆盖单词听力 / 短句听力 / 对话听力 / 篇章听力 / 口语跟读五大题型。", ""]
    for v in vols:
        md.append("## %s" % v["title"])
        for q in v["questions"]:
            if q["type"] == "passage":
                md.append("- [篇章听力] %s" % q["q"])
                for s in q["questions"]:
                    md.append("  - %s 选项：%s 答案：%s" % (s["q"], " / ".join(s["options"]), s["options"][s["answer"]]))
            else:
                md.append("- [%s] %s 选项：%s 答案：%s" % (q["type"], q["q"], " / ".join(q["options"]), q["options"][q["answer"]]))
        md.append("")
    with open(os.path.join(BASE, "..", "english-edu-company", "03交付素材库", "听说试卷包", "小学英语-剑桥PET备考包-听说模拟练习-B1.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print("写入完成：pet_exam.json（%d 卷 × 12 题）+ 素材 md" % len(vols))

def audio():
    os.makedirs(AUD, exist_ok=True)
    import glob
    existing = {os.path.basename(x) for x in glob.glob(os.path.join(AUD, "*.mp3"))}
    plan = []
    for v in build_volumes():
        for q in v["questions"]:
            fn = "%s%02d.mp3" % (v["id"], int(q["id"][-2:]))
            if fn not in existing:
                plan.append((fn, build_audio_text(q)))
    print("计划生成:", len(plan))
    for i, (fn, txt) in enumerate(plan, 1):
        if i % 20 == 0: print("[%d/%d]" % (i, len(plan)), end="")
        dst = os.path.join(AUD, fn)
        r = subprocess.run(["edge-tts", "--voice", "en-GB-SoniaNeural", "--text", txt,
                            "--rate=-15%", "--write-media", dst], capture_output=True, text=True)
        if r.returncode != 0:
            print("FAIL", fn, r.stderr[-200:])
    print("音频生成完成：%d/%d" % (len(plan), len(plan)))

def build_audio_text(q):
    if q["type"] == "passage":
        txt = re.sub(r"\b[AB]:\s*", "", q.get("audio_text") or "")
        parts = [txt]
        for i, s in enumerate(q.get("questions") or [], 1):
            parts.append("Question %d. %s" % (i, s["q"]))
        return "Listen to the passage. " + " ".join(parts)
    return re.sub(r"\b[AB]:\s*", "", q.get("audio_text") or "")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "audio":
        audio()
    else:
        gen()
