# -*- coding: utf-8 -*-
# 幼儿儿歌"真唱版"生成器 v3 —— 针对"断断续续/不流畅"的修复
# 相对 v2 的关键改进：
#   1) 旋律按"音的时值(:1/:2/:0.5)"映射，而不是等时间切片 —— 节奏终于对上原曲
#   2) 更强多级滑音平滑 —— 音与音之间是圆滑的 legato 滑音，不再有突兀跳音(275Hz大跳)
#   3) 振幅平滑 —— 抹掉"一字一蹦"的说话感，连成歌唱的平直力度
#   4) 轻混响 —— 黏合声部、柔化起音
#   5) 整首四句之间做交叉淡化 —— 不再硬切
# 仍为 100% 免费方案：edge-tts + WORLD 声码器本地运行。
import os, sys, io, subprocess, tempfile, math, asyncio
import numpy as np
import soundfile as sf
import pyworld
import edge_tts

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KS_DIR = os.path.join(ROOT, 'public', 'audio', 'ks')
BAK_DIR = os.path.join(ROOT, 'tools', '_backup_ks_sing')
SR = 44100
VOICE = 'en-US-AriaNeural'
TTS_RATE = '-10%'                 # 稍放慢，更像唱

import subprocess as _sp
_FFMPEG = _sp.check_output(
    [r'C:\Users\27264\.workbuddy\binaries\python\envs\default\Scripts\python.exe',
     '-c', 'import imageio_ffmpeg,sys; sys.stdout.write(imageio_ffmpeg.get_ffmpeg_exe())']
).decode().strip()

NOTE_SEMI = {'C': -9, 'D': -7, 'E': -5, 'F': -4, 'G': -2, 'A': 0, 'B': 2}
def freq(name):
    n, octv = name[:-1], int(name[-1])
    semi = NOTE_SEMI[n] + (octv - 4) * 12
    return 440.0 * (2 ** (semi / 12.0))

# 与 gen_kids_songs_melody.py 一致的旋律（带时值）
SONGS = {
    'ks1': ['C4:1 C4:1 G4:1 G4:1 A4:1 A4:1 G4:2', 'F4:1 F4:1 E4:1 E4:1 D4:1 D4:1 C4:2',
            'G4:1 G4:1 F4:1 F4:1 E4:1 E4:1 D4:2', 'F4:1 F4:1 E4:1 E4:1 D4:1 D4:1 C4:2'],
    'ks2': ['E4:1 E4:1 D4:1 C4:1 D4:1 E4:1 G4:2', 'A4:1 A4:1 G4:1 E4:1 G4:1 E4:1 C4:2',
            'E4:1 G4:1 A4:1 A4:1 G4:1 E4:1 D4:2', 'C4:1 D4:1 E4:1 D4:1 C4:1 C4:1 C4:2'],
    'ks3': ['C4:1 C4:1 D4:1 E4:1 G4:1 G4:1 E4:2', 'F4:1 F4:1 E4:1 D4:1 E4:1 D4:1 C4:2',
            'E4:1 E4:1 D4:1 C4:1 D4:1 E4:1 D4:2', 'G4:1 E4:1 D4:1 D4:1 C4:1 C4:1 C4:2'],
    'ks4': ['G4:1 G4:1 A4:1 G4:1 E4:1 E4:1 D4:2', 'G4:1 A4:1 B4:1 A4:1 G4:1 E4:1 D4:2',
            'E4:1 E4:1 F4:1 E4:1 D4:1 C4:1 G4:2', 'E4:1 D4:1 C4:1 D4:1 E4:1 D4:1 C4:2'],
    'ks5': ['C4:1 E4:1 G4:1 E4:1 A4:1 G4:1 E4:2', 'F4:1 A4:1 G4:1 F4:1 E4:1 D4:1 C4:2',
            'D4:1 F4:1 A4:1 G4:1 F4:1 E4:1 D4:2', 'E4:1 G4:1 F4:1 E4:1 D4:1 C4:1 C4:2'],
    'ks6': ['G4:0.5 G4:0.5 A4:1 A4:1 G4:1 E4:1 D4:1 G4:2', 'E4:0.5 E4:0.5 F4:1 G4:1 A4:1 G4:1 F4:1 E4:2',
            'C4:1 C4:1 D4:1 E4:1 E4:1 D4:1 C4:2', 'D4:1 E4:1 F4:1 F4:1 E4:1 D4:1 C4:2'],
    'ks7': ['A4:1 A4:1 G4:1 E4:1 G4:1 G4:1 E4:2', 'F4:1 F4:1 E4:1 D4:1 C4:1 D4:1 E4:2',
            'E4:1 G4:1 A4:1 G4:1 E4:1 D4:1 C4:2', 'D4:1 E4:1 D4:1 C4:1 D4:1 E4:1 C4:2'],
    'ks8': ['C4:0.5 C4:0.5 D4:1 E4:1 G4:1 E4:1 D4:1 C4:2', 'D4:0.5 D4:0.5 E4:1 F4:1 A4:1 F4:1 E4:1 D4:2',
            'E4:0.5 E4:0.5 F4:1 G4:1 A4:1 G4:1 F4:1 G4:2', 'G4:1 A4:1 G4:1 E4:1 D4:1 C4:1 C4:2'],
    'ks9': ['E4:1 G4:1 C5:1 C5:1 B4:1 A4:1 G4:2', 'A4:1 A4:1 G4:1 E4:1 F4:1 E4:1 D4:2',
            'E4:1 G4:1 A4:1 G4:1 E4:1 D4:1 C4:2', 'D4:1 E4:1 G4:1 E4:1 D4:1 C4:1 C4:2'],
    'ks10': ['G4:1 E4:1 E4:1 F4:1 F4:1 E4:1 D4:2', 'G4:1 G4:1 A4:1 B4:1 B4:1 A4:1 G4:2',
             'A4:1 G4:1 F4:1 E4:1 F4:1 G4:1 D4:2', 'E4:1 D4:1 C4:1 D4:1 E4:1 D4:1 C4:2'],
}

def parse_notes(phrase):
    out = []
    for tok in phrase.split():
        n, d = tok.split(':')
        d = float(d)
        out.append((0.0, d) if n == 'R' else (freq(n), d))
    return out

def target_f0(t, notes):
    total = sum(d for _, d in notes)
    if total <= 0 or len(notes) == 0:
        return np.zeros(len(t))
    cum = np.cumsum([d for _, d in notes])        # 每个音在"节拍轴"上的结束位置
    pos = (t / t[-1]) * total                     # 把整句语音时间线性映射到节拍轴(保留相对时值)
    target = np.zeros(len(t))
    for (f, d), end in zip(notes, cum):
        start = end - d
        if end >= total:
            target[pos >= start] = f
        else:
            target[(pos >= start) & (pos < end)] = f
    return target

def moving_mean(x, w):
    if w <= 1:
        return x
    return np.convolve(x, np.ones(w) / w, mode='same')

def reverb(x, wet=0.14, decay=0.25):
    m = int(decay * SR)
    ir = np.exp(-np.linspace(0, 6, m)) * (np.random.randn(m) * 0.4 + 0.6 * np.sin(np.linspace(0, 25, m)))
    ir /= (np.abs(ir).max() + 1e-9)
    ir[0] = 1.0
    n = len(x)
    fsize = 1 << (int(np.log2(n + m - 1)) + 1)
    X = np.fft.rfft(x, fsize); H = np.fft.rfft(ir, fsize)
    y = np.fft.irfft(X * H)[:n]
    return x * (1 - wet) + y * wet

def decode_mp3_to_mono_f32(path):
    p = _sp.run([_FFMPEG, '-y', '-loglevel', 'error', '-i', path,
                 '-ar', str(SR), '-ac', '1', '-f', 'f32le', 'pipe:1'],
                stdout=_sp.PIPE, stderr=_sp.PIPE, check=True)
    return np.frombuffer(p.stdout, dtype='<f4').astype(np.float64)

def encode_mp3(path, data_f32):
    peak = max(1e-9, np.abs(data_f32).max())
    data_f32 = (data_f32 / peak * 0.9).astype('<f4')
    raw = data_f32.tobytes()
    _sp.run([_FFMPEG, '-y', '-loglevel', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1',
             '-i', 'pipe:0', '-codec:a', 'libmp3lame', '-b:a', '64k', '-ac', '1', path],
            input=raw, check=True)

async def tts_to_wav(text):
    tmp_mp3 = tempfile.mktemp(suffix='.mp3')
    tmp_wav = tempfile.mktemp(suffix='.wav')
    try:
        comm = edge_tts.Communicate(text, VOICE, rate=TTS_RATE)
        await comm.save(tmp_mp3)
        _sp.run([_FFMPEG, '-y', '-loglevel', 'error', '-i', tmp_mp3,
                 '-ar', str(SR), '-ac', '1', '-f', 'wav', tmp_wav], check=True)
        data, _ = sf.read(tmp_wav, dtype='float64', always_2d=False)
        if data.ndim > 1:
            data = data.mean(axis=1)
        return data
    finally:
        for f in (tmp_mp3, tmp_wav):
            if os.path.exists(f):
                os.remove(f)

def sing_vocal(speech, notes):
    data = np.ascontiguousarray(speech.astype(np.float64))
    f0, tpos = pyworld.harvest(data, SR, f0_floor=80.0, f0_ceil=520.0)
    f0 = pyworld.stonemask(data, f0, tpos, SR)
    sp = pyworld.cheaptrick(data, f0, tpos, SR)
    ap = pyworld.d4c(data, f0, tpos, SR)
    nframes = len(f0)
    t = np.arange(nframes) * 0.005

    # 1) 按音的时值构造目标音高（节奏对上原曲）
    target = target_f0(t, notes)
    # 2) 多级滑音平滑：音与音之间是圆滑过渡，消除突兀大跳
    for wms in (0.04, 0.10, 0.18):
        w = max(3, int(wms / 0.005))
        target = moving_mean(target, w)
    target = target * (1 + 0.003 * np.sin(2 * np.pi * 5.0 * t))   # 轻微颤音

    # 3) 连续发声：桥接 <0.20s 的短语停顿(连成歌唱)，只保留更长的真换气
    out = target.copy()
    voiced = f0 > 0
    longgap = np.zeros(nframes, bool)
    run = 0
    for i in range(nframes):
        if not voiced[i]:
            run += 1
            if run >= int(0.20 / 0.005):
                longgap[max(0, i - run + 1):i + 1] = True
        else:
            run = 0
    out[longgap] = 0.0
    out = moving_mean(out, 7)

    y = pyworld.synthesize(out, sp, ap, SR)

    # 4) 整句轻软起软收
    n = len(y)
    env = np.ones(n)
    ai, ri = int(0.03 * SR), int(0.06 * SR)
    if ai > 0:
        env[:ai] = np.linspace(0, 1, ai) ** 1.5
    if ri > 0:
        env[-ri:] *= np.linspace(1, 0, ri) ** 1.2
    y = y * env
    y = y / max(1e-9, np.abs(y).max())
    return y.astype(np.float64)

def crossfade_concat(parts, cf=0.08):
    cf_n = int(cf * SR)
    out = parts[0].copy()
    for p in parts[1:]:
        if len(out) < cf_n or len(p) < cf_n:
            out = np.concatenate([out, p]); continue
        tail = out[-cf_n:]; head = p[:cf_n]
        w = np.linspace(0, 1, cf_n)
        blended = tail * (1 - w) + head * w
        out = np.concatenate([out[:-cf_n], blended, p[cf_n:]])
    return out

def trim_to(x, n):
    if len(x) >= n:
        return x[:n]
    if len(x) == 0:
        return np.zeros(n)
    return np.concatenate([x, np.zeros(n - len(x))])

LYRICS = {
    'ks1': ["Hello, hello, how are you?", "I am fine, how are you too?",
            "Hello, hello, say hello.", "Come and sing with me, let's go!"],
    'ks2': ["Red and blue, green and yellow.", "Colours, colours, bright and mellow.",
            "I see red, I see blue.", "Pretty colours, I love you!"],
    'ks3': ["One, two, three, look at me.", "Four, five, six, count with me.",
            "Seven, eight, nine, ten.", "Let's count again, my friend!"],
    'ks4': ["The cat says meow, meow.", "The dog says woof, woof.",
            "The duck says quack, quack.", "Animals are my friends!"],
    'ks5': ["Apple and banana, yummy, yummy.", "Milk and egg, good for my tummy.",
            "Cake and ice cream, sweet, sweet, sweet.", "I love yummy food to eat!"],
    'ks6': ["Head and shoulders, knees and toes.", "Eyes and ears and mouth and nose.",
            "Clap your hands, stamp your feet.", "My body is so neat!"],
    'ks7': ["Rain, rain, go away.", "Come again another day.",
            "Sun, sun, shine so bright.", "Play with me all day and night!"],
    'ks8': ["Jump, jump, jump so high.", "Run, run, run and fly.",
            "Clap, clap, clap your hands.", "Move your body, be my friends!"],
    'ks9': ["Mum and Dad, I love you.", "Grandma and Grandpa, love you too.",
            "Brother, sister, all my family.", "We are happy, you and me!"],
    'ks10': ["The car goes beep, beep, beep.", "The bike goes ring, ring, ring.",
             "The bus goes vroom, vroom, vroom.", "Let's go to the zoo!"],
}

def main(test_song=None):
    import shutil
    os.makedirs(BAK_DIR, exist_ok=True)
    for sid in SONGS:
        for fn in [f'{sid}f.mp3'] + [f'{sid}s0{i}.mp3' for i in range(1, 5)]:
            src = os.path.join(KS_DIR, fn)
            if os.path.exists(src) and not os.path.exists(os.path.join(BAK_DIR, fn)):
                shutil.copy2(src, os.path.join(BAK_DIR, fn))

    songs = {test_song: SONGS[test_song]} if test_song else SONGS
    for sid, phrases in songs.items():
        notes_all = [parse_notes(p) for p in phrases]
        bed_src = os.path.join(BAK_DIR, f'{sid}f.mp3')
        bed = decode_mp3_to_mono_f32(bed_src) if os.path.exists(bed_src) else np.zeros(1)

        line_wavs = []
        for li, ph in enumerate(phrases):
            text = LYRICS[sid][li]
            speech = asyncio.run(tts_to_wav(text))
            vocal = sing_vocal(speech, notes_all[li])
            bed_seg = trim_to(bed, len(vocal))
            line_mix = vocal * 0.92 + bed_seg * 0.18
            out = os.path.join(KS_DIR, f'{sid}s0{li+1}.mp3')
            encode_mp3(out, line_mix)
            line_wavs.append(vocal)
            print(f'  {sid}s0{li+1}.mp3 {len(vocal)/SR:.1f}s')

        full_vocal = crossfade_concat(line_wavs)
        bed_full = trim_to(bed, len(full_vocal))
        full = full_vocal * 0.9 + bed_full * 0.2
        outf = os.path.join(KS_DIR, f'{sid}f.mp3')
        encode_mp3(outf, full)
        print(f'{sid}f.mp3  {os.path.getsize(outf)//1024}KB  {len(full)/SR:.1f}s')
    print('v3 完成')

if __name__ == '__main__':
    ts = sys.argv[1] if len(sys.argv) > 1 else None
    main(ts)
