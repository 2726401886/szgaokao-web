# -*- coding: utf-8 -*-
"""幼儿启蒙英语听说题库 · 数据源驱动生成脚本
生成：
  1) data/kids_listening.json（4 卷 × 10 题，听单词/听句子选答）
  2) public/audio/kl/kl1NN.mp3 听力音频（英音女声慢速）
用法：
  python tools/gen_kids_listening.py gen
  python tools/gen_kids_listening.py audio
"""
import asyncio, io, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
AUDIO_KL = os.path.join(ROOT, 'public', 'audio', 'kl')
VOICE = 'en-GB-SoniaNeural'
RATE = '-12%'

# (id, 听力文本, 题干, [选项], 正确答案下标, 解析)
VOLUMES = [
    {"id": "kl1", "title": "问候与打招呼", "desc": "Hello, Good morning, How are you? 日常问候",
     "questions": [
         ("Hello! How are you?", "听句子，选出正确的回应", ["I am fine, thank you.", "Goodbye.", "I am a cat."], 0, "别人问 How are you，回答 I am fine, thank you."),
         ("Good morning, Mum.", "听句子，选出正确的中文意思", ["早上好，妈妈。", "晚安，妈妈。", "再见，妈妈。"], 0, "Good morning 是早上好。" ),
         ("Goodbye, see you tomorrow.", "听句子，选出正确的中文意思", ["再见，明天见。", "你好，明天见。", "谢谢，明天见。"], 0, "Goodbye 是再见；see you tomorrow 是明天见。"),
         ("What is your name?", "听句子，选出正确的回应", ["My name is Lily.", "I am six.", "I like milk."], 0, "问名字用 What is your name，回答 My name is..."),
         ("How old are you?", "听句子，选出正确的回应", ["I am five years old.", "My name is Tom.", "I am a boy."], 0, "How old 问年龄，回答 I am five years old."),
         ("Nice to meet you.", "听句子，选出正确的回应", ["Nice to meet you, too.", "Thank you.", "Good night."], 0, "Nice to meet you 的回应是 Nice to meet you, too."),
         ("Thank you very much.", "听句子，选出正确的中文意思", ["非常感谢你。", "对不起。", "没关系。"], 0, "Thank you very much 是非常感谢。"),
         ("Good night, baby.", "听句子，选出正确的中文意思", ["晚安，宝贝。", "早上好，宝贝。", "生日快乐，宝贝。"], 0, "Good night 是晚安。"),
         ("How do you do?", "听句子，选出正确的回应", ["How do you do?", "I am fine.", "Goodbye."], 0, "How do you do 是正式问候，回应也是 How do you do."),
         ("Welcome to our class.", "听句子，选出正确的中文意思", ["欢迎来到我们班。", "欢迎来我家。", "再见我们班。"], 0, "Welcome 是欢迎；our class 是我们班。"),
     ]},
    {"id": "kl2", "title": "动物乐园", "desc": "听动物单词与简单句，认识小动物",
     "questions": [
         ("cat", "听单词，选出正确的动物", ["猫", "狗", "鸟"], 0, "cat 是猫，喵喵叫的动物。"),
         ("dog", "听单词，选出正确的动物", ["狗", "鸭子", "鱼"], 0, "dog 是狗，会汪汪叫。"),
         ("duck", "听单词，选出正确的动物", ["鸭子", "猪", "羊"], 0, "duck 是鸭子，会嘎嘎叫。"),
         ("The monkey is eating a banana.", "听句子，选出正确的动物", ["猴子", "老虎", "大象"], 0, "monkey 是猴子，喜欢吃香蕉。"),
         ("The rabbit has long ears.", "听句子，选出正确的动物", ["兔子", "马", "蜜蜂"], 0, "rabbit 是兔子，有长长的耳朵。"),
         ("bird", "听单词，选出正确的动物", ["鸟", "青蛙", "老鼠"], 0, "bird 是鸟，会飞。"),
         ("elephant", "听单词，选出正确的动物", ["大象", "狮子", "熊猫"], 0, "elephant 是大象，有长长的鼻子。"),
         ("The panda is black and white.", "听句子，选出正确的动物", ["熊猫", "奶牛", "老虎"], 0, "panda 是熊猫，黑白相间。"),
         ("The bee makes honey.", "听句子，选出正确的动物", ["蜜蜂", "蝴蝶", "蚂蚁"], 0, "bee 是蜜蜂，会酿蜂蜜。"),
         ("The fish is swimming in the water.", "听句子，选出正确的动物", ["鱼", "鸟", "猫"], 0, "fish 是鱼，在水里游。"),
     ]},
    {"id": "kl3", "title": "颜色与数字", "desc": "听颜色单词与数字，认识红蓝黄绿",
     "questions": [
         ("red", "听单词，选出正确的颜色", ["红色", "蓝色", "绿色"], 0, "red 是红色。"),
         ("blue", "听单词，选出正确的颜色", ["蓝色", "黄色", "黑色"], 0, "blue 是蓝色，像天空。"),
         ("green", "听单词，选出正确的颜色", ["绿色", "白色", "紫色"], 0, "green 是绿色，像小草。"),
         ("The sky is blue.", "听句子，选出正确的颜色", ["蓝色", "红色", "橙色"], 0, "sky 是天空，天空是 blue 蓝色。"),
         ("The apple is red.", "听句子，选出正确的颜色", ["红色", "绿色", "黄色"], 0, "apple 苹果是 red 红色。"),
         ("five", "听单词，选出正确的数字", ["五", "三", "七"], 0, "five 是五。"),
         ("ten", "听单词，选出正确的数字", ["十", "六", "八"], 0, "ten 是十。"),
         ("I have three cats.", "听句子，选出正确的数字", ["三", "五", "九"], 0, "three 是三，我有三只猫。"),
         ("She has two hands.", "听句子，选出正确的数字", ["二", "四", "六"], 0, "two 是二，她有两只手。"),
         ("I am seven years old.", "听句子，选出正确的数字", ["七", "五", "十"], 0, "seven 是七，我七岁了。"),
     ]},
    {"id": "kl4", "title": "食物与喜好", "desc": "听食物单词与喜好问答，I like / I don't like",
     "questions": [
         ("apple", "听单词，选出正确的食物", ["苹果", "香蕉", "蛋糕"], 0, "apple 是苹果。"),
         ("milk", "听单词，选出正确的食物", ["牛奶", "果汁", "茶"], 0, "milk 是牛奶。"),
         ("I like bananas.", "听句子，选出正确的意思", ["我喜欢香蕉。", "我不喜欢香蕉。", "我要香蕉。"], 0, "I like 是我喜欢。"),
         ("Do you like milk?", "听句子，选出正确的回应", ["Yes, I do.", "Yes, it is.", "Thank you."], 0, "Do you like...? 用 Yes, I do. / No, I don't. 回答。"),
         ("I don't like candy.", "听句子，选出正确的意思", ["我不喜欢糖果。", "我喜欢糖果。", "我想要糖果。"], 0, "I don't like 是我不喜欢。"),
         ("Would you like some tea?", "听句子，选出正确的回应", ["Yes, please.", "Yes, I do.", "No, thank you is wrong."], 0, "Would you like...? 礼貌回应 Yes, please."),
         ("The cake is sweet.", "听句子，选出正确的意思", ["蛋糕是甜的。", "蛋糕是酸的。", "蛋糕是咸的。"], 0, "sweet 是甜的。"),
         ("I eat an egg every day.", "听句子，选出正确的意思", ["我每天吃一个鸡蛋。", "我每天喝牛奶。", "我每天吃苹果。"], 0, "eat an egg 是吃鸡蛋；every day 是每天。"),
         ("ice cream", "听单词，选出正确的食物", ["冰淇淋", "饼干", "面条"], 0, "ice cream 是冰淇淋。"),
         ("Noodles are my favourite food.", "听句子，选出正确的意思", ["面条是我最喜欢的食物。", "米饭是我最喜欢的食物。", "面包是我最喜欢的食物。"], 0, "favourite 是最喜欢的；noodles 是面条。"),
     ]},
]


def build_payload():
    vols = []
    for v in VOLUMES:
        qs = []
        for i, (txt, q, opts, ans, tip) in enumerate(v["questions"], 1):
            qid = v["id"] + ('%02d' % i)
            qs.append({"id": qid, "type": "listen-word" if len(txt.split()) <= 2 else "listen-sentence",
                       "q": q, "audio": "/audio/kl/" + qid + ".mp3", "audioText": txt,
                       "options": opts, "answer": ans, "tip": tip})
        vols.append({"id": v["id"], "title": v["title"], "desc": v["desc"], "questions": qs})
    return {"product": "幼儿启蒙英语听说题库", "version": "1.0", "schema_version": "1.0",
            "note": "3-6 岁听说启蒙：单词听力 + 短句听力，英音慢速",
            "volumes": vols}


def gen():
    payload = build_payload()
    os.makedirs(DATA, exist_ok=True)
    with io.open(os.path.join(DATA, 'kids_listening.json'), 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print('kids_listening.json 已生成；卷数:', len(VOLUMES), '题数:', sum(len(v['questions']) for v in VOLUMES))


def get_ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def normalize_audio(path):
    ff = get_ffmpeg()
    tmp = path + '.fix.mp3'
    subprocess.run([ff, '-y', '-i', path, '-ar', '44100', '-ac', '1', '-b:a', '128k',
                    '-f', 'mp3', tmp], check=True, capture_output=True)
    os.replace(tmp, path)


async def gen_audio():
    import edge_tts
    os.makedirs(AUDIO_KL, exist_ok=True)
    plan = []
    for v in VOLUMES:
        for i, (txt, q, opts, ans, tip) in enumerate(v["questions"], 1):
            plan.append((v["id"] + ('%02d' % i), txt))
    total = len(plan)
    for i, (fid, txt) in enumerate(plan, 1):
        out = os.path.join(AUDIO_KL, fid + '.mp3')
        if os.path.exists(out):
            print('[%d/%d] 跳过 %s' % (i, total, fid))
            continue
        tmp = out + '.raw.mp3'
        await edge_tts.Communicate(txt, VOICE, rate=RATE).save(tmp)
        normalize_audio(tmp)
        os.replace(tmp, out)
        print('[%d/%d] OK %s' % (i, total, fid))
    print('幼儿听说音频完成:', total)


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'gen'
    if cmd in ('gen', 'all'):
        gen()
    if cmd in ('audio', 'all'):
        asyncio.run(gen_audio())
