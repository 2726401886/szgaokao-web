# -*- coding: utf-8 -*-
"""小学英语听说题型库生成脚本（五大题型：单词/短句/对话/篇章/口语）
生成：
  1) data/primary_listening.json（本地题库数据）
  2) E:\\szgaokao.cn\\worker\\src\\primary_listening.json（线上 Workers 打包）
  3) 素材库《小学英语听说题型库-题目与音频脚本.md》
  4) public/audio/lt/ 题目音频（英音女声，慢速，增量跳过）
用法：
  python tools/gen_primary_listening.py gen
  python tools/gen_primary_listening.py audio
  python tools/gen_primary_listening.py all
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
AUDIO_LT = os.path.join(PUB, 'audio', 'lt')
WORKER_SRC = r'E:\szgaokao.cn\worker\src'
MATERIAL_MD = r'C:\Users\27264\WorkBuddy\2026-09-26-21-53-51\english-edu-company\03交付素材库\听说试卷包\小学英语听说题型库-题目与音频脚本.md'

VOICE = 'en-GB-SoniaNeural'
RATE = '-15%'

# —— 数据源：6 卷 × 12 题单元（word 听单词 / sentence 听句子 / dialogue 听对话 / passage 听短文 / speaking 口语跟读）——
VOLUMES = [
    {"id": "lt3", "grade": 3, "title": "三年级听说专项", "topic": "颜色数字·文具·动物水果",
     "questions": [
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "apple",
         "options": ["苹果", "香蕉", "橙子"], "answer": 0, "tip": "apple 是苹果，a 发 /æ/。"},
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "pencil",
         "options": ["钢笔", "铅笔", "尺子"], "answer": 1, "tip": "pen 是钢笔，pencil 是铅笔。"},
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "duck",
         "options": ["鸭子", "猫", "狗"], "answer": 0, "tip": "duck 鸭子，叫声 quack quack。"},
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "yellow",
         "options": ["蓝色", "红色", "黄色"], "answer": 2, "tip": "yellow 黄色，像香蕉的颜色。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "I have three books.",
         "options": ["我有三本书。", "我有三支笔。", "我买了三本书。"], "answer": 0, "tip": "three books = 三本书。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "The cat is on the mat.",
         "options": ["猫在垫子上。", "猫在桌子上。", "狗在垫子上。"], "answer": 0, "tip": "cat 猫，mat 垫子。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "Open your book, please.",
         "options": ["请合上书。", "请打开书。", "请拿出笔。"], "answer": 1, "tip": "open 打开，book 书。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "I like red apples.",
         "options": ["我喜欢红苹果。", "我喜欢绿苹果。", "我吃了一个红苹果。"], "answer": 0, "tip": "like 喜欢，red apples 红苹果。"},
        {"type": "dialogue", "q": "听对话，回答问题：Who is in the dialogue?", "audio": "A: Hello, Tom! B: Hi, Ann! Let's play together.",
         "q2": "对话里有谁？", "options": ["Tom and Ann", "Tom and Bob", "Ann and Lily"], "answer": 0, "tip": "对话开头：Hello, Tom! Hi, Ann!"},
        {"type": "dialogue", "q": "听对话，回答问题：What colour does the girl like?", "audio": "A: What colour do you like? B: I like blue.",
         "q2": "女孩喜欢什么颜色？", "options": ["红色", "蓝色", "绿色"], "answer": 1, "tip": "I like blue，喜欢蓝色。"},
        {"type": "passage", "q": "听短文，回答问题", "audio": "This is my dog. My dog is black and white. It can run fast.",
         "questions": [
            {"q2": "短文里的狗是什么颜色？", "options": ["黑白相间", "棕色", "黄色"], "answer": 0, "tip": "black and white 黑白相间。"},
            {"q2": "狗会做什么？", "options": ["跑得很快", "会游泳", "会唱歌"], "answer": 0, "tip": "It can run fast 跑得很快。"},
         ]},
        {"type": "speaking", "q": "跟读句子，模仿发音", "text": "I like apples.", "audio": "I like apples.", "ref": "我喜欢苹果。"},
        {"type": "speaking", "q": "跟读句子，模仿发音", "text": "The duck is yellow.", "audio": "The duck is yellow.", "ref": "鸭子是黄色的。"},
     ]},
    {"id": "lt4", "grade": 4, "title": "四年级听说专项", "topic": "家庭房间·食物饮料·衣物天气",
     "questions": [
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "mother",
         "options": ["妈妈", "爸爸", "奶奶"], "answer": 0, "tip": "mother 妈妈，father 爸爸。"},
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "milk",
         "options": ["果汁", "牛奶", "水"], "answer": 1, "tip": "milk 牛奶，juice 果汁。"},
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "coat",
         "options": ["衬衫", "外套", "裙子"], "answer": 1, "tip": "coat 外套，shirt 衬衫。"},
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "rainy",
         "options": ["晴天的", "下雨的", "刮风的"], "answer": 1, "tip": "rainy 下雨的，sunny 晴朗的。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "My mother cooks dinner.",
         "options": ["我妈妈做晚饭。", "我妈妈做早饭。", "我爸爸做晚饭。"], "answer": 0, "tip": "mother 妈妈，cook dinner 做晚饭。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "I drink milk every morning.",
         "options": ["我每天晚上喝牛奶。", "我每天早上喝牛奶。", "我每天早上喝水。"], "answer": 1, "tip": "every morning 每天早上。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "It's rainy today. Take an umbrella.",
         "options": ["今天下雨，带把伞。", "今天晴天，戴帽子。", "今天刮风，多穿衣。"], "answer": 0, "tip": "rainy 下雨，umbrella 伞。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "There are four people in my family.",
         "options": ["我家有四口人。", "我家有五口人。", "我家有四间房。"], "answer": 0, "tip": "four people 四口人。"},
        {"type": "dialogue", "q": "听对话，回答问题：What does the boy want for breakfast?", "audio": "A: What do you want for breakfast? B: I want some bread and milk.",
         "q2": "男孩早餐想吃什么？", "options": ["面包和牛奶", "米饭和鸡蛋", "面条和果汁"], "answer": 0, "tip": "bread and milk 面包和牛奶。"},
        {"type": "dialogue", "q": "听对话，回答问题：What's the weather like?", "audio": "A: What's the weather like today? B: It's windy and cold.",
         "q2": "今天天气怎么样？", "options": ["刮风又冷", "晴朗又热", "下雨又冷"], "answer": 0, "tip": "windy 刮风，cold 冷。"},
        {"type": "passage", "q": "听短文，回答问题", "audio": "My sister is six years old. She likes milk and eggs. She has a red dress.",
         "questions": [
            {"q2": "妹妹几岁？", "options": ["六岁", "七岁", "五岁"], "answer": 0, "tip": "six years old 六岁。"},
            {"q2": "妹妹喜欢什么？", "options": ["牛奶和鸡蛋", "面包和果汁", "苹果和牛奶"], "answer": 0, "tip": "likes milk and eggs 喜欢牛奶和鸡蛋。"},
         ]},
        {"type": "speaking", "q": "跟读句子，模仿发音", "text": "My mother cooks dinner.", "audio": "My mother cooks dinner.", "ref": "我妈妈做晚饭。"},
        {"type": "speaking", "q": "跟读句子，模仿发音", "text": "It's sunny and warm.", "audio": "It's sunny and warm.", "ref": "天气晴朗又暖和。"},
     ]},
    {"id": "lt5", "grade": 5, "title": "五年级听说专项", "topic": "科目学校·场所出行·活动爱好",
     "questions": [
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "science",
         "options": ["数学", "科学", "音乐"], "answer": 1, "tip": "science 科学，math 数学。"},
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "museum",
         "options": ["医院", "博物馆", "银行"], "answer": 1, "tip": "museum 博物馆，hospital 医院。"},
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "swim",
         "options": ["跑步", "游泳", "跳舞"], "answer": 1, "tip": "swim 游泳，run 跑步。"},
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "library",
         "options": ["图书馆", "教室", "操场"], "answer": 0, "tip": "library 图书馆，classroom 教室。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "We have a math class today.",
         "options": ["我们今天有数学课。", "我们今天有英语课。", "我们昨天有数学课。"], "answer": 0, "tip": "math class 数学课。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "Let's go to the park on Sunday.",
         "options": ["我们星期天去公园吧。", "我们星期六去公园吧。", "我们星期天去动物园吧。"], "answer": 0, "tip": "Sunday 星期天，park 公园。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "I read books before bed.",
         "options": ["我睡觉前看书。", "我起床后看书。", "我放学后看书。"], "answer": 0, "tip": "before bed 睡觉前。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "The bus station is over there.",
         "options": ["公交站在那边。", "火车站在那边。", "公交站离这儿很远。"], "answer": 0, "tip": "bus station 公交站。"},
        {"type": "dialogue", "q": "听对话，回答问题：What class does the girl like best?", "audio": "A: What classes do you have today? B: English, math and music. A: Which one do you like best? B: Music!",
         "q2": "女孩最喜欢什么课？", "options": ["音乐", "数学", "英语"], "answer": 0, "tip": "Music! 她最喜欢音乐。"},
        {"type": "dialogue", "q": "听对话，回答问题：How does the man go to the museum?", "audio": "A: Excuse me, how can I get to the museum? B: Walk straight and turn left.",
         "q2": "去博物馆怎么走？", "options": ["直走再左转", "直走再右转", "坐公交车"], "answer": 0, "tip": "walk straight and turn left 直走左转。"},
        {"type": "passage", "q": "听短文，回答问题", "audio": "We go to the zoo on Saturday. We see tigers, monkeys and elephants. I like monkeys best. They are funny.",
         "questions": [
            {"q2": "他们星期六去了哪里？", "options": ["动物园", "博物馆", "公园"], "answer": 0, "tip": "go to the zoo 去动物园。"},
            {"q2": "作者最喜欢什么动物？", "options": ["老虎", "猴子", "大象"], "answer": 1, "tip": "I like monkeys best 最喜欢猴子。"},
         ]},
        {"type": "speaking", "q": "跟读句子，模仿发音", "text": "Science is interesting.", "audio": "Science is interesting.", "ref": "科学很有趣。"},
        {"type": "speaking", "q": "跟读句子，模仿发音", "text": "I like swimming on weekends.", "audio": "I like swimming on weekends.", "ref": "我喜欢周末游泳。"},
     ]},
    {"id": "lt6", "grade": 6, "title": "六年级听说专项", "topic": "职业工作·感受情绪·自然环保",
     "questions": [
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "farmer",
         "options": ["司机", "农民", "医生"], "answer": 1, "tip": "farmer 农民，driver 司机。"},
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "thirsty",
         "options": ["饥饿的", "口渴的", "累的"], "answer": 1, "tip": "thirsty 口渴，hungry 饿。"},
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "environment",
         "options": ["环境", "天气", "季节"], "answer": 0, "tip": "environment 环境，weather 天气。"},
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "pollution",
         "options": ["污染", "保护", "垃圾"], "answer": 0, "tip": "pollution 污染，protect 保护。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "My father works in a hospital.",
         "options": ["我爸爸在医院工作。", "我爸爸在学校工作。", "我妈妈在医院工作。"], "answer": 0, "tip": "father 爸爸，hospital 医院。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "I'm tired after the long walk.",
         "options": ["走了很远的路，我很累。", "跑了很久，我很渴。", "走了很远的路，我很饿。"], "answer": 0, "tip": "tired 累的，long walk 长途步行。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "We should protect the environment.",
         "options": ["我们应该保护环境。", "我们应该保护动物。", "我们应该节约用水。"], "answer": 0, "tip": "protect the environment 保护环境。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "The sun rises in the east.",
         "options": ["太阳从东方升起。", "太阳从西方落下。", "月亮从东方升起。"], "answer": 0, "tip": "rises in the east 从东方升起。"},
        {"type": "dialogue", "q": "听对话，回答问题：What does the boy want to be?", "audio": "A: What do you want to be in the future? B: I want to be a doctor, because I want to help people.",
         "q2": "男孩想当什么？", "options": ["医生", "老师", "厨师"], "answer": 0, "tip": "a doctor 医生。"},
        {"type": "dialogue", "q": "听对话，回答问题：How does the girl feel?", "audio": "A: You look tired. Are you OK? B: I'm hungry and thirsty.",
         "q2": "女孩感觉怎么样？", "options": ["又饿又渴", "又累又困", "开心又兴奋"], "answer": 0, "tip": "hungry and thirsty 又饿又渴。"},
        {"type": "passage", "q": "听短文，回答问题", "audio": "Today is World Environment Day. We plant trees at school. Trees make the air clean. Everyone should protect our environment.",
         "questions": [
            {"q2": "他们在学校做了什么？", "options": ["种树", "扫地", "浇水浇花"], "answer": 0, "tip": "plant trees 种树。"},
            {"q2": "树能带来什么好处？", "options": ["让空气干净", "让天气变冷", "让马路变宽"], "answer": 0, "tip": "Trees make the air clean 让空气变干净。"},
         ]},
        {"type": "speaking", "q": "跟读句子，模仿发音", "text": "I want to be a doctor.", "audio": "I want to be a doctor.", "ref": "我想当一名医生。"},
        {"type": "speaking", "q": "跟读句子，模仿发音", "text": "We should protect the environment.", "audio": "We should protect the environment.", "ref": "我们应该保护环境。"},
     ]},
    {"id": "ltM1", "grade": 0, "title": "综合模拟卷（一）", "topic": "全学段综合",
     "questions": [
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "banana",
         "options": ["苹果", "香蕉", "葡萄"], "answer": 1, "tip": "banana 香蕉，apple 苹果。"},
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "doctor",
         "options": ["护士", "医生", "老师"], "answer": 1, "tip": "doctor 医生，nurse 护士。"},
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "cloud",
         "options": ["云", "雨", "雪"], "answer": 0, "tip": "cloud 云，rain 雨。"},
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "supermarket",
         "options": ["超市", "银行", "餐馆"], "answer": 0, "tip": "supermarket 超市，restaurant 餐馆。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "I have bread and milk for breakfast.",
         "options": ["我早餐吃面包喝牛奶。", "我午餐吃面条喝汤。", "我晚餐吃米饭和鱼。"], "answer": 0, "tip": "breakfast 早餐。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "My sister can draw a cat.",
         "options": ["我妹妹会画猫。", "我妹妹喜欢猫。", "我弟弟会画猫。"], "answer": 0, "tip": "draw a cat 画猫。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "Turn right at the second crossing.",
         "options": ["在第二个路口右转。", "在第一个路口左转。", "在第二个路口左转。"], "answer": 0, "tip": "turn right 右转。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "I'm excited about the school trip.",
         "options": ["我对学校旅行很兴奋。", "我对学校考试很紧张。", "我对运动会很期待。"], "answer": 0, "tip": "excited 兴奋的。"},
        {"type": "dialogue", "q": "听对话，回答问题：Where are they going?", "audio": "A: Where are you going this afternoon? B: We're going to the library to read books.",
         "q2": "他们下午要去哪里？", "options": ["图书馆", "超市", "公园"], "answer": 0, "tip": "the library 图书馆。"},
        {"type": "dialogue", "q": "听对话，回答问题：What's the matter with the boy?", "audio": "A: What's wrong? B: I have a headache. I need some rest.",
         "q2": "男孩怎么了？", "options": ["头疼", "肚子疼", "牙疼"], "answer": 0, "tip": "headache 头疼。"},
        {"type": "passage", "q": "听短文，回答问题", "audio": "Tom is a pupil. He gets up at seven. He has breakfast at half past seven. Then he goes to school by bus. He likes English best.",
         "questions": [
            {"q2": "汤姆几点起床？", "options": ["七点", "七点半", "六点"], "answer": 0, "tip": "gets up at seven 七点起床。"},
            {"q2": "汤姆最喜欢什么课？", "options": ["英语", "数学", "科学"], "answer": 0, "tip": "likes English best 最喜欢英语。"},
         ]},
        {"type": "speaking", "q": "跟读句子，模仿发音", "text": "I get up at seven.", "audio": "I get up at seven.", "ref": "我七点起床。"},
        {"type": "speaking", "q": "跟读句子，模仿发音", "text": "I like English best.", "audio": "I like English best.", "ref": "我最喜欢英语。"},
     ]},
    {"id": "ltM2", "grade": 0, "title": "综合模拟卷（二）", "topic": "全学段综合",
     "questions": [
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "noodles",
         "options": ["米饭", "面条", "饺子"], "answer": 1, "tip": "noodles 面条，rice 米饭。"},
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "hospital",
         "options": ["医院", "银行", "酒店"], "answer": 0, "tip": "hospital 医院，hotel 酒店。"},
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "snow",
         "options": ["雪", "风", "雨"], "answer": 0, "tip": "snow 雪，wind 风。"},
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "excited",
         "options": ["兴奋的", "难过的", "生气的"], "answer": 0, "tip": "excited 兴奋的，sad 难过的。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "My uncle is a cook.",
         "options": ["我叔叔是厨师。", "我叔叔是司机。", "我舅舅是医生。"], "answer": 0, "tip": "uncle 叔叔/舅舅，cook 厨师。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "It often rains in spring.",
         "options": ["春天经常下雨。", "夏天经常下雨。", "秋天经常刮风。"], "answer": 0, "tip": "in spring 在春天。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "We play basketball after school.",
         "options": ["我们放学后打篮球。", "我们放学后踢足球。", "我们上课前打篮球。"], "answer": 0, "tip": "after school 放学后。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "Don't worry. Everything will be OK.",
         "options": ["别担心，一切都会好起来的。", "别哭，我会帮你的。", "别跑，注意安全。"], "answer": 0, "tip": "Don't worry 别担心。"},
        {"type": "dialogue", "q": "听对话，回答问题：What season does the girl like best?", "audio": "A: Which season do you like best? B: I like winter. I can make a snowman.",
         "q2": "女孩最喜欢什么季节？", "options": ["冬天", "夏天", "春天"], "answer": 0, "tip": "winter 冬天，make a snowman 堆雪人。"},
        {"type": "dialogue", "q": "听对话，回答问题：What would the man like to drink?", "audio": "A: Can I help you? B: Yes, a glass of orange juice, please.",
         "q2": "男士想喝什么？", "options": ["橙汁", "牛奶", "茶"], "answer": 0, "tip": "orange juice 橙汁。"},
        {"type": "passage", "q": "听短文，回答问题", "audio": "My family goes to the beach in summer. We swim in the sea and build sand castles. My little sister likes collecting shells. We all have a good time.",
         "questions": [
            {"q2": "他们夏天去了哪里？", "options": ["海边", "山上", "公园"], "answer": 0, "tip": "the beach 海边。"},
            {"q2": "妹妹喜欢做什么？", "options": ["捡贝壳", "堆沙堡", "游泳"], "answer": 0, "tip": "collecting shells 捡贝壳。"},
         ]},
        {"type": "speaking", "q": "跟读句子，模仿发音", "text": "I like winter best.", "audio": "I like winter best.", "ref": "我最喜欢冬天。"},
        {"type": "speaking", "q": "跟读句子，模仿发音", "text": "We all have a good time.", "audio": "We all have a good time.", "ref": "我们都玩得很开心。"},
     ]},
]


def build_payload():
    volumes = []
    nq = 0
    for v in VOLUMES:
        qs = []
        for qi, q in enumerate(v['questions'], 1):
            nq += 1
            qid = v['id'] + ('%02d' % qi)
            item = {"id": qid, "type": q['type'], "q": q['q'], "audio": "/audio/lt/" + qid + ".mp3"}
            if q['type'] == 'speaking':
                item["text"] = q['text']
                item["ref"] = q['ref']
            elif q['type'] == 'passage':
                item["questions"] = q['questions']
            else:
                item["options"] = q['options']
                item["answer"] = q['answer']
                item["tip"] = q['tip']
                if q['type'] == 'dialogue':
                    item["q2"] = q['q2']
            qs.append(item)
        volumes.append({"id": v['id'], "grade": v['grade'], "title": v['title'], "topic": v['topic'],
                        "questions": qs})
    return {"product": "小学英语听说题型库（五大题型）", "version": "1.0", "schema_version": "1.0",
            "note": "6 卷：3/4/5/6 年级专项 + 2 套综合模拟；题型 word 单词听力 / sentence 短句听力 / dialogue 对话听力 / passage 篇章听力 / speaking 口语跟读；音频英音女声慢速",
            "volumes": volumes}, nq


def gen():
    payload, nq = build_payload()
    os.makedirs(DATA, exist_ok=True)
    with io.open(os.path.join(DATA, 'primary_listening.json'), 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    if os.path.isdir(WORKER_SRC):
        with io.open(os.path.join(WORKER_SRC, 'primary_listening.json'), 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print('已写入 worker:', WORKER_SRC)
    lines = ['# 小学英语听说题型库 · 题目与音频脚本',
             '',
             '> 数据源：6 卷（3-6 年级专项 + 2 套综合模拟），五大题型，共 %d 题单元' % nq,
             '> 标注：内容由 AI 生成，待创始人人工校对（红线条款）。',
             '']
    for v in VOLUMES:
        lines += ['', '## %s %s（%s）' % (v['id'].upper(), v['title'], v['topic']), '']
        for qi, q in enumerate(v['questions'], 1):
            qid = v['id'] + ('%02d' % qi)
            if q['type'] == 'speaking':
                lines.append('- **[口语]** %s → lt/%s.mp3（参考：%s）' % (q['text'], qid, q['ref']))
            elif q['type'] == 'passage':
                lines.append('- **[篇章]** 原文：%s → lt/%s.mp3' % (q['audio'], qid))
                for sub in q['questions']:
                    lines.append('  - 问题：%s｜答案：%s' % (sub['q2'], sub['options'][sub['answer']]))
            else:
                lines.append('- **[%s]** %s｜原文：%s → lt/%s.mp3｜答案：%s' % (
                    q['type'], q['q'], q['audio'], qid, q['options'][q['answer']]))
    os.makedirs(os.path.dirname(MATERIAL_MD), exist_ok=True)
    with io.open(MATERIAL_MD, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print('已写入素材库 md:', MATERIAL_MD)
    print('卷数:', len(VOLUMES), '题单元:', nq)


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
    os.makedirs(AUDIO_LT, exist_ok=True)
    plan = []
    for v in VOLUMES:
        for qi, q in enumerate(v['questions'], 1):
            qid = v['id'] + ('%02d' % qi)
            plan.append((qid, q['audio']))
    total = len(plan)
    ok = 0
    for i, (fid, text) in enumerate(plan, 1):
        out = os.path.join(AUDIO_LT, fid + '.mp3')
        if os.path.exists(out):
            ok += 1
            continue
        tmp = out + '.raw.mp3'
        try:
            await edge_tts.Communicate(text, VOICE, rate=RATE).save(tmp)
            normalize_audio(tmp)
            os.replace(tmp, out)
            ok += 1
            if i % 20 == 0 or i == total:
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
