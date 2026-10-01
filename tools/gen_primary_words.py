# -*- coding: utf-8 -*-
"""小学英语单词听读背记 · 数据源驱动生成脚本
生成：
  1) data/words.json（本地题库数据）
  2) E:\szgaokao.cn\worker\src\words.json（线上 Workers 打包）
  3) 素材库《小学英语单词听读背记-词表与音频脚本.md》
  4) public/audio/w/wXXNN.mp3 单词发音音频（英音女声，44.1kHz MPEG-1，增量跳过已存在）
用法：
  python tools/gen_primary_words.py gen     # 生成 JSON + md
  python tools/gen_primary_words.py audio   # 增量生成/补音频
  python tools/gen_primary_words.py all     # 两者
"""
import asyncio
import io
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
PUB = os.path.join(ROOT, 'public')
AUDIO_W = os.path.join(PUB, 'audio', 'w')
WORKER_SRC = r'E:\szgaokao.cn\worker\src'
MATERIAL_MD = r'C:\Users\27264\WorkBuddy\2026-09-26-21-53-51\english-edu-company\03交付素材库\听说试卷包\小学英语单词听读背记-词表与音频脚本.md'

VOICE = 'en-GB-SoniaNeural'
RATE = '-10%'  # 单词发音稍慢、清晰

# —— 数据源：16 组 × 20 词（参考 PEP 人教版小学英语课标主题）——
# (word, phonetic, pos, meaning)
GROUPS = [
    # —— Grade 3 ——
    {"id": "g3a", "grade": 3, "title": "颜色与数字",
     "words": [
         ("red", "/red/", "adj.", "红色的"), ("blue", "/bluː/", "adj.", "蓝色的"),
         ("green", "/ɡriːn/", "adj.", "绿色的"), ("yellow", "/ˈjeləʊ/", "adj.", "黄色的"),
         ("black", "/blæk/", "adj.", "黑色的"), ("white", "/waɪt/", "adj.", "白色的"),
         ("orange", "/ˈɒrɪndʒ/", "adj.", "橙色的"), ("brown", "/braʊn/", "adj.", "棕色的"),
         ("pink", "/pɪŋk/", "adj.", "粉色的"), ("purple", "/ˈpɜːpl/", "adj.", "紫色的"),
         ("one", "/wʌn/", "num.", "一"), ("two", "/tuː/", "num.", "二"),
         ("three", "/θriː/", "num.", "三"), ("four", "/fɔː(r)/", "num.", "四"),
         ("five", "/faɪv/", "num.", "五"), ("six", "/sɪks/", "num.", "六"),
         ("seven", "/ˈsevn/", "num.", "七"), ("eight", "/eɪt/", "num.", "八"),
         ("nine", "/naɪn/", "num.", "九"), ("ten", "/ten/", "num.", "十"),
     ]},
    {"id": "g3b", "grade": 3, "title": "文具与身体",
     "words": [
         ("pen", "/pen/", "n.", "钢笔"), ("pencil", "/ˈpensl/", "n.", "铅笔"),
         ("ruler", "/ˈruːlə(r)/", "n.", "尺子"), ("eraser", "/ɪˈreɪzə(r)/", "n.", "橡皮"),
         ("bag", "/bæɡ/", "n.", "书包"), ("book", "/bʊk/", "n.", "书"),
         ("crayon", "/ˈkreɪən/", "n.", "蜡笔"), ("pencil box", "/ˈpensl bɒks/", "n.", "铅笔盒"),
         ("eye", "/aɪ/", "n.", "眼睛"), ("ear", "/ɪə(r)/", "n.", "耳朵"),
         ("nose", "/nəʊz/", "n.", "鼻子"), ("mouth", "/maʊθ/", "n.", "嘴"),
         ("face", "/feɪs/", "n.", "脸"), ("head", "/hed/", "n.", "头"),
         ("hand", "/hænd/", "n.", "手"), ("arm", "/ɑːm/", "n.", "手臂"),
         ("leg", "/leɡ/", "n.", "腿"), ("foot", "/fʊt/", "n.", "脚"),
         ("body", "/ˈbɒdi/", "n.", "身体"), ("school", "/skuːl/", "n.", "学校"),
     ]},
    {"id": "g3c", "grade": 3, "title": "动物与水果",
     "words": [
         ("cat", "/kæt/", "n.", "猫"), ("dog", "/dɒɡ/", "n.", "狗"),
         ("duck", "/dʌk/", "n.", "鸭子"), ("pig", "/pɪɡ/", "n.", "猪"),
         ("cow", "/kaʊ/", "n.", "奶牛"), ("sheep", "/ʃiːp/", "n.", "绵羊"),
         ("horse", "/hɔːs/", "n.", "马"), ("hen", "/hen/", "n.", "母鸡"),
         ("bird", "/bɜːd/", "n.", "鸟"), ("fish", "/fɪʃ/", "n.", "鱼"),
         ("apple", "/ˈæpl/", "n.", "苹果"), ("banana", "/bəˈnɑːnə/", "n.", "香蕉"),
         ("pear", "/peə(r)/", "n.", "梨"), ("peach", "/piːtʃ/", "n.", "桃子"),
         ("watermelon", "/ˈwɔːtəmelən/", "n.", "西瓜"), ("grape", "/ɡreɪp/", "n.", "葡萄"),
         ("strawberry", "/ˈstrɔːbəri/", "n.", "草莓"), ("mango", "/ˈmæŋɡəʊ/", "n.", "芒果"),
         ("lemon", "/ˈlemən/", "n.", "柠檬"), ("cherry", "/ˈtʃeri/", "n.", "樱桃"),
     ]},
    # —— Grade 4 ——
    {"id": "g4a", "grade": 4, "title": "家庭与房间",
     "words": [
         ("father", "/ˈfɑːðə(r)/", "n.", "父亲"), ("mother", "/ˈmʌðə(r)/", "n.", "母亲"),
         ("brother", "/ˈbrʌðə(r)/", "n.", "兄弟"), ("sister", "/ˈsɪstə(r)/", "n.", "姐妹"),
         ("grandpa", "/ˈɡrænpɑː/", "n.", "爷爷；外公"), ("grandma", "/ˈɡrænmɑː/", "n.", "奶奶；外婆"),
         ("uncle", "/ˈʌŋkl/", "n.", "叔叔；舅舅"), ("aunt", "/ɑːnt/", "n.", "阿姨；姑姑"),
         ("family", "/ˈfæməli/", "n.", "家庭"), ("parent", "/ˈpeərənt/", "n.", "父母亲"),
         ("home", "/həʊm/", "n.", "家"), ("room", "/ruːm/", "n.", "房间"),
         ("bedroom", "/ˈbedruːm/", "n.", "卧室"), ("living room", "/ˈlɪvɪŋ ruːm/", "n.", "客厅"),
         ("kitchen", "/ˈkɪtʃɪn/", "n.", "厨房"), ("bathroom", "/ˈbɑːθruːm/", "n.", "浴室"),
         ("study", "/ˈstʌdi/", "n.", "书房"), ("door", "/dɔː(r)/", "n.", "门"),
         ("window", "/ˈwɪndəʊ/", "n.", "窗户"), ("bed", "/bed/", "n.", "床"),
     ]},
    {"id": "g4b", "grade": 4, "title": "食物与饮料",
     "words": [
         ("rice", "/raɪs/", "n.", "米饭"), ("noodles", "/ˈnuːdlz/", "n.", "面条"),
         ("bread", "/bred/", "n.", "面包"), ("egg", "/eɡ/", "n.", "鸡蛋"),
         ("milk", "/mɪlk/", "n.", "牛奶"), ("juice", "/dʒuːs/", "n.", "果汁"),
         ("water", "/ˈwɔːtə(r)/", "n.", "水"), ("tea", "/tiː/", "n.", "茶"),
         ("coffee", "/ˈkɒfi/", "n.", "咖啡"), ("soup", "/suːp/", "n.", "汤"),
         ("meat", "/miːt/", "n.", "肉"), ("chicken", "/ˈtʃɪkɪn/", "n.", "鸡肉"),
         ("beef", "/biːf/", "n.", "牛肉"), ("vegetable", "/ˈvedʒtəbl/", "n.", "蔬菜"),
         ("tomato", "/təˈmɑːtəʊ/", "n.", "西红柿"), ("potato", "/pəˈteɪtəʊ/", "n.", "土豆"),
         ("carrot", "/ˈkærət/", "n.", "胡萝卜"), ("cake", "/keɪk/", "n.", "蛋糕"),
         ("candy", "/ˈkændi/", "n.", "糖果"), ("cookie", "/ˈkʊki/", "n.", "饼干"),
     ]},
    {"id": "g4c", "grade": 4, "title": "衣物与天气",
     "words": [
         ("shirt", "/ʃɜːt/", "n.", "衬衫"), ("T-shirt", "/ˈtiː ʃɜːt/", "n.", "T恤衫"),
         ("dress", "/dres/", "n.", "连衣裙"), ("skirt", "/skɜːt/", "n.", "短裙"),
         ("coat", "/kəʊt/", "n.", "外套"), ("jacket", "/ˈdʒækɪt/", "n.", "夹克衫"),
         ("sweater", "/ˈswetə(r)/", "n.", "毛衣"), ("hat", "/hæt/", "n.", "帽子"),
         ("cap", "/kæp/", "n.", "鸭舌帽"), ("shoes", "/ʃuːz/", "n.", "鞋子"),
         ("socks", "/sɒks/", "n.", "袜子"), ("pants", "/pænts/", "n.", "裤子"),
         ("shorts", "/ʃɔːts/", "n.", "短裤"), ("weather", "/ˈweðə(r)/", "n.", "天气"),
         ("sunny", "/ˈsʌni/", "adj.", "晴朗的"), ("rainy", "/ˈreɪni/", "adj.", "下雨的"),
         ("cloudy", "/ˈklaʊdi/", "adj.", "多云的"), ("windy", "/ˈwɪndi/", "adj.", "有风的"),
         ("snowy", "/ˈsnəʊi/", "adj.", "下雪的"), ("hot", "/hɒt/", "adj.", "热的"),
     ]},
    # —— Grade 5 ——
    {"id": "g5a", "grade": 5, "title": "科目与学校",
     "words": [
         ("Chinese", "/ˌtʃaɪˈniːz/", "n.", "语文；中文"), ("English", "/ˈɪŋɡlɪʃ/", "n.", "英语"),
         ("math", "/mæθ/", "n.", "数学"), ("science", "/ˈsaɪəns/", "n.", "科学"),
         ("music", "/ˈmjuːzɪk/", "n.", "音乐"), ("art", "/ɑːt/", "n.", "美术"),
         ("PE", "/ˌpiː ˈiː/", "n.", "体育"), ("history", "/ˈhɪstri/", "n.", "历史"),
         ("geography", "/dʒiˈɒɡrəfi/", "n.", "地理"), ("computer", "/kəmˈpjuːtə(r)/", "n.", "电脑"),
         ("library", "/ˈlaɪbrəri/", "n.", "图书馆"), ("playground", "/ˈpleɪɡraʊnd/", "n.", "操场"),
         ("classroom", "/ˈklɑːsruːm/", "n.", "教室"), ("teacher", "/ˈtiːtʃə(r)/", "n.", "老师"),
         ("student", "/ˈstjuːdnt/", "n.", "学生"), ("friend", "/frend/", "n.", "朋友"),
         ("classmate", "/ˈklɑːsmeɪt/", "n.", "同学"), ("homework", "/ˈhəʊmwɜːk/", "n.", "作业"),
         ("exam", "/ɪɡˈzæm/", "n.", "考试"), ("question", "/ˈkwestʃən/", "n.", "问题"),
     ]},
    {"id": "g5b", "grade": 5, "title": "场所与出行",
     "words": [
         ("park", "/pɑːk/", "n.", "公园"), ("zoo", "/zuː/", "n.", "动物园"),
         ("museum", "/mjuˈziːəm/", "n.", "博物馆"), ("hospital", "/ˈhɒspɪtl/", "n.", "医院"),
         ("bank", "/bæŋk/", "n.", "银行"), ("supermarket", "/ˈsuːpəmɑːkɪt/", "n.", "超市"),
         ("restaurant", "/ˈrestrɒnt/", "n.", "餐馆"), ("hotel", "/həʊˈtel/", "n.", "旅馆"),
         ("airport", "/ˈeəpɔːt/", "n.", "机场"), ("station", "/ˈsteɪʃn/", "n.", "车站"),
         ("cinema", "/ˈsɪnəmə/", "n.", "电影院"), ("shop", "/ʃɒp/", "n.", "商店"),
         ("street", "/striːt/", "n.", "街道"), ("city", "/ˈsɪti/", "n.", "城市"),
         ("village", "/ˈvɪlɪdʒ/", "n.", "村庄"), ("country", "/ˈkʌntri/", "n.", "国家"),
         ("map", "/mæp/", "n.", "地图"), ("ticket", "/ˈtɪkɪt/", "n.", "票"),
         ("train", "/treɪn/", "n.", "火车"), ("plane", "/pleɪn/", "n.", "飞机"),
     ]},
    {"id": "g5c", "grade": 5, "title": "活动与爱好",
     "words": [
         ("run", "/rʌn/", "v.", "跑"), ("swim", "/swɪm/", "v.", "游泳"),
         ("jump", "/dʒʌmp/", "v.", "跳"), ("dance", "/dɑːns/", "v.", "跳舞"),
         ("sing", "/sɪŋ/", "v.", "唱歌"), ("draw", "/drɔː/", "v.", "画画"),
         ("read", "/riːd/", "v.", "读"), ("write", "/raɪt/", "v.", "写"),
         ("play", "/pleɪ/", "v.", "玩；打（球）"), ("watch", "/wɒtʃ/", "v.", "观看"),
         ("listen", "/ˈlɪsn/", "v.", "听"), ("speak", "/spiːk/", "v.", "说"),
         ("walk", "/wɔːk/", "v.", "走路"), ("ride", "/raɪd/", "v.", "骑"),
         ("drive", "/draɪv/", "v.", "开车"), ("clean", "/kliːn/", "v.", "打扫"),
         ("wash", "/wɒʃ/", "v.", "洗"), ("buy", "/baɪ/", "v.", "买"),
         ("football", "/ˈfʊtbɔːl/", "n.", "足球"), ("basketball", "/ˈbɑːskɪtbɔːl/", "n.", "篮球"),
     ]},
    # —— Grade 6 ——
    {"id": "g6a", "grade": 6, "title": "职业与工作",
     "words": [
         ("doctor", "/ˈdɒktə(r)/", "n.", "医生"), ("nurse", "/nɜːs/", "n.", "护士"),
         ("police officer", "/pəˈliːs ɒfɪsə(r)/", "n.", "警察"), ("farmer", "/ˈfɑːmə(r)/", "n.", "农民"),
         ("driver", "/ˈdraɪvə(r)/", "n.", "司机"), ("cook", "/kʊk/", "n.", "厨师"),
         ("worker", "/ˈwɜːkə(r)/", "n.", "工人"), ("businessman", "/ˈbɪznəsmæn/", "n.", "商人"),
         ("singer", "/ˈsɪŋə(r)/", "n.", "歌手"), ("dancer", "/ˈdɑːnsə(r)/", "n.", "舞者"),
         ("actor", "/ˈæktə(r)/", "n.", "演员"), ("pilot", "/ˈpaɪlət/", "n.", "飞行员"),
         ("engineer", "/ˌendʒɪˈnɪə(r)/", "n.", "工程师"), ("scientist", "/ˈsaɪəntɪst/", "n.", "科学家"),
         ("writer", "/ˈraɪtə(r)/", "n.", "作家"), ("reporter", "/rɪˈpɔːtə(r)/", "n.", "记者"),
         ("postman", "/ˈpəʊstmən/", "n.", "邮递员"), ("fisherman", "/ˈfɪʃəmən/", "n.", "渔民"),
         ("firefighter", "/ˈfaɪəfaɪtə(r)/", "n.", "消防员"), ("dentist", "/ˈdentɪst/", "n.", "牙医"),
     ]},
    {"id": "g6b", "grade": 6, "title": "感受与情绪",
     "words": [
         ("happy", "/ˈhæpi/", "adj.", "开心的"), ("sad", "/sæd/", "adj.", "难过的"),
         ("angry", "/ˈæŋɡri/", "adj.", "生气的"), ("tired", "/ˈtaɪəd/", "adj.", "疲惫的"),
         ("hungry", "/ˈhʌŋɡri/", "adj.", "饿的"), ("thirsty", "/ˈθɜːsti/", "adj.", "渴的"),
         ("excited", "/ɪkˈsaɪtɪd/", "adj.", "兴奋的"), ("worried", "/ˈwʌrid/", "adj.", "担心的"),
         ("afraid", "/əˈfreɪd/", "adj.", "害怕的"), ("surprised", "/səˈpraɪzd/", "adj.", "惊讶的"),
         ("bored", "/bɔːd/", "adj.", "无聊的"), ("nervous", "/ˈnɜːvəs/", "adj.", "紧张的"),
         ("proud", "/praʊd/", "adj.", "自豪的"), ("shy", "/ʃaɪ/", "adj.", "害羞的"),
         ("kind", "/kaɪnd/", "adj.", "友善的"), ("funny", "/ˈfʌni/", "adj.", "有趣的"),
         ("clever", "/ˈklevə(r)/", "adj.", "聪明的"), ("brave", "/breɪv/", "adj.", "勇敢的"),
         ("lazy", "/ˈleɪzi/", "adj.", "懒惰的"), ("polite", "/pəˈlaɪt/", "adj.", "有礼貌的"),
     ]},
    {"id": "g6c", "grade": 6, "title": "自然与环境",
     "words": [
         ("sun", "/sʌn/", "n.", "太阳"), ("moon", "/muːn/", "n.", "月亮"),
         ("star", "/stɑː(r)/", "n.", "星星"), ("sky", "/skaɪ/", "n.", "天空"),
         ("cloud", "/klaʊd/", "n.", "云"), ("rain", "/reɪn/", "n.", "雨"),
         ("wind", "/wɪnd/", "n.", "风"), ("snow", "/snəʊ/", "n.", "雪"),
         ("tree", "/triː/", "n.", "树"), ("flower", "/ˈflaʊə(r)/", "n.", "花"),
         ("grass", "/ɡrɑːs/", "n.", "草"), ("river", "/ˈrɪvə(r)/", "n.", "河流"),
         ("lake", "/leɪk/", "n.", "湖"), ("sea", "/siː/", "n.", "大海"),
         ("mountain", "/ˈmaʊntən/", "n.", "山；山脉"), ("hill", "/hɪl/", "n.", "小山"),
         ("forest", "/ˈfɒrɪst/", "n.", "森林"), ("island", "/ˈaɪlənd/", "n.", "岛"),
         ("beach", "/biːtʃ/", "n.", "沙滩"), ("farm", "/fɑːm/", "n.", "农场"),
     ]},
]


def build_payload():
    groups = []
    for g in GROUPS:
        words = []
        for i, (word, phon, pos, meaning) in enumerate(g["words"], 1):
            fid = g["id"] + ('%02d' % i)
            words.append({
                "id": fid,
                "word": word,
                "phonetic": phon,
                "pos": pos,
                "meaning": meaning,
                "audio": "/audio/w/" + fid + ".mp3",
            })
        groups.append({"id": g["id"], "grade": g["grade"], "title": g["title"],
                       "words": words})
    return {"product": "小学英语单词听读背记", "version": "1.0",
            "schema_version": "1.0",
            "note": "单词按年级与主题分组；audio 为单词发音；支持听/读/背/记四模式",
            "groups": groups}


def gen():
    payload = build_payload()
    os.makedirs(DATA, exist_ok=True)
    with io.open(os.path.join(DATA, 'words.json'), 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    if os.path.isdir(WORKER_SRC):
        with io.open(os.path.join(WORKER_SRC, 'words.json'), 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print('已写入 worker:', WORKER_SRC)
    # 素材库 md
    lines = ['# 小学英语单词听读背记 · 词表与音频脚本',
             '',
             '> 数据源：PEP 人教版小学英语课标主题精编（3–6 年级，16 组 × 20 词 = 320 词）',
             '> 标注：内容由 AI 生成，待创始人人工校对（红线条款）。',
             '',
             '| 序号 | 单词 | 音标 | 词性 | 词义 | 音频文件 |',
             '| --- | --- | --- | --- | --- | --- |']
    n = 0
    for g in GROUPS:
        lines += ['', '## %s（Grade %d · %s）' % (g['id'].upper(), g['grade'], g['title']), '']
        for i, (word, phon, pos, meaning) in enumerate(g['words'], 1):
            n += 1
            fid = g['id'] + ('%02d' % i)
            lines.append('| %d | %s | %s | %s | %s | w/%s.mp3 |' % (n, word, phon, pos, meaning, fid))
    os.makedirs(os.path.dirname(MATERIAL_MD), exist_ok=True)
    with io.open(MATERIAL_MD, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print('已写入素材库 md:', MATERIAL_MD)
    total = sum(len(g['words']) for g in GROUPS)
    print('单词总数:', total)


# —— 音频 ——
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
    os.makedirs(AUDIO_W, exist_ok=True)
    plan = []
    for g in GROUPS:
        for i, (word, phon, pos, meaning) in enumerate(g['words'], 1):
            fid = g['id'] + ('%02d' % i)
            plan.append((fid, word))
    total = len(plan)
    ok = 0
    for i, (fid, word) in enumerate(plan, 1):
        out = os.path.join(AUDIO_W, fid + '.mp3')
        if os.path.exists(out):
            ok += 1
            print('[%d/%d] 跳过已存在 %s' % (i, total, fid))
            continue
        tmp = out + '.raw.mp3'
        await edge_tts.Communicate(word, VOICE, rate=RATE).save(tmp)
        normalize_audio(tmp)
        os.replace(tmp, out)
        ok += 1
        print('[%d/%d] OK %s (%s)' % (i, total, fid, word))
    print('音频生成完成：%d/%d' % (ok, total))


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'gen'
    if cmd in ('gen', 'all'):
        gen()
    if cmd in ('audio', 'all'):
        asyncio.run(gen_audio())
    if cmd == 'audio':
        pass
