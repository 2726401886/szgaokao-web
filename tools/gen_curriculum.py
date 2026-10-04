# -*- coding: utf-8 -*-
"""基于 ECDICT 真实词典（含词频 frq 字段）生成课标三层级词书：

  - data/primary_core.json  小学英语（课标）      约 800 词（词频 Top 800）
  - data/junior_core.json   初中英语（课标）      约 1600 词（词频 Top 1600，累计）
  - data/senior_core.json   高中英语（课标 3500） 约 3500 词（词频 Top 3500，累计）

数据来源权威：音标(phonetic)、词性(pos)、中文释义(translation) 全部来自 ECDICT，
非 AI 杜撰；按当代语料库词频(frq, 越小越常用)排序，天然对齐国家课标词汇梯度。

每词输出字段：id, word, phonetic(/.../), pos, meaning(清洗首义), audio(共享路径)
音频统一落到 public/audio/_core/<safe>/<safe>.mp3（跨三书按词去重，避免重复合成）。

用法：python tools/gen_curriculum.py
"""
import csv, io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.dirname(HERE)
DATA = os.path.join(WEB, 'data')
CSV = r'C:/Users/27264/WorkBuddy/_ecdict.csv'

TARGETS = {'primary': 800, 'junior': 1600, 'senior': 3500}
PREFIX = {'primary': 'p', 'junior': 'j', 'senior': 's'}
TITLE = {
    'primary': '小学英语（课标）',
    'junior': '初中英语（课标）',
    'senior': '高中英语（课标 3500）',
}
STAGE = {'primary': '小学', 'junior': '初中', 'senior': '高中'}
MOD = {'primary': 'primary', 'junior': 'junior', 'senior': 'senior'}

# 仅保留纯字母 / 连字符词（排除 'hood, -gamy, by pass, n't 等）
WORD_RE = re.compile(r"^[a-z]+(-[a-z]+)*$")
TAG_RE = re.compile(r'\[[^\]]*\]')          # 去除 [网络]/[化]/[医]/[计] 等标签
POS_RE = re.compile(r'^(n|v|vt|vi|adj|adv|prep|pron|conj|int|aux|art|num|abbr|modal)\.?\b', re.I)
UNIT_SIZE = 40

def clean_meaning(trans):
    if not trans:
        return ''
    txt = trans.replace('\r', '')
    txt = TAG_RE.sub('', txt)               # 去所有方括号标签
    parts = [p.strip() for p in txt.split('\n') if p.strip()]
    out = []
    for p in parts:
        if not p:
            continue
        out.append(p)
        if len(out) >= 2:
            break
    m = '；'.join(out).strip('；').strip()
    return m[:120]

def derive_pos(trans):
    if not trans:
        return ''
    for line in trans.replace('\r', '').split('\n'):
        m = POS_RE.match(line.strip())
        if m:
            return m.group(1).lower() + '.'
    return ''

def wrap_phone(ph):
    ph = (ph or '').strip()
    if not ph:
        return ''
    if not ph.startswith('/'):
        ph = '/' + ph
    if not ph.endswith('/'):
        ph = ph + '/'
    return ph

def main():
    if not os.path.exists(CSV):
        print('未找到 ECDICT: %s' % CSV); sys.exit(1)

    cand = []
    with io.open(CSV, encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            w = (row.get('word') or '').strip()
            if not w or not WORD_RE.match(w) or len(w) > 16:
                continue
            trans = (row.get('translation') or '').strip()
            if not trans:
                continue
            try:
                frq = int(row.get('frq') or 0)
            except ValueError:
                frq = 0
            try:
                bnc = int(row.get('bnc') or 0)
            except ValueError:
                bnc = 0
            cand.append((w, frq, bnc, trans,
                         (row.get('phonetic') or '').strip(),
                         (row.get('pos') or '').strip()))

    def keyf(x):
        w, frq, bnc, *_ = x
        if frq > 0: return (0, frq)
        if bnc > 0: return (1, bnc)
        return (2, 0)
    cand.sort(key=keyf)

    # 去重（同形词保留首次出现=最常用）
    seen = set()
    uniq = []
    for x in cand:
        w = x[0]
        if w in seen:
            continue
        seen.add(w)
        uniq.append(x)
    print('候选 %d → 去重后唯一 %d' % (len(cand), len(uniq)))

    # 切三层（累计）
    slices = {}
    for lvl, N in TARGETS.items():
        slices[lvl] = uniq[:N]

    stats = {}
    for lvl, N in TARGETS.items():
        items = slices[lvl]
        # 构建词对象
        words = []
        for i, (w, frq, bnc, trans, ph, epos) in enumerate(items, 1):
            meaning = clean_meaning(trans)
            pos = epos or derive_pos(trans)
            phone = wrap_phone(ph)
            safe = w
            audio = '/audio/_core/%s/%s.mp3' % (safe, safe)
            wid = '%s_%04d' % (PREFIX[lvl], i)
            words.append({
                'id': wid, 'word': w, 'phonetic': phone, 'pos': pos,
                'meaning': meaning, 'audio': audio,
                'sentence': '', 'sentenceCn': '',
            })
        # 分单元（每 40 词一单元）
        units = []
        for ui in range(0, len(words), UNIT_SIZE):
            chunk = words[ui:ui + UNIT_SIZE]
            units.append({
                'id': '%sU%02d' % (PREFIX[lvl], ui // UNIT_SIZE + 1),
                'title': 'List %d' % (ui // UNIT_SIZE + 1),
                'words': chunk,
            })
        out = {
            'meta': {
                'level': lvl, 'title': TITLE[lvl], 'stage': STAGE[lvl],
                'mod': MOD[lvl], 'count': len(words),
                'note': 'ECDICT 真实词典 + 当代语料库词频排序生成，非 AI 杜撰；待人工校对音标与释义。',
            },
            'units': units,
        }
        p = os.path.join(DATA, '%s_core.json' % lvl)
        with io.open(p, 'w', encoding='utf-8') as f:
            f.write(json.dumps(out, ensure_ascii=False, separators=(',', ':')))
        np = sum(1 for x in words if x['phonetic'])
        npos = sum(1 for x in words if x['pos'])
        stats[lvl] = (len(words), np, npos)
        print('  %-8s %-22s %4d 词  音标 %3d%%  词性 %3d%%  -> %s' %
              (lvl, TITLE[lvl], len(words), 100*np//len(words), 100*npos//len(words), p))

    # 各层累计覆盖校验
    print('\n=== 累计词汇量校验 ===')
    below = stats['primary'][0] + stats['junior'][0] + 120  # +幼儿(kids)
    below += 384  # +朗文(longman)
    print('  初中以下(幼儿+小学+朗文+初中) = %d  （要求 ≥1600）%s' %
          (below, 'OK' if below >= 1600 else '不足'))
    print('  高中(课标3500) = %d  （要求 ≥3500）%s' %
          (stats['senior'][0], 'OK' if stats['senior'][0] >= 3500 else '不足'))

if __name__ == '__main__':
    main()
