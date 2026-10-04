# -*- coding: utf-8 -*-
"""把现有 7 套英语词书归一化为 vocab.json（专业单词记忆模块统一 schema）。

统一词条 schema：
{ id, word, phonetic, pos, meaning, audio, level, stage, unit, unitId,
  sentence, sentenceCn, syllables, phonics }

- level  词书 id（kids / primary / longman / junior / senior / ket / pet）
- stage  学段标签（幼儿/小学/初中/高中/出国考）
- syllables 音节切分（小学低年级用；无则空）
- phonics  自然拼读提示（小学用）

用法：python tools/build_vocab.py
输出：data/vocab.json
"""
import io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), 'data')

STAGE = {
    'kids':    ('幼儿启蒙', 'kids'),
    'primary': ('小学英语', 'primary'),
    'longman': ('小学英语', 'longman'),
    'junior':  ('初中英语', 'junior'),
    'senior':  ('高中英语', 'senior'),
    'ket':     ('出国考', 'ket'),
    'pet':     ('出国考', 'pet'),
    # 考试类词书（由 tools/build_exam_books.py 生成，schema 略有差异）
    'ky':      ('考研', 'ky'),
    'cet4':    ('四六级', 'cet4'),
    'cet6':    ('四六级', 'cet6'),
    'tem8':    ('四六级', 'tem8'),
    'ielts':   ('出国考', 'ielts'),
    'toefl':   ('出国考', 'toefl'),
    'oral':    ('出国考', 'oral'),
}

# 小学阶段需要音节切分与自然拼读提示
SPLIT_TARGETS = {'kids', 'primary'}

# 常见词缀/词根，用于生成自然拼读提示（简版）
PHONICS_HINT = [
    (r'^re', '前缀 re- 表"再、回"'),
    (r'^(un|in|dis|non)', '否定前缀'),
    (r'^(pre|post)', '前缀 表"前后"'),
    (r'^(sub|inter|trans|super|over|under)', '前缀 表位置/程度'),
    (r'^(able|ible|ful|less|ous|ive|al|ic|ish)', '后缀 表性质'),
    (r'^(ly)', '后缀 -ly 表副词'),
    (r'^(tion|sion|ment|ness|ity|ance|ence|ship|dom)', '后缀 表名词'),
    (r'^(ize|ise|ify)', '后缀 表动词化'),
]

def load(name):
    p = os.path.join(DATA, name)
    if not os.path.exists(p):
        return None
    with io.open(p, encoding='utf-8') as f:
        return json.load(f)

def syllabify(word):
    """极简音节切分：按元音簇切分，够用于小学跟读提示。"""
    w = re.sub(r'[^a-zA-Z]', '', word or '').lower()
    if not w:
        return []
    # 常见构词后缀整体成节
    for suf in ('tion', 'sion', 'ing', 'ness', 'ment', 'able', 'ible', 'ful', 'less',
                'ous', 'ive', 'ity', 'ance', 'ence', 'ship', 'ly', 'er', 'est', 'al', 'y'):
        if w.endswith(suf) and len(w) - len(suf) >= 2:
            head = w[:-len(suf)]
            parts = syllabify(head)
            parts.append(suf)
            return parts
    # 元音簇切分
    groups, cur = [], ''
    vowels = 'aeiouy'
    prev_v = False
    for ch in w:
        isv = ch in vowels
        if isv and not prev_v:
            if cur: groups.append(cur)
            cur = ch
        else:
            cur += ch
        prev_v = isv
    if cur: groups.append(cur)
    return [g for g in groups if g]

def phonics_hint(word):
    w = (word or '').lower()
    for pat, hint in PHONICS_HINT:
        if re.match(pat, w):
            return hint
    return ''

def mk(wid, w, level, unit, unitId, **kw):
    stage, mod = STAGE.get(level, ('其他', 'primary'))
    word = (w or '').strip()
    item = {
        'id': wid,
        'word': word,
        'phonetic': kw.get('phonetic', ''),
        'pos': kw.get('pos', ''),
        'meaning': kw.get('meaning', ''),
        'audio': kw.get('audio', ''),
        'level': level,
        'stage': stage,
        'mod': mod,
        'unit': unit,
        'unitId': unitId,
        'sentence': kw.get('sentence', ''),
        'sentenceCn': kw.get('sentenceCn', ''),
        'syllables': syllabify(word) if mod in SPLIT_TARGETS else [],
        'phonics': phonics_hint(word) if mod in SPLIT_TARGETS else '',
    }
    if kw.get('tag'):
        item['tag'] = kw['tag']
    if kw.get('freq'):
        item['freq'] = kw['freq']
    # 例句音频（若有）
    if kw.get('audioSent'):
        item['audioSent'] = kw['audioSent']
    return item


# 考试类词书（vocab_<key>.json）：schema 为 books[].units[].words[]
def collect_exam(key):
    """加载 tools/build_exam_books.py 生成的词书，并回填 TTS 生成的音频路径。"""
    p = os.path.join(DATA, 'vocab_%s.json' % key)
    d = load('vocab_%s.json' % key)
    if not d:
        return None
    audio_root = r'E:/szgaokao.cn/worker/public/audio'
    local_root = os.path.join(os.path.dirname(DATA), 'public', 'audio')
    root = audio_root if os.path.isdir(audio_root) else local_root

    books = []
    for b in d.get('books', []):
        units = []
        for u in b.get('units', []):
            ws = []
            for w in u.get('words', []):
                wid = w['id']
                safe = (w.get('word') or '').replace(' ', '_').replace('/', '_')
                wdir = os.path.join(root, key, wid)
                wa = os.path.join(wdir, safe + '.mp3')
                sa = os.path.join(wdir, 'sent.mp3')
                has_wa = os.path.exists(wa)
                has_sa = os.path.exists(sa)
                ws.append(mk(wid, w.get('word'), key, u.get('title', ''), u.get('id'),
                             phonetic=w.get('phonetic', ''), pos=w.get('pos', ''),
                             meaning=w.get('meaning', ''),
                             audio=('/audio/%s/%s/%s.mp3' % (key, wid, safe)) if has_wa else '',
                             sentence=w.get('sentence', ''), sentenceCn=w.get('sentenceCn', ''),
                             tag=w.get('tag', ''), freq=w.get('freq', ''),
                             audioSent=('/audio/%s/%s/sent.mp3' % (key, wid)) if has_sa else ''))
            units.append({'id': u.get('id'), 'title': u.get('title', ''), 'words': ws})
        books.append({'id': b.get('id', key), 'title': b.get('title', d.get('level', key)),
                      'units': units})
    # 词书中文名：优先 books[0].title（build_exam_books 写入），否则回退 STAGE
    disp = ''
    try:
        disp = (d.get('books') or [{}])[0].get('title', '') or ''
    except Exception:
        pass
    if not disp:
        disp = d.get('product', '') or d.get('level', key)
    return {
        'level': key,
        'title': disp,
        'stage': d.get('stage', STAGE.get(key, ('其他', 'primary'))[0]),
        'mod': d.get('mod', STAGE.get(key, ('其他', 'primary'))[1]),
        'count': sum(len(u['words']) for b in books for u in b['units']),
        'note': d.get('note', ''),
        'books': books,
    }

def collect():
    levels = []   # [{level, title, stage, mod, books:[{id,title,units:[{id,title,words:[...]}]}], count}]
    allitems = {}
    NOTES = {}     # level -> 词书说明（考试类词书自带 note）

    def add_level(level, title, books):
        stage, mod = STAGE.get(level, ('其他', 'primary'))
        cnt = sum(len(u['words']) for b in books for u in b['units'])
        levels.append({'level': level, 'title': title, 'stage': stage, 'mod': mod,
                       'count': cnt, 'books': books})
        for b in books:
            for u in b['units']:
                for it in u['words']:
                    allitems[it['id']] = it

    # ---- 1. 幼儿 ----
    d = load('kids_words.json')
    if d:
        books = []
        units = []
        for g in d.get('groups', []):
            ws = [mk(w['id'], w.get('word'), 'kids', g.get('title', ''), g.get('id'),
                     phonetic=w.get('phonetic', ''), pos=w.get('pos', ''),
                     meaning=w.get('meaning', ''), audio=w.get('audio', ''))
                  for w in g.get('words', [])]
            units.append({'id': g['id'], 'title': g.get('title', ''), 'words': ws})
        books.append({'id': 'kids', 'title': '幼儿启蒙 3-6 岁', 'units': units})
        add_level('kids', '幼儿启蒙 3-6 岁', books)

    # ---- 2. 小学（主题词书）----
    d = load('words.json')
    if d:
        books = []
        by_grade = {}
        for g in d.get('groups', []):
            by_grade.setdefault(g.get('grade', 0), []).append(g)
        for gr in sorted(by_grade):
            units = []
            for g in by_grade[gr]:
                ws = [mk(w['id'], w.get('word'), 'primary', g.get('title', ''), g.get('id'),
                         phonetic=w.get('phonetic', ''), pos=w.get('pos', ''),
                         meaning=w.get('meaning', ''), audio=w.get('audio', ''))
                      for w in g.get('words', [])]
                units.append({'id': g['id'], 'title': g.get('title', ''), 'words': ws})
            books.append({'id': 'p%d' % gr, 'title': '%d 年级' % gr, 'units': units})
        add_level('primary', '小学英语 3-6 年级', books)

    # ---- 3. 朗文小学同步 ----
    d = load('longman.json')
    if d:
        books = []
        for b in d.get('books', []):
            units = []
            for u in b.get('units', []):
                ws = [mk(w['id'], w.get('word'), 'longman', u.get('title', ''), u.get('id'),
                         phonetic=w.get('phonetic', ''),
                         meaning=w.get('meaning', ''), audio=w.get('audio', ''))
                      for w in u.get('words', [])]
                units.append({'id': u['id'], 'title': u.get('title', ''), 'words': ws})
            books.append({'id': b.get('level', b.get('id')), 'title': b.get('title', ''), 'units': units})
        add_level('longman', '朗文小学同步 1A-6B', books)

    # ---- 4. 初中 ----
    d = load('junior_words.json')
    if d:
        books = []
        by_grade = {}
        for g in d.get('groups', []):
            by_grade.setdefault(g.get('grade', 7), []).append(g)
        for gr in sorted(by_grade):
            units = []
            for g in by_grade[gr]:
                ws = [mk(w['id'], w.get('word'), 'junior', g.get('title', ''), g.get('id'),
                         phonetic=w.get('phonetic', ''), pos=w.get('pos', ''),
                         meaning=w.get('meaning', ''), audio=w.get('audio', ''),
                         sentence=w.get('sentence', ''), sentenceCn=w.get('sentenceCn', ''))
                      for w in g.get('words', [])]
                units.append({'id': g['id'], 'title': g.get('title', ''), 'words': ws})
            books.append({'id': 'j%d' % gr, 'title': '%d 年级' % gr, 'units': units})
        add_level('junior', '初中英语 7-9 年级', books)

    # ---- 5. 高中课本 ----
    d = load('senior_textbook.json')
    if d:
        books = []
        for b in d.get('books', []):
            bid = b.get('id') or b.get('name') or 'b'
            units = []
            for u in b.get('units', []):
                ws = []
                for i, w in enumerate(u.get('words', [])):
                    wid = w.get('id') or ('senior-%s-w%d' % (u.get('id', 'u'), i + 1))
                    ws.append(mk(wid, w.get('word'), 'senior', u.get('title', ''), u.get('id'),
                                 phonetic=w.get('phonetic', ''), pos=w.get('pos', ''),
                                 meaning=w.get('meaning', ''), audio=w.get('audio', ''),
                                 sentence=w.get('sentence', ''), sentenceCn=w.get('sentenceCn', '')))
                units.append({'id': u.get('id'), 'title': u.get('title', ''), 'words': ws})
            books.append({'id': bid, 'title': b.get('name') or bid, 'units': units})
        add_level('senior', '高中英语 课本同步', books)

    # ---- 6. KET ----
    d = load('ket_words.json')
    if d:
        books = []
        for gi, g in enumerate(d.get('groups', []), 1):
            ws = [mk(w['id'], w.get('word'), 'ket', g.get('title', ''), g.get('id'),
                     phonetic=w.get('phonetic', ''), pos=w.get('pos', ''),
                     meaning=w.get('meaning', ''), audio=w.get('audio', ''))
                  for w in g.get('words', [])]
            books.append({'id': g.get('id'), 'title': g.get('title', ''),
                          'units': [{'id': g.get('id'), 'title': g.get('title', ''), 'words': ws}]})
        add_level('ket', 'KET / A2 剑桥英语', books)

    # ---- 7. PET ----
    d = load('pet_words.json')
    if d:
        books = []
        for gi, g in enumerate(d.get('groups', []), 1):
            ws = [mk(w['id'], w.get('word'), 'pet', g.get('title', ''), g.get('id'),
                     phonetic=w.get('phonetic', ''), pos=w.get('pos', ''),
                     meaning=w.get('meaning', ''), audio=w.get('audio', ''))
                  for w in g.get('words', [])]
            books.append({'id': g.get('id'), 'title': g.get('title', ''),
                          'units': [{'id': g.get('id'), 'title': g.get('title', ''), 'words': ws}]})
        add_level('pet', 'PET / B1 剑桥英语', books)

    # ---- 8~13. 考试类词书（ky/cet4/cet6/tem8/ielts/toefl/oral，存在才加载）----
    for key in ['ky', 'cet4', 'cet6', 'tem8', 'ielts', 'toefl', 'oral']:
        lv = collect_exam(key)
        if lv:
            add_level(lv['level'], lv['title'], lv['books'])
            if lv.get('note'):
                NOTES[lv['level']] = lv['note']

    return levels, allitems

def main():
    levels, allitems = collect()
    if not levels:
        print('未找到任何词书'); sys.exit(1)

    words = []
    for lv in levels:
        for b in lv['books']:
            for u in b['units']:
                for it in u['words']:
                    words.append(it)

    out = {
        'product': '专业英语单词记忆 · 全学段词书库',
        'version': '1.0',
        'schema_version': '1.0',
        'note': ('全学段统一词条库：幼儿/小学/朗文/初中/高中/KET/PET。'
                 '字段：word 单词、phonetic 音标、pos 词性、meaning 释义、audio 发音、'
                 'sentence/sentenceCn 例句、syllables 音节、phonics 自然拼读提示。'
                 '配套 FSRS 间隔重复记忆引擎与 8 种题型。内容由 AI 整理，待人工校对。'),
        'levels': levels,
        'words': words,
    }
    p = os.path.join(DATA, 'vocab.json')
    with io.open(p, 'w', encoding='utf-8') as f:
        f.write(json.dumps(out, ensure_ascii=False, separators=(',', ':')))

    print('=== vocab.json 构建完成 ===')
    print('文件: %s  (%.1f KB)' % (p, os.path.getsize(p) / 1024.0))
    print('学段词书 %d 套，总词条 %d' % (len(levels), len(words)))
    for lv in levels:
        nb = len(lv['books']); nu = sum(len(b['units']) for b in lv['books'])
        print('  %-9s %-22s %3d 册 %3d 单元 %4d 词' % (lv['level'], lv['title'], nb, nu, lv['count']))

    # 覆盖率体检
    print('\n=== 字段覆盖率 ===')
    def cov(field):
        n = sum(1 for w in words if w.get(field))
        return '%s %d/%d (%.0f%%)' % (field, n, len(words), 100.0 * n / len(words))
    for f in ['phonetic', 'pos', 'meaning', 'audio', 'sentence', 'syllables', 'phonics']:
        print('  ' + cov(f))
    ids = [w['id'] for w in words]
    print('  id 唯一: %s (%d/%d)' % (len(set(ids)) == len(ids), len(set(ids)), len(ids)))
    bad = [w['word'] for w in words if not w.get('word')]
    print('  空 word: %d' % len(bad))

if __name__ == '__main__':
    main()
