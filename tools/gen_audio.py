# 英文听力 MP3 生成器（双声部对话 + 英音 + 慢速版）
# 用法：
#   python tools/gen_audio.py check   # 只提取并打印待生成文本，不调用 TTS
#   python tools/gen_audio.py run      # 生成全部 MP3 并回填 data/quiz.json
#
# 依赖：edge-tts  (pip install edge-tts) + imageio-ffmpeg（内置 ffmpeg，用于拼接双声部）
#
# 说明：
#   - Part A 单词 / B 短句 / D 篇章：单声（默认英音女声 Sonia），语速放慢便于中考听力
#   - Part C 对话：女声(W) + 男声(M) 双声部，轮次间留短静音，更接近真实对话
#   - 想换回美音/不同语音：改下方 VOICE_* ；想调语速：改 RATE（如 '-10%' 慢一点 / '+0%' 原速）
import os, re, sys, json, asyncio, subprocess, tempfile, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
PUB = os.path.join(ROOT, 'public')
AUDIO_DIR = os.path.join(PUB, 'audio')
MD_DIR = os.path.join(ROOT, '..', 'english-edu-company', '03交付素材库', '听说试卷包')

# ===== 语音配置（改这里即可切换口音/语速）=====
VOICE_FEMALE = 'en-GB-SoniaNeural'   # 女声（英音）
VOICE_MALE   = 'en-GB-RyanNeural'    # 男声（英音）
# 美音备选：VOICE_FEMALE='en-US-AriaNeural'  VOICE_MALE='en-US-GuyNeural'
SINGLE_VOICE = VOICE_FEMALE          # A/B/D 单声统一用女声
RATE = '-15%'                        # 放慢 15%，更适合中考听力（可改 -10% / +0%）
GAP_SEC = 0.35                       # 对话轮次间的静音间隙（秒）

MD_NAMES = {
    'v01': '中考听说专项-试卷01-音频脚本与生词表.md',
    'v02': '中考听说专项-试卷02-音频脚本与生词表.md',
    'v03': '中考听说专项-试卷03-音频脚本与生词表.md',
    'v04': '中考听说专项-试卷04-音频脚本与生词表.md',
    'v05': '中考听说专项-试卷05-音频脚本与生词表.md',
    'v06': '中考听说专项-试卷06-音频脚本与生词表.md',
    'v07': '中考听说专项-试卷07-音频脚本与生词表.md',
    'v08': '中考听说专项-试卷08-音频脚本与生词表.md',
    'v09': '中考听说专项-试卷09-音频脚本与生词表.md',
    'v10': '中考听说专项-试卷10-音频脚本与生词表.md',
    'v11': '中考听说专项-试卷11-音频脚本与生词表.md',
    'v12': '中考听说专项-试卷12-音频脚本与生词表.md',
    'v13': '中考听说专项-试卷13-音频脚本与生词表.md',
    'v14': '中考听说专项-试卷14-音频脚本与生词表.md',
    'v15': '中考听说专项-试卷15-音频脚本与生词表.md',
    'v16': '中考听说专项-试卷16-音频脚本与生词表.md',
    'v17': '中考听说专项-试卷17-音频脚本与生词表.md',
    'v18': '中考听说专项-试卷18-音频脚本与生词表.md',
    'v19': '中考听说专项-试卷19-音频脚本与生词表.md',
    'v20': '中考听说专项-试卷20-音频脚本与生词表.md',
    'v21': '中考听说专项-试卷21-音频脚本与生词表.md',
    'v22': '中考听说专项-试卷22-音频脚本与生词表.md',
}

def get_ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()

def extract_part_d(md_path):
    try:
        txt = open(md_path, encoding='utf-8').read()
    except Exception:
        return ''
    m = re.search(r'Part\s*D[^\n]*\n?.*?"([^"]+)"', txt, re.S)
    return m.group(1).strip() if m else ''

def dialogue_turns(audio):
    """把 ['W: ...','M: ...'] 拆成 [(speaker,text)]，W->女(F) M->男(M)。"""
    turns = []
    for ln in audio:
        s = str(ln).strip()
        if re.match(r'^W\s*:', s, re.I):
            sp, txt = 'F', re.sub(r'^W\s*:\s*', '', s, flags=re.I).strip()
        elif re.match(r'^M\s*:', s, re.I):
            sp, txt = 'M', re.sub(r'^M\s*:\s*', '', s, flags=re.I).strip()
        else:
            sp, txt = 'F', s
        turns.append((sp, txt))
    return turns

def build_plan(quiz):
    seen = {}
    passages = {}
    def skip_existing(rel):
        # 增量模式：音频文件已存在则跳过，不重复生成
        return os.path.exists(os.path.join(PUB, rel))
    for vol in quiz['volumes']:
        vid = vol['id']
        md = os.path.join(MD_DIR, MD_NAMES.get(vid, ''))
        passage = extract_part_d(md) if MD_NAMES.get(vid) else ''
        passages[vid] = passage
        for p in vol['parts']:
            if p.get('type') == 'speaking':
                continue
            if p.get('part') == 'D':
                if not passage:
                    # 无 MD 脚本（如 v17-v22）时，回退到卷内已内联的篇章文本
                    passage = (p.get('audio') or '').strip()
                if passage:
                    rel = 'audio/' + vid + '-D.mp3'
                    if rel not in seen and not skip_existing(rel):
                        seen[rel] = {'rel': rel, 'kind': 'single', 'text': passage, 'refs': []}
                continue
            for q in p.get('questions', []):
                # 原文在 audioText（上一轮已把 audio 改成路径）；兜底用 audio 中非路径文本
                a = q.get('audioText')
                if not a and not str(q.get('audio') or '').startswith('/audio/'):
                    a = q.get('audio')
                if not a:
                    continue
                rel = 'audio/' + q['id'] + '.mp3'
                if rel not in seen and not skip_existing(rel):
                    if isinstance(a, list):
                        seen[rel] = {'rel': rel, 'kind': 'dialogue', 'turns': dialogue_turns(a), 'refs': []}
                    else:
                        seen[rel] = {'rel': rel, 'kind': 'single', 'text': str(a).strip(), 'refs': []}
                if rel in seen:
                    seen[rel]['refs'].append((vid, q['id']))
    return list(seen.values()), passages

async def synth_turn(text, voice, rate, out_path):
    import edge_tts
    await edge_tts.Communicate(text, voice, rate=rate).save(out_path)

def merge_dialogue(temps, out_path, ffmpeg):
    args = [ffmpeg]
    for tp in temps:
        args += ['-i', tp]
    args += ['-f', 'lavfi', '-i', f'anullsrc=r=44100:cl=mono:d={GAP_SEC}']
    sil = len(temps)
    chains = [f'[{i}:a]aresample=44100[{i}a]' for i in range(len(temps))]
    seq = ''
    for i in range(len(temps)):
        seq += f'[{i}a]'
        if i < len(temps) - 1:
            seq += f'[{sil}:a]'
    seq += f'concat=n={2 * len(temps) - 1}:v=0:a=1[out]'
    filt = ';'.join(chains) + ';' + seq
    args += ['-filter_complex', filt, '-map', '[out]', '-ar', '44100', '-ac', '1', '-y', out_path]
    subprocess.run(args, check=True, capture_output=True)

def normalize_audio(path):
    """转码为 44.1kHz MPEG-1 L3，保证所有浏览器可在线播放（edge-tts 默认 24kHz MPEG-2 部分内核不支持）。"""
    ff = get_ffmpeg()
    tmp = path + '.fix.mp3'
    subprocess.run([ff, '-y', '-i', path, '-ar', '44100', '-ac', '1', '-b:a', '128k',
                    '-f', 'mp3', tmp], check=True, capture_output=True)
    os.replace(tmp, path)

async def run_gen(plan):
    os.makedirs(AUDIO_DIR, exist_ok=True)
    ffmpeg = get_ffmpeg()
    total = len(plan)
    ok = 0
    for i, item in enumerate(plan, 1):
        out = os.path.join(PUB, item['rel'])
        try:
            if item['kind'] == 'dialogue':
                tmp = tempfile.mkdtemp()
                try:
                    temps = []
                    for j, (sp, txt) in enumerate(item['turns']):
                        v = VOICE_FEMALE if sp == 'F' else VOICE_MALE
                        tp = os.path.join(tmp, f't{j}.mp3')
                        await synth_turn(txt, v, RATE, tp)
                        temps.append(tp)
                    merge_dialogue(temps, out, ffmpeg)
                    normalize_audio(out)
                    tag = '双声对话'
                finally:
                    shutil.rmtree(tmp, ignore_errors=True)
            else:
                await synth_turn(item['text'], SINGLE_VOICE, RATE, out)
                normalize_audio(out)
                tag = '单声'
            ok += 1
            prev = (item['text'][:40] if item['kind'] == 'single' else ' | '.join(t for _, t in item['turns'])[:40])
            print(f'[{i}/{total}] OK  {item["rel"]}  [{tag}] ({len(item["refs"])}题共用)')
        except Exception as e:
            print(f'[{i}/{total}] FAIL {item["rel"]}: {e}')
    print(f'\n生成完成：成功 {ok}/{total}')
    return ok

def apply_to_quiz(quiz, plan, passages):
    by_rel = {it['rel']: it for it in plan}
    for vol in quiz['volumes']:
        vid = vol['id']
        for p in vol['parts']:
            if p.get('type') == 'speaking':
                continue
            for q in p.get('questions', []):
                a = q.get('audio')
                if p.get('part') == 'D':
                    # 已回填（audio 是路径）则跳过，避免覆盖 audioText
                    if str(a or '').startswith('/audio/'):
                        continue
                    rel = 'audio/' + vid + '-D.mp3'
                    item = by_rel.get(rel)
                    if item:
                        q['audioText'] = passages.get(vid, '')
                        q['audio'] = '/' + rel
                    continue
                if not a or str(a).startswith('/audio/'):
                    continue
                rel = 'audio/' + q['id'] + '.mp3'
                item = by_rel.get(rel)
                q['audioText'] = a
                q['audio'] = '/' + rel
    return quiz

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'check'
    quiz = json.load(open(os.path.join(DATA, 'quiz.json'), encoding='utf-8'))
    plan, passages = build_plan(quiz)
    if mode == 'check':
        print(f'待生成音频文件数: {len(plan)}  | 口音: {VOICE_FEMALE.split("-")[0]}  语速: {RATE}')
        print('=' * 60)
        for it in plan:
            if it['kind'] == 'dialogue':
                prev = ' | '.join(f'{"女" if sp=="F" else "男"}:{t}' for sp, t in it['turns'])[:80]
            else:
                prev = it['text'][:80]
            print(f'{it["rel"]}  [{it["kind"]}] {len(it["refs"])}题 | {prev}')
        return
    ok = asyncio.run(run_gen(plan))
    if ok == len(plan):
        quiz = apply_to_quiz(quiz, plan, passages)
        json.dump(quiz, open(os.path.join(DATA, 'quiz.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        print('quiz.json 已回填 audio 路径与 audioText。')
    else:
        print('存在失败项，未回填 quiz.json（请检查网络后重试 run）。')

if __name__ == '__main__':
    main()
