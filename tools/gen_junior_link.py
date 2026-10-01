# -*- coding: utf-8 -*-
"""小升初衔接包生成脚本（8 单元：语法要点 + 衔接词 + 小测）
生成：
  1) data/junior_link.json（本地）+ E:\\szgaokao.cn\\worker\\src\\junior_link.json（线上）
  2) 素材库《小学英语-小升初衔接包-8单元.md》
  3) public/audio/jl/ 衔接词+例句音频（英音女声，增量跳过）
用法：python tools/gen_junior_link.py gen / audio / all
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
AUDIO_JL = os.path.join(PUB, 'audio', 'jl')
WORKER_SRC = r'E:\szgaokao.cn\worker\src'
MATERIAL_MD = r'C:\Users\27264\WorkBuddy\2026-09-26-21-53-51\english-edu-company\03交付素材库\听说试卷包\小学英语-小升初衔接包-8单元.md'

VOICE = 'en-GB-SoniaNeural'
RATE = '-10%'

# 数据源：8 单元（语法点 + 衔接词 8 个 + 4 道小测）
UNITS = [
    {"id": "jl1", "title": "be 动词与自我介绍",
     "grammar": [
        ("be 动词三兄弟：am / is / are", "I am Tom. You are my friend. He is a pupil.", "我是汤姆。你是我的朋友。他是小学生。"),
        ("I 用 am，he/she/it 用 is，you/we/they 用 are", "She is a teacher. We are students.", "她是老师。我们是学生。"),
     ],
     "words": [("name","neɪm","名字"),("age","eɪdʒ","年龄"),("hobby","ˈhɒbi","爱好"),("birthday","ˈbɜːθdeɪ","生日"),("address","əˈdres","地址"),("email","ˈiːmeɪl","电子邮件"),("phone","fəʊn","电话"),("introduce","ˌɪntrəˈdjuːs","介绍")],
     "practice": [
        ("I ___ a pupil.", ["am", "is", "are"], 0, "I 用 am。"),
        ("She ___ my sister.", ["am", "is", "are"], 1, "she 用 is。"),
        ("We ___ good friends.", ["am", "is", "are"], 2, "we 用 are。"),
        ("___ you Tom? Yes, I am.", ["Is", "Are", "Am"], 1, "you 用 are。"),
     ]},
    {"id": "jl2", "title": "名词复数",
     "grammar": [
        ("规则复数：一般加 -s；s/x/ch/sh 结尾加 -es", "book → books; box → boxes; watch → watches", "书；盒子；手表。"),
        ("辅音字母 + y 结尾：变 y 为 i 加 -es", "city → cities; baby → babies", "城市；婴儿。"),
        ("不规则复数要牢记", "man → men; child → children; foot → feet", "男人；孩子；脚。"),
     ],
     "words": [("book","bʊk","书"),("box","bɒks","盒子"),("city","ˈsɪti","城市"),("baby","ˈbeɪbi","婴儿"),("man","mæn","男人"),("child","tʃaɪld","孩子"),("foot","fʊt","脚"),("tooth","tuːθ","牙齿")],
     "practice": [
        ("one box, two ___", ["boxs", "boxes", "box"], 1, "box 加 -es。"),
        ("one city, two ___", ["citys", "cities", "cityes"], 1, "city → cities。"),
        ("one man, two ___", ["mans", "men", "mens"], 1, "man 不规则，men。"),
        ("one child, three ___", ["childs", "children", "childrens"], 1, "child → children。"),
     ]},
    {"id": "jl3", "title": "代词",
     "grammar": [
        ("主格做主语：I / you / he / she / it / we / they", "I like English. They are my friends.", "我喜欢英语。他们是我的朋友。"),
        ("宾格做宾语：me / you / him / her / it / us / them", "Please help me. I like her.", "请帮帮我。我喜欢她。"),
        ("物主代词表所属：my / your / his / her / its / our / their", "This is my book. That is your pen.", "这是我的书。那是你的钢笔。"),
     ],
     "words": [("I","aɪ","我"),("you","juː","你"),("he","hiː","他"),("she","ʃiː","她"),("we","wiː","我们"),("they","ðeɪ","他们"),("my","maɪ","我的"),("their","ðeə","他们的")],
     "practice": [
        ("___ am a pupil.", ["I", "Me", "My"], 0, "主格 I 做主语。"),
        ("Please give ___ the book.", ["I", "me", "my"], 1, "give 后接宾格 me。"),
        ("This is ___ new bag.", ["I", "me", "my"], 2, "我的书包 my bag。"),
        ("___ are good students.", ["She", "They", "Her"], 1, "复数主格 they。"),
     ]},
    {"id": "jl4", "title": "一般现在时",
     "grammar": [
        ("表示经常性动作：动词原形（第三人称单数加 -s/-es）", "I get up at seven. She gets up at seven too.", "我七点起床。她也七点起床。"),
        ("频率词：always / usually / often / sometimes", "I usually walk to school.", "我通常步行上学。"),
     ],
     "words": [("always","ˈɔːlweɪz","总是"),("usually","ˈjuːʒuəli","通常"),("often","ˈɒfn","经常"),("sometimes","ˈsʌmtaɪmz","有时"),("never","ˈnevə","从不"),("get up","ɡet ʌp","起床"),("go to school","ɡəʊ tuː skuːl","去上学"),("every day","ˈevri deɪ","每天")],
     "practice": [
        ("She ___ to school by bus.", ["go", "goes", "going"], 1, "第三人称单数 goes。"),
        ("I ___ my homework every day.", ["do", "does", "doing"], 0, "I 用原形 do。"),
        ("He ___ English very much.", ["like", "likes", "liking"], 1, "he 用 likes。"),
        ("They ___ football on Sundays.", ["play", "plays", "playing"], 0, "they 用原形 play。"),
     ]},
    {"id": "jl5", "title": "现在进行时",
     "grammar": [
        ("表示正在发生：be + 动词-ing", "I am reading. She is singing.", "我正在看书。她正在唱歌。"),
        ("动词加 -ing 的规则", "run → running; make → making; read → reading", "双写；去 e；直接加。"),
     ],
     "words": [("read","riːd","读"),("write","raɪt","写"),("run","rʌn","跑"),("swim","swɪm","游泳"),("draw","drɔː","画"),("listen","ˈlɪsn","听"),("watch","wɒtʃ","看"),("now","naʊ","现在")],
     "practice": [
        ("Look! She ___ dancing.", ["is", "are", "am"], 0, "she 用 is + dancing。"),
        ("I ___ my homework now.", ["am doing", "is doing", "do"], 0, "I am doing 现在进行。"),
        ("They ___ playing games.", ["is", "are", "am"], 1, "they 用 are。"),
        ("run 的 -ing 形式是 ___", ["runing", "running", "run"], 1, "run 双写 n。"),
     ]},
    {"id": "jl6", "title": "介词",
     "grammar": [
        ("in / on / at 表时间与位置", "in the morning; on Monday; at 8 o'clock", "在早上；在周一；在八点。"),
        ("under / behind / next to 表方位", "The cat is under the desk. The boy is behind the door.", "猫在桌子下面。男孩在门后面。"),
     ],
     "words": [("in","ɪn","在…里"),("on","ɒn","在…上"),("at","æt","在（时刻）"),("under","ˈʌndə","在…下面"),("behind","bɪˈhaɪnd","在…后面"),("next to","nekst tuː","在…旁边"),("between","bɪˈtwiːn","在…之间"),("in front of","ɪn frʌnt ɒv","在…前面")],
     "practice": [
        ("I get up ___ seven.", ["in", "at", "on"], 1, "时刻用 at。"),
        ("We have PE ___ Monday.", ["in", "at", "on"], 2, "星期用 on。"),
        ("The ball is ___ the chair.", ["under", "at", "on time"], 0, "在椅子下面 under。"),
        ("She is sitting ___ me.", ["between", "next to", "at"], 1, "在我旁边 next to。"),
     ]},
    {"id": "jl7", "title": "一般过去时",
     "grammar": [
        ("表示过去发生：be 动词 was/were；行为动词过去式", "I was at home yesterday. She went to the park.", "我昨天在家。她去了公园。"),
        ("常见规则过去式加 -ed；不规则要记忆", "play → played; go → went; see → saw", "玩过；去过；看见过。"),
     ],
     "words": [("yesterday","ˈjestədeɪ","昨天"),("last","lɑːst","上一个"),("ago","əˈɡəʊ","以前"),("went","went","去过"),("saw","sɔː","看见过"),("was","wɒz","是（过去）"),("were","wɜː","是（过去复数）"),("visited","ˈvɪzɪtɪd","参观过")],
     "practice": [
        ("I ___ at home yesterday.", ["am", "was", "is"], 1, "过去用 was。"),
        ("They ___ in the park last Sunday.", ["was", "were", "are"], 1, "复数过去 were。"),
        ("She ___ to Beijing last month.", ["go", "goes", "went"], 2, "过去式 went。"),
        ("We ___ a film last night.", ["see", "saw", "seeing"], 1, "过去式 saw。"),
     ]},
    {"id": "jl8", "title": "there be 句型",
     "grammar": [
        ("表示某地有某物：There is + 单数；There are + 复数", "There is a book on the desk. There are two pens in the bag.", "书桌上有一本书。书包里有两支钢笔。"),
        ("就近原则：靠近 be 的名词决定 is/are", "There is a pen and two books. / There are two books and a pen.", "一支钢笔和两本书。/ 两本书和一支钢笔。"),
     ],
     "words": [("there","ðeə","那里"),("is","ɪz","是（单数）"),("are","ɑː","是（复数）"),("some","sʌm","一些"),("any","ˈeni","任何"),("room","ruːm","房间"),("place","pleɪs","地方"),("everything","ˈevriθɪŋ","一切")],
     "practice": [
        ("There ___ a book on the desk.", ["is", "are", "am"], 0, "单数用 is。"),
        ("There ___ many students in the school.", ["is", "are", "am"], 1, "复数用 are。"),
        ("There ___ an apple and two oranges.", ["is", "are", "be"], 0, "就近 apple 单数。"),
        ("Are there ___ books in your bag?", ["some", "any", "a"], 1, "疑问句用 any。"),
     ]},
]


def build_payload():
    units = []
    nw = 0
    np = 0
    for u in UNITS:
        g = [{"point": p, "example": e, "cn": c, "audio": "/audio/jl/%s-g%d.mp3" % (u['id'], gi + 1)} for gi, (p, e, c) in enumerate(u['grammar'])]
        wl = []
        for wi, (w, ph, mean) in enumerate(u['words'], 1):
            nw += 1
            wid = u['id'] + ('-w%d' % wi)
            wl.append({"id": wid, "word": w, "phonetic": ph, "meaning": mean, "audio": "/audio/jl/" + wid + ".mp3"})
        pr = []
        for pi, (q, opts, ans, tip) in enumerate(u['practice'], 1):
            np += 1
            pr.append({"id": u['id'] + ('-p%d' % pi), "q": q, "options": opts, "answer": ans, "tip": tip})
        units.append({"id": u['id'], "title": u['title'], "grammar": g, "words": wl, "practice": pr})
    return {"product": "小升初英语衔接包（8 单元）", "version": "1.0", "schema_version": "1.0",
            "note": "语法要点 + 衔接词 + 小测；内容 AI 生成待创始人校对",
            "units": units}, nw, np


def gen():
    payload, nw, np = build_payload()
    os.makedirs(DATA, exist_ok=True)
    with io.open(os.path.join(DATA, 'junior_link.json'), 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    if os.path.isdir(WORKER_SRC):
        with io.open(os.path.join(WORKER_SRC, 'junior_link.json'), 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    lines = ['# 小升初英语衔接包（8 单元）', '', '> 数据源：8 单元 ×（语法 + 8 词 + 4 测）；内容 AI 生成待创始人校对。', '']
    for u in UNITS:
        lines += ['', '## %s %s' % (u['id'].upper(), u['title'])]
        for p, e, c in u['grammar']:
            lines.append('- **%s**：%s（%s）' % (p, e, c))
        lines.append('- 衔接词：%s' % '、'.join(w for w, _, _ in u['words']))
        for q, opts, ans, tip in u['practice']:
            lines.append('- 小测：%s｜答案：%s' % (q, opts[ans]))
    os.makedirs(os.path.dirname(MATERIAL_MD), exist_ok=True)
    with io.open(MATERIAL_MD, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print('写入完成：junior_link.json（%d 词 / %d 题）+ 素材 md' % (nw, np))


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
    os.makedirs(AUDIO_JL, exist_ok=True)
    plan = []
    for u in UNITS:
        for wi, (w, ph, mean) in enumerate(u['words'], 1):
            plan.append((u['id'] + ('-w%d' % wi), w))
        for gi, (p, e, c) in enumerate(u['grammar'], 1):
            plan.append((u['id'] + ('-g%d' % gi), e))
    total = len(plan)
    ok = 0
    for i, (fid, text) in enumerate(plan, 1):
        out = os.path.join(AUDIO_JL, fid + '.mp3')
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
