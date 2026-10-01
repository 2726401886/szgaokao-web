# -*- coding: utf-8 -*-
"""分级阅读起步生成脚本（3 级 × 4 篇 = 12 篇短文 + 生词 + 理解题）
生成：
  1) data/graded_reading.json（本地）+ E:\\szgaokao.cn\\worker\\src\\graded_reading.json（线上）
  2) 素材库《小学英语-分级阅读起步-3级12篇.md》
  3) public/audio/rd/ 短文朗读+生词音频（英音女声，增量跳过）
用法：python tools/gen_graded_reading.py gen / audio / all
"""
import asyncio
import io
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
PUB = os.path.join(ROOT, 'public')
AUDIO_RD = os.path.join(PUB, 'audio', 'rd')
WORKER_SRC = r'E:\szgaokao.cn\worker\src'
MATERIAL_MD = r'C:\Users\27264\WorkBuddy\2026-09-26-21-53-51\english-edu-company\03交付素材库\听说试卷包\小学英语-分级阅读起步-3级12篇.md'

VOICE = 'en-GB-SoniaNeural'
RATE = '-10%'

# 数据源：3 级 × 4 篇短文（title, text, words[词/义], questions[2-3 题]）
LEVELS = [
    {"id": "r1", "name": "起步级", "desc": "适合 3-4 年级 · 每篇约 80 词",
     "articles": [
        {"id": "r1a1", "title": "My School Day",
         "text": "Hello! I am Ben. I am eight years old. I go to school at seven thirty. We have English, math and music today. At noon, I have lunch with my friends. After school, I play football in the playground. I love my school.",
         "words": [("school","学校"),("lunch","午餐"),("friends","朋友们"),("playground","操场"),("love","爱")],
         "questions": [
            ("Ben 几岁了？", ["七岁", "八岁", "九岁"], 1, "I am eight years old."),
            ("放学后 Ben 做什么？", ["踢足球", "读书", "画画"], 0, "After school, I play football."),
            ("Ben 喜欢学校吗？", ["喜欢", "不喜欢", "不确定"], 0, "I love my school."),
         ]},
        {"id": "r1a2", "title": "My Pet Dog",
         "text": "I have a pet dog. Its name is Lucky. Lucky is white and brown. It has big eyes and a long tail. Lucky likes to run and jump. It likes eating bones. I play with Lucky every day. It is my best friend.",
         "words": [("pet","宠物"),("tail","尾巴"),("bones","骨头"),("best","最好的"),("friend","朋友")],
         "questions": [
            ("狗叫什么名字？", ["Lucky", "Ben", "Tom"], 0, "Its name is Lucky."),
            ("Lucky 喜欢做什么？", ["跑和跳", "睡觉", "游泳"], 0, "Lucky likes to run and jump."),
            ("狗喜欢吃什么？", ["骨头", "米饭", "苹果"], 0, "eating bones 吃骨头。"),
         ]},
        {"id": "r1a3", "title": "At the Zoo",
         "text": "Today is Sunday. We go to the zoo. There are many animals. The monkeys are funny. They jump and climb. The pandas are fat and cute. They eat bamboo. The elephants are very big. I like the monkeys best.",
         "words": [("zoo","动物园"),("monkeys","猴子"),("pandas","熊猫"),("bamboo","竹子"),("elephants","大象")],
         "questions": [
            ("他们去了哪里？", ["动物园", "公园", "博物馆"], 0, "go to the zoo."),
            ("熊猫吃什么？", ["竹子", "香蕉", "鱼"], 0, "They eat bamboo."),
            ("作者最喜欢什么动物？", ["猴子", "熊猫", "大象"], 0, "I like the monkeys best."),
         ]},
        {"id": "r1a4", "title": "The Weather",
         "text": "Look at the sky. It is cloudy today. The wind is blowing. Mum says it will rain soon. I take my umbrella to school. In the afternoon, it rains. After the rain, the sky is blue and clean. The flowers are beautiful.",
         "words": [("cloudy","多云的"),("wind","风"),("rain","雨"),("umbrella","雨伞"),("flowers","花朵")],
         "questions": [
            ("今天的天气怎么样？", ["多云", "下雪", "晴朗"], 0, "It is cloudy today."),
            ("谁说要下雨了？", ["妈妈", "爸爸", "老师"], 0, "Mum says it will rain."),
            ("下雨后天空怎么样？", ["蓝而干净", "灰暗", "有彩虹"], 0, "the sky is blue and clean."),
         ]},
     ]},
    {"id": "r2", "name": "进阶级", "desc": "适合 4-5 年级 · 每篇约 110 词",
     "articles": [
        {"id": "r2a1", "title": "My Favourite Season",
         "text": "There are four seasons in a year. My favourite season is autumn. The weather is cool and nice. The leaves turn yellow and red. They fall from the trees. I like to collect the beautiful leaves. In autumn, we also have the Mid-Autumn Festival. My family eats mooncakes and watches the bright moon together. It is a happy time.",
         "words": [("season","季节"),("autumn","秋天"),("leaves","叶子"),("collect","收集"),("mooncakes","月饼")],
         "questions": [
            ("作者最喜欢的季节是？", ["秋天", "夏天", "春天"], 0, "favourite season is autumn."),
            ("秋天树叶变成什么颜色？", ["黄和红", "绿和蓝", "白和黑"], 0, "turn yellow and red."),
            ("中秋节他们做什么？", ["吃月饼看月亮", "放鞭炮", "吃粽子"], 0, "eats mooncakes and watches the moon."),
         ]},
        {"id": "r2a2", "title": "Helping at Home",
         "text": "I am a helpful child. I help my mother at home. After dinner, I wash the dishes. On weekends, I clean my room and sweep the floor. I also water the flowers on the balcony. My parents are happy. They say I am a good boy. Helping at home makes me happy too.",
         "words": [("helpful","乐于助人的"),("dishes","碗碟"),("sweep","扫地"),("balcony","阳台"),("parents","父母")],
         "questions": [
            ("作者帮妈妈做什么？", ["洗碗", "做饭", "洗衣"], 0, "I wash the dishes."),
            ("周末他做什么？", ["打扫房间扫地", "去公园玩", "看电视"], 0, "clean my room and sweep the floor."),
            ("父母觉得作者怎么样？", ["好孩子", "淘气", "懒惰"], 0, "a good boy."),
         ]},
        {"id": "r2a3", "title": "Going to the Museum",
         "text": "Last Saturday, my family went to the Science Museum. It is near the city centre. We saw robots, dinosaurs and space things. The robots could dance and talk. I asked many questions. The guide was very kind. She told us the history of the museum. We had a wonderful time there.",
         "words": [("museum","博物馆"),("robots","机器人"),("dinosaurs","恐龙"),("guide","讲解员"),("wonderful","精彩的")],
         "questions": [
            ("他们去了哪个博物馆？", ["科学博物馆", "历史博物馆", "美术博物馆"], 0, "Science Museum."),
            ("机器人会做什么？", ["跳舞说话", "飞行", "游泳"], 0, "dance and talk."),
            ("讲解员怎么样？", ["善良友好", "严厉", "沉默"], 0, "was very kind."),
         ]},
        {"id": "r2a4", "title": "Healthy Food",
         "text": "Eating healthy food is important. Fruit and vegetables are good for us. They give us vitamins. Milk and eggs make our bones strong. We should drink water every day. But we shouldn't eat too many sweets or chips. They are bad for our teeth. A healthy diet helps us study well and play well.",
         "words": [("important","重要的"),("vitamins","维生素"),("strong","强壮的"),("sweets","糖果"),("diet","饮食")],
         "questions": [
            ("什么对健康有好处？", ["水果蔬菜", "糖果薯片", "汽水"], 0, "Fruit and vegetables are good."),
            ("牛奶和鸡蛋有什么作用？", ["让骨骼强壮", "让头发变黑", "让眼睛明亮"], 0, "make our bones strong."),
            ("我们应该少吃什么？", ["糖果薯片", "水果", "牛奶"], 0, "shouldn't eat too many sweets."),
         ]},
     ]},
    {"id": "r3", "name": "提升级", "desc": "适合 5-6 年级 · 每篇约 140 词",
     "articles": [
        {"id": "r3a1", "title": "The Little Hero",
         "text": "Tom is a ten-year-old boy. One day, he saw smoke from the house next door. He ran to the house and shouted, \"Fire! Fire!\" People came quickly and called 119. The firemen arrived soon and put out the fire. An old woman was inside. She was saved in time. The reporter asked Tom, \"Weren't you afraid?\" Tom said, \"I just wanted to help.\" Everyone praised Tom. He is a little hero.",
         "words": [("smoke","烟雾"),("shouted","大喊"),("firemen","消防员"),("saved","获救"),("hero","英雄")],
         "questions": [
            ("Tom 看到了什么？", ["烟雾", "火光", "小偷"], 0, "saw smoke from the house."),
            ("谁救了老奶奶？", ["消防员", "Tom 自己", "警察"], 0, "The firemen... She was saved."),
            ("Tom 为什么去救火？", ["想帮忙", "想出名", "被要求"], 0, "I just wanted to help."),
         ]},
        {"id": "r3a2", "title": "A Special Gift",
         "text": "Tomorrow is my mother's birthday. I want to give her a special gift. I have no money, so I decide to make a card myself. I draw a big flower and write \"Happy Birthday, Mum!\" on the card. In the evening, I also help Mum wash the dishes and clean the house. When Mum sees the card, she smiles happily. She says it is the best gift in the world.",
         "words": [("gift","礼物"),("birthday","生日"),("decide","决定"),("card","贺卡"),("smiles","微笑")],
         "questions": [
            ("作者为什么自己做贺卡？", ["没有钱买", "喜欢画画", "商店关门"], 0, "I have no money."),
            ("作者还在晚上做了什么？", ["帮忙洗碗打扫", "出去买礼物", "看电视"], 0, "wash the dishes and clean."),
            ("妈妈觉得贺卡怎么样？", ["世界上最好的礼物", "一般", "不够好"], 0, "the best gift in the world."),
         ]},
        {"id": "r3a3", "title": "Protect the Earth",
         "text": "The Earth is our home. But today, our Earth is in danger. The rivers are dirty and the air is not clean. Many animals lose their homes because forests are cut down. We should do something. We can save water and electricity. We can ride bikes instead of driving cars. We can plant trees and recycle rubbish. Small actions make a big difference. Let's protect the Earth together.",
         "words": [("danger","危险"),("forests","森林"),("electricity","电"),("recycle","回收"),("difference","改变")],
         "questions": [
            ("地球面临什么问题？", ["河流脏空气不干净", "人口太少", "天气太热"], 0, "rivers are dirty, air is not clean."),
            ("我们可以怎么做？", ["节水节电", "多开车", "砍树"], 0, "save water and electricity."),
            ("短文告诉我们什么道理？", ["小行动带来大改变", "保护地球很难", "地球不需要保护"], 0, "Small actions make a big difference."),
         ]},
        {"id": "r3a4", "title": "Graduation Day",
         "text": "Today is our graduation day. We wear beautiful clothes and take photos in the school garden. Our head teacher gives a speech. She says, \"You have grown up. Study hard and be kind. The world is waiting for you.\" Then we give flowers to our teachers. We thank them for their help. In the afternoon, we have a party. We sing, dance and share stories. Some of us cry, but we are happy. We will never forget this day.",
         "words": [("graduation","毕业"),("speech","演讲"),("grown up","长大"),("party","聚会"),("forget","忘记")],
         "questions": [
            ("毕业典礼上他们做什么？", ["拍照听演讲", "考试", "打扫学校"], 0, "take photos, head teacher gives a speech."),
            ("班主任说了什么？", ["努力学习做个善良的人", "多看电视", "早点睡觉"], 0, "Study hard and be kind."),
            ("他们给老师什么？", ["花", "礼物", "贺卡"], 0, "give flowers to our teachers."),
         ]},
     ]},
]


def build_payload():
    levels = []
    na = 0
    for lv in LEVELS:
        arts = []
        for a in lv['articles']:
            na += 1
            wl = [{"word": w, "meaning": m} for w, m in a['words']]
            qs = [{"q2": q, "options": o, "answer": a_, "tip": t} for q, o, a_, t in a['questions']]
            arts.append({"id": a['id'], "title": a['title'], "text": a['text'],
                         "audio": "/audio/rd/" + a['id'] + ".mp3",
                         "words": wl, "questions": qs})
        levels.append({"id": lv['id'], "name": lv['name'], "desc": lv['desc'], "articles": arts})
    return {"product": "小学英语分级阅读起步（3 级 12 篇）", "version": "1.0", "schema_version": "1.0",
            "note": "对应新课标课外阅读量要求；内容 AI 生成待创始人校对",
            "levels": levels}, na


def gen():
    payload, na = build_payload()
    os.makedirs(DATA, exist_ok=True)
    with io.open(os.path.join(DATA, 'graded_reading.json'), 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    if os.path.isdir(WORKER_SRC):
        with io.open(os.path.join(WORKER_SRC, 'graded_reading.json'), 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    lines = ['# 小学英语分级阅读起步（3 级 12 篇）', '', '> 数据源：3 级 × 4 篇 = 12 篇；内容 AI 生成待创始人校对。', '']
    for lv in LEVELS:
        lines += ['', '## %s %s（%s）' % (lv['id'].upper(), lv['name'], lv['desc'])]
        for a in lv['articles']:
            lines += ['', '### %s %s → rd/%s.mp3' % (a['id'].upper(), a['title'], a['id'])]
            lines.append(a['text'])
            lines.append('生词：%s' % '、'.join('%s（%s）' % (w, m) for w, m in a['words']))
            for q, o, ans, t in a['questions']:
                lines.append('- %s｜答案：%s' % (q, o[ans]))
    os.makedirs(os.path.dirname(MATERIAL_MD), exist_ok=True)
    with io.open(MATERIAL_MD, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print('写入完成：graded_reading.json（%d 篇）+ 素材 md' % na)


def get_ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def normalize_audio(path):
    ff = get_ffmpeg()
    tmp = path + '.fix.mp3'
    subprocess.run([ff, '-y', '-i', path, '-ar', '44100', '-ac', '1', '-b:a', '128k', '-f', 'mp3', tmp],
                   check=True, capture_output=True)
    os.replace(tmp, path)


async def gen_audio():
    import edge_tts
    os.makedirs(AUDIO_RD, exist_ok=True)
    plan = []
    for lv in LEVELS:
        for a in lv['articles']:
            plan.append((a['id'], a['text']))
    total = len(plan)
    ok = 0
    for i, (fid, text) in enumerate(plan, 1):
        out = os.path.join(AUDIO_RD, fid + '.mp3')
        if os.path.exists(out):
            ok += 1
            continue
        tmp = out + '.raw.mp3'
        try:
            await edge_tts.Communicate(text, VOICE, rate=RATE).save(tmp)
            normalize_audio(tmp)
            os.replace(tmp, out)
            ok += 1
            print('[%d/%d] %s' % (i, total, fid))
        except Exception as e:
            print('[%d/%d] FAIL %s: %s' % (i, total, fid, e))
    print('音频生成完成：%d/%d' % (ok, total))


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'gen'
    if cmd in ('gen', 'all'):
        gen()
    if cmd in ('audio', 'all'):
        asyncio.run(gen_audio())
