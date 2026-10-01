# -*- coding: utf-8 -*-
"""生成初中英语单词音频 -> public/audio/jw/
词池 junior_words.json 的 audio 字段 (/audio/jw/jwXXnn.mp3)
课本 junior_textbook.json 中 /audio/jw/x<word>.mp3 的独有词
已存在的文件跳过（可断点续跑）。
依赖 edge-tts（venv: E:/WorkBuddyData/.workbuddy/binaries/python/envs/default）
"""
import os, sys, json, asyncio, edge_tts

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(ROOT, 'public', 'audio', 'jw')
VOICE = 'en-GB-SoniaNeural'
RATE = '-15%'
CONCURRENCY = 12

os.makedirs(AUDIO_DIR, exist_ok=True)

def collect():
    jobs = []  # (text, relpath)
    # 1) 词池
    pool = json.load(open(os.path.join(ROOT, 'data', 'junior_words.json'), encoding='utf-8'))
    for g in pool['groups']:
        for w in g['words']:
            ap = w.get('audio', '')
            if ap and ap.startswith('/audio/jw/'):
                fn = os.path.basename(ap)
                jobs.append((w['word'], fn))
    # 2) 课本独有 x<word>
    tb = json.load(open(os.path.join(ROOT, 'data', 'junior_textbook.json'), encoding='utf-8'))
    seen = set(j[1] for j in jobs)
    for b in tb['books']:
        for u in b['units']:
            for wd in u['words']:
                ap = wd.get('audio', '')
                if ap and ap.startswith('/audio/jw/x'):
                    fn = os.path.basename(ap)
                    if fn not in seen:
                        seen.add(fn)
                        jobs.append((wd['word'], fn))
    return jobs

async def gen_one(sem, text, fn, out, stats):
    async with sem:
        if os.path.exists(out):
            stats['skip'] += 1
            return
        try:
            comm = edge_tts.Communicate(text=text, voice=VOICE, rate=RATE)
            await comm.save(out)
            stats['ok'] += 1
        except Exception as e:
            stats['fail'] += 1
            print('FAIL', fn, repr(e)[:80], file=sys.stderr)

async def main():
    jobs = collect()
    print('待生成任务数:', len(jobs))
    sem = asyncio.Semaphore(CONCURRENCY)
    stats = {'ok': 0, 'skip': 0, 'fail': 0}
    tasks = [gen_one(sem, t, fn, os.path.join(AUDIO_DIR, fn), stats) for t, fn in jobs]
    await asyncio.gather(*tasks)
    print('生成:', stats['ok'], ' 跳过(已存在):', stats['skip'], ' 失败:', stats['fail'])

if __name__ == '__main__':
    asyncio.run(main())
