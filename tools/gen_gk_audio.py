# -*- coding: utf-8 -*-
"""
广东高考听说 Part B 音频生成（12 套 × 3 段 = 36 个）
  python tools/gen_gk_audio.py run   # 生成全部（跳过已存在）
依赖：edge-tts + imageio-ffmpeg
说明：对话=女+男双声；提问=女声原速；慢速=女声 -35%。
"""
import os, json, asyncio, subprocess, tempfile, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB = os.path.join(ROOT, 'public')
GK_DIR = os.path.join(PUB, 'audio', 'gk')
DATA = json.load(open(os.path.join(ROOT, 'data', 'gaokao_partb.json'), encoding='utf-8'))

VOICE_F = 'en-GB-SoniaNeural'
VOICE_M = 'en-GB-RyanNeural'
RATE_DIALOGUE = '-10%'
RATE_QUEST = '-5%'
RATE_SLOW = '-35%'
GAP = 0.35

def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()

def normalize(path):
    ff = ffmpeg()
    tmp = path + '.fix.mp3'
    subprocess.run([ff, '-y', '-i', path, '-ar', '44100', '-ac', '1', '-b:a', '128k', '-f', 'mp3', tmp],
                   check=True, capture_output=True)
    os.replace(tmp, path)

def merge(temps, out):
    ff = ffmpeg()
    args = [ff]
    for tp in temps:
        args += ['-i', tp]
    args += ['-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono:d=%s' % GAP]
    sil = len(temps)
    chains = ['[%d:a]aresample=44100[%da]' % (i, i) for i in range(len(temps))]
    seq = ''
    for i in range(len(temps)):
        seq += '[%da]' % i
        if i < len(temps) - 1:
            seq += '[%d:a]' % sil
    seq += 'concat=n=%d:v=0:a=1[out]' % (2 * len(temps) - 1)
    args += ['-filter_complex', ';'.join(chains) + ';' + seq, '-map', '[out]', '-ar', '44100', '-ac', '1', '-y', out]
    subprocess.run(args, check=True, capture_output=True)

async def synth(text, voice, rate, out):
    import edge_tts
    await edge_tts.Communicate(text, voice, rate=rate).save(out)

async def gen():
    os.makedirs(GK_DIR, exist_ok=True)
    total = len(DATA['sets']) * 3
    ok = 0
    for s in DATA['sets']:
        sid = s['id']
        # 1) 对话（女+男）
        d_out = os.path.join(GK_DIR, sid + '-dialogue.mp3')
        if not os.path.exists(d_out):
            tmp = tempfile.mkdtemp()
            try:
                temps = []
                for i, d in enumerate(s['dialogue']):
                    v = VOICE_F if d['s'] == 'W' else VOICE_M
                    tp = os.path.join(tmp, 't%d.mp3' % i)
                    await synth(d['t'], v, RATE_DIALOGUE, tp)
                    temps.append(tp)
                merge(temps, d_out)
                normalize(d_out)
            finally:
                shutil.rmtree(tmp, ignore_errors=True)
            print('[OK] %s-dialogue.mp3' % sid); ok += 1
        else:
            print('[skip] %s-dialogue.mp3' % sid)
        # 2) 提问原速（女声，5 问连读）
        q_out = os.path.join(GK_DIR, sid + '-questions.mp3')
        if not os.path.exists(q_out):
            text = ' '.join(a['q'] for a in s['a5'])
            await synth(text, VOICE_F, RATE_QUEST, q_out)
            normalize(q_out)
            print('[OK] %s-questions.mp3' % sid); ok += 1
        else:
            print('[skip] %s-questions.mp3' % sid)
        # 3) 提问慢速
        qs_out = os.path.join(GK_DIR, sid + '-questions-slow.mp3')
        if not os.path.exists(qs_out):
            text = ' '.join(a['q'] for a in s['a5'])
            await synth(text, VOICE_F, RATE_SLOW, qs_out)
            normalize(qs_out)
            print('[OK] %s-questions-slow.mp3' % sid); ok += 1
        else:
            print('[skip] %s-questions-slow.mp3' % sid)
    print('\n生成完成：%d/%d' % (ok, total))

if __name__ == '__main__':
    asyncio.run(gen())
