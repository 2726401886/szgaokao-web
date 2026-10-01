# -*- coding: utf-8 -*-
# 客观诊断儿歌音频的"断断续续"程度：静音间隙、音节停顿、音高连续性
import os, sys, subprocess as _sp, numpy as np, pyworld
FFMPEG = _sp.check_output(
    [r'C:\Users\27264\.workbuddy\binaries\python\envs\default\Scripts\python.exe',
     '-c', 'import imageio_ffmpeg,sys; sys.stdout.write(imageio_ffmpeg.get_ffmpeg_exe())']
).decode().strip()
SR = 44100

def decode(path):
    p = _sp.run([FFMPEG, '-y', '-loglevel', 'error', '-i', path,
                 '-ar', str(SR), '-ac', '1', '-f', 'f32le', 'pipe:1'],
                stdout=_sp.PIPE, stderr=_sp.PIPE, check=True)
    return np.frombuffer(p.stdout, dtype='<f4').astype(np.float64)

def rms_frames(x, win=441):  # 10ms
    n = len(x) // win
    if n == 0: return np.array([0.0])
    y = x[:n*win].reshape(n, win)
    return np.sqrt((y**2).mean(axis=1) + 1e-12)

def analyze(path, label):
    x = decode(path)
    dur = len(x)/SR
    rms = rms_frames(x)
    # 静音阈值：相对峰值
    peak = rms.max()
    th = peak * 0.04
    silent = rms < th
    # 找连续静音段
    gaps = []
    run = 0
    for i, s in enumerate(silent):
        if s:
            run += 1
        else:
            if run > 0:
                gaps.append(run * 0.010)
                run = 0
    if run > 0: gaps.append(run * 0.010)
    gaps = [g for g in gaps if g >= 0.05]   # 只统计 >50ms 的明显间隙
    silent_total = silent.sum() * 0.010
    # 音高连续性
    f0, tpos = pyworld.harvest(x, SR, f0_floor=80.0, f0_ceil=520.0)
    f0 = pyworld.stonemask(x, f0, tpos, SR)
    voiced = f0 > 0
    diff = np.abs(np.diff(f0[voiced]))
    max_jump = diff.max() if len(diff) else 0
    med_jump = np.median(diff) if len(diff) else 0
    print(f'== {label} ({os.path.basename(path)}) ==')
    print(f'  时长 {dur:.2f}s | 峰值RMS {peak:.4f}')
    print(f'  静音占比 {100*silent_total/dur:.1f}% | >50ms 间隙数 {len(gaps)} | 间隙时长(s): {[round(g,2) for g in gaps]}')
    print(f'  浊音帧占比 {100*voiced.mean():.1f}% | F0最大跳变 {max_jump:.1f}Hz | 中位跳变 {med_jump:.2f}Hz')
    return dur, gaps, silent_total

KS = r'C:\Users\27264\WorkBuddy\2026-09-26-21-53-51\szgaokao-web\public\audio\ks'
print('### 逐句 (line) ###')
for i in (1,2):
    analyze(os.path.join(KS, f'ks1s0{i}.mp3'), f'ks1 line{i}')
print('\n### 整首 (full) ###')
analyze(os.path.join(KS, 'ks1f.mp3'), 'ks1 full')
