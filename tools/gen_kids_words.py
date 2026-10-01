# -*- coding: utf-8 -*-
"""幼儿启蒙英语单词听读背记 · 数据源驱动生成脚本
生成：
  1) data/kids_words.json（本地题库数据）
  2) public/audio/ki/kiXNN.mp3 单词发音音频（英音女声，增量跳过已存在）
  3) 素材库《幼儿启蒙英语-核心词表与音频脚本.md》
用法：
  python tools/gen_kids_words.py gen
  python tools/gen_kids_words.py audio
"""
import asyncio, io, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
AUDIO_KI = os.path.join(ROOT, 'public', 'audio', 'ki')
MATERIAL_MD = r'C:\Users\27264\WorkBuddy\2026-09-26-21-53-51\english-edu-company\03交付素材库\听说试卷包\幼儿启蒙英语-核心词表与音频脚本.md'

VOICE = 'en-GB-SoniaNeural'
RATE = '-10%'

# (word, phonetic, pos, meaning)  6 组 × 20 词（3-6 岁启蒙主题）
GROUPS = [
    {"id": "k1", "grade": 0, "title": "动物乐园",
     "words": [
         ("cat", "/kæt/", "n.", "猫"), ("dog", "/dɒɡ/", "n.", "狗"), ("duck", "/dʌk/", "n.", "鸭子"),
         ("pig", "/pɪɡ/", "n.", "猪"), ("cow", "/kaʊ/", "n.", "奶牛"), ("sheep", "/ʃiːp/", "n.", "绵羊"),
         ("bird", "/bɜːd/", "n.", "鸟"), ("fish", "/fɪʃ/", "n.", "鱼"), ("rabbit", "/ˈræbɪt/", "n.", "兔子"),
         ("elephant", "/ˈelɪfənt/", "n.", "大象"), ("lion", "/ˈlaɪən/", "n.", "狮子"), ("tiger", "/ˈtaɪɡə(r)/", "n.", "老虎"),
         ("monkey", "/ˈmʌŋki/", "n.", "猴子"), ("bear", "/beə(r)/", "n.", "熊"), ("panda", "/ˈpændə/", "n.", "熊猫"),
         ("hen", "/hen/", "n.", "母鸡"), ("frog", "/frɒɡ/", "n.", "青蛙"), ("bee", "/biː/", "n.", "蜜蜂"),
         ("horse", "/hɔːs/", "n.", "马"), ("mouse", "/maʊs/", "n.", "老鼠"),
     ]},
    {"id": "k2", "grade": 0, "title": "颜色与数字",
     "words": [
         ("red", "/red/", "adj.", "红色的"), ("blue", "/bluː/", "adj.", "蓝色的"), ("green", "/ɡriːn/", "adj.", "绿色的"),
         ("yellow", "/ˈjeləʊ/", "adj.", "黄色的"), ("white", "/waɪt/", "adj.", "白色的"), ("black", "/blæk/", "adj.", "黑色的"),
         ("orange", "/ˈɒrɪndʒ/", "adj.", "橙色的"), ("pink", "/pɪŋk/", "adj.", "粉色的"), ("purple", "/ˈpɜːpl/", "adj.", "紫色的"),
         ("brown", "/braʊn/", "adj.", "棕色的"), ("one", "/wʌn/", "num.", "一"), ("two", "/tuː/", "num.", "二"),
         ("three", "/θriː/", "num.", "三"), ("four", "/fɔː(r)/", "num.", "四"), ("five", "/faɪv/", "num.", "五"),
         ("six", "/sɪks/", "num.", "六"), ("seven", "/ˈsevn/", "num.", "七"), ("eight", "/eɪt/", "num.", "八"),
         ("nine", "/naɪn/", "num.", "九"), ("ten", "/ten/", "num.", "十"),
     ]},
    {"id": "k3", "grade": 0, "title": "美味食物",
     "words": [
         ("apple", "/ˈæpl/", "n.", "苹果"), ("banana", "/bəˈnɑːnə/", "n.", "香蕉"), ("orange", "/ˈɒrɪndʒ/", "n.", "橙子"),
         ("milk", "/mɪlk/", "n.", "牛奶"), ("egg", "/eɡ/", "n.", "鸡蛋"), ("bread", "/bred/", "n.", "面包"),
         ("rice", "/raɪs/", "n.", "米饭"), ("cake", "/keɪk/", "n.", "蛋糕"), ("candy", "/ˈkændi/", "n.", "糖果"),
         ("water", "/ˈwɔːtə(r)/", "n.", "水"), ("juice", "/dʒuːs/", "n.", "果汁"), ("tea", "/tiː/", "n.", "茶"),
         ("cookie", "/ˈkʊki/", "n.", "饼干"), ("ice cream", "/ˌaɪs ˈkriːm/", "n.", "冰淇淋"), ("grape", "/ɡreɪp/", "n.", "葡萄"),
         ("pear", "/peə(r)/", "n.", "梨"), ("meat", "/miːt/", "n.", "肉"), ("fish", "/fɪʃ/", "n.", "鱼"),
         ("noodle", "/ˈnuːdl/", "n.", "面条"), ("soup", "/suːp/", "n.", "汤"),
     ]},
    {"id": "k4", "grade": 0, "title": "我的家庭与身体",
     "words": [
         ("mum", "/mʌm/", "n.", "妈妈"), ("dad", "/dæd/", "n.", "爸爸"), ("baby", "/ˈbeɪbi/", "n.", "婴儿"),
         ("brother", "/ˈbrʌðə(r)/", "n.", "哥哥；弟弟"), ("sister", "/ˈsɪstə(r)/", "n.", "姐姐；妹妹"), ("grandpa", "/ˈɡrænpɑː/", "n.", "爷爷；外公"),
         ("grandma", "/ˈɡrænmɑː/", "n.", "奶奶；外婆"), ("family", "/ˈfæməli/", "n.", "家庭"), ("eye", "/aɪ/", "n.", "眼睛"),
         ("ear", "/ɪə(r)/", "n.", "耳朵"), ("nose", "/nəʊz/", "n.", "鼻子"), ("mouth", "/maʊθ/", "n.", "嘴"),
         ("hand", "/hænd/", "n.", "手"), ("foot", "/fʊt/", "n.", "脚"), ("head", "/hed/", "n.", "头"),
         ("hair", "/heə(r)/", "n.", "头发"), ("arm", "/ɑːm/", "n.", "手臂"), ("leg", "/leɡ/", "n.", "腿"),
         ("face", "/feɪs/", "n.", "脸"), ("tooth", "/tuːθ/", "n.", "牙齿"),
     ]},
    {"id": "k5", "grade": 0, "title": "玩具与学校",
     "words": [
         ("toy", "/tɔɪ/", "n.", "玩具"), ("ball", "/bɔːl/", "n.", "球"), ("doll", "/dɒl/", "n.", "娃娃"),
         ("kite", "/kaɪt/", "n.", "风筝"), ("bike", "/baɪk/", "n.", "自行车"), ("car", "/kɑː(r)/", "n.", "小汽车"),
         ("book", "/bʊk/", "n.", "书"), ("bag", "/bæɡ/", "n.", "书包"), ("pen", "/pen/", "n.", "钢笔"),
         ("pencil", "/ˈpensl/", "n.", "铅笔"), ("desk", "/desk/", "n.", "课桌"), ("chair", "/tʃeə(r)/", "n.", "椅子"),
         ("teacher", "/ˈtiːtʃə(r)/", "n.", "老师"), ("student", "/ˈstjuːdnt/", "n.", "学生"), ("school", "/skuːl/", "n.", "学校"),
         ("classroom", "/ˈklɑːsruːm/", "n.", "教室"), ("picture", "/ˈpɪktʃə(r)/", "n.", "图画"), ("crayon", "/ˈkreɪən/", "n.", "蜡笔"),
         ("ruler", "/ˈruːlə(r)/", "n.", "尺子"), ("eraser", "/ɪˈreɪzə(r)/", "n.", "橡皮"),
     ]},
    {"id": "k6", "grade": 0, "title": "自然与天气",
     "words": [
         ("sun", "/sʌn/", "n.", "太阳"), ("moon", "/muːn/", "n.", "月亮"), ("star", "/stɑː(r)/", "n.", "星星"),
         ("sky", "/skaɪ/", "n.", "天空"), ("cloud", "/klaʊd/", "n.", "云"), ("rain", "/reɪn/", "n.", "雨"),
         ("snow", "/snəʊ/", "n.", "雪"), ("wind", "/wɪnd/", "n.", "风"), ("tree", "/triː/", "n.", "树"),
         ("flower", "/ˈflaʊə(r)/", "n.", "花"), ("grass", "/ɡrɑːs/", "n.", "草"), ("water", "/ˈwɔːtə(r)/", "n.", "水"),
         ("hill", "/hɪl/", "n.", "小山"), ("river", "/ˈrɪvə(r)/", "n.", "河流"), ("sea", "/siː/", "n.", "大海"),
         ("day", "/deɪ/", "n.", "白天"), ("night", "/naɪt/", "n.", "夜晚"), ("hot", "/hɒt/", "adj.", "热的"),
         ("cold", "/kəʊld/", "adj.", "冷的"), ("warm", "/wɔːm/", "adj.", "温暖的"),
     ]},
]


def build_payload():
    groups = []
    for g in GROUPS:
        words = []
        for i, (word, phon, pos, meaning) in enumerate(g["words"], 1):
            fid = g["id"] + ('%02d' % i)
            words.append({"id": fid, "word": word, "phonetic": phon, "pos": pos,
                          "meaning": meaning, "audio": "/audio/ki/" + fid + ".mp3"})
        groups.append({"id": g["id"], "grade": g["grade"], "title": g["title"], "words": words})
    return {"product": "幼儿启蒙英语单词听读背记", "version": "1.0", "schema_version": "1.0",
            "note": "3-6 岁启蒙词汇，按主题分组；audio 为单词发音；支持听/读/背/记四模式",
            "groups": groups}


def gen():
    payload = build_payload()
    os.makedirs(DATA, exist_ok=True)
    with io.open(os.path.join(DATA, 'kids_words.json'), 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    lines = ['# 幼儿启蒙英语 · 核心词表与音频脚本',
             '',
             '> 数据源：3-6 岁启蒙主题精编（6 组 × 20 词 = 120 词，英音女声）',
             '> 标注：内容由 AI 生成，待创始人人工校对（红线条款）。',
             '',
             '| 序号 | 单词 | 音标 | 词性 | 词义 | 音频文件 |',
             '| --- | --- | --- | --- | --- | --- |']
    n = 0
    for g in GROUPS:
        lines += ['', '## %s · %s' % (g['id'].upper(), g['title']), '']
        for i, (word, phon, pos, meaning) in enumerate(g['words'], 1):
            n += 1
            fid = g['id'] + ('%02d' % i)
            lines.append('| %d | %s | %s | %s | %s | ki/%s.mp3 |' % (n, word, phon, pos, meaning, fid))
    os.makedirs(os.path.dirname(MATERIAL_MD), exist_ok=True)
    with io.open(MATERIAL_MD, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print('kids_words.json 已生成；素材库 md 已写入；单词总数:', n)


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
    os.makedirs(AUDIO_KI, exist_ok=True)
    plan = []
    for g in GROUPS:
        for i, (word, phon, pos, meaning) in enumerate(g['words'], 1):
            plan.append((g['id'] + ('%02d' % i), word))
    total = len(plan)
    for i, (fid, word) in enumerate(plan, 1):
        out = os.path.join(AUDIO_KI, fid + '.mp3')
        if os.path.exists(out):
            print('[%d/%d] 跳过 %s' % (i, total, fid))
            continue
        tmp = out + '.raw.mp3'
        await edge_tts.Communicate(word, VOICE, rate=RATE).save(tmp)
        normalize_audio(tmp)
        os.replace(tmp, out)
        print('[%d/%d] OK %s (%s)' % (i, total, fid, word))
    print('幼儿单词音频完成:', total)


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'gen'
    if cmd in ('gen', 'all'):
        gen()
    if cmd in ('audio', 'all'):
        asyncio.run(gen_audio())
