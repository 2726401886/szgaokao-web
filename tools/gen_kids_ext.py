# -*- coding: utf-8 -*-
"""幼儿启蒙英语 P0/P1 扩展内容生成脚本
生成：
  1) data/kids_songs.json   儿歌磨耳朵（10 首，逐句歌词+中文）
  2) data/kids_tpr.json     TPR 日常指令（5 组 × 16 条）
  3) data/kids_phonics.json 自然拼读启蒙（26 字母音 + 字母歌 + CVC 入门）
  4) data/kids_reading.json 迷你绘本（8 本 × 6 句）
  5) public/audio/{ks,kt,kp,kr}/*.mp3 英音音频
  6) 素材库 md ×4（AI 初稿，待创始人人工校对）
用法：
  python tools/gen_kids_ext.py gen
  python tools/gen_kids_ext.py audio
"""
import asyncio, io, json, os, subprocess, sys
import edge_tts

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
MAT_DIR = r'C:\Users\27264\WorkBuddy\2026-09-26-21-53-51\english-edu-company\03交付素材库\听说试卷包'

VOICE = 'en-GB-SoniaNeural'
RATE = '-12%'

# ---------------- 1. 儿歌（10 首 × 4 句） ----------------
SONGS = [
    {"id": "ks1", "title": "Hello Song", "zhTitle": "你好歌", "emoji": "👋", "theme": "问候",
     "lines": [
        ("Hello, hello, how are you?", "你好，你好，你好吗？"),
        ("I am fine, how are you too?", "我很好，你也好吗？"),
        ("Hello, hello, say hello.", "你好，你好，说声你好。"),
        ("Come and sing with me, let's go!", "来和我一起唱，我们出发吧！"),
     ]},
    {"id": "ks2", "title": "Colour Song", "zhTitle": "颜色歌", "emoji": "🎨", "theme": "颜色",
     "lines": [
        ("Red and blue, green and yellow.", "红和蓝，绿和黄。"),
        ("Colours, colours, bright and mellow.", "颜色，颜色，又亮又柔。"),
        ("I see red, I see blue.", "我看见红色，我看见蓝色。"),
        ("Pretty colours, I love you!", "漂亮的颜色，我爱你们！"),
     ]},
    {"id": "ks3", "title": "Counting Song", "zhTitle": "数数歌", "emoji": "🔢", "theme": "数字",
     "lines": [
        ("One, two, three, look at me.", "一，二，三，看看我。"),
        ("Four, five, six, count with me.", "四，五，六，和我一起数。"),
        ("Seven, eight, nine, ten.", "七，八，九，十。"),
        ("Let's count again, my friend!", "朋友，我们再数一次！"),
     ]},
    {"id": "ks4", "title": "Animal Sounds", "zhTitle": "动物叫声歌", "emoji": "🐾", "theme": "动物",
     "lines": [
        ("The cat says meow, meow.", "小猫说喵，喵。"),
        ("The dog says woof, woof.", "小狗说汪，汪。"),
        ("The duck says quack, quack.", "小鸭说嘎，嘎。"),
        ("Animals are my friends!", "动物是我的朋友！"),
     ]},
    {"id": "ks5", "title": "Yummy Food", "zhTitle": "美味食物歌", "emoji": "🍎", "theme": "食物",
     "lines": [
        ("Apple and banana, yummy, yummy.", "苹果和香蕉，美味，美味。"),
        ("Milk and egg, good for my tummy.", "牛奶和鸡蛋，对身体好。"),
        ("Cake and ice cream, sweet, sweet, sweet.", "蛋糕和冰淇淋，甜，甜，甜。"),
        ("I love yummy food to eat!", "我爱吃美味的食物！"),
     ]},
    {"id": "ks6", "title": "My Body", "zhTitle": "身体歌", "emoji": "🧍", "theme": "身体",
     "lines": [
        ("Head and shoulders, knees and toes.", "头和肩膀，膝盖和脚趾。"),
        ("Eyes and ears and mouth and nose.", "眼睛耳朵嘴巴和鼻子。"),
        ("Clap your hands, stamp your feet.", "拍拍手，跺跺脚。"),
        ("My body is so neat!", "我的身体真棒！"),
     ]},
    {"id": "ks7", "title": "Rain and Sun", "zhTitle": "雨和太阳歌", "emoji": "🌦️", "theme": "天气",
     "lines": [
        ("Rain, rain, go away.", "雨啊雨啊快走开。"),
        ("Come again another day.", "改天你再来。"),
        ("Sun, sun, shine so bright.", "太阳太阳闪闪亮。"),
        ("Play with me all day and night!", "白天黑夜和我玩！"),
     ]},
    {"id": "ks8", "title": "Let's Move", "zhTitle": "动起来歌", "emoji": "🏃", "theme": "动作",
     "lines": [
        ("Jump, jump, jump so high.", "跳，跳，跳得高。"),
        ("Run, run, run and fly.", "跑，跑，跑得快。"),
        ("Clap, clap, clap your hands.", "拍，拍，拍拍你的手。"),
        ("Move your body, be my friends!", "动动身体，做我的好朋友！"),
     ]},
    {"id": "ks9", "title": "My Family", "zhTitle": "家人歌", "emoji": "👨‍👩‍👧", "theme": "家庭",
     "lines": [
        ("Mum and Dad, I love you.", "妈妈爸爸，我爱你们。"),
        ("Grandma and Grandpa, love you too.", "爷爷奶奶，也爱你们。"),
        ("Brother, sister, all my family.", "哥哥姐姐，我的全家。"),
        ("We are happy, you and me!", "我们很快乐，你和我！"),
     ]},
    {"id": "ks10", "title": "Let's Go Out", "zhTitle": "出行歌", "emoji": "🚌", "theme": "出行",
     "lines": [
        ("The car goes beep, beep, beep.", "小汽车嘟嘟嘟。"),
        ("The bike goes ring, ring, ring.", "自行车铃铃铃。"),
        ("The bus goes vroom, vroom, vroom.", "公交车轰轰轰。"),
        ("Let's go to the zoo!", "我们去动物园吧！"),
     ]},
]

# ---------------- 2. TPR 指令（5 组 × 16 条） ----------------
TPR_GROUPS = [
    {"id": "kt1", "title": "晨间日常", "emoji": "🌅", "items": [
        ("Wake up!", "起床啦！", "😴"), ("Get up, get up!", "起来，起来！", "🛏️"),
        ("Stretch your arms.", "伸伸你的胳膊。", "🙆"), ("Open your eyes.", "睁开你的眼睛。", "👀"),
        ("Look at the sun.", "看看太阳。", "🌞"), ("Say good morning.", "说早上好。", "👋"),
        ("Comb your hair.", "梳梳你的头发。", "💇"), ("Wash your face.", "洗洗你的脸。", "🫧"),
        ("Brush your teeth.", "刷刷你的牙齿。", "🪥"), ("Put on your clothes.", "穿上你的衣服。", "👕"),
        ("Put on your shoes.", "穿上你的鞋子。", "👟"), ("Eat your breakfast.", "吃你的早餐。", "🥣"),
        ("Drink some milk.", "喝点牛奶。", "🥛"), ("Go to school.", "去上学。", "🏫"),
        ("Wave goodbye.", "挥手说再见。", "👋"), ("Give me a hug.", "给我一个拥抱。", "🤗"),
    ]},
    {"id": "kt2", "title": "洗漱清洁", "emoji": "🧼", "items": [
        ("Wash your hands.", "洗洗你的手。", "🧼"), ("Rinse your mouth.", "漱漱口。", "💧"),
        ("Take a bath.", "洗个澡。", "🛁"), ("Dry your hands.", "擦干你的手。", "🧻"),
        ("Blow your nose.", "擤擤鼻子。", "🤧"), ("Clean your face.", "擦擦脸。", "🧴"),
        ("Use the soap.", "用一用肥皂。", "🧽"), ("Turn on the tap.", "打开水龙头。", "🚰"),
        ("Turn off the tap.", "关掉水龙头。", "🚱"), ("Dry your hair.", "擦干头发。", "🧖"),
        ("Put on your socks.", "穿上袜子。", "🧦"), ("Take off your shoes.", "脱下鞋子。", "👞"),
        ("Wipe your mouth.", "擦擦嘴。", "😋"), ("Flush the toilet.", "冲一冲马桶。", "🚽"),
        ("Cut your nails.", "剪剪指甲。", "💅"), ("Put on your pyjamas.", "穿上睡衣。", "😴"),
    ]},
    {"id": "kt3", "title": "穿衣出行", "emoji": "🚦", "items": [
        ("Put on your coat.", "穿上外套。", "🧥"), ("Take off your hat.", "摘下帽子。", "🧢"),
        ("Button your shirt.", "扣上扣子。", "👔"), ("Zip up your jacket.", "拉上拉链。", "🤐"),
        ("Tie your shoes.", "系好鞋带。", "🪢"), ("Wear your scarf.", "戴上围巾。", "🧣"),
        ("Put on your gloves.", "戴上手套。", "🧤"), ("Carry your bag.", "背上书包。", "🎒"),
        ("Walk slowly.", "慢慢走。", "🚶"), ("Run fast.", "快快跑。", "🏃"),
        ("Stop! Wait!", "停！等一等！", "✋"), ("Look left.", "看看左边。", "👈"),
        ("Look right.", "看看右边。", "👉"), ("Cross the road.", "过马路。", "🚸"),
        ("Get on the bus.", "上公交车。", "🚌"), ("Get off the bus.", "下公交车。", "🚏"),
    ]},
    {"id": "kt4", "title": "吃饭时间", "emoji": "🍽️", "items": [
        ("Sit at the table.", "坐到桌边。", "🪑"), ("Put your napkin on.", "放好餐巾。", "🧻"),
        ("Use your spoon.", "用你的勺子。", "🥄"), ("Use your fork.", "用你的叉子。", "🍴"),
        ("Pick up your chopsticks.", "拿起筷子。", "🥢"), ("Eat your rice.", "吃你的米饭。", "🍚"),
        ("Drink your soup.", "喝你的汤。", "🥣"), ("Chew your food.", "嚼一嚼食物。", "😬"),
        ("Say yummy!", "说真好吃！", "😋"), ("Wipe the table.", "擦擦桌子。", "🧹"),
        ("Put away your bowl.", "收好碗。", "🥣"), ("Wash the dishes.", "洗洗盘子。", "🍽️"),
        ("Have a nap.", "睡个午觉。", "😴"), ("Share your food.", "分享你的食物。", "🤝"),
        ("Don't spill it.", "别洒了。", "⚠️"), ("Drink some water.", "喝点水。", "💧"),
    ]},
    {"id": "kt5", "title": "游戏课堂", "emoji": "🎈", "items": [
        ("Raise your hand.", "举起你的手。", "🙋"), ("Stand up.", "站起来。", "🧍"),
        ("Sit down.", "坐下。", "🪑"), ("Listen to me.", "听我说。", "👂"),
        ("Look at me.", "看着我。", "👀"), ("Point to the cat.", "指指小猫。", "🐱"),
        ("Touch your nose.", "摸摸你的鼻子。", "👃"), ("Clap your hands.", "拍拍你的手。", "👏"),
        ("Stamp your feet.", "跺跺你的脚。", "🦶"), ("Jump up!", "跳起来！", "🦘"),
        ("Turn around.", "转个圈。", "🔄"), ("Sing a song.", "唱首歌。", "🎤"),
        ("Say hello.", "说你好。", "👋"), ("Draw a picture.", "画幅画。", "✏️"),
        ("Colour it red.", "涂成红色。", "🔴"), ("Clean up!", "收拾好！", "🧹"),
    ]},
]

# ---------------- 3. 自然拼读（26 字母 + CVC） ----------------
LETTERS = [
    ("A", "A", "a", "/æ/", "apple", "苹果"), ("B", "B", "b", "/b/", "ball", "球"),
    ("C", "C", "c", "/k/", "cat", "猫"), ("D", "D", "d", "/d/", "dog", "狗"),
    ("E", "E", "e", "/e/", "egg", "鸡蛋"), ("F", "F", "f", "/f/", "fish", "鱼"),
    ("G", "G", "g", "/ɡ/", "goat", "山羊"), ("H", "H", "h", "/h/", "hat", "帽子"),
    ("I", "I", "i", "/ɪ/", "ink", "墨水"), ("J", "J", "j", "/dʒ/", "juice", "果汁"),
    ("K", "K", "k", "/k/", "kite", "风筝"), ("L", "L", "l", "/l/", "lion", "狮子"),
    ("M", "M", "m", "/m/", "milk", "牛奶"), ("N", "N", "n", "/n/", "nose", "鼻子"),
    ("O", "O", "o", "/ɒ/", "orange", "橙子"), ("P", "P", "p", "/p/", "pig", "猪"),
    ("Q", "Q", "q", "/kw/", "queen", "女王"), ("R", "R", "r", "/r/", "rabbit", "兔子"),
    ("S", "S", "s", "/s/", "sun", "太阳"), ("T", "T", "t", "/t/", "tiger", "老虎"),
    ("U", "U", "u", "/ʌ/", "umbrella", "雨伞"), ("V", "V", "v", "/v/", "van", "货车"),
    ("W", "W", "w", "/w/", "water", "水"), ("X", "X", "x", "/ks/", "box", "盒子"),
    ("Y", "Y", "y", "/j/", "yellow", "黄色"), ("Z", "Z", "z", "/z/", "zebra", "斑马"),
]
SONG_TEXT = "A, B, C, D, E, F, G. H, I, J, K, L, M, N. O, P, Q. R, S, T. U, V, W, X, Y, Z. Now I know my ABC. Next time won't you sing with me."
CVC_WORDS = [
    ("cat", "/kæt/", "猫"), ("hat", "/hæt/", "帽子"), ("dog", "/dɒɡ/", "狗"),
    ("pig", "/pɪɡ/", "猪"), ("sun", "/sʌn/", "太阳"), ("bed", "/bed/", "床"),
    ("pen", "/pen/", "钢笔"), ("bus", "/bʌs/", "公交车"),
]

# ---------------- 4. 迷你绘本（8 本 × 6 句） ----------------
BOOKS = [
    {"id": "kr1", "title": "My Cat", "zhTitle": "我的小猫", "emoji": "🐱", "pages": [
        ("This is my cat.", "这是我的猫。"), ("My cat is small.", "我的猫很小。"),
        ("My cat is white.", "我的猫是白色的。"), ("My cat can jump.", "我的猫会跳。"),
        ("My cat says meow.", "我的猫说喵喵。"), ("I love my cat.", "我爱我的猫。"),
    ]},
    {"id": "kr2", "title": "Colours Around Me", "zhTitle": "身边的颜色", "emoji": "🌈", "pages": [
        ("I see a red apple.", "我看见一个红苹果。"), ("I see a yellow sun.", "我看见一个黄太阳。"),
        ("I see a blue sky.", "我看见蓝蓝的天。"), ("I see a green tree.", "我看见一棵绿树。"),
        ("I see a pink flower.", "我看见一朵粉花。"), ("Colours are so pretty.", "颜色真漂亮。"),
    ]},
    {"id": "kr3", "title": "I Can Run", "zhTitle": "我会跑", "emoji": "🏃", "pages": [
        ("I can run.", "我会跑。"), ("I can jump.", "我会跳。"),
        ("I can clap my hands.", "我会拍手。"), ("I can stamp my feet.", "我会跺脚。"),
        ("I can sing a song.", "我会唱歌。"), ("I can do it all day.", "我能玩一整天。"),
    ]},
    {"id": "kr4", "title": "Good Morning", "zhTitle": "早上好", "emoji": "☀️", "pages": [
        ("Good morning, Mum.", "早上好，妈妈。"), ("Good morning, Dad.", "早上好，爸爸。"),
        ("I open my eyes.", "我睁开眼睛。"), ("I wash my face.", "我洗脸。"),
        ("I brush my teeth.", "我刷牙。"), ("I am ready for the day.", "我准备好过这一天了。"),
    ]},
    {"id": "kr5", "title": "My Family", "zhTitle": "我的家", "emoji": "👨‍👩‍👧", "pages": [
        ("This is my family.", "这是我的家。"), ("This is my mum.", "这是我的妈妈。"),
        ("This is my dad.", "这是我的爸爸。"), ("This is my sister.", "这是我的姐姐。"),
        ("We laugh together.", "我们一起笑。"), ("I love my family.", "我爱我的家。"),
    ]},
    {"id": "kr6", "title": "At the Park", "zhTitle": "在公园", "emoji": "🌳", "pages": [
        ("Let's go to the park.", "我们去公园吧。"), ("I see a big tree.", "我看见一棵大树。"),
        ("I see a little bird.", "我看见一只小鸟。"), ("I play on the slide.", "我玩滑梯。"),
        ("I run on the grass.", "我在草地上跑。"), ("I am so happy.", "我太开心了。"),
    ]},
    {"id": "kr7", "title": "Bedtime", "zhTitle": "睡觉时间", "emoji": "🌙", "pages": [
        ("It is night time.", "到晚上了。"), ("The moon is bright.", "月亮很亮。"),
        ("I take a bath.", "我洗个澡。"), ("I put on my pyjamas.", "我穿上睡衣。"),
        ("Mum reads me a book.", "妈妈给我读书。"), ("Good night, sleep tight.", "晚安，睡个好觉。"),
    ]},
    {"id": "kr8", "title": "Yummy Food", "zhTitle": "美味的食物", "emoji": "🍎", "pages": [
        ("I like apples.", "我喜欢苹果。"), ("I like bananas.", "我喜欢香蕉。"),
        ("I drink milk.", "我喝牛奶。"), ("I eat an egg.", "我吃鸡蛋。"),
        ("Yummy, yummy, yummy!", "好吃，好吃，真好吃！"), ("I like all my food.", "我喜欢我所有的食物。"),
    ]},
]

# ---------------- 构建 JSON ----------------
def build_songs():
    songs = []
    for s in SONGS:
        lines = []
        for i, (en, zh) in enumerate(s["lines"], 1):
            fid = s["id"] + "s%02d" % i
            lines.append({"id": fid, "en": en, "zh": zh, "audio": "/audio/ks/" + fid + ".mp3"})
        songs.append({"id": s["id"], "title": s["title"], "zhTitle": s["zhTitle"],
                      "emoji": s["emoji"], "theme": s["theme"], "lines": lines,
                      "fullAudio": "/audio/ks/" + s["id"] + "f.mp3"})
    return {"product": "幼儿启蒙英语 · 儿歌磨耳朵", "version": "1.0", "schema_version": "1.0",
            "note": "10 首原创韵律儿歌：整首跟唱 + 逐句点读，歌词中文对照（可理解性输入）",
            "songs": songs}

def build_tpr():
    groups = []
    for g in TPR_GROUPS:
        items = []
        for i, (en, zh, emoji) in enumerate(g["items"], 1):
            fid = g["id"] + "%02d" % i
            items.append({"id": fid, "en": en, "zh": zh, "emoji": emoji,
                          "audio": "/audio/kt/" + fid + ".mp3"})
        groups.append({"id": g["id"], "title": g["title"], "emoji": g["emoji"], "items": items})
    return {"product": "幼儿启蒙英语 · TPR 日常指令", "version": "1.0", "schema_version": "1.0",
            "note": "5 组 × 16 条日常指令：听指令做动作（TPR 教学法），家长零基础可陪玩",
            "groups": groups}

def build_phonics():
    letters = []
    for i, (upper, lower, name, sound, word, zh) in enumerate(LETTERS):
        lid = "kp%02d" % (i + 1)
        letters.append({
            "id": lid, "upper": upper, "lower": lower, "name": name, "sound": sound,
            "word": word, "zh": zh,
            "nameAudio": "/audio/kp/" + lid + "n.mp3",
            "soundAudio": "/audio/kp/" + lid + "s.mp3",
            "wordAudio": "/audio/kp/" + lid + "w.mp3",
        })
    cvc = []
    for i, (word, phon, zh) in enumerate(CVC_WORDS):
        cid = "kc%02d" % (i + 1)
        cvc.append({"id": cid, "word": word, "phonetic": phon, "zh": zh,
                    "audio": "/audio/kp/" + cid + ".mp3"})
    return {"product": "幼儿启蒙英语 · 自然拼读启蒙", "version": "1.0", "schema_version": "1.0",
            "note": "26 个字母名/字母音 + 字母歌 + CVC 拼读入门（对标牛津拼读体系轻量版）",
            "song": {"text": SONG_TEXT, "audio": "/audio/kp/ksong.mp3"},
            "letters": letters, "cvc": cvc}

def build_reading():
    books = []
    for b in BOOKS:
        pages = []
        for i, (en, zh) in enumerate(b["pages"], 1):
            fid = b["id"] + "%02d" % i
            pages.append({"id": fid, "en": en, "zh": zh, "audio": "/audio/kr/" + fid + ".mp3"})
        books.append({"id": b["id"], "title": b["title"], "zhTitle": b["zhTitle"],
                      "emoji": b["emoji"], "pages": pages})
    return {"product": "幼儿启蒙英语 · 迷你绘本", "version": "1.0", "schema_version": "1.0",
            "note": "8 本迷你绘本：整句点读 + 中文对照，起步阅读（衔接小学分级阅读）",
            "books": books}

def gen():
    payloads = [("kids_songs.json", build_songs()), ("kids_tpr.json", build_tpr()),
                ("kids_phonics.json", build_phonics()), ("kids_reading.json", build_reading())]
    for fn, payload in payloads:
        with io.open(os.path.join(DATA, fn), 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print('已生成', fn)
    # 素材库 md
    os.makedirs(MAT_DIR, exist_ok=True)
    _md_songs(); _md_tpr(); _md_phonics(); _md_reading()
    print('素材库 md ×4 已写入（AI 初稿，待创始人人工校对）')

def _md_songs():
    lines = ['# 幼儿启蒙英语 · 儿歌歌词本（10 首）', '',
             '> 数据源：3-6 岁原创韵律儿歌，可理解性输入（整首跟唱 + 逐句点读）',
             '> 标注：内容由 AI 生成，待创始人人工校对（红线条款）。', '']
    for s in SONGS:
        lines += ['## %s %s · %s（%s）' % (s['emoji'], s['title'], s['zhTitle'], s['theme']), '']
        for i, (en, zh) in enumerate(s['lines'], 1):
            lines.append('%d. %s ｜ %s（音频 ks%s%02d.mp3 / 整首 ks%sf.mp3）' % (i, en, zh, s['id'], i, s['id']))
        lines.append('')
    with io.open(os.path.join(MAT_DIR, '幼儿启蒙英语-儿歌歌词本.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

def _md_tpr():
    lines = ['# 幼儿启蒙英语 · TPR 日常指令卡（80 条）', '',
             '> 数据源：TPR 教学法（Total Physical Response），听指令做动作，家长零基础可陪玩',
             '> 标注：内容由 AI 生成，待创始人人工校对（红线条款）。', '']
    for g in TPR_GROUPS:
        lines += ['## %s %s（%s）' % (g['emoji'], g['title'], g['id']), '']
        for i, (en, zh, emoji) in enumerate(g['items'], 1):
            lines.append('%d. %s %s ｜ %s（音频 %s%02d.mp3）' % (i, emoji, en, zh, g['id'], i))
        lines.append('')
    with io.open(os.path.join(MAT_DIR, '幼儿启蒙英语-TPR指令卡.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

def _md_phonics():
    lines = ['# 幼儿启蒙英语 · 自然拼读启蒙（26 字母 + CVC）', '',
             '> 数据源：对标 Oxford Phonics World 轻量版：字母名 → 字母音 → 单词 → CVC 拼读',
             '> 标注：内容由 AI 生成，待创始人人工校对（红线条款）。', '',
             '## 字母歌', '', SONG_TEXT, '', '## 26 个字母音', '',
             '| 字母 | 字母音 | 示例词 | 词义 | 音频 |', '| --- | --- | --- | --- | --- |']
    for i, (upper, lower, name, sound, word, zh) in enumerate(LETTERS, 1):
        lines.append('| %s%s | %s | %s | %s | kp%02d n/s/w.mp3 |' % (upper, lower, sound, word, zh, i))
    lines += ['', '## CVC 拼读入门', '', '| 单词 | 音标 | 词义 | 音频 |', '| --- | --- | --- | --- |']
    for i, (word, phon, zh) in enumerate(CVC_WORDS, 1):
        lines.append('| %s | %s | %s | kc%02d.mp3 |' % (word, phon, zh, i))
    with io.open(os.path.join(MAT_DIR, '幼儿启蒙英语-自然拼读启蒙.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

def _md_reading():
    lines = ['# 幼儿启蒙英语 · 迷你绘本（8 本）', '',
             '> 数据源：起步阅读绘本，每本 6 句，整句点读 + 中文对照',
             '> 标注：内容由 AI 生成，待创始人人工校对（红线条款）。', '']
    for b in BOOKS:
        lines += ['## %s %s · %s' % (b['emoji'], b['title'], b['zhTitle']), '']
        for i, (en, zh) in enumerate(b['pages'], 1):
            lines.append('%d. %s ｜ %s（音频 %s%02d.mp3）' % (i, en, zh, b['id'], i))
        lines.append('')
    with io.open(os.path.join(MAT_DIR, '幼儿启蒙英语-迷你绘本.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

# ---------------- 音频 ----------------
def get_ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()

def normalize_audio(path):
    ff = get_ffmpeg()
    tmp = path + '.fix.mp3'
    subprocess.run([ff, '-y', '-i', path, '-ar', '44100', '-ac', '1', '-b:a', '128k',
                    '-f', 'mp3', tmp], check=True, capture_output=True)
    os.replace(tmp, path)

async def _tts(text, out):
    tmp = out + '.raw.mp3'
    await edge_tts.Communicate(text, VOICE, rate=RATE).save(tmp)
    normalize_audio(tmp)
    os.replace(tmp, out)

async def gen_audio():
    dirs = {'ks': os.path.join(ROOT, 'public', 'audio', 'ks'),
            'kt': os.path.join(ROOT, 'public', 'audio', 'kt'),
            'kp': os.path.join(ROOT, 'public', 'audio', 'kp'),
            'kr': os.path.join(ROOT, 'public', 'audio', 'kr')}
    for d in dirs.values():
        os.makedirs(d, exist_ok=True)
    plan = []
    # 儿歌：逐句 + 整首
    for s in SONGS:
        full = []
        for i, (en, zh) in enumerate(s['lines'], 1):
            fid = s['id'] + 's%02d' % i
            plan.append((os.path.join(dirs['ks'], fid + '.mp3'), en))
            full.append(en)
        plan.append((os.path.join(dirs['ks'], s['id'] + 'f.mp3'), ' '.join(full)))
    # TPR
    for g in TPR_GROUPS:
        for i, (en, zh, emoji) in enumerate(g['items'], 1):
            plan.append((os.path.join(dirs['kt'], g['id'] + '%02d' % i + '.mp3'), en))
    # 拼读：字母名/音/词 + 字母歌 + CVC
    for i, (upper, lower, name, sound, word, zh) in enumerate(LETTERS, 1):
        lid = 'kp%02d' % i
        plan.append((os.path.join(dirs['kp'], lid + 'n.mp3'), name))
        plan.append((os.path.join(dirs['kp'], lid + 's.mp3'), sound))
        plan.append((os.path.join(dirs['kp'], lid + 'w.mp3'), word))
    plan.append((os.path.join(dirs['kp'], 'ksong.mp3'), SONG_TEXT))
    for i, (word, phon, zh) in enumerate(CVC_WORDS, 1):
        plan.append((os.path.join(dirs['kp'], 'kc%02d' % i + '.mp3'), word))
    # 绘本
    for b in BOOKS:
        for i, (en, zh) in enumerate(b['pages'], 1):
            plan.append((os.path.join(dirs['kr'], b['id'] + '%02d' % i + '.mp3'), en))
    total = len(plan)
    print('音频计划总数:', total)
    for i, (out, text) in enumerate(plan, 1):
        if os.path.exists(out):
            print('[%d/%d] 跳过 %s' % (i, total, os.path.basename(out)))
            continue
        await _tts(text, out)
        print('[%d/%d] OK %s' % (i, total, os.path.basename(out)))
    print('全部音频完成:', total)

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'gen'
    if cmd in ('gen', 'all'):
        gen()
    if cmd in ('audio', 'all'):
        asyncio.run(gen_audio())
