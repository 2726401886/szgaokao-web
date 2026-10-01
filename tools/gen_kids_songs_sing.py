# -*- coding: utf-8 -*-
# 幼儿儿歌"真唱版"生成器（免费方案）
# 背景：之前 ks?f.mp3 是八音盒旋律（无人声），ks?s0N 是 edge-tts 朗读（念不是唱）。
# 用户要求：儿歌要"唱出来"，且要免费的。
# 方案：edge-tts 提供清晰英文人声歌词（免费）→ WORLD 声码器把人声调到每首儿歌的旋律音高上
#       （保留频谱包络=保留咬字清晰度）→ 叠加八音盒旋律作轻柔伴奏。
#       结果：清晰的人声"唱"出歌词 + 真实旋律，100% 免费、无版权风险、本地运行。
# 依赖：edge_tts, numpy, pyworld, soundfile（系统 Python 3.10）；ffmpeg 由 imageio_ffmpeg 提供（托管 python）
import os, sys, io, subprocess, tempfile, math
import numpy as np
import soundfile as sf
import pyworld
import edge_tts

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KS_DIR = os.path.join(ROOT, 'public', 'audio', 'ks')
BAK_DIR = os.path.join(ROOT, 'tools', '_backup_ks_sing')
SR = 44100
VOICE = 'en-US-AriaNeural'          # 清晰、温暖的女声，适合儿童
TTS_RATE = '-8%'                    # 略放慢，便于跟唱

# ffmpeg 取自托管 python 的 imageio_ffmpeg（系统 python 未装）
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

# 与 gen_kids_songs_melody.py 完全一致的旋律（用于把人声映射到音高）
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

def line_notes(phrase):
    """把一句旋律串解析成音高列表（去掉休止），供逐音节映射。"""
    out = []
    for tok in phrase.split():
        n, _ = tok.split(':')
        if n != 'R':
            out.append(freq(n))
    return out

def decode_mp3_to_mono_f32(path):
    p = _sp.run([_FFMPEG, '-y', '-loglevel', 'error', '-i', path,
                 '-ar', str(SR), '-ac', '1', '-f', 'f32le', 'pipe:1'],
                stdout=_sp.PIPE, stderr=_sp.PIPE, check=True)
    return np.frombuffer(p.stdout, dtype='<f4').astype(np.float64)

def encode_mp3(path, data_f32):
    # data_f32: float64 mono
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

def sing_vocal(speech, note_freqs):
    """把朗读人声平滑地唱成旋律（保留咬字，连续不卡顿）。"""
    data = np.ascontiguousarray(speech.astype(np.float64))
    f0, tpos = pyworld.harvest(data, SR, f0_floor=80.0, f0_ceil=520.0)
    f0 = pyworld.stonemask(data, f0, tpos, SR)
    sp = pyworld.cheaptrick(data, f0, tpos, SR)
    ap = pyworld.d4c(data, f0, tpos, SR)
    nframes = len(f0)
    t = np.arange(nframes) * 0.005

    # 1) 整句连续目标音高：按时间在旋律音之间平滑过渡（带滑音），不再逐音节硬切
    if note_freqs:
        N = len(note_freqs)
        idx = np.minimum(N - 1, (t / t[-1] * N).astype(int)) if nframes > 1 else np.zeros(nframes, int)
        target = np.array([note_freqs[i] for i in idx], dtype=float)
        for wms in (0.05, 0.09):                      # 多级滑动平均 => 音与音之间柔和滑音
            w = max(3, int(wms / 0.005))
            target = np.convolve(target, np.ones(w) / w, mode='same')
        target = target * (1 + 0.004 * np.sin(2 * np.pi * 5.0 * t))   # 轻微颤音
    else:
        target = f0.copy()

    # 2) 连续发声：以目标音高桥接短促的清音/停顿，只在 >0.18s 的长停顿处留白
    out = target.copy()
    voiced = f0 > 0
    longgap = np.zeros(nframes, bool)
    run = 0
    for i in range(nframes):
        if not voiced[i]:
            run += 1
            if run >= int(0.18 / 0.005):
                longgap[max(0, i - run + 1):i + 1] = True
        else:
            run = 0
    out[longgap] = 0.0
    out = np.convolve(out, np.ones(5) / 5, mode='same')

    y = pyworld.synthesize(out, sp, ap, SR)

    # 3) 整句轻软起软收，避免爆音/咔哒（按采样点长度做包络）
    n = len(y)
    env = np.ones(n)
    ai, ri = int(0.04 * SR), int(0.08 * SR)
    if ai > 0:
        env[:ai] = np.linspace(0, 1, ai) ** 1.5
    if ri > 0:
        env[-ri:] *= np.linspace(1, 0, ri) ** 1.2
    y = y * env
    y = y / max(1e-9, np.abs(y).max())
    return y.astype(np.float64)

def main():
    import asyncio
    os.makedirs(BAK_DIR, exist_ok=True)
    # 备份当前线上版（八音盒/朗读）一次（复制，不移动，保证源文件在生成成功前不被移除）
    import shutil
    for sid in SONGS:
        for fn in [f'{sid}f.mp3'] + [f'{sid}s0{i}.mp3' for i in range(1, 5)]:
            src = os.path.join(KS_DIR, fn)
            if os.path.exists(src) and not os.path.exists(os.path.join(BAK_DIR, fn)):
                shutil.copy2(src, os.path.join(BAK_DIR, fn))

    for sid, phrases in SONGS.items():
        notes_all = [line_notes(p) for p in phrases]
        # 伴奏床：原有八音盒整首（已被备份移走，这里从备份读）
        bed_src = os.path.join(BAK_DIR, f'{sid}f.mp3')
        bed = decode_mp3_to_mono_f32(bed_src) if os.path.exists(bed_src) else np.zeros(1)

        line_wavs = []
        for li, ph in enumerate(phrases):
            text = LYRICS[sid][li]
            speech = asyncio.run(tts_to_wav(text))
            vocal = sing_vocal(speech, notes_all[li])
            # 逐句点读文件：人声 + 该句对应的轻柔伴奏片段
            bed_seg = trim_to(bed, len(vocal))
            line_mix = vocal * 0.92 + bed_seg * 0.18
            out = os.path.join(KS_DIR, f'{sid}s0{li+1}.mp3')
            encode_mp3(out, line_mix)
            line_wavs.append(vocal)
            print(f'  {sid}s0{li+1}.mp3 {len(vocal)/SR:.1f}s')

        # 整首：四句人声顺次拼接 + 整段轻柔伴奏
        full_vocal = np.concatenate(line_wavs)
        bed_full = trim_to(bed, len(full_vocal))
        full = full_vocal * 0.9 + bed_full * 0.2
        outf = os.path.join(KS_DIR, f'{sid}f.mp3')
        encode_mp3(outf, full)
        print(f'{sid}f.mp3  {os.path.getsize(outf)//1024}KB  {len(full)/SR:.1f}s')

    print('完成：10 首"真唱版"已生成（清晰人声+旋律，免费方案）')

def trim_to(x, n):
    if len(x) >= n:
        return x[:n]
    if len(x) == 0:
        return np.zeros(n)
    return np.concatenate([x, np.zeros(n - len(x))])

# 歌词（与 kids_songs.json 一致）
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

if __name__ == '__main__':
    main()
