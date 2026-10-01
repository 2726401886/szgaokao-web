# -*- coding: utf-8 -*-
# 幼儿儿歌"旋律演唱版"生成器
# 背景：原先 ks?f.mp3（整首）是 edge-tts 直接朗读歌词，听起来是"念"不是"唱"。
# 方案：给每首儿歌作曲（四句经典童谣式旋律），合成【哼唱领奏 + 八音盒伴奏】的演唱版，
#       孩子可以跟着旋律哼唱/填词唱；逐句点读 ks?s0N.mp3 仍是 TTS 英音（学发音用），不动。
# 运行：python tools/gen_kids_songs_melody.py
# 依赖：numpy + imageio-ffmpeg（venv: binaries/python/envs/default）
import os, subprocess, wave, array, math

import numpy as np
from imageio_ffmpeg import get_ffmpeg_exe

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'public', 'audio', 'ks')
BAK_DIR = os.path.join(ROOT, 'tools', '_backup_ks_tts')
SR = 44100
BPM = 100                      # 每分钟拍数
BEAT = 60.0 / BPM              # 一拍秒数（0.6s）
LINE_BEATS = 8                 # 每句歌词占 8 拍（两小节）
GAP_BEATS = 0.75               # 句间呼吸
INTRO_BEATS = 8                # 前奏两小节
OUTRO_BEATS = 6                # 尾奏收束

# 音名 -> 频率（A4=440，十二平均律）
NOTE_SEMI = {'C': -9, 'D': -7, 'E': -5, 'F': -4, 'G': -2, 'A': 0, 'B': 2}
def freq(name):
    n, octv = name[:-1], int(name[-1])
    semi = NOTE_SEMI[n] + (octv - 4) * 12
    return 440.0 * (2 ** (semi / 12.0))

def parse_phrase(s):
    """'C4:1 C4:1 G4:2' -> [(freq, beats)]，R 为休止。校验每句拍数。"""
    out, total = [], 0.0
    for tok in s.split():
        n, d = tok.split(':')
        total += float(d)
        out.append((0.0 if n == 'R' else freq(n), float(d)))
    assert abs(total - LINE_BEATS) < 1e-6, f'拍数错误({total}): {s}'
    return out

# ===== 10 首儿歌：每首 4 句旋律 + 每句配和弦（I/IV/V 进行为主） =====
CHORDS = {
    'C':  ['C3', 'E4', 'G4'], 'F': ['F3', 'A4', 'C5'], 'G': ['G3', 'B4', 'D5'],
    'Am': ['A3', 'C4', 'E4'], 'G7': ['G3', 'F4', 'B4'],
}
SONGS = {
    'ks1': dict(bpm=96, lines=[          # Hello Song：小星星式，最上口
        'C4:1 C4:1 G4:1 G4:1 A4:1 A4:1 G4:2',
        'F4:1 F4:1 E4:1 E4:1 D4:1 D4:1 C4:2',
        'G4:1 G4:1 F4:1 F4:1 E4:1 E4:1 D4:2',
        'F4:1 F4:1 E4:1 E4:1 D4:1 D4:1 C4:2'],
        chords=['C', 'F', 'C', 'F'], final='C'),
    'ks2': dict(bpm=100, lines=[          # Colour Song
        'E4:1 E4:1 D4:1 C4:1 D4:1 E4:1 G4:2',
        'A4:1 A4:1 G4:1 E4:1 G4:1 E4:1 C4:2',
        'E4:1 G4:1 A4:1 A4:1 G4:1 E4:1 D4:2',
        'C4:1 D4:1 E4:1 D4:1 C4:1 C4:1 C4:2'],
        chords=['C', 'Am', 'F', 'C'], final='C'),
    'ks3': dict(bpm=104, lines=[          # Counting Song
        'C4:1 C4:1 D4:1 E4:1 G4:1 G4:1 E4:2',
        'F4:1 F4:1 E4:1 D4:1 E4:1 D4:1 C4:2',
        'E4:1 E4:1 D4:1 C4:1 D4:1 E4:1 D4:2',
        'G4:1 E4:1 D4:1 D4:1 C4:1 C4:1 C4:2'],
        chords=['C', 'F', 'G', 'C'], final='C'),
    'ks4': dict(bpm=102, lines=[          # Animal Sounds
        'G4:1 G4:1 A4:1 G4:1 E4:1 E4:1 D4:2',
        'G4:1 A4:1 B4:1 A4:1 G4:1 E4:1 D4:2',
        'E4:1 E4:1 F4:1 E4:1 D4:1 C4:1 G4:2',
        'E4:1 D4:1 C4:1 D4:1 E4:1 D4:1 C4:2'],
        chords=['C', 'G', 'F', 'C'], final='C'),
    'ks5': dict(bpm=98, lines=[           # Yummy Food
        'C4:1 E4:1 G4:1 E4:1 A4:1 G4:1 E4:2',
        'F4:1 A4:1 G4:1 F4:1 E4:1 D4:1 C4:2',
        'D4:1 F4:1 A4:1 G4:1 F4:1 E4:1 D4:2',
        'E4:1 G4:1 F4:1 E4:1 D4:1 C4:1 C4:2'],
        chords=['C', 'F', 'G', 'C'], final='C'),
    'ks6': dict(bpm=104, lines=[          # My Body（头肩膝脚趾节奏）
        'G4:0.5 G4:0.5 A4:1 A4:1 G4:1 E4:1 D4:1 G4:2',
        'E4:0.5 E4:0.5 F4:1 G4:1 A4:1 G4:1 F4:1 E4:2',
        'C4:1 C4:1 D4:1 E4:1 E4:1 D4:1 C4:2',
        'D4:1 E4:1 F4:1 F4:1 E4:1 D4:1 C4:2'],
        chords=['C', 'F', 'C', 'G'], final='C'),
    'ks7': dict(bpm=92, lines=[           # Rain and Sun（舒缓）
        'A4:1 A4:1 G4:1 E4:1 G4:1 G4:1 E4:2',
        'F4:1 F4:1 E4:1 D4:1 C4:1 D4:1 E4:2',
        'E4:1 G4:1 A4:1 G4:1 E4:1 D4:1 C4:2',
        'D4:1 E4:1 D4:1 C4:1 D4:1 E4:1 C4:2'],
        chords=['Am', 'F', 'C', 'C'], final='C'),
    'ks8': dict(bpm=108, lines=[          # Let's Move（活泼）
        'C4:0.5 C4:0.5 D4:1 E4:1 G4:1 E4:1 D4:1 C4:2',
        'D4:0.5 D4:0.5 E4:1 F4:1 A4:1 F4:1 E4:1 D4:2',
        'E4:0.5 E4:0.5 F4:1 G4:1 A4:1 G4:1 F4:1 G4:2',
        'G4:1 A4:1 G4:1 E4:1 D4:1 C4:1 C4:2'],
        chords=['C', 'F', 'C', 'G'], final='C'),
    'ks9': dict(bpm=96, lines=[           # My Family（温馨）
        'E4:1 G4:1 C5:1 C5:1 B4:1 A4:1 G4:2',
        'A4:1 A4:1 G4:1 E4:1 F4:1 E4:1 D4:2',
        'E4:1 G4:1 A4:1 G4:1 E4:1 D4:1 C4:2',
        'D4:1 E4:1 G4:1 E4:1 D4:1 C4:1 C4:2'],
        chords=['C', 'F', 'Am', 'C'], final='C'),
    'ks10': dict(bpm=106, lines=[         # Let's Go Out
        'G4:1 E4:1 E4:1 F4:1 F4:1 E4:1 D4:2',
        'G4:1 G4:1 A4:1 B4:1 B4:1 A4:1 G4:2',
        'A4:1 G4:1 F4:1 E4:1 F4:1 G4:1 D4:2',
        'E4:1 D4:1 C4:1 D4:1 E4:1 D4:1 C4:2'],
        chords=['C', 'G', 'G7', 'C'], final='C'),
}

def hum_note(f, dur):
    """哼唱领奏：基频+泛音、软起音、末端微颤，像小朋友闭口哼鸣。"""
    n = int(SR * dur)
    t = np.arange(n) / SR
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5.2 * t) * np.minimum(t / 0.25, 1.0)
    phase = 2 * np.pi * f * np.cumsum(vib) / SR
    s = np.zeros(n)
    for k, a in ((1, 1.0), (2, 0.42), (3, 0.22), (4, 0.10), (5, 0.05)):
        s += a * np.sin(k * phase)
    atk = int(0.045 * SR); rel = int(0.09 * SR)
    env = np.ones(n)
    env[:atk] = np.linspace(0, 1, atk) ** 1.5
    env[-rel:] *= np.linspace(1, 0, rel) ** 1.2
    return s * env

def box_note(f, dur):
    """八音盒音色：衰减正弦 + 少量非谐泛音。"""
    n = int(SR * min(dur + 0.9, 2.2))
    t = np.arange(n) / SR
    s = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 3.02 * f * t)
         + 0.18 * np.sin(2 * np.pi * 5.41 * f * t))
    return s * np.exp(-t / 0.38)

def bass_note(f, dur):
    n = int(SR * dur)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * f * t) * np.exp(-t / 0.5) * 0.9

def place(buf, snd, start):
    i0 = int(start * SR); i1 = min(i0 + len(snd), len(buf))
    if i1 > i0: buf[i0:i1] += snd[:i1 - i0]

def render(song_id, cfg):
    beat = 60.0 / cfg['bpm']
    total = (INTRO_BEATS + 4 * (LINE_BEATS + GAP_BEATS) + OUTRO_BEATS) * beat + 1.5
    buf = np.zeros(int(SR * total))
    phrases = [parse_phrase(x) for x in cfg['lines']]
    chordseq = [CHORDS[c] for c in cfg['chords']]

    t = 0.0
    # 前奏：主和弦分解八音盒
    for e in range(INTRO_BEATS * 2):
        f = freq(['C4', 'G4', 'E4', 'G4'][e % 4])
        place(buf, box_note(f, 0.9) * 0.35, t + e * beat * 0.5)
    place(buf, bass_note(freq('C2'), beat * 2) * 0.5, t)
    t += INTRO_BEATS * beat

    # 四句：哼唱领奏 + 旋律八音盒点缀 + 和声伴奏
    for pi, ph in enumerate(phrases):
        chord = chordseq[pi]
        t_line = t
        for f, b in ph:                      # 领奏
            if f: place(buf, hum_note(f, b * beat) * 0.52, t_line)
            place(buf, box_note(f or freq('C5'), min(b * beat, 0.9)) * 0.12, t_line)
            t_line += b * beat
        for bar in range(2):                 # 每句两小节伴奏
            tb = t + bar * 4 * beat
            root, third, fifth = (freq(x) for x in chord)
            place(buf, bass_note(root, beat * 1.6) * 0.42, tb)
            place(buf, bass_note(fifth, beat * 1.6) * 0.30, tb + 2 * beat)
            arp = [root, fifth, third * 2, fifth, root * 2, fifth, third * 2, fifth]
            for e, f in enumerate(arp):
                place(buf, box_note(f, 0.8) * 0.20, tb + e * beat * 0.5)
        t += (LINE_BEATS + GAP_BEATS) * beat

    # 尾奏：主和弦收束
    place(buf, bass_note(freq('C2'), OUTRO_BEATS * beat) * 0.5, t)
    for i, x in enumerate(['C4', 'E4', 'G4', 'C5']):
        place(buf, box_note(freq(x), 1.8) * (0.4 - i * 0.05), t + i * 0.09)
    f_end = freq('C4')
    place(buf, hum_note(f_end, OUTRO_BEATS * beat * 0.8) * 0.45, t)

    # 轻混响（反馈延迟）+ 归一化
    d = int(0.22 * SR)
    echo = np.zeros_like(buf); echo[d:] = buf[:-d] * 0.24
    mix = buf + echo
    mix = mix / max(1e-9, np.abs(mix).max()) * 0.82
    return (mix * 32767).astype(np.int16)

def main():
    os.makedirs(BAK_DIR, exist_ok=True)
    ffmpeg = get_ffmpeg_exe()
    for sid, cfg in SONGS.items():
        pcm = render(sid, cfg)
        wav = os.path.join(BAK_DIR, f'{sid}f_tmp.wav')
        with wave.open(wav, 'wb') as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
            w.writeframes(pcm.tobytes())
        out = os.path.join(OUT_DIR, f'{sid}f.mp3')
        old = out + '.tts.bak'
        if os.path.exists(out) and not os.path.exists(old):
            os.replace(out, old)             # 备份原 TTS 朗读版
        subprocess.run([ffmpeg, '-y', '-loglevel', 'error', '-i', wav,
                        '-codec:a', 'libmp3lame', '-b:a', '48k', '-ac', '1', out], check=True)
        os.remove(wav)
        dur = len(pcm) / SR
        print(f'{sid}f.mp3  {os.path.getsize(out)//1024}KB  {dur:.1f}s  bpm={cfg["bpm"]}')
    print('完成：10 首旋律演唱版已生成，原 TTS 版备份在 tools/_backup_ks_tts/')

if __name__ == '__main__':
    main()
