# -*- coding: utf-8 -*-
"""校内期末同步包生成脚本（3-6 年级 × 上下学期 = 8 套期末复习卷）
题型：单词听力 word / 短句听力 sentence / 对话听力 dialogue / 篇章听力 passage / 口语跟读 speaking
生成：
  1) data/primary_exam.json（本地）+ E:\\szgaokao.cn\\worker\\src\\primary_exam.json（线上）
  2) 素材库《小学英语-校内期末同步包-3至6年级8套.md》
  3) public/audio/ex/ 音频（英音女声慢速，增量跳过）
用法：python tools/gen_primary_exam.py gen / audio / all
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
AUDIO_EX = os.path.join(PUB, 'audio', 'ex')
WORKER_SRC = r'E:\szgaokao.cn\worker\src'
MATERIAL_MD = r'C:\Users\27264\WorkBuddy\2026-09-26-21-53-51\english-edu-company\03交付素材库\听说试卷包\小学英语-校内期末同步包-3至6年级8套.md'

VOICE = 'en-GB-SoniaNeural'
RATE = '-15%'

# 数据源：8 套期末卷 × 12 题单元（word3/sentence3/dialogue2/passage1/speaking3）
EXAMS = [
    {"id": "ex3a", "grade": 3, "sem": "上", "title": "三年级上册期末复习", "topic": "颜色数字·文具·动物水果·家庭成员",
     "questions": [
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "red", "options": ["红色", "蓝色", "绿色"], "answer": 0, "tip": "red 红色。"},
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "pencil", "options": ["钢笔", "铅笔", "蜡笔"], "answer": 1, "tip": "pencil 铅笔。"},
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "grandma", "options": ["爷爷", "奶奶", "妈妈"], "answer": 1, "tip": "grandma 奶奶/外婆。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "I have two books.", "options": ["我有两本书。", "我有三本书。", "我有两支笔。"], "answer": 0, "tip": "two books 两本书。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "The cat is on the desk.", "options": ["猫在书桌上。", "猫在垫子上。", "狗在书桌上。"], "answer": 0, "tip": "on the desk 在书桌上。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "My sister is my friend.", "options": ["我姐姐是我的朋友。", "我弟弟是我的同学。", "我妹妹是老师。"], "answer": 0, "tip": "sister 姐妹，friend 朋友。"},
        {"type": "dialogue", "q": "听对话，回答问题：How old is the boy?", "audio": "A: How old are you? B: I'm eight years old.",
         "q2": "男孩几岁？", "options": ["八岁", "九岁", "七岁"], "answer": 0, "tip": "eight years old 八岁。"},
        {"type": "dialogue", "q": "听对话，回答问题：What does the girl like?", "audio": "A: What do you like? B: I like apples and bananas.",
         "q2": "女孩喜欢什么？", "options": ["苹果和香蕉", "梨和葡萄", "蛋糕和牛奶"], "answer": 0, "tip": "apples and bananas 苹果和香蕉。"},
        {"type": "passage", "q": "听短文，回答问题", "audio": "Hello, I'm Amy. I'm nine. I have a dog. The dog is white.",
         "questions": [
            {"q2": "艾米几岁？", "options": ["九岁", "八岁", "十岁"], "answer": 0, "tip": "I'm nine 九岁。"},
            {"q2": "她的狗是什么颜色？", "options": ["白色", "黑色", "棕色"], "answer": 0, "tip": "The dog is white 白色。"},
         ]},
        {"type": "speaking", "q": "跟读句子，模仿发音", "text": "I have two books.", "audio": "I have two books.", "ref": "我有两本书。"},
        {"type": "speaking", "q": "跟读句子，模仿发音", "text": "The cat is on the desk.", "audio": "The cat is on the desk.", "ref": "猫在书桌上。"},
        {"type": "speaking", "q": "跟读句子，模仿发音", "text": "My sister is my friend.", "audio": "My sister is my friend.", "ref": "我姐姐是我的朋友。"},
     ]},
    {"id": "ex3b", "grade": 3, "sem": "下", "title": "三年级下册期末复习", "topic": "动物食物·天气季节·衣物",
     "questions": [
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "rabbit", "options": ["兔子", "老虎", "猴子"], "answer": 0, "tip": "rabbit 兔子。"},
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "sunny", "options": ["晴朗的", "下雨的", "刮风的"], "answer": 0, "tip": "sunny 晴朗的。"},
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "shirt", "options": ["外套", "衬衫", "裙子"], "answer": 1, "tip": "shirt 衬衫。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "It's rainy today.", "options": ["今天下雨。", "今天下雪。", "今天刮风。"], "answer": 0, "tip": "rainy 下雨。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "I like spring best.", "options": ["我最喜欢春天。", "我最喜欢夏天。", "我不喜欢春天。"], "answer": 0, "tip": "spring 春天。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "Put on your coat.", "options": ["穿上外套。", "脱掉外套。", "洗洗外套。"], "answer": 0, "tip": "put on 穿上。"},
        {"type": "dialogue", "q": "听对话，回答问题：What do they have for lunch?", "audio": "A: What do you have for lunch? B: Rice and fish.",
         "q2": "午餐吃什么？", "options": ["米饭和鱼", "面包和牛奶", "面条和鸡蛋"], "answer": 0, "tip": "rice and fish 米饭和鱼。"},
        {"type": "dialogue", "q": "听对话，回答问题：Where is the ball?", "audio": "A: Where is the ball? B: It's under the chair.",
         "q2": "球在哪里？", "options": ["椅子下面", "桌子上", "书包里"], "answer": 0, "tip": "under the chair 椅子下面。"},
        {"type": "passage", "q": "听短文，回答问题", "audio": "Today is Sunday. It's sunny. We go to the park. I fly a kite. My sister rides a bike.",
         "questions": [
            {"q2": "今天是什么天气？", "options": ["晴朗", "下雨", "下雪"], "answer": 0, "tip": "It's sunny 晴朗。"},
            {"q2": "谁在骑自行车？", "options": ["妹妹", "哥哥", "妈妈"], "answer": 0, "tip": "My sister rides a bike 妹妹骑车。"},
         ]},
        {"type": "speaking", "q": "跟读句子，模仿发音", "text": "It's rainy today.", "audio": "It's rainy today.", "ref": "今天下雨。"},
        {"type": "speaking", "q": "跟读句子，模仿发音", "text": "I like spring best.", "audio": "I like spring best.", "ref": "我最喜欢春天。"},
        {"type": "speaking", "q": "跟读句子，模仿发音", "text": "Put on your coat.", "audio": "Put on your coat.", "ref": "穿上外套。"},
     ]},
    {"id": "ex4a", "grade": 4, "sem": "上", "title": "四年级上册期末复习", "topic": "家庭房间·食物饮料·购物",
     "questions": [
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "kitchen", "options": ["厨房", "卧室", "浴室"], "answer": 0, "tip": "kitchen 厨房。"},
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "juice", "options": ["果汁", "牛奶", "水"], "answer": 0, "tip": "juice 果汁。"},
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "buy", "options": ["买", "卖", "看"], "answer": 0, "tip": "buy 买，sell 卖。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "My father is cooking in the kitchen.", "options": ["我爸爸在厨房做饭。", "我爸爸在卧室睡觉。", "我妈妈在厨房做饭。"], "answer": 0, "tip": "cooking in the kitchen 在厨房做饭。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "How much is the dress?", "options": ["这条连衣裙多少钱？", "这件外套多少钱？", "这双鞋多少钱？"], "answer": 0, "tip": "the dress 连衣裙。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "I'd like some noodles, please.", "options": ["我想要一些面条。", "我想要一些米饭。", "我想要一些饺子。"], "answer": 0, "tip": "noodles 面条。"},
        {"type": "dialogue", "q": "听对话，回答问题：What would the girl like to drink?", "audio": "A: Can I help you? B: Yes, a glass of milk, please.",
         "q2": "女孩想喝什么？", "options": ["牛奶", "果汁", "茶"], "answer": 0, "tip": "a glass of milk 一杯牛奶。"},
        {"type": "dialogue", "q": "听对话，回答问题：How much are the shoes?", "audio": "A: How much are the shoes? B: They're fifty yuan.",
         "q2": "鞋子多少钱？", "options": ["五十元", "十五元", "四十元"], "answer": 0, "tip": "fifty yuan 五十元。"},
        {"type": "passage", "q": "听短文，回答问题", "audio": "My home is not big. There are four rooms: a kitchen, a bathroom, a living room and a bedroom. I like my home.",
         "questions": [
            {"q2": "家里有几个房间？", "options": ["四个", "三个", "五个"], "answer": 0, "tip": "four rooms 四个房间。"},
            {"q2": "作者喜欢自己的家吗？", "options": ["喜欢", "不喜欢", "不确定"], "answer": 0, "tip": "I like my home 喜欢。"},
         ]},
        {"type": "speaking", "q": "跟读句子，模仿发音", "text": "My father is cooking in the kitchen.", "audio": "My father is cooking in the kitchen.", "ref": "我爸爸在厨房做饭。"},
        {"type": "speaking", "q": "跟读句子，模仿发音", "text": "How much is the dress?", "audio": "How much is the dress?", "ref": "这条连衣裙多少钱？"},
        {"type": "speaking", "q": "跟读句子，模仿发音", "text": "I'd like some noodles, please.", "audio": "I'd like some noodles, please.", "ref": "我想要一些面条。"},
     ]},
    {"id": "ex4b", "grade": 4, "sem": "下", "title": "四年级下册期末复习", "topic": "运动爱好·假期·月份",
     "questions": [
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "swimming", "options": ["游泳", "跑步", "骑车"], "answer": 0, "tip": "swimming 游泳。"},
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "holiday", "options": ["假期", "节日", "周末"], "answer": 0, "tip": "holiday 假期。"},
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "August", "options": ["八月", "四月", "十月"], "answer": 0, "tip": "August 八月。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "I can swim in summer.", "options": ["夏天我能游泳。", "冬天我能滑雪。", "春天我能放风筝。"], "answer": 0, "tip": "swim in summer 夏天游泳。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "We are going to the beach for the holiday.", "options": ["我们要去海滩度假。", "我们要去山上度假。", "我们去了公园。"], "answer": 0, "tip": "the beach 海滩。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "My hobby is collecting stamps.", "options": ["我的爱好是集邮。", "我的爱好是画画。", "我的爱好是钓鱼。"], "answer": 0, "tip": "collecting stamps 集邮。"},
        {"type": "dialogue", "q": "听对话，回答问题：What sport does the boy like?", "audio": "A: What sport do you like? B: I like basketball.",
         "q2": "男孩喜欢什么运动？", "options": ["篮球", "足球", "羽毛球"], "answer": 0, "tip": "basketball 篮球。"},
        {"type": "dialogue", "q": "听对话，回答问题：When is the trip?", "audio": "A: When is our school trip? B: It's in May.",
         "q2": "学校旅行在什么时候？", "options": ["五月", "六月", "四月"], "answer": 0, "tip": "in May 五月。"},
        {"type": "passage", "q": "听短文，回答问题", "audio": "My brother likes sports. He plays football on Monday and Wednesday. He goes swimming on Saturday.",
         "questions": [
            {"q2": "哥哥星期几踢足球？", "options": ["周一和周三", "周二和周四", "周六和周日"], "answer": 0, "tip": "Monday and Wednesday 周一和周三。"},
            {"q2": "哥哥周六做什么？", "options": ["游泳", "跑步", "踢球"], "answer": 0, "tip": "goes swimming 游泳。"},
         ]},
        {"type": "speaking", "q": "跟读句子，模仿发音", "text": "I can swim in summer.", "audio": "I can swim in summer.", "ref": "夏天我能游泳。"},
        {"type": "speaking", "q": "跟读句子，模仿发音", "text": "My hobby is collecting stamps.", "audio": "My hobby is collecting stamps.", "ref": "我的爱好是集邮。"},
        {"type": "speaking", "q": "跟读句子，模仿发音", "text": "We are going to the beach for the holiday.", "audio": "We are going to the beach for the holiday.", "ref": "我们要去海滩度假。"},
     ]},
    {"id": "ex5a", "grade": 5, "sem": "上", "title": "五年级上册期末复习", "topic": "科目学校·城市场所·问路",
     "questions": [
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "library", "options": ["图书馆", "教室", "操场"], "answer": 0, "tip": "library 图书馆。"},
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "museum", "options": ["博物馆", "医院", "银行"], "answer": 0, "tip": "museum 博物馆。"},
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "straight", "options": ["直的", "转弯的", "旁边的"], "answer": 0, "tip": "go straight 直走。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "We have science on Tuesday.", "options": ["我们周二有科学课。", "我们周二有数学课。", "我们周四有科学课。"], "answer": 0, "tip": "science on Tuesday 周二科学。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "The supermarket is next to the park.", "options": ["超市在公园旁边。", "超市在公园对面。", "银行在公园旁边。"], "answer": 0, "tip": "next to 在旁边。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "Turn left at the second crossing.", "options": ["在第二个路口左转。", "在第二个路口右转。", "在第一个路口左转。"], "answer": 0, "tip": "turn left 左转。"},
        {"type": "dialogue", "q": "听对话，回答问题：Which subject does the girl like best?", "audio": "A: What's your favourite subject? B: Science. It's interesting.",
         "q2": "女孩最喜欢的科目是什么？", "options": ["科学", "数学", "音乐"], "answer": 0, "tip": "favourite subject 最喜欢的科目。"},
        {"type": "dialogue", "q": "听对话，回答问题：How does the man get to the cinema?", "audio": "A: How do I get to the cinema? B: Take the metro to City Park Station.",
         "q2": "去电影院怎么走？", "options": ["坐地铁", "坐公交", "步行"], "answer": 0, "tip": "take the metro 坐地铁。"},
        {"type": "passage", "q": "听短文，回答问题", "audio": "Our school is big and beautiful. There is a library, a playground and a garden. We read books in the library and play in the playground.",
         "questions": [
            {"q2": "学校有什么？", "options": ["图书馆和操场", "游泳池和食堂", "电影院和公园"], "answer": 0, "tip": "library and playground 图书馆和操场。"},
            {"q2": "他们在哪里读书？", "options": ["图书馆", "操场", "花园"], "answer": 0, "tip": "read books in the library 图书馆。"},
         ]},
        {"type": "speaking", "q": "跟读句子，模仿发音", "text": "We have science on Tuesday.", "audio": "We have science on Tuesday.", "ref": "我们周二有科学课。"},
        {"type": "speaking", "q": "跟读句子，模仿发音", "text": "Turn left at the second crossing.", "audio": "Turn left at the second crossing.", "ref": "在第二个路口左转。"},
        {"type": "speaking", "q": "跟读句子，模仿发音", "text": "The supermarket is next to the park.", "audio": "The supermarket is next to the park.", "ref": "超市在公园旁边。"},
     ]},
    {"id": "ex5b", "grade": 5, "sem": "下", "title": "五年级下册期末复习", "topic": "健康环保·自然·节日",
     "questions": [
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "environment", "options": ["环境", "天气", "季节"], "answer": 0, "tip": "environment 环境。"},
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "headache", "options": ["头疼", "肚子疼", "牙疼"], "answer": 0, "tip": "headache 头疼。"},
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "recycle", "options": ["回收", "污染", "保护"], "answer": 0, "tip": "recycle 回收。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "We should protect the environment.", "options": ["我们应该保护环境。", "我们应该多锻炼。", "我们应该早点睡。"], "answer": 0, "tip": "protect the environment 保护环境。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "Don't throw rubbish on the ground.", "options": ["不要往地上扔垃圾。", "不要往河里倒水。", "不要摘公园的花。"], "answer": 0, "tip": "throw rubbish 扔垃圾。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "I have a fever. I need to see a doctor.", "options": ["我发烧了，需要看医生。", "我感冒了，需要休息。", "我咳嗽了，需要吃药。"], "answer": 0, "tip": "have a fever 发烧。"},
        {"type": "dialogue", "q": "听对话，回答问题：What's wrong with the boy?", "audio": "A: What's wrong? B: I have a stomachache.",
         "q2": "男孩怎么了？", "options": ["肚子疼", "头疼", "发烧"], "answer": 0, "tip": "stomachache 肚子疼。"},
        {"type": "dialogue", "q": "听对话，回答问题：What do they do at the festival?", "audio": "A: What do you do at the Mid-Autumn Festival? B: We eat mooncakes and watch the moon.",
         "q2": "中秋节他们做什么？", "options": ["吃月饼看月亮", "放烟花吃粽子", "挂灯笼猜灯谜"], "answer": 0, "tip": "eat mooncakes and watch the moon 吃月饼看月亮。"},
        {"type": "passage", "q": "听短文，回答问题", "audio": "Our class plants trees every year. Trees make the air clean and give us shade in summer. Everyone should love nature.",
         "questions": [
            {"q2": "他们每年做什么？", "options": ["种树", "种花", "浇水"], "answer": 0, "tip": "plant trees 种树。"},
            {"q2": "树在夏天能做什么？", "options": ["提供树荫", "结出果实", "开出花朵"], "answer": 0, "tip": "give us shade 提供树荫。"},
         ]},
        {"type": "speaking", "q": "跟读句子，模仿发音", "text": "We should protect the environment.", "audio": "We should protect the environment.", "ref": "我们应该保护环境。"},
        {"type": "speaking", "q": "跟读句子，模仿发音", "text": "Don't throw rubbish on the ground.", "audio": "Don't throw rubbish on the ground.", "ref": "不要往地上扔垃圾。"},
        {"type": "speaking", "q": "跟读句子，模仿发音", "text": "I have a fever. I need to see a doctor.", "audio": "I have a fever. I need to see a doctor.", "ref": "我发烧了，需要看医生。"},
     ]},
    {"id": "ex6a", "grade": 6, "sem": "上", "title": "六年级上册期末复习", "topic": "过去经历·旅行购物·校园活动",
     "questions": [
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "yesterday", "options": ["昨天", "今天", "明天"], "answer": 0, "tip": "yesterday 昨天。"},
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "passport", "options": ["护照", "车票", "地图"], "answer": 0, "tip": "passport 护照。"},
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "competition", "options": ["比赛", "假期", "旅行"], "answer": 0, "tip": "competition 比赛。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "I went to Beijing last summer.", "options": ["去年夏天我去了北京。", "今年夏天我去了上海。", "上周末我去了北京。"], "answer": 0, "tip": "went to Beijing last summer 去年夏天去北京。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "She bought a new dress yesterday.", "options": ["她昨天买了一条新裙子。", "她昨天买了一件新外套。", "她前天买了一条新裙子。"], "answer": 0, "tip": "bought a new dress 买新裙子。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "Our team won the match.", "options": ["我们队赢了比赛。", "我们队输了比赛。", "他们队赢了比赛。"], "answer": 0, "tip": "won the match 赢了比赛。"},
        {"type": "dialogue", "q": "听对话，回答问题：Where did the girl go last Sunday?", "audio": "A: Where did you go last Sunday? B: I went to the museum with my family.",
         "q2": "女孩上周日去了哪里？", "options": ["博物馆", "动物园", "商场"], "answer": 0, "tip": "went to the museum 去了博物馆。"},
        {"type": "dialogue", "q": "听对话，回答问题：What did the boy do at the weekend?", "audio": "A: What did you do at the weekend? B: I played football with my friends.",
         "q2": "男孩周末做了什么？", "options": ["和朋友踢足球", "在家看书", "去游泳"], "answer": 0, "tip": "played football 踢足球。"},
        {"type": "passage", "q": "听短文，回答问题", "audio": "Last week, our class had a sports day. We ran, jumped and played ball games. My friend Lily won the running race. We were very happy.",
         "questions": [
            {"q2": "上周他们做了什么？", "options": ["开了运动会", "去旅行", "开了班会"], "answer": 0, "tip": "had a sports day 开运动会。"},
            {"q2": "谁赢了跑步比赛？", "options": ["莉莉", "作者", "汤姆"], "answer": 0, "tip": "Lily won the running race 莉莉赢了。"},
         ]},
        {"type": "speaking", "q": "跟读句子，模仿发音", "text": "I went to Beijing last summer.", "audio": "I went to Beijing last summer.", "ref": "去年夏天我去了北京。"},
        {"type": "speaking", "q": "跟读句子，模仿发音", "text": "Our team won the match.", "audio": "Our team won the match.", "ref": "我们队赢了比赛。"},
        {"type": "speaking", "q": "跟读句子，模仿发音", "text": "She bought a new dress yesterday.", "audio": "She bought a new dress yesterday.", "ref": "她昨天买了一条新裙子。"},
     ]},
    {"id": "ex6b", "grade": 6, "sem": "下", "title": "六年级下册期末复习", "topic": "理想未来·友谊毕业·综合",
     "questions": [
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "astronaut", "options": ["宇航员", "科学家", "工程师"], "answer": 0, "tip": "astronaut 宇航员。"},
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "graduate", "options": ["毕业", "考试", "开学"], "answer": 0, "tip": "graduate 毕业。"},
        {"type": "word", "q": "听单词，选出正确的中文意思", "audio": "honest", "options": ["诚实的", "聪明的", "勇敢的"], "answer": 0, "tip": "honest 诚实的。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "I want to be a scientist in the future.", "options": ["我将来想当科学家。", "我将来想当老师。", "我现在是科学家。"], "answer": 0, "tip": "in the future 将来。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "We should share things with our friends.", "options": ["我们应该和朋友分享。", "我们应该向朋友借钱。", "我们应该帮助陌生人。"], "answer": 0, "tip": "share things 分享。"},
        {"type": "sentence", "q": "听句子，选出正确的意思", "audio": "I will study hard in middle school.", "options": ["我将在中学努力学习。", "我将在小学努力学习。", "我过去在中学很努力。"], "answer": 0, "tip": "study hard 努力学习。"},
        {"type": "dialogue", "q": "听对话，回答问题：What does the boy want to be?", "audio": "A: What do you want to be? B: I want to be a pilot and fly planes.",
         "q2": "男孩想当什么？", "options": ["飞行员", "司机", "船员"], "answer": 0, "tip": "a pilot 飞行员。"},
        {"type": "dialogue", "q": "听对话，回答问题：What is the girl like?", "audio": "A: What is your best friend like? B: She is kind and helpful.",
         "q2": "女孩的朋友怎么样？", "options": ["善良乐于助人", "严厉", "害羞"], "answer": 0, "tip": "kind and helpful 善良乐于助人。"},
        {"type": "passage", "q": "听短文，回答问题", "audio": "We are going to graduate from primary school. We thank our teachers and classmates. We will remember the happy days and keep in touch.",
         "questions": [
            {"q2": "他们将要做什么？", "options": ["小学毕业", "升入中学考试", "参加比赛"], "answer": 0, "tip": "graduate from primary school 小学毕业。"},
            {"q2": "他们会怎么做？", "options": ["保持联系", "互相忘记", "搬家离开"], "answer": 0, "tip": "keep in touch 保持联系。"},
         ]},
        {"type": "speaking", "q": "跟读句子，模仿发音", "text": "I want to be a scientist in the future.", "audio": "I want to be a scientist in the future.", "ref": "我将来想当科学家。"},
        {"type": "speaking", "q": "跟读句子，模仿发音", "text": "We should share things with our friends.", "audio": "We should share things with our friends.", "ref": "我们应该和朋友分享。"},
        {"type": "speaking", "q": "跟读句子，模仿发音", "text": "I will study hard in middle school.", "audio": "I will study hard in middle school.", "ref": "我将在中学努力学习。"},
     ]},
]


def build_payload():
    volumes = []
    nq = 0
    for v in EXAMS:
        qs = []
        for qi, q in enumerate(v['questions'], 1):
            nq += 1
            qid = v['id'] + ('%02d' % qi)
            item = {"id": qid, "type": q['type'], "q": q['q'], "audio": "/audio/ex/" + qid + ".mp3"}
            if q['type'] == 'speaking':
                item["text"] = q['text']; item["ref"] = q['ref']
            elif q['type'] == 'passage':
                item["questions"] = q['questions']
            else:
                item["options"] = q['options']; item["answer"] = q['answer']; item["tip"] = q['tip']
                if q['type'] == 'dialogue':
                    item["q2"] = q['q2']
            qs.append(item)
        volumes.append({"id": v['id'], "grade": v['grade'], "sem": v['sem'], "title": v['title'],
                        "topic": v['topic'], "questions": qs})
    return {"product": "校内期末同步包（3-6 年级 × 上下学期 8 套）", "version": "1.0", "schema_version": "1.0",
            "note": "8 套期末复习卷：word/sentence/dialogue/passage/speaking 五大题型；内容 AI 生成待创始人校对",
            "volumes": volumes}, nq


def gen():
    payload, nq = build_payload()
    os.makedirs(DATA, exist_ok=True)
    with io.open(os.path.join(DATA, 'primary_exam.json'), 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    if os.path.isdir(WORKER_SRC):
        with io.open(os.path.join(WORKER_SRC, 'primary_exam.json'), 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    lines = ['# 校内期末同步包（3-6 年级 × 上下学期 8 套）',
             '', '> 数据源：8 套卷 × 12 题单元，共 %d 题；内容 AI 生成待创始人校对。' % nq, '']
    for v in EXAMS:
        lines += ['', '## %s %s（%s）' % (v['id'].upper(), v['title'], v['topic'])]
        for qi, q in enumerate(v['questions'], 1):
            qid = v['id'] + ('%02d' % qi)
            if q['type'] == 'speaking':
                lines.append('- **[口语]** %s → ex/%s.mp3（参考：%s）' % (q['text'], qid, q['ref']))
            elif q['type'] == 'passage':
                lines.append('- **[篇章]** 原文：%s → ex/%s.mp3' % (q['audio'], qid))
                for sub in q['questions']:
                    lines.append('  - %s｜答案：%s' % (sub['q2'], sub['options'][sub['answer']]))
            else:
                lines.append('- **[%s]** %s｜原文：%s → ex/%s.mp3｜答案：%s' % (
                    q['type'], q['q'], q['audio'], qid, q['options'][q['answer']]))
    os.makedirs(os.path.dirname(MATERIAL_MD), exist_ok=True)
    with io.open(MATERIAL_MD, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print('写入完成：primary_exam.json（%d 题）+ 素材 md' % nq)


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
    os.makedirs(AUDIO_EX, exist_ok=True)
    plan = []
    for v in EXAMS:
        for qi, q in enumerate(v['questions'], 1):
            plan.append((v['id'] + ('%02d' % qi), q['audio']))
    total = len(plan)
    ok = 0
    for i, (fid, text) in enumerate(plan, 1):
        out = os.path.join(AUDIO_EX, fid + '.mp3')
        if os.path.exists(out):
            ok += 1
            continue
        tmp = out + '.raw.mp3'
        try:
            await edge_tts.Communicate(text, VOICE, rate=RATE).save(tmp)
            normalize_audio(tmp)
            os.replace(tmp, out)
            ok += 1
            if i % 40 == 0 or i == total:
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
