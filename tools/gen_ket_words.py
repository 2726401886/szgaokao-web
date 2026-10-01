# -*- coding: utf-8 -*-
# KET 核心词（剑桥 A2 Key 备考核心词）12 主题 × 20 词 = 240 词
# 音频命名 /audio/kw/kw{group}-w{no}.mp3
import json, os, subprocess, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
AUD = os.path.join(BASE, "public", "audio", "kw")

GROUPS = [
    ("kw1", "家庭与朋友", [
        ("family", "/ˈfæməli/", "n.", "家庭"), ("father", "/ˈfɑːðə/", "n.", "父亲"),
        ("mother", "/ˈmʌðə/", "n.", "母亲"), ("brother", "/ˈbrʌðə/", "n.", "兄弟"),
        ("sister", "/ˈsɪstə/", "n.", "姐妹"), ("grandfather", "/ˈɡrænfɑːðə/", "n.", "祖父"),
        ("grandmother", "/ˈɡrænmʌðə/", "n.", "祖母"), ("uncle", "/ˈʌŋkl/", "n.", "叔叔；舅舅"),
        ("aunt", "/ɑːnt/", "n.", "阿姨；姑姑"), ("cousin", "/ˈkʌzn/", "n.", "堂（表）兄弟姐妹"),
        ("friend", "/frend/", "n.", "朋友"), ("classmate", "/ˈklɑːsmeɪt/", "n.", "同学"),
        ("neighbour", "/ˈneɪbə/", "n.", "邻居"), ("parent", "/ˈpeərənt/", "n.", "父亲或母亲"),
        ("child", "/tʃaɪld/", "n.", "孩子"), ("baby", "/ˈbeɪbi/", "n.", "婴儿"),
        ("wife", "/waɪf/", "n.", "妻子"), ("husband", "/ˈhʌzbənd/", "n.", "丈夫"),
        ("daughter", "/ˈdɔːtə/", "n.", "女儿"), ("son", "/sʌn/", "n.", "儿子"),
    ]),
    ("kw2", "学校与学习", [
        ("school", "/skuːl/", "n.", "学校"), ("teacher", "/ˈtiːtʃə/", "n.", "老师"),
        ("student", "/ˈstjuːdnt/", "n.", "学生"), ("classroom", "/ˈklɑːsrʊm/", "n.", "教室"),
        ("lesson", "/ˈlesn/", "n.", "课"), ("homework", "/ˈhəʊmwɜːk/", "n.", "家庭作业"),
        ("exam", "/ɪɡˈzæm/", "n.", "考试"), ("book", "/bʊk/", "n.", "书"),
        ("pen", "/pen/", "n.", "钢笔"), ("pencil", "/ˈpensl/", "n.", "铅笔"),
        ("ruler", "/ˈruːlə/", "n.", "尺子"), ("bag", "/bæɡ/", "n.", "书包；袋子"),
        ("subject", "/ˈsʌbdʒɪkt/", "n.", "学科；科目"), ("maths", "/mæθs/", "n.", "数学"),
        ("science", "/ˈsaɪəns/", "n.", "科学"), ("history", "/ˈhɪstri/", "n.", "历史"),
        ("geography", "/dʒiˈɒɡrəfi/", "n.", "地理"), ("art", "/ɑːt/", "n.", "美术；艺术"),
        ("music", "/ˈmjuːzɪk/", "n.", "音乐"), ("library", "/ˈlaɪbrəri/", "n.", "图书馆"),
    ]),
    ("kw3", "食物与饮品", [
        ("food", "/fuːd/", "n.", "食物"), ("bread", "/bred/", "n.", "面包"),
        ("rice", "/raɪs/", "n.", "米饭"), ("meat", "/miːt/", "n.", "肉"),
        ("chicken", "/ˈtʃɪkɪn/", "n.", "鸡肉"), ("fish", "/fɪʃ/", "n.", "鱼"),
        ("egg", "/eɡ/", "n.", "鸡蛋"), ("milk", "/mɪlk/", "n.", "牛奶"),
        ("juice", "/dʒuːs/", "n.", "果汁"), ("water", "/ˈwɔːtə/", "n.", "水"),
        ("tea", "/tiː/", "n.", "茶"), ("coffee", "/ˈkɒfi/", "n.", "咖啡"),
        ("fruit", "/fruːt/", "n.", "水果"), ("apple", "/ˈæpl/", "n.", "苹果"),
        ("banana", "/bəˈnɑːnə/", "n.", "香蕉"), ("orange", "/ˈɒrɪndʒ/", "n.", "橙子"),
        ("vegetable", "/ˈvedʒtəbl/", "n.", "蔬菜"), ("lunch", "/lʌntʃ/", "n.", "午餐"),
        ("dinner", "/ˈdɪnə/", "n.", "晚餐"), ("breakfast", "/ˈbrekfəst/", "n.", "早餐"),
    ]),
    ("kw4", "衣服与购物", [
        ("clothes", "/kləʊðz/", "n.", "衣服"), ("shirt", "/ʃɜːt/", "n.", "衬衫"),
        ("dress", "/dres/", "n.", "连衣裙"), ("skirt", "/skɜːt/", "n.", "短裙"),
        ("trousers", "/ˈtraʊzəz/", "n.", "长裤"), ("jeans", "/dʒiːnz/", "n.", "牛仔裤"),
        ("coat", "/kəʊt/", "n.", "外套"), ("jacket", "/ˈdʒækɪt/", "n.", "夹克"),
        ("shoe", "/ʃuː/", "n.", "鞋"), ("hat", "/hæt/", "n.", "帽子"),
        ("scarf", "/skɑːf/", "n.", "围巾"), ("glove", "/ɡlʌv/", "n.", "手套"),
        ("shop", "/ʃɒp/", "n.", "商店"), ("market", "/ˈmɑːkɪt/", "n.", "市场"),
        ("buy", "/baɪ/", "v.", "买"), ("sell", "/sel/", "v.", "卖"),
        ("price", "/praɪs/", "n.", "价格"), ("money", "/ˈmʌni/", "n.", "钱"),
        ("cheap", "/tʃiːp/", "adj.", "便宜的"), ("expensive", "/ɪkˈspensɪv/", "adj.", "昂贵的"),
    ]),
    ("kw5", "健康与身体", [
        ("health", "/helθ/", "n.", "健康"), ("body", "/ˈbɒdi/", "n.", "身体"),
        ("head", "/hed/", "n.", "头"), ("hair", "/heə/", "n.", "头发"),
        ("face", "/feɪs/", "n.", "脸"), ("eye", "/aɪ/", "n.", "眼睛"),
        ("ear", "/ɪə/", "n.", "耳朵"), ("nose", "/nəʊz/", "n.", "鼻子"),
        ("mouth", "/maʊθ/", "n.", "嘴"), ("hand", "/hænd/", "n.", "手"),
        ("arm", "/ɑːm/", "n.", "手臂"), ("leg", "/leɡ/", "n.", "腿"),
        ("foot", "/fʊt/", "n.", "脚"), ("doctor", "/ˈdɒktə/", "n.", "医生"),
        ("nurse", "/nɜːs/", "n.", "护士"), ("hospital", "/ˈhɒspɪtl/", "n.", "医院"),
        ("medicine", "/ˈmedsn/", "n.", "药"), ("ill", "/ɪl/", "adj.", "生病的"),
        ("cold", "/kəʊld/", "n.", "感冒"), ("healthy", "/ˈhelθi/", "adj.", "健康的"),
    ]),
    ("kw6", "旅行与交通", [
        ("travel", "/ˈtrævl/", "v.", "旅行"), ("trip", "/trɪp/", "n.", "短途旅行"),
        ("journey", "/ˈdʒɜːni/", "n.", "旅程"), ("train", "/treɪn/", "n.", "火车"),
        ("bus", "/bʌs/", "n.", "公交车"), ("car", "/kɑː/", "n.", "小汽车"),
        ("bike", "/baɪk/", "n.", "自行车"), ("plane", "/pleɪn/", "n.", "飞机"),
        ("ship", "/ʃɪp/", "n.", "轮船"), ("taxi", "/ˈtæksi/", "n.", "出租车"),
        ("station", "/ˈsteɪʃn/", "n.", "车站"), ("airport", "/ˈeəpɔːt/", "n.", "机场"),
        ("ticket", "/ˈtɪkɪt/", "n.", "票"), ("luggage", "/ˈlʌɡɪdʒ/", "n.", "行李"),
        ("map", "/mæp/", "n.", "地图"), ("arrive", "/əˈraɪv/", "v.", "到达"),
        ("leave", "/liːv/", "v.", "离开"), ("road", "/rəʊd/", "n.", "公路；道路"),
        ("street", "/striːt/", "n.", "街道"), ("tourist", "/ˈtʊərɪst/", "n.", "游客"),
    ]),
    ("kw7", "城市与地点", [
        ("city", "/ˈsɪti/", "n.", "城市"), ("town", "/taʊn/", "n.", "城镇"),
        ("village", "/ˈvɪlɪdʒ/", "n.", "村庄"), ("square", "/skweə/", "n.", "广场"),
        ("park", "/pɑːk/", "n.", "公园"), ("zoo", "/zuː/", "n.", "动物园"),
        ("museum", "/mjuˈziːəm/", "n.", "博物馆"), ("cinema", "/ˈsɪnəmə/", "n.", "电影院"),
        ("theatre", "/ˈθɪətə/", "n.", "剧院"), ("restaurant", "/ˈrestrɒnt/", "n.", "餐厅"),
        ("bank", "/bæŋk/", "n.", "银行"), ("post", "/pəʊst/", "n.", "邮局"),
        ("office", "/ˈɒfɪs/", "n.", "办公室"), ("bridge", "/brɪdʒ/", "n.", "桥"),
        ("tower", "/ˈtaʊə/", "n.", "塔"), ("building", "/ˈbɪldɪŋ/", "n.", "建筑物"),
        ("hotel", "/həʊˈtel/", "n.", "旅馆"), ("supermarket", "/ˈsuːpəmɑːkɪt/", "n.", "超市"),
        ("church", "/tʃɜːtʃ/", "n.", "教堂"), ("library", "/ˈlaɪbrəri/", "n.", "图书馆"),
    ]),
    ("kw8", "天气与自然", [
        ("weather", "/ˈweðə/", "n.", "天气"), ("sun", "/sʌn/", "n.", "太阳"),
        ("rain", "/reɪn/", "n.", "雨"), ("snow", "/snəʊ/", "n.", "雪"),
        ("wind", "/wɪnd/", "n.", "风"), ("cloud", "/klaʊd/", "n.", "云"),
        ("sky", "/skaɪ/", "n.", "天空"), ("sea", "/siː/", "n.", "大海"),
        ("river", "/ˈrɪvə/", "n.", "河流"), ("lake", "/leɪk/", "n.", "湖"),
        ("mountain", "/ˈmaʊntən/", "n.", "山"), ("forest", "/ˈfɒrɪst/", "n.", "森林"),
        ("tree", "/triː/", "n.", "树"), ("flower", "/ˈflaʊə/", "n.", "花"),
        ("grass", "/ɡrɑːs/", "n.", "草"), ("animal", "/ˈænɪml/", "n.", "动物"),
        ("bird", "/bɜːd/", "n.", "鸟"), ("dog", "/dɒɡ/", "n.", "狗"),
        ("cat", "/kæt/", "n.", "猫"), ("horse", "/hɔːs/", "n.", "马"),
    ]),
    ("kw9", "运动与爱好", [
        ("sport", "/spɔːt/", "n.", "体育运动"), ("football", "/ˈfʊtbɔːl/", "n.", "足球"),
        ("basketball", "/ˈbɑːskɪtbɔːl/", "n.", "篮球"), ("tennis", "/ˈtenɪs/", "n.", "网球"),
        ("swimming", "/ˈswɪmɪŋ/", "n.", "游泳"), ("running", "/ˈrʌnɪŋ/", "n.", "跑步"),
        ("cycling", "/ˈsaɪklɪŋ/", "n.", "骑自行车"), ("hobby", "/ˈhɒbi/", "n.", "爱好"),
        ("guitar", "/ɡɪˈtɑː/", "n.", "吉他"), ("piano", "/piˈænəʊ/", "n.", "钢琴"),
        ("dance", "/dɑːns/", "v.", "跳舞"), ("painting", "/ˈpeɪntɪŋ/", "n.", "绘画"),
        ("photo", "/ˈfəʊtəʊ/", "n.", "照片"), ("game", "/ɡeɪm/", "n.", "游戏；比赛"),
        ("team", "/tiːm/", "n.", "队"), ("match", "/mætʃ/", "n.", "比赛"),
        ("win", "/wɪn/", "v.", "赢"), ("lose", "/luːz/", "v.", "输；丢失"),
        ("exercise", "/ˈeksəsaɪz/", "n.", "锻炼"), ("volleyball", "/ˈvɒlibɔːl/", "n.", "排球"),
    ]),
    ("kw10", "时间与日期", [
        ("time", "/taɪm/", "n.", "时间"), ("clock", "/klɒk/", "n.", "钟"),
        ("hour", "/ˈaʊə/", "n.", "小时"), ("minute", "/ˈmɪnɪt/", "n.", "分钟"),
        ("second", "/ˈsekənd/", "n.", "秒"), ("morning", "/ˈmɔːnɪŋ/", "n.", "早晨"),
        ("afternoon", "/ˌɑːftəˈnuːn/", "n.", "下午"), ("evening", "/ˈiːvnɪŋ/", "n.", "傍晚"),
        ("night", "/naɪt/", "n.", "夜晚"), ("today", "/təˈdeɪ/", "n.", "今天"),
        ("tomorrow", "/təˈmɒrəʊ/", "n.", "明天"), ("yesterday", "/ˈjestədeɪ/", "n.", "昨天"),
        ("week", "/wiːk/", "n.", "星期；周"), ("month", "/mʌnθ/", "n.", "月份"),
        ("year", "/jɪə/", "n.", "年"), ("date", "/deɪt/", "n.", "日期"),
        ("birthday", "/ˈbɜːθdeɪ/", "n.", "生日"), ("holiday", "/ˈhɒlədeɪ/", "n.", "假期"),
        ("season", "/ˈsiːzn/", "n.", "季节"), ("weekend", "/ˌwiːkˈend/", "n.", "周末"),
    ]),
    ("kw11", "工作与职业", [
        ("work", "/wɜːk/", "v.", "工作"), ("job", "/dʒɒb/", "n.", "工作；职业"),
        ("driver", "/ˈdraɪvə/", "n.", "司机"), ("farmer", "/ˈfɑːmə/", "n.", "农民"),
        ("cook", "/kʊk/", "n.", "厨师"), ("waiter", "/ˈweɪtə/", "n.", "服务员"),
        ("engineer", "/ˌendʒɪˈnɪə/", "n.", "工程师"), ("policeman", "/pəˈliːsmən/", "n.", "警察"),
        ("singer", "/ˈsɪŋə/", "n.", "歌手"), ("actor", "/ˈæktə/", "n.", "演员"),
        ("writer", "/ˈraɪtə/", "n.", "作家"), ("manager", "/ˈmænɪdʒə/", "n.", "经理"),
        ("office", "/ˈɒfɪs/", "n.", "办公室"), ("factory", "/ˈfæktri/", "n.", "工厂"),
        ("salary", "/ˈsæləri/", "n.", "薪水"), ("interview", "/ˈɪntəvjuː/", "n.", "面试"),
        ("career", "/kəˈrɪə/", "n.", "职业生涯"), ("shopkeeper", "/ˈʃɒpkiːpə/", "n.", "店主"),
        ("businessman", "/ˈbɪznəsmæn/", "n.", "商人"), ("artist", "/ˈɑːtɪst/", "n.", "艺术家"),
    ]),
    ("kw12", "日常活动", [
        ("wake", "/weɪk/", "v.", "醒来"), ("wash", "/wɒʃ/", "v.", "洗"),
        ("brush", "/brʌʃ/", "v.", "刷"), ("dress", "/dres/", "v.", "穿衣"),
        ("study", "/ˈstʌdi/", "v.", "学习"), ("play", "/pleɪ/", "v.", "玩；打（球）"),
        ("watch", "/wɒtʃ/", "v.", "观看"), ("read", "/riːd/", "v.", "阅读"),
        ("write", "/raɪt/", "v.", "写"), ("listen", "/ˈlɪsn/", "v.", "听"),
        ("speak", "/spiːk/", "v.", "说（话）"), ("sleep", "/sliːp/", "v.", "睡觉"),
        ("rest", "/rest/", "v.", "休息"), ("clean", "/kliːn/", "v.", "打扫"),
        ("cook", "/kʊk/", "v.", "做饭"), ("walk", "/wɔːk/", "v.", "走路"),
        ("phone", "/fəʊn/", "v.", "打电话"), ("visit", "/ˈvɪzɪt/", "v.", "拜访；参观"),
        ("swim", "/swɪm/", "v.", "游泳"), ("run", "/rʌn/", "v.", "跑"),
    ]),
]

def build_payload():
    groups = []
    for gid, title, words in GROUPS:
        wl = [{"id": "%s-w%d" % (gid, i + 1), "word": w, "phonetic": ph.strip("/"), "pos": p, "meaning": m,
               "audio": "/audio/kw/%s-w%d.mp3" % (gid, i + 1)} for i, (w, ph, p, m) in enumerate(words)]
        groups.append({"id": gid, "title": title, "count": len(wl), "words": wl})
    return {"level": "KET", "name": "KET 核心词（A2）", "groups": groups}

def gen():
    os.makedirs(DATA, exist_ok=True)
    p = build_payload()
    with open(os.path.join(DATA, "ket_words.json"), "w", encoding="utf-8") as f:
        json.dump(p, f, ensure_ascii=False, indent=1)
    # 素材 md
    md = ["# 小学英语-剑桥KET备考包-核心词表（A2）", "",
          "> 内容由 AI 生成，待创始人人工校对（红线条款）", "",
          "共 12 主题 × 20 词 = 240 词，覆盖剑桥 A2 Key 高频核心词。", ""]
    for g in p["groups"]:
        md.append("## %s（%s）" % (g["title"], g["id"]))
        for w in g["words"]:
            md.append("- %s /%s/ %s %s（%s）" % (w["word"], w["phonetic"].strip("/"), w["pos"], w["meaning"], w["id"]))
        md.append("")
    with open(os.path.join(BASE, "..", "english-edu-company", "03交付素材库", "听说试卷包", "小学英语-剑桥KET备考包-核心词表-A2.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print("写入完成：ket_words.json（%d 词）+ 素材 md" % (len(p["groups"]) * 20))

def audio():
    os.makedirs(AUD, exist_ok=True)
    # 已存在跳过
    import glob
    existing = {os.path.basename(x) for x in glob.glob(os.path.join(AUD, "*.mp3"))}
    plan = []
    for gid, _, words in GROUPS:
        for i, (w, _, _, _) in enumerate(words):
            fn = "%s-w%d.mp3" % (gid, i + 1)
            if fn not in existing:
                plan.append((fn, w))
    print("计划生成:", len(plan))
    for i, (fn, txt) in enumerate(plan, 1):
        if i % 60 == 0: print("[%d/%d]" % (i, len(plan)), end="")
        dst = os.path.join(AUD, fn)
        r = subprocess.run(["edge-tts", "--voice", "en-GB-SoniaNeural", "--text", txt,
                            "--rate=-10%", "--write-media", dst], capture_output=True, text=True)
        if r.returncode != 0:
            print("FAIL", fn, r.stderr[-200:])
    print("音频生成完成：%d/%d" % (len(plan), len(plan)))

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "audio":
        audio()
    else:
        gen()
