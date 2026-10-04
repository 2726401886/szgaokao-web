# -*- coding: utf-8 -*-
"""为三套课标词书（primary/junior/senior core）生成共享音频。

策略：
1) 复用 worker/public/audio 中已存在的同名词音频（避免重复 TTS），约 652 个；
2) 其余用 edge-tts(en-US-AvaNeural, rate=-10%) 合成，落到
   worker/public/audio/_core/<safe>/<safe>.mp3（部署源），
   并镜像到 szgaokao-web/public/audio/_core/（本地预览）。

音频路径与 build_vocab 写出的 /audio/_core/<safe>/<safe>.mp3 一致。
用法：python tools/gen_core_audio.py   （需系统 Python3.10 的 edge-tts）
"""
import asyncio, json, os, shutil, sys

WORKER_AUDIO = r'E:/szgaokao.cn/worker/public/audio'
WEB = r'C:/Users/27264/WorkBuddy/2026-09-26-21-53-51/szgaokao-web'
WEB_AUDIO = os.path.join(WEB, 'public', 'audio')
DATA = os.path.join(WEB, 'data')
CORE = ['primary_core.json', 'junior_core.json', 'senior_core.json']
VOICE = 'en-US-AvaNeural'
RATE = '-10%'
CONC = 8


def valid_mp3(p):
    if not os.path.exists(p) or os.path.getsize(p) < 512:
        return False
    with open(p, 'rb') as f:
        h = f.read(4)
    return len(h) >= 2 and h[0] == 0xFF and (h[1] & 0xE0) == 0xE0


def build_reuse():
    reuse = {}
    for dp, dn, fn in os.walk(WORKER_AUDIO):
        if '_core' in dp.split(os.sep):
            continue
        for f in fn:
            if f.endswith('.mp3') and valid_mp3(os.path.join(dp, f)):
                reuse.setdefault(f[:-4].lower(), os.path.join(dp, f))
    return reuse


def collect_words():
    words = set()
    for c in CORE:
        d = json.load(open(os.path.join(DATA, c), encoding='utf-8'))
        for u in d['units']:
            for w in u['words']:
                words.add(w['word'].lower())
    return sorted(words)


async def synth_one(sem, text, out1, out2):
    import edge_tts
    async with sem:
        last = ''
        for _ in range(3):
            try:
                os.makedirs(os.path.dirname(out1), exist_ok=True)
                await edge_tts.Communicate(text, VOICE, rate=RATE).save(out1)
                if valid_mp3(out1):
                    if out2 != out1:
                        os.makedirs(os.path.dirname(out2), exist_ok=True)
                        shutil.copyfile(out1, out2)
                    return True, ''
                return False, '校验失败'
            except Exception as e:
                await asyncio.sleep(2)
                last = str(e)[:80]
        return False, last


async def main():
    reuse = build_reuse()
    words = collect_words()
    can_reuse = sum(1 for w in words if w in reuse)
    print('唯一词 %d  可复用 %d  需新合成 %d' % (len(words), can_reuse, len(words) - can_reuse))

    skip = reuse_n = 0
    q = []
    for w in words:
        safe = w
        t1 = os.path.join(WORKER_AUDIO, '_core', safe, safe + '.mp3')
        t2 = os.path.join(WEB_AUDIO, '_core', safe, safe + '.mp3')
        if valid_mp3(t1) and valid_mp3(t2):
            skip += 1
            continue
        if w in reuse and valid_mp3(reuse[w]):
            os.makedirs(os.path.dirname(t1), exist_ok=True)
            shutil.copyfile(reuse[w], t1)
            os.makedirs(os.path.dirname(t2), exist_ok=True)
            shutil.copyfile(reuse[w], t2)
            reuse_n += 1
            continue
        q.append((w, t1, t2))
    print('跳过已存在 %d  复用复制 %d  进入合成队列 %d' % (skip, reuse_n, len(q)))

    sem = asyncio.Semaphore(CONC)
    ok = fail = 0
    for i in range(0, len(q), 40):
        chunk = q[i:i + 40]
        res = await asyncio.gather(*[synth_one(sem, w, t1, t2) for w, t1, t2 in chunk])
        for (w, t1, t2), r in zip(chunk, res):
            if r[0]:
                ok += 1
            else:
                fail += 1
                if fail <= 8:
                    print('  失败 %s %s' % (w, r[1]))
        print('  进度 %d/%d  成功 %d  失败 %d' % (min(i + 40, len(q)), len(q), ok, fail))
    print('\n完成：跳过 %d  复用 %d  合成成功 %d  合成失败 %d' % (skip, reuse_n, ok, fail))


if __name__ == '__main__':
    asyncio.run(main())
