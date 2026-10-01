# -*- coding: utf-8 -*-
"""深圳朗文《新思维小学英语》1A-6B 同步核心词生成脚本
生成：
  1) data/longman.json（本地）+ E:\\szgaokao.cn\\worker\\src\\longman.json（线上）
  2) 素材库《小学英语-深圳朗文新思维同步核心词-1A-6B.md》
  3) public/audio/lw/ 单词音频（英音女声，增量跳过）
用法：python tools/gen_longman.py gen / audio / all
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
AUDIO_LW = os.path.join(PUB, 'audio', 'lw')
WORKER_SRC = r'E:\szgaokao.cn\worker\src'
MATERIAL_MD = r'C:\Users\27264\WorkBuddy\2026-09-26-21-53-51\english-edu-company\03交付素材库\听说试卷包\小学英语-深圳朗文新思维同步核心词-1A-6B.md'

VOICE = 'en-GB-SoniaNeural'
RATE = '-10%'

# 数据源：12 册 × 4 单元 × 8 核心词（word, phonetic, meaning）
BOOKS = [
    {"level": "1A", "title": "开学与打招呼",
     "units": [
        ("打招呼", [("hello","həˈləʊ","你好"),("hi","haɪ","嗨"),("goodbye","ˌɡʊdˈbaɪ","再见"),("name","neɪm","名字"),("friend","frend","朋友"),("class","klɑːs","班级"),("teacher","ˈtiːtʃə","老师"),("pupil","ˈpjuːpl","小学生")]),
        ("数字1-10", [("one","wʌn","一"),("two","tuː","二"),("three","θriː","三"),("four","fɔː","四"),("five","faɪv","五"),("six","sɪks","六"),("seven","ˈsevn","七"),("ten","ten","十")]),
        ("颜色", [("red","red","红色"),("yellow","ˈjeləʊ","黄色"),("blue","bluː","蓝色"),("green","ɡriːn","绿色"),("black","blæk","黑色"),("white","waɪt","白色"),("pink","pɪŋk","粉色"),("brown","braʊn","棕色")]),
        ("文具", [("pen","pen","钢笔"),("pencil","ˈpensl","铅笔"),("book","bʊk","书"),("bag","bæɡ","书包"),("ruler","ˈruːlə","尺子"),("eraser","ɪˈreɪzə","橡皮"),("crayon","ˈkreɪən","蜡笔"),("desk","desk","书桌")]),
     ]},
    {"level": "1B", "title": "家庭与动物",
     "units": [
        ("家庭成员", [("father","ˈfɑːðə","爸爸"),("mother","ˈmʌðə","妈妈"),("brother","ˈbrʌðə","兄弟"),("sister","ˈsɪstə","姐妹"),("grandpa","ˈɡrænpɑː","爷爷/外公"),("grandma","ˈɡrænmɑː","奶奶/外婆"),("baby","ˈbeɪbi","婴儿"),("family","ˈfæməli","家庭")]),
        ("身体部位", [("head","hed","头"),("eye","aɪ","眼睛"),("ear","ɪə","耳朵"),("nose","nəʊz","鼻子"),("mouth","maʊθ","嘴巴"),("hand","hænd","手"),("leg","leɡ","腿"),("foot","fʊt","脚")]),
        ("动物", [("cat","kæt","猫"),("dog","dɒɡ","狗"),("duck","dʌk","鸭子"),("rabbit","ˈræbɪt","兔子"),("bird","bɜːd","鸟"),("fish","fɪʃ","鱼"),("monkey","ˈmʌŋki","猴子"),("tiger","ˈtaɪɡə","老虎")]),
        ("食物", [("apple","ˈæpl","苹果"),("banana","bəˈnɑːnə","香蕉"),("orange","ˈɒrɪndʒ","橙子"),("egg","eɡ","鸡蛋"),("milk","mɪlk","牛奶"),("bread","bred","面包"),("rice","raɪs","米饭"),("cake","keɪk","蛋糕")]),
     ]},
    {"level": "2A", "title": "教室与玩具",
     "units": [
        ("教室物品", [("chair","tʃeə","椅子"),("table","ˈteɪbl","桌子"),("board","bɔːd","黑板"),("door","dɔː","门"),("window","ˈwɪndəʊ","窗户"),("picture","ˈpɪktʃə","图画"),("clock","klɒk","时钟"),("school","skuːl","学校")]),
        ("玩具", [("ball","bɔːl","球"),("doll","dɒl","洋娃娃"),("robot","ˈrəʊbɒt","机器人"),("toy","tɔɪ","玩具"),("kite","kaɪt","风筝"),("car","kɑː","小汽车"),("plane","pleɪn","飞机"),("ship","ʃɪp","轮船")]),
        ("天气", [("sunny","ˈsʌni","晴朗的"),("rainy","ˈreɪni","下雨的"),("cloudy","ˈklaʊdi","多云的"),("windy","ˈwɪndi","刮风的"),("snowy","ˈsnəʊi","下雪的"),("hot","hɒt","热的"),("cold","kəʊld","冷的"),("warm","wɔːm","暖和的")]),
        ("季节", [("spring","sprɪŋ","春天"),("summer","ˈsʌmə","夏天"),("autumn","ˈɔːtəm","秋天"),("winter","ˈwɪntə","冬天"),("season","ˈsiːzn","季节"),("flower","ˈflaʊə","花"),("tree","triː","树"),("leaf","liːf","叶子")]),
     ]},
    {"level": "2B", "title": "衣物与星期",
     "units": [
        ("衣物", [("shirt","ʃɜːt","衬衫"),("coat","kəʊt","外套"),("dress","dres","连衣裙"),("skirt","skɜːt","短裙"),("hat","hæt","帽子"),("shoes","ʃuːz","鞋子"),("socks","sɒks","袜子"),("gloves","ɡlʌvz","手套")]),
        ("星期", [("Monday","ˈmʌndeɪ","星期一"),("Tuesday","ˈtjuːzdeɪ","星期二"),("Wednesday","ˈwenzdeɪ","星期三"),("Thursday","ˈθɜːzdeɪ","星期四"),("Friday","ˈfraɪdeɪ","星期五"),("Saturday","ˈsætədeɪ","星期六"),("Sunday","ˈsʌndeɪ","星期日"),("week","wiːk","星期")]),
        ("活动", [("run","rʌn","跑"),("jump","dʒʌmp","跳"),("walk","wɔːk","走"),("sing","sɪŋ","唱歌"),("dance","dɑːns","跳舞"),("draw","drɔː","画画"),("write","raɪt","写"),("read","riːd","读")]),
        ("交通工具", [("bus","bʌs","公交车"),("taxi","ˈtæksi","出租车"),("bike","baɪk","自行车"),("train","treɪn","火车"),("metro","ˈmetrəʊ","地铁"),("boat","bəʊt","小船"),("motorbike","ˈməʊtəbaɪk","摩托车"),("walk to","wɔːk tuː","步行去")]),
     ]},
    {"level": "3A", "title": "科目与时间",
     "units": [
        ("科目", [("English","ˈɪŋɡlɪʃ","英语"),("math","mæθ","数学"),("Chinese","ˌtʃaɪˈniːz","语文"),("science","ˈsaɪəns","科学"),("music","ˈmjuːzɪk","音乐"),("art","ɑːt","美术"),("PE","ˌpiːˈiː","体育"),("subject","ˈsʌbdʒɪkt","科目")]),
        ("学校场所", [("classroom","ˈklɑːsruːm","教室"),("library","ˈlaɪbrəri","图书馆"),("playground","ˈpleɪɡraʊnd","操场"),("gym","dʒɪm","体育馆"),("canteen","kænˈtiːn","食堂"),("office","ˈɒfɪs","办公室"),("hall","hɔːl","大厅"),("lab","læb","实验室")]),
        ("时间", [("morning","ˈmɔːnɪŋ","早上"),("afternoon","ˌɑːftəˈnuːn","下午"),("evening","ˈiːvnɪŋ","晚上"),("noon","nuːn","中午"),("night","naɪt","夜晚"),("o'clock","əˈklɒk","整点"),("hour","ˈaʊə","小时"),("minute","ˈmɪnɪt","分钟")]),
        ("一日活动", [("get up","ɡet ʌp","起床"),("breakfast","ˈbrekfəst","早餐"),("lunch","lʌntʃ","午餐"),("dinner","ˈdɪnə","晚餐"),("homework","ˈhəʊmwɜːk","作业"),("sleep","sliːp","睡觉"),("study","ˈstʌdi","学习"),("play","pleɪ","玩耍")]),
     ]},
    {"level": "3B", "title": "果蔬与购物",
     "units": [
        ("水果蔬菜", [("grape","ɡreɪp","葡萄"),("pear","peə","梨"),("watermelon","ˈwɔːtəmelən","西瓜"),("peach","piːtʃ","桃子"),("carrot","ˈkærət","胡萝卜"),("tomato","təˈmɑːtəʊ","西红柿"),("potato","pəˈteɪtəʊ","土豆"),("cabbage","ˈkæbɪdʒ","卷心菜")]),
        ("饮料", [("water","ˈwɔːtə","水"),("juice","dʒuːs","果汁"),("tea","tiː","茶"),("cola","ˈkəʊlə","可乐"),("lemonade","ˌleməˈneɪd","柠檬水"),("soup","suːp","汤"),("coffee","ˈkɒfi","咖啡"),("milkshake","ˈmɪlkʃeɪk","奶昔")]),
        ("三餐", [("noodles","ˈnuːdlz","面条"),("dumplings","ˈdʌmplɪŋz","饺子"),("chicken","ˈtʃɪkɪn","鸡肉"),("beef","biːf","牛肉"),("pork","pɔːk","猪肉"),("fish","fɪʃ","鱼"),("vegetables","ˈvedʒtəblz","蔬菜"),("fruit","fruːt","水果")]),
        ("购物", [("shop","ʃɒp","商店"),("buy","baɪ","买"),("sell","sel","卖"),("money","ˈmʌni","钱"),("cheap","tʃiːp","便宜的"),("expensive","ɪkˈspensɪv","昂贵的"),("shopping","ˈʃɒpɪŋ","购物"),("price","praɪs","价格")]),
     ]},
    {"level": "4A", "title": "职业与房间",
     "units": [
        ("职业", [("doctor","ˈdɒktə","医生"),("nurse","nɜːs","护士"),("teacher","ˈtiːtʃə","老师"),("driver","ˈdraɪvə","司机"),("farmer","ˈfɑːmə","农民"),("cook","kʊk","厨师"),("policeman","pəˈliːsmən","警察"),("worker","ˈwɜːkə","工人")]),
        ("工作地点", [("hospital","ˈhɒspɪtl","医院"),("factory","ˈfæktri","工厂"),("farm","fɑːm","农场"),("bank","bæŋk","银行"),("shop","ʃɒp","商店"),("company","ˈkʌmpəni","公司"),("school","skuːl","学校"),("zoo","zuː","动物园")]),
        ("家庭房间", [("bedroom","ˈbedruːm","卧室"),("kitchen","ˈkɪtʃɪn","厨房"),("bathroom","ˈbɑːθruːm","浴室"),("living room","ˈlɪvɪŋ ruːm","客厅"),("study","ˈstʌdi","书房"),("balcony","ˈbælkəni","阳台"),("floor","flɔː","地板/楼层"),("home","həʊm","家")]),
        ("家务", [("clean","kliːn","打扫"),("sweep","swiːp","扫地"),("wash","wɒʃ","洗"),("cook","kʊk","做饭"),("tidy","ˈtaɪdi","整理"),("water","ˈwɔːtə","浇水"),("feed","fiːd","喂"),("help","help","帮助")]),
     ]},
    {"level": "4B", "title": "运动与假期",
     "units": [
        ("运动", [("football","ˈfʊtbɔːl","足球"),("basketball","ˈbɑːskɪtbɔːl","篮球"),("badminton","ˈbædmɪntən","羽毛球"),("table tennis","ˈteɪbl tenɪs","乒乓球"),("swimming","ˈswɪmɪŋ","游泳"),("running","ˈrʌnɪŋ","跑步"),("cycling","ˈsaɪklɪŋ","骑行"),("sport","spɔːt","运动")]),
        ("爱好", [("hobby","ˈhɒbi","爱好"),("collect","kəˈlekt","收集"),("stamps","stæmps","邮票"),("painting","ˈpeɪntɪŋ","绘画"),("singing","ˈsɪŋɪŋ","唱歌"),("reading","ˈriːdɪŋ","阅读"),("fishing","ˈfɪʃɪŋ","钓鱼"),("camping","ˈkæmpɪŋ","露营")]),
        ("假期", [("holiday","ˈhɒlədeɪ","假期"),("trip","trɪp","旅行"),("travel","ˈtrævl","旅行"),("beach","biːtʃ","海滩"),("mountain","ˈmaʊntən","山"),("hotel","həʊˈtel","酒店"),("ticket","ˈtɪkɪt","票"),("suitcase","ˈsuːtkeɪs","行李箱")]),
        ("月份", [("January","ˈdʒænjuəri","一月"),("April","ˈeɪprəl","四月"),("July","dʒuˈlaɪ","七月"),("August","ˈɔːɡəst","八月"),("October","ɒkˈtəʊbə","十月"),("December","dɪˈsembə","十二月"),("month","mʌnθ","月份"),("year","jɪə","年")]),
     ]},
    {"level": "5A", "title": "城市与节日",
     "units": [
        ("城市场所", [("museum","mjuˈziːəm","博物馆"),("park","pɑːk","公园"),("cinema","ˈsɪnəmə","电影院"),("supermarket","ˈsuːpəmɑːkɪt","超市"),("restaurant","ˈrestrɒnt","餐馆"),("post office","pəʊst ˈɒfɪs","邮局"),("station","ˈsteɪʃn","车站"),("street","striːt","街道")]),
        ("问路", [("turn left","tɜːn left","左转"),("turn right","tɜːn raɪt","右转"),("go straight","ɡəʊ streɪt","直走"),("cross","krɒs","穿过"),("near","nɪə","在附近"),("far","fɑː","远"),("between","bɪˈtwiːn","在之间"),("opposite","ˈɒpəzɪt","在对面")]),
        ("公共交通", [("underground","ˈʌndəɡraʊnd","地铁"),("ferry","ˈferi","渡轮"),("minibus","ˈmɪnibʌs","小巴"),("double-decker","ˌdʌbl ˈdekə","双层巴士"),("passenger","ˈpæsɪndʒə","乘客"),("stop","stɒp","车站/停"),("route","ruːt","路线"),("traffic","ˈtræfɪk","交通")]),
        ("节日", [("festival","ˈfestɪvl","节日"),("Christmas","ˈkrɪsməs","圣诞节"),("Mid-Autumn","ˌmɪd ˈɔːtəm","中秋"),("Dragon Boat","ˈdræɡən bəʊt","端午"),("lantern","ˈlæntən","灯笼"),("firework","ˈfaɪəwɜːk","烟花"),("present","ˈpreznt","礼物"),("celebrate","ˈselɪbreɪt","庆祝")]),
     ]},
    {"level": "5B", "title": "健康与环境",
     "units": [
        ("疾病健康", [("headache","ˈhedeɪk","头疼"),("stomachache","ˈstʌməkeɪk","肚子疼"),("fever","ˈfiːvə","发烧"),("cold","kəʊld","感冒"),("cough","kɒf","咳嗽"),("medicine","ˈmedsn","药"),("doctor","ˈdɒktə","医生"),("rest","rest","休息")]),
        ("医院", [("patient","ˈpeɪʃnt","病人"),("nurse","nɜːs","护士"),("check","tʃek","检查"),("temperature","ˈtemprətʃə","体温"),("pain","peɪn","疼痛"),("healthy","ˈhelθi","健康的"),("exercise","ˈeksəsaɪz","锻炼"),("sleep","sliːp","睡觉")]),
        ("环保", [("environment","ɪnˈvaɪrənmənt","环境"),("pollution","pəˈluːʃn","污染"),("rubbish","ˈrʌbɪʃ","垃圾"),("recycle","ˌriːˈsaɪkl","回收"),("protect","prəˈtekt","保护"),("plastic","ˈplæstɪk","塑料"),("bin","bɪn","垃圾桶"),("earth","ɜːθ","地球")]),
        ("自然", [("mountain","ˈmaʊntən","山"),("river","ˈrɪvə","河流"),("lake","leɪk","湖"),("forest","ˈfɒrɪst","森林"),("ocean","ˈəʊʃn","海洋"),("island","ˈaɪlənd","岛屿"),("animal","ˈænɪml","动物"),("plant","plɑːnt","植物")]),
     ]},
    {"level": "6A", "title": "故事与旅行",
     "units": [
        ("过去故事词", [("yesterday","ˈjestədeɪ","昨天"),("last week","lɑːst wiːk","上周"),("visited","ˈvɪzɪtɪd","参观过"),("watched","wɒtʃt","看过"),("played","pleɪd","玩过"),("went","went","去过"),("saw","sɔː","看见过"),("did","dɪd","做过")]),
        ("旅行经历", [("journey","ˈdʒɜːni","旅程"),("abroad","əˈbrɔːd","国外"),("passport","ˈpɑːspɔːt","护照"),("luggage","ˈlʌɡɪdʒ","行李"),("guide","ɡaɪd","导游"),("map","mæp","地图"),("camera","ˈkæmərə","相机"),("photo","ˈfəʊtəʊ","照片")]),
        ("购物经历", [("bought","bɔːt","买过"),("tried","traɪd","试过"),("size","saɪz","尺码"),("colour","ˈkʌlə","颜色"),("fit","fɪt","合身"),("change","tʃeɪndʒ","零钱/换"),("receipt","rɪˈsiːt","收据"),("discount","ˈdɪskaʊnt","折扣")]),
        ("校园活动", [("activity","ækˈtɪvəti","活动"),("competition","ˌkɒmpəˈtɪʃn","比赛"),("prize","praɪz","奖品"),("team","tiːm","队伍"),("win","wɪn","赢"),("lose","luːz","输"),("practice","ˈpræktɪs","练习"),("match","mætʃ","比赛")]),
     ]},
    {"level": "6B", "title": "理想与未来",
     "units": [
        ("理想职业", [("dream","driːm","梦想"),("future","ˈfjuːtʃə","未来"),("scientist","ˈsaɪəntɪst","科学家"),("engineer","ˌendʒɪˈnɪə","工程师"),("pilot","ˈpaɪlət","飞行员"),("artist","ˈɑːtɪst","艺术家"),("singer","ˈsɪŋə","歌手"),("astronaut","ˈæstrənɔːt","宇航员")]),
        ("未来计划", [("plan","plæn","计划"),("will","wɪl","将要"),("hope","həʊp","希望"),("study hard","ˈstʌdi hɑːd","努力学习"),("college","ˈkɒlɪdʒ","大学"),("university","ˌjuːnɪˈvɜːsəti","大学"),("graduate","ˈɡrædʒueɪt","毕业"),("career","kəˈrɪə","职业")]),
        ("友谊", [("friend","frend","朋友"),("kind","kaɪnd","善良的"),("helpful","ˈhelpfl","乐于助人的"),("honest","ˈɒnɪst","诚实的"),("share","ʃeə","分享"),("together","təˈɡeðə","一起"),("trust","trʌst","信任"),("respect","rɪˈspekt","尊重")]),
        ("毕业", [("graduation","ˌɡrædʒuˈeɪʃn","毕业"),("primary school","ˈpraɪməri skuːl","小学"),("middle school","ˈmɪdl skuːl","中学"),("remember","rɪˈmembə","记得"),("thank","θæŋk","感谢"),("best wishes","best ˈwɪʃɪz","美好祝愿"),("classmate","ˈklɑːsmeɪt","同学"),("memory","ˈmeməri","回忆")]),
     ]},
]


def build_payload():
    books = []
    nw = 0
    for bk in BOOKS:
        units = []
        for ui, (title, words) in enumerate(bk['units'], 1):
            wlist = []
            for wi, (w, ph, mean) in enumerate(words, 1):
                nw += 1
                wid = 'lw%s-u%d-w%d' % (bk['level'].lower(), ui, wi)
                wlist.append({"id": wid, "word": w, "phonetic": ph, "meaning": mean,
                              "audio": "/audio/lw/%s.mp3" % wid})
            units.append({"id": 'lw%s-u%d' % (bk['level'].lower(), ui), "title": title, "words": wlist})
        books.append({"level": bk['level'], "title": bk['title'], "units": units})
    return {"product": "深圳朗文《新思维小学英语》1A-6B 同步核心词", "version": "1.0", "schema_version": "1.0",
            "note": "12 册 × 4 单元 × 8 核心词；内容为 AI 按教材主题整理，待创始人人工校对（红线条款）",
            "books": books}, nw


def gen():
    payload, nw = build_payload()
    os.makedirs(DATA, exist_ok=True)
    with io.open(os.path.join(DATA, 'longman.json'), 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    if os.path.isdir(WORKER_SRC):
        with io.open(os.path.join(WORKER_SRC, 'longman.json'), 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    lines = ['# 深圳朗文《新思维小学英语》1A-6B 同步核心词',
             '',
             '> 数据源：12 册 × 4 单元 × 8 词 = %d 词' % nw,
             '> 标注：内容由 AI 按教材主题整理，待创始人人工校对（红线条款）。', '']
    for bk in BOOKS:
        lines += ['', '## %s %s' % (bk['level'], bk['title'])]
        for title, words in bk['units']:
            lines.append('- **%s**：%s' % (title, '、'.join('%s %s' % (w, p) for w, p, _ in words)))
    os.makedirs(os.path.dirname(MATERIAL_MD), exist_ok=True)
    with io.open(MATERIAL_MD, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print('写入完成：longman.json（%d 词）+ 素材 md' % nw)


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
    os.makedirs(AUDIO_LW, exist_ok=True)
    plan = []
    for bk in BOOKS:
        for ui, (title, words) in enumerate(bk['units'], 1):
            for wi, (w, ph, mean) in enumerate(words, 1):
                wid = 'lw%s-u%d-w%d' % (bk['level'].lower(), ui, wi)
                plan.append((wid, w))
    total = len(plan)
    ok = 0
    for i, (fid, text) in enumerate(plan, 1):
        out = os.path.join(AUDIO_LW, fid + '.mp3')
        if os.path.exists(out):
            ok += 1
            continue
        tmp = out + '.raw.mp3'
        try:
            await edge_tts.Communicate(text, VOICE, rate=RATE).save(tmp)
            normalize_audio(tmp)
            os.replace(tmp, out)
            ok += 1
            if i % 60 == 0 or i == total:
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
