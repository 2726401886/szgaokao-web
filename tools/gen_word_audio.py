# -*- coding: utf-8 -*-
"""为新词书（考研/四级等）批量生成单词发音 mp3 —— edge-tts，en-US-AvaNeural。

背景：新词书没有现成音频，而现有 7 套词书都自带 mp3。本脚本补齐音频缺口。
与已有的 tools/gen_audio.py（中考听说双声部对话）职责不同，故独立成文件。

音频规格（对齐现有资产）：
- 路径 public/audio/<mod>/<wordid>/<word>.mp3
- 语速 rate="-10%"（略慢，适合跟读）
- 单文件约 8-10KB（现有词书平均 37KB，同量级）

依赖：系统 Python 的 edge-tts（不是托管 Python）
用法：
  python tools/gen_word_audio.py --dry-run          # 先看将生成什么
  python tools/gen_word_audio.py                    # 生成
  python tools/gen_word_audio.py --sentences        # 同时生成例句音频
  python tools/gen_word_audio.py --force            # 重生成已存在的
"""
import argparse, asyncio, io, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.dirname(HERE)
DATA = os.path.join(WEB, 'data')
# 输出根：优先线上部署仓（E 盘，部署时读这里），否则本地
AUDIO_ROOTS = [r'E:/szgaokao.cn/worker/public/audio', os.path.join(WEB, 'public', 'audio')]

VOICE = 'en-US-AvaNeural'
RATE = '-10%'
CONCURRENCY = 6
BATCH = 60


def load_books(names):
    out = {}
    for n in names:
        p = os.path.join(DATA, 'vocab_%s.json' % n)
        if not os.path.exists(p):
            print('跳过（不存在）: vocab_%s.json' % n)
            continue
        with io.open(p, encoding='utf-8') as f:
            d = json.load(f)
        words = []
        for b in d.get('books', []):
            for u in b.get('units', []):
                words.extend(u.get('words', []))
        out[n] = words
    return out


def audio_root():
    for r in AUDIO_ROOTS:
        if os.path.isdir(r):
            return r
    r = AUDIO_ROOTS[0]
    os.makedirs(r, exist_ok=True)
    return r


def valid_mp3(path):
    """合法 MP3 校验：帧同步 0xFF 0xFx（无 ID3 标签也合法，浏览器可播）"""
    if not os.path.exists(path) or os.path.getsize(path) < 512:
        return False
    with open(path, 'rb') as f:
        head = f.read(4)
    return len(head) >= 2 and head[0] == 0xFF and (head[1] & 0xE0) == 0xE0


async def synth_one(sem, text, out_path):
    import edge_tts
    async with sem:
        for attempt in range(3):
            try:
                await edge_tts.Communicate(text, VOICE, rate=RATE).save(out_path)
                if valid_mp3(out_path):
                    return True, ''
                return False, '音频校验失败'
            except Exception as e:
                if attempt < 2:
                    await asyncio.sleep(2 * (attempt + 1))
                    continue
                return False, str(e)[:80]


async def run(books, want_sentences, dry_run, force):
    root = audio_root()
    tasks = []
    for key, words in books.items():
        for w in words:
            wid = w['id']
            wdir = os.path.join(root, key, wid)
            safe = w['word'].replace(' ', '_').replace('/', '_')
            wp = os.path.join(wdir, safe + '.mp3')
            if force or not valid_mp3(wp):
                tasks.append(('word', w['word'], wp))
            if want_sentences and w.get('sentence'):
                sp = os.path.join(wdir, 'sent.mp3')
                if force or not valid_mp3(sp):
                    tasks.append(('sent', w['sentence'], sp))

    if dry_run:
        print('[dry-run] 音频根: %s' % root)
        print('[dry-run] 待生成 %d 个文件' % len(tasks))
        for t in tasks[:8]:
            print('   %-4s %-24s -> %s' % (t[0], t[1][:24], t[2].replace(root, '...')))
        if len(tasks) > 8:
            print('   ... 其余 %d 个' % (len(tasks) - 8))
        return 0, 0

    if not tasks:
        print('全部音频已存在，无需生成')
        return 0, 0

    print('音频根: %s' % root)
    print('待生成 %d 个文件（并发 %d，音色 %s，语速 %s）' % (len(tasks), CONCURRENCY, VOICE, RATE))
    t0 = time.time()
    sem = asyncio.Semaphore(CONCURRENCY)
    ok = fail = 0
    errs = {}
    for i in range(0, len(tasks), BATCH):
        chunk = tasks[i:i + BATCH]
        coros = []
        for kind, text, path in chunk:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            coros.append(synth_one(sem, text, path))
        results = await asyncio.gather(*coros, return_exceptions=True)
        for (kind, text, path), r in zip(chunk, results):
            if isinstance(r, Exception):
                fail += 1
                k = str(r)[:60]; errs[k] = errs.get(k, 0) + 1
            elif r[0]:
                ok += 1
            else:
                fail += 1
                errs[r[1]] = errs.get(r[1], 0) + 1
        done = min(i + BATCH, len(tasks))
        el = time.time() - t0
        eta = el / done * (len(tasks) - done) if done else 0
        print('  进度 %d/%d  成功 %d  失败 %d  已用 %.0fs  剩余约 %.0fs'
              % (done, len(tasks), ok, fail, el, eta))
    print('\n完成：成功 %d / 失败 %d，总耗时 %.0fs' % (ok, fail, time.time() - t0))
    if errs:
        print('错误分布:')
        for e, c in sorted(errs.items(), key=lambda x: -x[1])[:5]:
            print('   %3d 次  %s' % (c, e))
    sample = [t[2] for t in tasks[:6] if os.path.exists(t[2])]
    if sample:
        print('抽样体积: %s' % ', '.join('%.1fKB' % (os.path.getsize(s) / 1024.0) for s in sample))
    return ok, fail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--books', nargs='*', default=['ky', 'cet4'])
    ap.add_argument('--sentences', action='store_true')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--force', action='store_true')
    args = ap.parse_args()

    books = load_books(args.books)
    if not books:
        print('未找到词书'); sys.exit(1)
    print('词书: %s  共 %d 词' % (', '.join('%s(%d)' % (k, len(v)) for k, v in books.items()),
                                sum(len(v) for v in books.values())))
    ok, fail = asyncio.run(run(books, args.sentences, args.dry_run, args.force))
    sys.exit(1 if fail else 0)


if __name__ == '__main__':
    main()
