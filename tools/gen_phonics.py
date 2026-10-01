# -*- coding: utf-8 -*-
"""小学英语自然拼读专项 · 数据源驱动生成脚本
生成：
  1) data/phonics.json（本地题库数据）
  2) E:\\szgaokao.cn\\worker\\src\\phonics.json（线上 Workers 打包）
  3) 素材库《小学英语自然拼读专项-规则与音频脚本.md》
  4) public/audio/ph/pXXX.mp3 规则发音 + pXXXwN.mp3 示例词发音（英音女声，增量跳过）
用法：
  python tools/gen_phonics.py gen     # 生成 JSON + md
  python tools/gen_phonics.py audio   # 增量生成/补音频
  python tools/gen_phonics.py all     # 两者
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
AUDIO_PH = os.path.join(PUB, 'audio', 'ph')
WORKER_SRC = r'E:\szgaokao.cn\worker\src'
MATERIAL_MD = r'C:\Users\27264\WorkBuddy\2026-09-26-21-53-51\english-edu-company\03交付素材库\听说试卷包\小学英语自然拼读专项-规则与音频脚本.md'

VOICE = 'en-GB-SoniaNeural'
RATE = '-10%'

# —— 数据源：5 级 × 42 条规则（对标小学自然拼读教学顺序）——
LEVELS = [
    {"id": "p1", "name": "第一级 · 短元音（CVC）", "desc": "26 个字母音打底后，先学 5 个短元音：a e i o u，见词能拼 cat、dog 这类 CVC 单词。",
     "rules": [
        {"rule": "a", "sound": "/æ/", "cn": "字母 a 在 cat 中发短音 /æ/", "tip": "嘴巴张大、短促有力，像中文的“哎”但更短。",
         "words": [("cat", "/kæt/", "猫"), ("bat", "/bæt/", "蝙蝠"), ("hat", "/hæt/", "帽子"), ("map", "/mæp/", "地图")]},
        {"rule": "e", "sound": "/e/", "cn": "字母 e 在 bed 中发短音 /e/", "tip": "嘴唇微扁、声音短，像“诶”的短促版。",
         "words": [("bed", "/bed/", "床"), ("pen", "/pen/", "钢笔"), ("hen", "/hen/", "母鸡"), ("red", "/red/", "红色的")]},
        {"rule": "i", "sound": "/ɪ/", "cn": "字母 i 在 pig 中发短音 /ɪ/", "tip": "比 /e/ 更放松，像“一”但嘴形放松。",
         "words": [("pig", "/pɪɡ/", "猪"), ("six", "/sɪks/", "六"), ("fish", "/fɪʃ/", "鱼"), ("big", "/bɪɡ/", "大的")]},
        {"rule": "o", "sound": "/ɒ/", "cn": "字母 o 在 dog 中发短音 /ɒ/", "tip": "嘴巴圆、声音低沉，像“哦”的短促版。",
         "words": [("dog", "/dɒɡ/", "狗"), ("box", "/bɒks/", "盒子"), ("hot", "/hɒt/", "热的"), ("frog", "/frɒɡ/", "青蛙")]},
        {"rule": "u", "sound": "/ʌ/", "cn": "字母 u 在 bus 中发短音 /ʌ/", "tip": "嘴巴半开、放松，像“啊”的短促版。",
         "words": [("bus", "/bʌs/", "公共汽车"), ("cup", "/kʌp/", "杯子"), ("sun", "/sʌn/", "太阳"), ("duck", "/dʌk/", "鸭子")]},
     ]},
    {"id": "p2", "name": "第二级 · 长元音（Magic e 与元音组合）", "desc": "学完短元音后进阶长元音：末尾加 e 让元音“念自己的名字”，以及常见元音组合。",
     "rules": [
        {"rule": "a_e", "sound": "/eɪ/", "cn": "a_e（如 cake）：末尾 e 让 a 发字母音 /eɪ/", "tip": "先读 a 的字母音，再读辅音：c-a-k-e → /keɪk/。",
         "words": [("cake", "/keɪk/", "蛋糕"), ("lake", "/leɪk/", "湖"), ("name", "/neɪm/", "名字"), ("plane", "/pleɪn/", "飞机")]},
        {"rule": "i_e", "sound": "/aɪ/", "cn": "i_e（如 five）：末尾 e 让 i 发字母音 /aɪ/", "tip": "i 念自己的名字“爱”：f-i-v-e → /faɪv/。",
         "words": [("five", "/faɪv/", "五"), ("nine", "/naɪn/", "九"), ("kite", "/kaɪt/", "风筝"), ("rice", "/raɪs/", "米饭")]},
        {"rule": "o_e", "sound": "/əʊ/", "cn": "o_e（如 home）：末尾 e 让 o 发字母音 /əʊ/", "tip": "o 念自己的名字，口型从圆到扁：h-o-m-e。",
         "words": [("home", "/həʊm/", "家"), ("nose", "/nəʊz/", "鼻子"), ("rose", "/rəʊz/", "玫瑰"), ("stone", "/stəʊn/", "石头")]},
        {"rule": "u_e", "sound": "/juː/", "cn": "u_e（如 cute）：末尾 e 让 u 发字母音 /juː/", "tip": "先读“you”再读辅音：c-u-t-e → /kjuːt/。",
         "words": [("cute", "/kjuːt/", "可爱的"), ("cube", "/kjuːb/", "立方体"), ("mule", "/mjuːl/", "骡子"), ("tube", "/tjuːb/", "管子")]},
        {"rule": "ee/ea", "sound": "/iː/", "cn": "ee 与 ea 都发长音 /iː/（如 see、tea）", "tip": "嘴唇向两边微笑，声音拉长：s-ee → /siː/。",
         "words": [("see", "/siː/", "看见"), ("green", "/ɡriːn/", "绿色的"), ("tea", "/tiː/", "茶"), ("sea", "/siː/", "大海")]},
        {"rule": "ai/ay", "sound": "/eɪ/", "cn": "ai 与 ay 都发 /eɪ/（如 rain、day）", "tip": "和 a_e 同音，多在词中写 ai、词尾写 ay。",
         "words": [("rain", "/reɪn/", "雨"), ("train", "/treɪn/", "火车"), ("day", "/deɪ/", "白天"), ("play", "/pleɪ/", "玩")]},
        {"rule": "oa/ow", "sound": "/əʊ/", "cn": "oa 与 ow 都发 /əʊ/（如 boat、snow）", "tip": "和 o_e 同音：b-oa-t → /bəʊt/。",
         "words": [("boat", "/bəʊt/", "小船"), ("coat", "/kəʊt/", "外套"), ("snow", "/snəʊ/", "雪"), ("bowl", "/bəʊl/", "碗")]},
        {"rule": "igh/ie", "sound": "/aɪ/", "cn": "igh 与 ie 都发 /aɪ/（如 light、pie）", "tip": "和 i_e 同音：l-igh-t → /laɪt/。",
         "words": [("light", "/laɪt/", "灯"), ("night", "/naɪt/", "夜晚"), ("high", "/haɪ/", "高的"), ("pie", "/paɪ/", "馅饼")]},
     ]},
    {"id": "p3", "name": "第三级 · 辅音组合", "desc": "两个字母组合发一个新音（sh、ch、th 等），以及常见“双辅音”开头（bl、br、fl、fr…）。",
     "rules": [
        {"rule": "sh", "sound": "/ʃ/", "cn": "sh 发 /ʃ/，像“嘘”（如 ship）", "tip": "嘴唇向前突出，轻轻吹气。",
         "words": [("ship", "/ʃɪp/", "轮船"), ("fish", "/fɪʃ/", "鱼"), ("sheep", "/ʃiːp/", "绵羊"), ("shop", "/ʃɒp/", "商店")]},
        {"rule": "ch", "sound": "/tʃ/", "cn": "ch 发 /tʃ/，像“吃”的轻读（如 chair）", "tip": "先做 /t/ 的口型再快速接 /ʃ/。",
         "words": [("chair", "/tʃeə(r)/", "椅子"), ("chicken", "/ˈtʃɪkɪn/", "鸡肉"), ("lunch", "/lʌntʃ/", "午餐"), ("chat", "/tʃæt/", "聊天")]},
        {"rule": "th", "sound": "/θ/ 或 /ð/", "cn": "th 发 /θ/（three）或 /ð/（this），舌尖轻咬", "tip": "舌尖放在上下牙之间，轻轻送气。",
         "words": [("three", "/θriː/", "三"), ("thin", "/θɪn/", "瘦的"), ("this", "/ðɪs/", "这个"), ("mother", "/ˈmʌðə(r)/", "母亲")]},
        {"rule": "wh", "sound": "/w/", "cn": "wh 发 /w/（如 white），口型收圆", "tip": "像中文“哇”的开头，嘴唇收圆。",
         "words": [("white", "/waɪt/", "白色的"), ("where", "/weə(r)/", "哪里"), ("what", "/wɒt/", "什么"), ("wheel", "/wiːl/", "轮子")]},
        {"rule": "ph", "sound": "/f/", "cn": "ph 发 /f/（如 phone），希腊语来源", "tip": "看到 ph 就读 /f/：ph-one → phone。",
         "words": [("phone", "/fəʊn/", "电话"), ("photo", "/ˈfəʊtəʊ/", "照片"), ("elephant", "/ˈelɪfənt/", "大象"), ("dolphin", "/ˈdɒlfɪn/", "海豚")]},
        {"rule": "ck", "sound": "/k/", "cn": "ck 发 /k/，跟在短元音后（如 duck）", "tip": "词尾短元音后常写 ck：du-ck。",
         "words": [("duck", "/dʌk/", "鸭子"), ("sock", "/sɒk/", "袜子"), ("clock", "/klɒk/", "钟"), ("black", "/blæk/", "黑色的")]},
        {"rule": "ng", "sound": "/ŋ/", "cn": "ng 发 /ŋ/，舌根堵住气流（如 sing）", "tip": "像“嗯”的后半段，声音从鼻腔出。",
         "words": [("sing", "/sɪŋ/", "唱歌"), ("ring", "/rɪŋ/", "戒指"), ("long", "/lɒŋ/", "长的"), ("king", "/kɪŋ/", "国王")]},
        {"rule": "bl/br", "sound": "/bl/ /br/", "cn": "b 快速接 l 或 r（如 blue、bread）", "tip": "两个音连读，不要停顿。",
         "words": [("blue", "/bluː/", "蓝色的"), ("black", "/blæk/", "黑色的"), ("bread", "/bred/", "面包"), ("bridge", "/brɪdʒ/", "桥")]},
        {"rule": "fl/fr", "sound": "/fl/ /fr/", "cn": "f 快速接 l 或 r（如 flag、frog）", "tip": "先摆好 /f/ 的口型，快速滑向 l/r。",
         "words": [("flag", "/flæɡ/", "旗子"), ("flower", "/ˈflaʊə(r)/", "花"), ("frog", "/frɒɡ/", "青蛙"), ("fruit", "/fruːt/", "水果")]},
        {"rule": "pl/pr", "sound": "/pl/ /pr/", "cn": "p 快速接 l 或 r（如 plane、prize）", "tip": "注意 p 后不夹带“呃”音。",
         "words": [("plane", "/pleɪn/", "飞机"), ("plate", "/pleɪt/", "盘子"), ("prize", "/praɪz/", "奖品"), ("pretty", "/ˈprɪti/", "漂亮的")]},
        {"rule": "sp/st", "sound": "/sp/ /st/", "cn": "s 快速接 p 或 t（如 spider、star）", "tip": "词首的 sp/st，p/t 读得接近浊音。",
         "words": [("spider", "/ˈspaɪdə(r)/", "蜘蛛"), ("spoon", "/spuːn/", "勺子"), ("star", "/stɑː(r)/", "星星"), ("stop", "/stɒp/", "停止")]},
        {"rule": "sl/sm", "sound": "/sl/ /sm/", "cn": "s 快速接 l 或 m（如 slide、smile）", "tip": "s 轻短，快速滑向后面的音。",
         "words": [("slide", "/slaɪd/", "滑梯"), ("sleep", "/sliːp/", "睡觉"), ("smile", "/smaɪl/", "微笑"), ("small", "/smɔːl/", "小的")]},
        {"rule": "sw/tr", "sound": "/sw/ /tr/", "cn": "s 接 w、t 接 r（如 swim、tree）", "tip": "tr 的 /r/ 要卷舌，像“戳”的轻读。",
         "words": [("swim", "/swɪm/", "游泳"), ("sweet", "/swiːt/", "甜的"), ("tree", "/triː/", "树"), ("train", "/treɪn/", "火车")]},
     ]},
    {"id": "p4", "name": "第四级 · r 控制元音与更多元音组合", "desc": "元音后面跟着 r，发音被“控制”（ar、er、ir、or、ur），以及 oo、ou、ow、oi、oy 等组合。",
     "rules": [
        {"rule": "ar", "sound": "/ɑː/", "cn": "ar 发 /ɑː/（如 car），嘴巴张大", "tip": "像“啊”但拉长：c-ar → /kɑː/。",
         "words": [("car", "/kɑː(r)/", "汽车"), ("star", "/stɑː(r)/", "星星"), ("park", "/pɑːk/", "公园"), ("farm", "/fɑːm/", "农场")]},
        {"rule": "er", "sound": "/ɜː/", "cn": "er 发 /ɜː/（如 her），舌中部抬起", "tip": "像“饿”的轻读，多在词尾：sist-er。",
         "words": [("her", "/hɜː(r)/", "她的"), ("sister", "/ˈsɪstə(r)/", "姐妹"), ("tiger", "/ˈtaɪɡə(r)/", "老虎"), ("father", "/ˈfɑːðə(r)/", "父亲")]},
        {"rule": "ir", "sound": "/ɜː/", "cn": "ir 发 /ɜː/（如 bird），与 er 同音", "tip": "看到 ir 就读“饿”：b-ir-d → /bɜːd/。",
         "words": [("bird", "/bɜːd/", "鸟"), ("girl", "/ɡɜːl/", "女孩"), ("shirt", "/ʃɜːt/", "衬衫"), ("first", "/fɜːst/", "第一")]},
        {"rule": "or", "sound": "/ɔː/", "cn": "or 发 /ɔː/（如 for），嘴唇收圆", "tip": "像“哦”但更圆更重：f-or → /fɔː/。",
         "words": [("for", "/fɔː(r)/", "为了"), ("horse", "/hɔːs/", "马"), ("morning", "/ˈmɔːnɪŋ/", "早晨"), ("short", "/ʃɔːt/", "短的")]},
        {"rule": "ur", "sound": "/ɜː/", "cn": "ur 发 /ɜː/（如 nurse），与 er/ir 同音", "tip": "n-ur-se → /nɜːs/，记住“一家人”。",
         "words": [("nurse", "/nɜːs/", "护士"), ("turn", "/tɜːn/", "转弯"), ("purple", "/ˈpɜːpl/", "紫色的"), ("hurt", "/hɜːt/", "受伤")]},
        {"rule": "oo", "sound": "/ʊ/ 或 /uː/", "cn": "oo 发 /ʊ/（book）或 /uː/（moon）", "tip": "短音常见于 k/d：b-oo-k；长音拉长：m-oo-n。",
         "words": [("book", "/bʊk/", "书"), ("foot", "/fʊt/", "脚"), ("moon", "/muːn/", "月亮"), ("school", "/skuːl/", "学校")]},
        {"rule": "ou", "sound": "/aʊ/", "cn": "ou 发 /aʊ/（如 house），嘴巴由大到小", "tip": "像“奥”加“乌”：h-ou-se → /haʊs/。",
         "words": [("house", "/haʊs/", "房子"), ("mouse", "/maʊs/", "老鼠"), ("mouth", "/maʊθ/", "嘴"), ("cloud", "/klaʊd/", "云")]},
        {"rule": "ow", "sound": "/aʊ/", "cn": "ow 也发 /aʊ/（如 cow），与 ou 同音", "tip": "c-ow → /kaʊ/；注意与第三级 /əʊ/ 区分。",
         "words": [("cow", "/kaʊ/", "奶牛"), ("now", "/naʊ/", "现在"), ("brown", "/braʊn/", "棕色的"), ("flower", "/ˈflaʊə(r)/", "花")]},
        {"rule": "oi/oy", "sound": "/ɔɪ/", "cn": "oi 与 oy 都发 /ɔɪ/（如 coin、boy）", "tip": "先“哦”再“一”快速连读：b-oy → /bɔɪ/。",
         "words": [("boy", "/bɔɪ/", "男孩"), ("toy", "/tɔɪ/", "玩具"), ("coin", "/kɔɪn/", "硬币"), ("point", "/pɔɪnt/", "指向")]},
        {"rule": "au/aw", "sound": "/ɔː/", "cn": "au 与 aw 都发 /ɔː/（如 August、draw）", "tip": "和 or 同音：dr-aw → /drɔː/。",
         "words": [("August", "/ˈɔːɡəst/", "八月"), ("autumn", "/ˈɔːtəm/", "秋天"), ("draw", "/drɔː/", "画画"), ("saw", "/sɔː/", "锯；看见(过去式)")]},
     ]},
    {"id": "p5", "name": "第五级 · 特殊规则", "desc": "进阶拼读：软音 c/g、不发音字母、双写字母、词尾 y 的发音。",
     "rules": [
        {"rule": "soft c", "sound": "/s/", "cn": "c 后面跟 e/i/y 时发 /s/（如 city）", "tip": "ce/ci/cy 里的 c 都读 /s/：ci-ty → /ˈsɪti/。",
         "words": [("city", "/ˈsɪti/", "城市"), ("circle", "/ˈsɜːkl/", "圆圈"), ("face", "/feɪs/", "脸"), ("ice", "/aɪs/", "冰")]},
        {"rule": "soft g", "sound": "/dʒ/", "cn": "g 后面跟 e/i/y 时常发 /dʒ/（如 orange）", "tip": "ge/gi 里的 g 常读 /dʒ/，像“知”的浊音。",
         "words": [("giraffe", "/dʒəˈrɑːf/", "长颈鹿"), ("orange", "/ˈɒrɪndʒ/", "橙子"), ("page", "/peɪdʒ/", "页"), ("cage", "/keɪdʒ/", "笼子")]},
        {"rule": "silent k", "sound": "/n/ 前 k 不发音", "cn": "kn 开头的 k 不发音（如 knife）", "tip": "k 不读，直接读 n：kn-ife → /naɪf/。",
         "words": [("knife", "/naɪf/", "小刀"), ("knee", "/niː/", "膝盖"), ("knock", "/nɒk/", "敲门"), ("know", "/nəʊ/", "知道")]},
        {"rule": "silent w", "sound": "/r/ 前 w 不发音", "cn": "wr 开头的 w 不发音（如 write）", "tip": "w 不读，直接读 r：wr-ite → /raɪt/。",
         "words": [("write", "/raɪt/", "写"), ("wrist", "/rɪst/", "手腕"), ("wrap", "/ræp/", "包裹"), ("wrong", "/rɒŋ/", "错误的")]},
        {"rule": "ll/ss", "sound": "双写字母只读一个音", "cn": "词尾双写 ll/ss 只读一个音（如 ball、class）", "tip": "看到双写读一个音：ba-ll → /bɔːl/。",
         "words": [("ball", "/bɔːl/", "球"), ("hill", "/hɪl/", "小山"), ("class", "/klɑːs/", "班级"), ("glass", "/ɡlɑːs/", "玻璃杯")]},
        {"rule": "y 结尾", "sound": "/i/ 或 /aɪ/", "cn": "词尾 y：多音节发 /i/（happy），单音节发 /aɪ/（my）", "tip": "happy 的 y 读“一”，my 的 y 读“爱”。",
         "words": [("happy", "/ˈhæpi/", "开心的"), ("sunny", "/ˈsʌni/", "晴朗的"), ("my", "/maɪ/", "我的"), ("fly", "/flaɪ/", "飞")]},
     ]},
]


def build_payload():
    levels = []
    nw = 0
    pool = {}
    for lv in LEVELS:
        for ri, r in enumerate(lv["rules"], 1):
            rid = lv["id"] + ('%02d' % ri)
            for wi, (w, ph, cn) in enumerate(r["words"], 1):
                pool[w] = rid

    def distractors(target_word, target_rid, n):
        same_letter = [w for w, rid in pool.items() if rid != target_rid and w != target_word and w[0] == target_word[0]]
        same_len = [w for w, rid in pool.items() if rid != target_rid and w != target_word and len(w) == len(target_word) and w not in same_letter]
        others = [w for w, rid in pool.items() if rid != target_rid and w != target_word and w not in same_letter and w not in same_len]
        return (same_letter + same_len + others)[:n]

    for lv in LEVELS:
        rules = []
        for ri, r in enumerate(lv["rules"], 1):
            rid = lv["id"] + ('%02d' % ri)
            words = []
            for wi, (w, ph, cn) in enumerate(r["words"], 1):
                nw += 1
                words.append({"id": rid + 'w%d' % wi, "word": w, "phonetic": ph,
                              "meaning": cn, "audio": "/audio/ph/" + rid + 'w%d.mp3' % wi})
            d1 = distractors(words[0]["word"], rid, 1)
            d2 = distractors(words[0]["word"], rid, 2)
            quiz = [
                {"type": "listen", "q": "听发音，选出你听到的单词", "audio": words[0]["audio"],
                 "options": [words[0]["word"], words[1]["word"], words[2]["word"]] + d1,
                 "answer": 0,
                 "tip": "先听清第一个音，再对比选项中单词的拼读规律。"},
                {"type": "find", "q": "哪个单词含有这个发音？", "sound": r["sound"],
                 "options": [words[0]["word"]] + d2,
                 "answer": 0,
                 "tip": "用拼读规则先自己读一遍每个词，再判断。"},
                {"type": "write", "q": "听音写单词（用拼读规则拼出来）", "audio": words[1]["audio"],
                 "answer": words[1]["word"], "tip": "按音节拆分拼写：" + words[1]["word"] + " → " + " · ".join(list(words[1]["word"])),
                 "phonetic": words[1]["phonetic"]},
            ]
            rules.append({"id": rid, "rule": r["rule"], "sound": r["sound"], "cn": r["cn"],
                          "tip": r["tip"], "audio": "/audio/ph/" + rid + ".mp3",
                          "words": words, "quiz": quiz})
        levels.append({"id": lv["id"], "name": lv["name"], "desc": lv["desc"], "rules": rules})
    return {"product": "小学英语自然拼读专项", "version": "1.0", "schema_version": "1.0",
            "note": "5 级 42 条规则 × 4 示例词；audio 为规则/单词发音（英音女声）；quiz 每规则 3 题（听音选词/找规律词/听音写词）",
            "levels": levels}, nw


def gen():
    payload, nw = build_payload()
    os.makedirs(DATA, exist_ok=True)
    with io.open(os.path.join(DATA, 'phonics.json'), 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    if os.path.isdir(WORKER_SRC):
        with io.open(os.path.join(WORKER_SRC, 'phonics.json'), 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print('已写入 worker:', WORKER_SRC)
    lines = ['# 小学英语自然拼读专项 · 规则与音频脚本',
             '',
             '> 数据源：对标小学自然拼读教学顺序（5 级 42 条规则 × 4 示例词 = %d 词）' % nw,
             '> 标注：内容由 AI 生成，待创始人人工校对（红线条款）。',
             '']
    for lv in LEVELS:
        lines += ['', '## %s %s' % (lv['id'].upper(), lv['name']), '']
        lines += ['> ' + lv['desc'], '']
        for ri, r in enumerate(lv['rules'], 1):
            rid = lv['id'] + ('%02d' % ri)
            lines.append('- **%s → %s** %s（%s）' % (r['rule'], r['sound'], r['cn'], r['tip']))
            for wi, (w, ph, cn) in enumerate(r['words'], 1):
                lines.append('  - %s %s %s → ph/%sw%d.mp3' % (w, ph, cn, rid, wi))
    os.makedirs(os.path.dirname(MATERIAL_MD), exist_ok=True)
    with io.open(MATERIAL_MD, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print('已写入素材库 md:', MATERIAL_MD)
    print('规则数:', sum(len(l['rules']) for l in LEVELS), '单词数:', nw)


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
    os.makedirs(AUDIO_PH, exist_ok=True)
    plan = []
    for lv in LEVELS:
        for ri, r in enumerate(lv['rules'], 1):
            rid = lv['id'] + ('%02d' % ri)
            plan.append((rid, r['rule']))
            for wi, (w, ph, cn) in enumerate(r['words'], 1):
                plan.append((rid + 'w%d' % wi, w))
    total = len(plan)
    ok = 0
    for i, (fid, text) in enumerate(plan, 1):
        out = os.path.join(AUDIO_PH, fid + '.mp3')
        if os.path.exists(out):
            ok += 1
            continue
        tmp = out + '.raw.mp3'
        try:
            await edge_tts.Communicate(text, VOICE, rate=RATE).save(tmp)
            normalize_audio(tmp)
            os.replace(tmp, out)
            ok += 1
            if i % 25 == 0 or i == total:
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
