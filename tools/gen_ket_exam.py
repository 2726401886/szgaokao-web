# -*- coding: utf-8 -*-
# KET 听说模拟练习（剑桥 A2 Key）4 卷 × 12 题，五大题型
# 音频命名 /audio/kx/kx{vol}-{no}.mp3；题 id kx1a01...
import json, os, subprocess, re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
AUD = os.path.join(BASE, "public", "audio", "kx")

def Q(vol, no, qtype, q, audio_text, options, answer, tip, subs=None):
    d = {"id": "%s%02d" % (vol, no), "type": qtype, "q": q, "audio": "/audio/kx/%s%02d.mp3" % (vol, no),
         "audio_text": audio_text, "options": options, "answer": answer, "tip": tip}
    if subs:
        d["questions"] = subs
    return d

def build_volumes():
    vols = []
    # —— 卷一：校园生活 ——
    v = {"id": "kx1a", "title": "KET 模拟卷一 · 校园生活", "topic": "校园 · 学习 · 考试", "questions": [
        Q("kx1a", 1, "word", "听单词，选出正确的中文意思", "library", ["图书馆", "实验室", "食堂"], 0, "library = 图书馆，注意与 lab（实验室）区分。"),
        Q("kx1a", 2, "word", "听单词，选出正确的中文意思", "homework", ["考试", "作业", "笔记"], 1, "homework 是不可数名词，意为家庭作业。"),
        Q("kx1a", 3, "sentence", "听短句，选出正确的翻译", "I have an English lesson at nine o'clock.", ["我九点有一节英语课", "我九点有一场考试", "我九点要去图书馆"], 0, "have a lesson = 上课。"),
        Q("kx1a", 4, "sentence", "听短句，选出正确的翻译", "Our teacher is very kind to us.", ["我们的老师对我们很严格", "我们的老师对我们很和蔼", "我们的老师经常表扬我们"], 1, "be kind to sb = 对某人友好/和蔼。"),
        Q("kx1a", 5, "dialogue", "听对话，选择正确的答案", "A: Can I borrow your pen, please? B: Sure. Here you are.", ["借给 A 一支钢笔", "向 A 借钢笔", "让 A 去买钢笔"], 0, "Here you are. = 给你。borrow = 借入。"),
        Q("kx1a", 6, "dialogue", "听对话，选择正确的答案", "A: How often do you have P.E. class? B: Twice a week, on Tuesday and Friday.", ["每周两次", "每周一次", "每天一次"], 0, "twice a week = 每周两次。"),
        Q("kx1a", 7, "dialogue", "听对话，选择正确的答案", "A: I can't find my maths book. B: Maybe it's in your desk.", ["在书桌里", "在书包里", "在家里"], 0, "maybe = 也许。注意推测语气。"),
        Q("kx1a", 8, "passage", "听短文，回答问题", "Tom is a primary school student. He gets up at six thirty every morning. He walks to school with his best friend Jack. His favourite subject is science because he likes doing experiments. After school, he plays basketball for an hour.",
            None, 0, "", [
            {"id": "kx1a08a", "q": "How does Tom go to school?", "options": ["On foot", "By bus", "By bike"], "answer": 0, "tip": "walks to school = 步行上学，即 on foot。"},
            {"id": "kx1a08b", "q": "Why does Tom like science?", "options": ["Because he likes doing experiments", "Because his teacher is kind", "Because it is easy"], "answer": 0, "tip": "because he likes doing experiments = 因为他喜欢做实验。"},
            {"id": "kx1a08c", "q": "What does Tom do after school?", "options": ["He plays football", "He plays basketball", "He reads books"], "answer": 1, "tip": "plays basketball for an hour = 打一小时篮球。"},
        ]),
        Q("kx1a", 9, "speaking", "跟读下列句子（口语题）", "My favourite subject is English, because I like speaking with my classmates.", ["✅ 点击播放并跟读"], 0, "注意 favourite 的重音在第一个音节，speaking 的 ng 音要读到位。"),
        Q("kx1a", 10, "dialogue", "听对话，选择正确的答案", "A: Who is the girl in the photo? B: She is my cousin. She lives in Shanghai and she is two years older than me.", ["她是我妹妹", "她是我表姐，住在上海", "她是我同学"], 1, "cousin = 堂（表）姐妹；older than = 比……大。"),
        Q("kx1a", 11, "passage", "听短文，回答问题", "Our school has three interesting clubs. The Music Club meets on Monday afternoon. Students there play the guitar, the piano or sing songs. The Sports Club is very popular. Children play basketball and football after class on Tuesday and Thursday. The Art Club is on Friday. Students draw pictures and make cards. You can join the club you like at the office on the first floor.",
            None, 0, "", [
            {"id": "kx1a11a", "q": "When does the Music Club meet?", "options": ["On Monday afternoon", "On Tuesday", "On Friday"], "answer": 0, "tip": "The Music Club meets on Monday afternoon."},
            {"id": "kx1a11b", "q": "What do students do in the Sports Club?", "options": ["Sing songs", "Play basketball and football", "Draw pictures"], "answer": 1, "tip": "Children play basketball and football after class on Tuesday and Thursday."},
            {"id": "kx1a11c", "q": "Where can students join a club?", "options": ["In the library", "At the office on the first floor", "In the dining hall"], "answer": 1, "tip": "You can join the club at the office on the first floor."},
        ]),
        Q("kx1a", 12, "speaking", "跟读下列句子（口语题）", "After school, I often go to the library to read story books with my friends.", ["✅ 点击播放并跟读"], 0, "注意 often 的 t 可轻读，story 的 o 音要饱满。"),
    ]}
    vols.append(v)
    # —— 卷二：家庭与休闲 ——
    v = {"id": "kx1b", "title": "KET 模拟卷二 · 家庭与休闲", "topic": "家庭 · 周末 · 爱好", "questions": [
        Q("kx1b", 1, "word", "听单词，选出正确的中文意思", "weekend", ["周末", "工作日", "假期"], 0, "weekend = 周末，指周六和周日。"),
        Q("kx1b", 2, "word", "听单词，选出正确的中文意思", "hobby", ["作业", "爱好", "习惯"], 1, "hobby = 爱好，如 collecting stamps 集邮。"),
        Q("kx1b", 3, "sentence", "听短句，选出正确的翻译", "My family usually have dinner together on Sundays.", ["我们家通常在周日一起吃晚饭", "我们家通常在周日一起去公园", "我们家通常在周日一起看电视"], 0, "have dinner together = 一起吃晚饭。"),
        Q("kx1b", 4, "sentence", "听短句，选出正确的翻译", "She spends two hours playing the piano every day.", ["她每天花两小时弹钢琴", "她每天花两小时练跑步", "她每天花两小时写作业"], 0, "spend time doing sth = 花时间做某事。"),
        Q("kx1b", 5, "dialogue", "听对话，选择正确的答案", "A: What are you going to do this weekend? B: I'm going to visit my grandparents with my parents.", ["去看望祖父母", "在家做作业", "去公园野餐"], 0, "be going to = 打算做某事。"),
        Q("kx1b", 6, "dialogue", "听对话，选择正确的答案", "A: Do you like swimming? B: Yes, but I like cycling better.", ["游泳", "骑自行车", "跑步"], 1, "like ... better = 更喜欢……。"),
        Q("kx1b", 7, "dialogue", "听对话，选择正确的答案", "A: How was your holiday? B: It was wonderful! We went to the beach every day.", ["每天去海滩", "每天去爬山", "每天在家休息"], 0, "wonderful = 棒极了。went to the beach = 去了海滩。"),
        Q("kx1b", 8, "passage", "听短文，回答问题", "Linda's family has four people: her father, her mother, her brother and her. On Saturday morning, they go to the supermarket together. Her father buys some bread and milk. Her mother buys vegetables and fruit. Linda and her brother buy a big cake. They have a picnic in the park at noon.",
            None, 0, "", [
            {"id": "kx1b08a", "q": "How many people are there in Linda's family?", "options": ["Three", "Four", "Five"], "answer": 1, "tip": "father, mother, brother and Linda = 4 人。"},
            {"id": "kx1b08b", "q": "What does her father buy?", "options": ["Vegetables and fruit", "Bread and milk", "A big cake"], "answer": 1, "tip": "Her father buys some bread and milk."},
            {"id": "kx1b08c", "q": "Where do they have a picnic?", "options": ["At home", "In the park", "At the supermarket"], "answer": 1, "tip": "They have a picnic in the park at noon."},
        ]),
        Q("kx1b", 9, "speaking", "跟读下列句子（口语题）", "On weekends, I like playing football with my friends in the park.", ["✅ 点击播放并跟读"], 0, "注意 weekends 的 s 要轻读，playing 的 ing 音清晰。"),
        Q("kx1b", 10, "dialogue", "听对话，选择正确的答案", "A: We planned a picnic tomorrow. But the weather report says it will rain. B: Then let's stay at home and watch a film instead.", ["明天去野餐", "下雨就待在家看电影", "明天去游泳"], 1, "weather report = 天气预报；stay at home = 待在家。"),
        Q("kx1b", 11, "passage", "听短文，回答问题", "Amy likes collecting stamps. She has stamps from more than twenty countries. Her friend Jack is interested in taking photos. He takes pictures of birds and flowers in the park. On Sunday afternoon, Amy and Jack usually go to the park with their families. They fly kites, ride bikes and have a small picnic under the big tree. Everyone enjoys the happy time together.",
            None, 0, "", [
            {"id": "kx1b11a", "q": "What does Amy like doing?", "options": ["Taking photos", "Collecting stamps", "Riding bikes"], "answer": 1, "tip": "Amy likes collecting stamps."},
            {"id": "kx1b11b", "q": "What does Jack take pictures of?", "options": ["Birds and flowers", "Cars and buses", "Food and drinks"], "answer": 0, "tip": "He takes pictures of birds and flowers in the park."},
            {"id": "kx1b11c", "q": "Where do they have a small picnic?", "options": ["Under the big tree", "At home", "At school"], "answer": 0, "tip": "They have a small picnic under the big tree."},
        ]),
        Q("kx1b", 12, "speaking", "跟读下列句子（口语题）", "My hobby is collecting stamps from different countries around the world.", ["✅ 点击播放并跟读"], 0, "注意 collecting 双写 l，countries 的 ou 音。"),
    ]}
    vols.append(v)
    # —— 卷三：饮食与购物 ——
    v = {"id": "kx2a", "title": "KET 模拟卷三 · 饮食与购物", "topic": "食物 · 餐厅 · 购物", "questions": [
        Q("kx2a", 1, "word", "听单词，选出正确的中文意思", "vegetable", ["蔬菜", "水果", "肉类"], 0, "vegetable = 蔬菜，常与 fruit 一起记忆。"),
        Q("kx2a", 2, "word", "听单词，选出正确的中文意思", "expensive", ["便宜的", "昂贵的", "好吃的"], 1, "expensive = 昂贵的，反义词 cheap。"),
        Q("kx2a", 3, "sentence", "听短句，选出正确的翻译", "I'd like a glass of orange juice, please.", ["请给我一杯橙汁", "请给我一个橙子", "请给我一杯牛奶"], 0, "a glass of = 一杯（玻璃杯）。"),
        Q("kx2a", 4, "sentence", "听短句，选出正确的翻译", "The blue T-shirt is cheaper than the red one.", ["蓝色T恤比红色那件便宜", "蓝色T恤比红色那件贵", "蓝色T恤和红色那件一样贵"], 0, "cheaper than = 比……更便宜。比较级。"),
        Q("kx2a", 5, "dialogue", "听对话，选择正确的答案", "A: Can I help you? B: Yes, I'm looking for a school bag.", ["在文具店", "在医院", "在车站"], 0, "Can I help you? = 购物时的招呼语。looking for = 寻找。"),
        Q("kx2a", 6, "dialogue", "听对话，选择正确的答案", "A: What would you like for lunch? B: I'd like some noodles with vegetables.", ["蔬菜面", "牛肉面", "鸡蛋面"], 0, "noodles with vegetables = 蔬菜面。"),
        Q("kx2a", 7, "dialogue", "听对话，选择正确的答案", "A: How much is this jacket? B: It's fifty dollars. But it's on sale today, so you can get it for thirty.", ["50 美元", "30 美元", "20 美元"], 1, "on sale = 打折促销，30 美元是折后价。"),
        Q("kx2a", 8, "passage", "听短文，回答问题", "Yesterday was Jane's birthday. Her mother cooked a big dinner for her: chicken, fish, rice and vegetables. Her father bought a birthday cake with ten candles. Her friends came to her party and brought her presents. She got a new dress from her best friend Lucy. Everyone had a great time.",
            None, 0, "", [
            {"id": "kx2a08a", "q": "Who cooked the dinner?", "options": ["Jane", "Jane's mother", "Jane's father"], "answer": 1, "tip": "Her mother cooked a big dinner for her."},
            {"id": "kx2a08b", "q": "What did her father buy?", "options": ["A new dress", "A birthday cake", "Some chicken"], "answer": 1, "tip": "Her father bought a birthday cake with ten candles."},
            {"id": "kx2a08c", "q": "Who gave Jane a new dress?", "options": ["Lucy", "Her mother", "Her father"], "answer": 0, "tip": "She got a new dress from her best friend Lucy."},
        ]),
        Q("kx2a", 9, "speaking", "跟读下列句子（口语题）", "I usually have bread and milk for breakfast, and I often eat fruit after dinner.", ["✅ 点击播放并跟读"], 0, "注意 breakfast 的重音在第一个音节，fruit 的 u 音。"),
        Q("kx2a", 10, "dialogue", "听对话，选择正确的答案", "A: Are you ready to order, sir? B: Yes, I'd like beef with rice and a cup of tea, please.", ["牛肉饭和一杯茶", "鸡肉面和一杯咖啡", "鱼和一瓶果汁"], 0, "order = 点餐；beef with rice = 牛肉饭。"),
        Q("kx2a", 11, "passage", "听短文，回答问题", "Every Friday, the supermarket has a big sale. Milk is cheaper on that day, so many people buy it. Fruit like apples and bananas are also on sale. Linda's mother always makes a shopping list before going there. She buys food for the week and checks the prices carefully. She says it helps the family save a lot of money.",
            None, 0, "", [
            {"id": "kx2a11a", "q": "When does the supermarket have a big sale?", "options": ["On Monday", "On Friday", "On Sunday"], "answer": 1, "tip": "Every Friday, the supermarket has a big sale."},
            {"id": "kx2a11b", "q": "What does Linda's mother do before going shopping?", "options": ["Makes a shopping list", "Calls her friends", "Watches TV"], "answer": 0, "tip": "She always makes a shopping list before going there."},
            {"id": "kx2a11c", "q": "Why does she check the prices carefully?", "options": ["To save money", "To buy more", "To sell the food"], "answer": 0, "tip": "It helps the family save a lot of money."},
        ]),
        Q("kx2a", 12, "speaking", "跟读下列句子（口语题）", "I often help my mother do some shopping at the supermarket on Saturday morning.", ["✅ 点击播放并跟读"], 0, "注意 shopping 双写 p，supermarket 的重音在第一个音节。"),
    ]}
    vols.append(v)
    # —— 卷四：旅行与城市 ——
    v = {"id": "kx2b", "title": "KET 模拟卷四 · 旅行与城市", "topic": "旅行 · 问路 · 城市地标", "questions": [
        Q("kx2b", 1, "word", "听单词，选出正确的中文意思", "station", ["车站", "机场", "码头"], 0, "station = 车站，train station 火车站。"),
        Q("kx2b", 2, "word", "听单词，选出正确的中文意思", "museum", ["电影院", "博物馆", "剧院"], 1, "museum = 博物馆，注意发音 /mjuˈziːəm/。"),
        Q("kx2b", 3, "sentence", "听短句，选出正确的翻译", "Excuse me, how can I get to the city library?", ["请问去市图书馆怎么走", "请问市图书馆几点关门", "请问市图书馆在哪里工作"], 0, "How can I get to ...? = 我怎么去……？问路句型。"),
        Q("kx2b", 4, "sentence", "听短句，选出正确的翻译", "The bus takes about twenty minutes to get to the airport.", ["坐公交去机场大约需要二十分钟", "坐地铁去机场大约需要二十分钟", "走路去机场大约需要二十分钟"], 0, "It takes ... to do = 做某事需要（时间）。"),
        Q("kx2b", 5, "dialogue", "听对话，选择正确的答案", "A: Excuse me, where is the nearest bank? B: Go straight on, and turn left at the second crossing.", ["直走，第二个路口左转", "直走，第二个路口右转", "左转，第一个路口直走"], 0, "turn left at the second crossing = 在第二个十字路口左转。"),
        Q("kx2b", 6, "dialogue", "听对话，选择正确的答案", "A: Shall we take the bus or the underground? B: The underground is faster. Let's take it.", ["坐公交", "坐地铁", "坐出租车"], 1, "underground = 地铁（英式），faster = 更快。"),
        Q("kx2b", 7, "dialogue", "听对话，选择正确的答案", "A: What time does the train leave? B: At half past nine. We still have thirty minutes.", ["九点", "九点半", "十点"], 0, "half past nine = 九点半；还有三十分钟，所以现在是九点。"),
        Q("kx2b", 8, "passage", "听短文，回答问题", "Last summer, Mike went to London with his parents. They visited the Tower Bridge and the British Museum. They took a boat trip on the River Thames and saw many famous buildings. Mike liked the food there, especially the fish and chips. They stayed in London for five days. Mike said he wanted to go there again.",
            None, 0, "", [
            {"id": "kx2b08a", "q": "When did Mike go to London?", "options": ["Last summer", "Last winter", "This spring"], "answer": 0, "tip": "Last summer, Mike went to London with his parents."},
            {"id": "kx2b08b", "q": "What did they do on the River Thames?", "options": ["Swimming", "A boat trip", "Fishing"], "answer": 1, "tip": "They took a boat trip on the River Thames."},
            {"id": "kx2b08c", "q": "How long did they stay in London?", "options": ["Three days", "Four days", "Five days"], "answer": 2, "tip": "They stayed in London for five days."},
        ]),
        Q("kx2b", 9, "speaking", "跟读下列句子（口语题）", "I like travelling by train because I can see the beautiful scenery on the way.", ["✅ 点击播放并跟读"], 0, "注意 travelling 双写 l，scenery 的重音在第一个音节。"),
        Q("kx2b", 10, "dialogue", "听对话，选择正确的答案", "A: Excuse me, where is the museum? B: It's next to the post office. Take the second turning on your left and walk straight.", ["在邮局旁边", "在银行对面", "在公园后面"], 0, "next to = 在……旁边；take the second turning = 在第二个路口转弯。"),
        Q("kx2b", 11, "passage", "听短文，回答问题", "There are different ways to travel around the city. The underground is the fastest, but it can be very crowded in the morning. The bus is cheaper, but it is slow because there are many stops. Many people now ride bicycles, because it is good for the environment and keeps them healthy. On sunny days, more and more people choose to walk short distances instead of taking buses.",
            None, 0, "", [
            {"id": "kx2b11a", "q": "Why is the underground not always good?", "options": ["It is too expensive", "It can be very crowded", "It is too slow"], "answer": 1, "tip": "It can be very crowded in the morning."},
            {"id": "kx2b11b", "q": "Why do many people ride bicycles?", "options": ["Because it is good for the environment and health", "Because it is the fastest", "Because it is free"], "answer": 0, "tip": "It is good for the environment and keeps them healthy."},
            {"id": "kx2b11c", "q": "What do people do on sunny days?", "options": ["Stay at home", "Walk short distances", "Take taxis"], "answer": 1, "tip": "People choose to walk short distances instead of taking buses."},
        ]),
        Q("kx2b", 12, "speaking", "跟读下列句子（口语题）", "The underground is the fastest way to travel around the city centre.", ["✅ 点击播放并跟读"], 0, "注意 underground 的重音在第一个音节，centre 的 re 轻读。"),
    ]}
    vols.append(v)
    return vols

def gen():
    os.makedirs(DATA, exist_ok=True)
    vols = build_volumes()
    payload = {"level": "KET", "name": "KET 听说模拟（A2）", "volumes": vols}
    with open(os.path.join(DATA, "ket_exam.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    md = ["# 小学英语-剑桥KET备考包-听说模拟练习（A2）", "",
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
    with open(os.path.join(BASE, "..", "english-edu-company", "03交付素材库", "听说试卷包", "小学英语-剑桥KET备考包-听说模拟练习-A2.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print("写入完成：ket_exam.json（%d 卷 × 12 题）+ 素材 md" % len(vols))

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
    # 朗读英文内容本身：word=单词，sentence/dialogue/speaking=英文句子；passage=短文+各小题问题
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
