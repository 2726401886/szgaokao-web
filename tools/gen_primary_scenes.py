# -*- coding: utf-8 -*-
"""小学英语单词场景化（词→句→对话）生成脚本
生成：
  1) data/primary_scenes.json（本地题库数据）
  2) E:\\szgaokao.cn\\worker\\src\\primary_scenes.json（线上 Workers 打包）
  3) 素材库《小学英语单词场景化-句子与对话脚本.md》
  4) public/audio/sc/ 例句 + 对话音频（英音女声，增量跳过）
用法：
  python tools/gen_primary_scenes.py gen
  python tools/gen_primary_scenes.py audio
  python tools/gen_primary_scenes.py all
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
AUDIO_SC = os.path.join(PUB, 'audio', 'sc')
WORKER_SRC = r'E:\szgaokao.cn\worker\src'
MATERIAL_MD = r'C:\Users\27264\WorkBuddy\2026-09-26-21-53-51\english-edu-company\03交付素材库\听说试卷包\小学英语单词场景化-句子与对话脚本.md'

VOICE = 'en-GB-SoniaNeural'
RATE = '-10%'

# —— 数据源：12 组场景（词→句→对话），内容对标小学 3-6 年级词汇 ——
# sentences: (word, sentence, cn)；dialogue: (title, [ (role, text, cn), ... ])
SCENES = [
    {"id": "s3a", "grade": 3, "title": "颜色与数字",
     "sentences": [
        ("red", "I see a red apple.", "我看见一个红苹果。"),
        ("blue", "The sky is blue.", "天空是蓝色的。"),
        ("green", "The grass is green.", "草地是绿色的。"),
        ("three", "I have three books.", "我有三本书。"),
        ("five", "There are five birds.", "有五只鸟。"),
        ("ten", "Ten plus two is twelve.", "十加二等于十二。"),
     ],
     "dialogue": ("数一数", [
        ("A", "Hello, Lily! How many crayons do you have?", "你好，莉莉！你有多少支蜡笔？"),
        ("B", "I have ten crayons.", "我有十支蜡笔。"),
        ("A", "What colour is your favourite one?", "你最喜欢哪一支？"),
        ("B", "It's blue. Blue is my favourite colour.", "是蓝色的。蓝色是我最喜欢的颜色。"),
        ("A", "Wow, blue is nice!", "哇，蓝色真好看！"),
     ])},
    {"id": "s3b", "grade": 3, "title": "文具与身体",
     "sentences": [
        ("pen", "This is my pen.", "这是我的钢笔。"),
        ("pencil", "I write with a pencil.", "我用铅笔写字。"),
        ("book", "Open your book, please.", "请打开你的书。"),
        ("bag", "My bag is heavy.", "我的书包很重。"),
        ("eye", "I have two eyes.", "我有两只眼睛。"),
        ("ear", "I listen with my ears.", "我用耳朵听。"),
     ],
     "dialogue": ("借文具", [
        ("A", "May I borrow your ruler?", "我可以借你的尺子吗？"),
        ("B", "Sure. Here you are.", "当然可以。给你。"),
        ("A", "Thank you! It's very nice.", "谢谢你！它真好用。"),
        ("B", "You're welcome. Don't forget to give it back.", "不客气。别忘了还给我。"),
        ("A", "OK, I will. See you later!", "好的，我会的。回头见！"),
     ])},
    {"id": "s3c", "grade": 3, "title": "动物与水果",
     "sentences": [
        ("cat", "The cat likes fish.", "猫喜欢鱼。"),
        ("dog", "The dog can run fast.", "狗跑得很快。"),
        ("duck", "The duck is in the water.", "鸭子在水中。"),
        ("apple", "I like apples.", "我喜欢苹果。"),
        ("banana", "The banana is yellow.", "香蕉是黄色的。"),
        ("orange", "I eat an orange.", "我吃了一个橙子。"),
     ],
     "dialogue": ("在农场", [
        ("A", "Look! What's that?", "看！那是什么？"),
        ("B", "It's a cow. It's white and black.", "那是一头奶牛。它是黑白相间的。"),
        ("A", "And what are those?", "那些是什么？"),
        ("B", "They are ducks. Quack, quack!", "它们是鸭子。嘎嘎！"),
        ("A", "Ha ha! The ducks are funny. I like them.", "哈哈！鸭子真有趣。我喜欢它们。"),
     ])},
    {"id": "s4a", "grade": 4, "title": "家庭与房间",
     "sentences": [
        ("father", "My father is tall.", "我爸爸个子很高。"),
        ("mother", "My mother cooks dinner.", "我妈妈做晚饭。"),
        ("sister", "My sister is six years old.", "我妹妹六岁。"),
        ("brother", "My brother plays football.", "我哥哥踢足球。"),
        ("room", "My room is clean and tidy.", "我的房间干净整洁。"),
        ("kitchen", "We eat in the kitchen.", "我们在厨房吃饭。"),
     ],
     "dialogue": ("我的家人", [
        ("A", "How many people are there in your family?", "你家有几口人？"),
        ("B", "There are four: my father, my mother, my sister and me.", "有四口：爸爸、妈妈、妹妹和我。"),
        ("A", "What does your father do at home?", "你爸爸在家做什么？"),
        ("B", "He reads books in the living room.", "他在客厅看书。"),
        ("A", "Your family is nice!", "你的家庭真温馨！"),
     ])},
    {"id": "s4b", "grade": 4, "title": "食物与饮料",
     "sentences": [
        ("rice", "I eat rice every day.", "我每天吃米饭。"),
        ("bread", "I have bread for breakfast.", "我早餐吃面包。"),
        ("milk", "I drink milk in the morning.", "我早上喝牛奶。"),
        ("juice", "Orange juice is my favourite.", "橙汁是我的最爱。"),
        ("egg", "There is an egg on the plate.", "盘子里有一个鸡蛋。"),
        ("water", "Drink some water, please.", "请喝点水。"),
     ],
     "dialogue": ("早餐时间", [
        ("A", "What do you want for breakfast?", "你早餐想吃什么？"),
        ("B", "I want some bread and milk.", "我想要面包和牛奶。"),
        ("A", "Would you like an egg too?", "还要一个鸡蛋吗？"),
        ("B", "Yes, please. Eggs are yummy.", "好的，谢谢。鸡蛋很好吃。"),
        ("A", "OK, breakfast is ready. Enjoy!", "好，早餐准备好了。慢慢享用！"),
     ])},
    {"id": "s4c", "grade": 4, "title": "衣物与天气",
     "sentences": [
        ("shirt", "He is wearing a white shirt.", "他穿着一件白衬衫。"),
        ("coat", "Put on your coat, it's cold.", "穿上外套，天冷了。"),
        ("hat", "She has a red hat.", "她有一顶红帽子。"),
        ("shoes", "My shoes are new.", "我的鞋子是新的。"),
        ("rainy", "It's rainy today. Take an umbrella.", "今天下雨，带把伞。"),
        ("sunny", "It's sunny and warm.", "天气晴朗又暖和。"),
     ],
     "dialogue": ("出门穿衣", [
        ("A", "What's the weather like today?", "今天天气怎么样？"),
        ("B", "It's windy and cold.", "刮风又冷。"),
        ("A", "Then I should wear my coat and hat.", "那我应该穿外套戴帽子。"),
        ("B", "Yes, and don't forget your gloves.", "对，别忘了戴手套。"),
        ("A", "Good idea! Let's go.", "好主意！我们走吧。"),
     ])},
    {"id": "s5a", "grade": 5, "title": "科目与学校",
     "sentences": [
        ("math", "We have a math class today.", "我们今天有数学课。"),
        ("English", "I like English very much.", "我非常喜欢英语。"),
        ("science", "Science is interesting.", "科学很有趣。"),
        ("music", "She sings in the music class.", "她在音乐课上唱歌。"),
        ("art", "I draw pictures in art class.", "我在美术课上画画。"),
        ("library", "We read books in the library.", "我们在图书馆看书。"),
     ],
     "dialogue": ("课表", [
        ("A", "What classes do you have today?", "你今天有什么课？"),
        ("B", "We have English, math and music.", "我们有英语、数学和音乐。"),
        ("A", "Music is my favourite class!", "音乐是我最喜欢的课！"),
        ("B", "Me too. I love singing.", "我也是。我喜欢唱歌。"),
        ("A", "Let's sing together at lunch break.", "午休时我们一起唱歌吧。"),
     ])},
    {"id": "s5b", "grade": 5, "title": "场所与出行",
     "sentences": [
        ("park", "Let's go to the park on Sunday.", "我们星期天去公园吧。"),
        ("zoo", "We saw many animals at the zoo.", "我们在动物园看到很多动物。"),
        ("hospital", "The hospital is near my home.", "医院在我家附近。"),
        ("supermarket", "My mother goes to the supermarket.", "我妈妈去超市。"),
        ("restaurant", "We had dinner at the restaurant.", "我们在餐馆吃的晚饭。"),
        ("station", "The bus station is over there.", "公交站在那边。"),
     ],
     "dialogue": ("问路", [
        ("A", "Excuse me, where is the museum?", "打扰一下，博物馆在哪里？"),
        ("B", "Go straight and turn left. It's next to the park.", "直走然后左转。它在公园旁边。"),
        ("A", "Is it far from here?", "离这儿远吗？"),
        ("B", "No, you can walk there in five minutes.", "不远，步行五分钟就到。"),
        ("A", "Thank you so much!", "非常感谢！"),
     ])},
    {"id": "s5c", "grade": 5, "title": "活动与爱好",
     "sentences": [
        ("swim", "I can swim in summer.", "夏天我能游泳。"),
        ("dance", "She dances very well.", "她跳舞跳得很好。"),
        ("sing", "He likes to sing songs.", "他喜欢唱歌。"),
        ("read", "I read books before bed.", "我睡觉前看书。"),
        ("draw", "My sister can draw a cat.", "我妹妹会画猫。"),
        ("play", "We play basketball after school.", "放学后我们打篮球。"),
     ],
     "dialogue": ("周末爱好", [
        ("A", "What do you do on weekends?", "你周末做什么？"),
        ("B", "I like swimming. It's fun!", "我喜欢游泳，很好玩！"),
        ("A", "I can't swim. I like drawing.", "我不会游泳。我喜欢画画。"),
        ("B", "Can you draw a dog for me?", "你能给我画一只狗吗？"),
        ("A", "Of course! I'll show you tomorrow.", "当然！明天画给你看。"),
     ])},
    {"id": "s6a", "grade": 6, "title": "职业与工作",
     "sentences": [
        ("doctor", "The doctor helps sick people.", "医生帮助生病的人。"),
        ("nurse", "The nurse works in the hospital.", "护士在医院工作。"),
        ("farmer", "The farmer grows vegetables.", "农民种蔬菜。"),
        ("driver", "The bus driver is friendly.", "公交车司机很友好。"),
        ("cook", "My uncle is a cook.", "我叔叔是一名厨师。"),
        ("teacher", "She is a good teacher.", "她是一位好老师。"),
     ],
     "dialogue": ("职业梦想", [
        ("A", "What do you want to be in the future?", "你将来想做什么？"),
        ("B", "I want to be a doctor. I want to help people.", "我想当医生，我想帮助别人。"),
        ("A", "That's great! What about your brother?", "太棒了！你哥哥呢？"),
        ("B", "He wants to be a cook. He loves cooking.", "他想当厨师，他喜欢做饭。"),
        ("A", "A doctor and a cook! Your family will be busy.", "医生和厨师！你们家会很忙。"),
     ])},
    {"id": "s6b", "grade": 6, "title": "感受与情绪",
     "sentences": [
        ("happy", "I feel happy today.", "我今天很开心。"),
        ("sad", "Don't be sad. Everything will be OK.", "别难过，一切都会好起来的。"),
        ("tired", "I'm tired after the long walk.", "走了很远的路，我很累。"),
        ("hungry", "I'm hungry. Let's have lunch.", "我饿了，我们吃午饭吧。"),
        ("thirsty", "After running, I feel thirsty.", "跑完步我觉得口渴。"),
        ("excited", "I'm excited about the trip.", "我对这次旅行感到兴奋。"),
     ],
     "dialogue": ("你还好吗", [
        ("A", "You look tired. Are you OK?", "你看起来很累。你还好吗？"),
        ("B", "Not very well. I'm hungry and thirsty.", "不太好。我又饿又渴。"),
        ("A", "Let's get some food and water.", "我们去弄点吃的和水吧。"),
        ("B", "That sounds great. Thanks!", "听起来不错。谢谢！"),
        ("A", "After eating, you will feel happy again.", "吃完东西你就会又开心起来。"),
     ])},
    {"id": "s6c", "grade": 6, "title": "自然与环境",
     "sentences": [
        ("sun", "The sun rises in the east.", "太阳从东方升起。"),
        ("moon", "The moon is bright at night.", "月亮在夜里很亮。"),
        ("cloud", "There are white clouds in the sky.", "天空中有白云。"),
        ("rain", "It often rains in spring.", "春天经常下雨。"),
        ("snow", "It snows in winter.", "冬天会下雪。"),
        ("flower", "The flowers are beautiful.", "这些花很漂亮。"),
     ],
     "dialogue": ("四季", [
        ("A", "Which season do you like best?", "你最喜欢哪个季节？"),
        ("B", "I like winter best. I can make a snowman.", "我最喜欢冬天。我可以堆雪人。"),
        ("A", "I like spring. The flowers are beautiful.", "我喜欢春天。花儿很漂亮。"),
        ("B", "And the trees turn green in spring.", "而且春天树都变绿了。"),
        ("A", "Every season is beautiful!", "每个季节都很美！"),
     ])},
]


def build_payload():
    scenes = []
    ns = 0
    nd = 0
    for sc in SCENES:
        sentences = []
        for i, (w, sent, cn) in enumerate(sc['sentences'], 1):
            ns += 1
            sentences.append({"id": "%s%02d" % (sc['id'], i), "word": w, "sentence": sent,
                              "cn": cn, "audio": "/audio/sc/%s%02d.mp3" % (sc['id'], i)})
        title, lines = sc['dialogue']
        dlines = []
        for j, (role, text, cn) in enumerate(lines, 1):
            dlines.append({"role": role, "text": text, "cn": cn,
                           "audio": "/audio/sc/%sd1-%d.mp3" % (sc['id'], j)})
        nd += 1
        scenes.append({"id": sc['id'], "grade": sc['grade'], "title": sc['title'],
                       "sentences": sentences,
                       "dialogue": {"id": sc['id'] + 'd1', "title": title, "lines": dlines}})
    return {"product": "小学英语单词场景化（词→句→对话）", "version": "1.0", "schema_version": "1.0",
            "note": "12 组场景：每组 6 个场景句（含核心词）+ 1 个情景对话；audio 为英音女声",
            "scenes": scenes}, ns, nd


def gen():
    payload, ns, nd = build_payload()
    os.makedirs(DATA, exist_ok=True)
    with io.open(os.path.join(DATA, 'primary_scenes.json'), 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    if os.path.isdir(WORKER_SRC):
        with io.open(os.path.join(WORKER_SRC, 'primary_scenes.json'), 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print('已写入 worker:', WORKER_SRC)
    lines = ['# 小学英语单词场景化 · 句子与对话脚本',
             '',
             '> 数据源：12 组场景（词→句→对话），共 %d 个场景句 + %d 段对话' % (ns, nd),
             '> 标注：内容由 AI 生成，待创始人人工校对（红线条款）。',
             '']
    for sc in SCENES:
        lines += ['', '## %s %s（Grade %d）' % (sc['id'].upper(), sc['title'], sc['grade']), '']
        lines.append('### 词→句')
        for i, (w, sent, cn) in enumerate(sc['sentences'], 1):
            lines.append('- **%s**：%s（%s）→ sc/%s%02d.mp3' % (w, sent, cn, sc['id'], i))
        title, dlines = sc['dialogue']
        lines += ['', '### 对话《%s》' % title]
        for j, (role, text, cn) in enumerate(dlines, 1):
            lines.append('- %s：%s（%s）→ sc/%sd1-%d.mp3' % (role, text, cn, sc['id'], j))
    os.makedirs(os.path.dirname(MATERIAL_MD), exist_ok=True)
    with io.open(MATERIAL_MD, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print('已写入素材库 md:', MATERIAL_MD)
    print('场景组数:', len(SCENES), '场景句:', ns, '对话:', nd)


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
    os.makedirs(AUDIO_SC, exist_ok=True)
    plan = []
    for sc in SCENES:
        for i, (w, sent, cn) in enumerate(sc['sentences'], 1):
            plan.append((sc['id'] + ('%02d' % i), sent))
        for j, (role, text, cn) in enumerate(sc['dialogue'][1], 1):
            plan.append((sc['id'] + 'd1-%d' % j, text))
    total = len(plan)
    ok = 0
    for i, (fid, text) in enumerate(plan, 1):
        out = os.path.join(AUDIO_SC, fid + '.mp3')
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
