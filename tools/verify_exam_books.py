# -*- coding: utf-8 -*-
"""新词书上线验证：确认 14 套词书、2984 词、音频、标签、例句均已线上可用。

走代理（szgaokao 域名可直连，但为稳妥起见默认直连）。
用法：python tools/verify_exam_books.py
"""
import json, os, ssl, sys, time, urllib.request, urllib.error

PROXY = 'http://127.0.0.1:29290'
BASE = 'https://szgaokao.toolshe.cn'
SECRET = 'eqD7tVejuzbWmFg6'

if os.environ.get('VOCAB_PROXY') == '1':
    op = urllib.request.build_opener(
        urllib.request.ProxyHandler({'http': PROXY, 'https': PROXY}),
        urllib.request.HTTPSHandler(context=ssl.create_default_context()))
    print('[走代理]')
else:
    op = urllib.request.build_opener(
        urllib.request.ProxyHandler({}),
        urllib.request.HTTPSHandler(context=ssl.create_default_context()))
    print('[直连]')

def req(m, u, d=None, h=None, retry=3):
    for a in range(retry):
        b = json.dumps(d).encode() if d is not None else None
        hh = {'Content-Type': 'application/json', 'User-Agent': 'verify'}
        if h: hh.update(h)
        try:
            r = urllib.request.Request(u, data=b, method=m, headers=hh)
            with op.open(r, timeout=90) as x:
                return x.status, json.loads(x.read().decode())
        except urllib.error.HTTPError as e:
            try: return e.code, json.loads(e.read().decode())
            except Exception: return e.code, {}
        except Exception as e:
            if a < retry - 1: time.sleep(3); continue
            return 0, {'error': str(e)}

P = F = 0
def check(name, cond, detail=''):
    global P, F
    if cond: P += 1; print('  [PASS] %s%s' % (name, (' — ' + detail) if detail else ''))
    else:    F += 1; print('  [FAIL] %s%s' % (name, (' — ' + detail) if detail else ''))

# ---------- 登录并授权 ----------
U = 'vexa%d' % int(time.time() % 100000)
DEV = 'verify-exa-dev'
st, r = req('POST', BASE + '/api/register', {'username': U, 'password': 'test123456', 'device': DEV})
T = r.get('token', '')
st, r = req('POST', BASE + '/api/admin/login', {'secret': SECRET})
AT = r.get('token', '')
req('POST', BASE + '/api/admin/users/grant',
    {'username': U, 'plan': 'permanent', 'modules': ['vocab']},
    {'Authorization': 'Bearer ' + AT})
st, r = req('POST', BASE + '/api/login', {'username': U, 'password': 'test123456', 'device': DEV})
T = r.get('token', '')
H = {'Authorization': 'Bearer ' + T, 'X-Device': DEV}

print('\n=== 1. 词书总览（应 14 套 / 2984 词）===')
st, r = req('GET', BASE + '/api/vocab?stats=1', h=H)
check('统计接口可用', st == 200, 'HTTP %s' % st)
levels = r.get('levels', [])
check('词书数量 = 14', len(levels) == 14, '实际 %d 套' % len(levels))
check('总词数 = 2984', r.get('total') == 2984, '实际 %s' % r.get('total'))
NEW = {'ky', 'cet4', 'cet6', 'tem8', 'ielts', 'toefl', 'oral'}
have = {l['level'] for l in levels}
check('7 套新词书全部上线', NEW.issubset(have), '缺: %s' % (NEW - have if not NEW.issubset(have) else '无'))
print()
print('  %-9s %-24s %5s  %s' % ('level', '词书名', '词数', '学段'))
for l in levels:
    mark = '★' if l['level'] in NEW else ' '
    print('  %s %-9s %-22s %5d  %s' % (mark, l['level'], l['title'][:22], l['count'], l['stage']))

print('\n=== 2. 新词书逐套取词（验队列可用）===')
for lv in ['ky', 'cet4', 'cet6', 'tem8', 'ielts', 'toefl', 'oral']:
    st, rr = req('GET', BASE + '/api/vocab?level=' + lv, h=H)
    q = rr.get('queue', []) if st == 200 else []
    n = rr.get('est', {}).get('total', 0) if st == 200 else 0
    check('%-6s 取词' % lv, st == 200 and len(q) > 0, '%d 词 / 队列 %d / 每日上限 %d' % (n, len(q), rr.get('daily', 0)))

print('\n=== 3. 词条字段完整性（音标/释义/例句/标签）===')
st, rr = req('GET', BASE + '/api/vocab?level=ky&word=ky-g1-w1', h=H)
w = rr.get('word', {})
check('考研首词字段完整',
      bool(w.get('word')) and bool(w.get('phonetic')) and bool(w.get('meaning')),
      '%s %s %s' % (w.get('word'), w.get('phonetic'), w.get('meaning')))
check('含例句 + 例句翻译', bool(w.get('sentence')) and bool(w.get('sentenceCn')),
      (w.get('sentence') or '')[:50])
check('含考点标签', bool(w.get('tag')), 'tag=%s' % w.get('tag'))
check('含音频路径', bool(w.get('audio')), w.get('audio'))
check('干扰项 3 个', len(rr.get('distractors', [])) == 3, '实际 %d' % len(rr.get('distractors', [])))

print('\n=== 4. 音频文件真实可访问（抽验 6 个新词书音频）===')
samples = [
    ('ky', 'ky-g1-w1', 'abandon'),
    ('cet4', 'cet4-g1-w1', 'accommodate'),
    ('cet6', 'cet6-g1-w1', 'abstract'),
    ('ielts', 'ielts-g1-w1', 'abundant'),
    ('toefl', 'toefl-g1-w1', 'abstract'),
    ('oral', 'oral-g1-w1', 'accommodation'),
]
for mod, wid, word in samples:
    url = '%s/audio/%s/%s/%s.mp3' % (BASE, mod, wid, word)
    try:
        rq = urllib.request.Request(url, headers={'User-Agent': 'verify'})
        with op.open(rq, timeout=45) as x:
            b = x.read(2048)
            ok = x.status == 200 and len(b) > 0 and b[0] == 0xFF
            clen = x.headers.get('Content-Length', '0')
            check('%-6s %-14s' % (mod, word), ok,
                  'HTTP %s  %s B  帧头 %s' % (x.status, clen, b[:2].hex()))
    except Exception as e:
        check('%-6s %-14s' % (mod, word), False, str(e)[:50])

print('\n=== 5. SRS 引擎对新词书生效 ===')
st, rr = req('GET', BASE + '/api/vocab?level=ky&word=ky-g1-w1', h=H)
wid = rr['word']['id']
prev = 0; mono = True; gaps = []
for i in range(3):
    st, r3 = req('POST', BASE + '/api/vocab/review', {'id': wid, 'grade': 2, 'time': 900}, h=H)
    g = r3.get('nextIn', 0); gaps.append(g)
    if g < prev - 0.01: mono = False
    prev = g
print('       间隔序列: %s 天' % ' -> '.join('%.2f' % g for g in gaps))
check('评分提交成功', st == 200)
check('间隔单调递增（FSRS 生效）', mono, 'SRS 未按记忆曲线拉长间隔' if not mono else '')
check('间隔逐步拉长', gaps[-1] > gaps[0], '%.2f -> %.2f 天' % (gaps[0], gaps[-1]))
st, rf = req('POST', BASE + '/api/vocab/review', {'id': wid, 'grade': 0}, h=H)
check('「忘记」后当天再练', rf.get('nextIn', 99) < 1, '%.3f 天' % rf.get('nextIn', 0))

print('\n=== 6. 云端持久化与错题本 ===')
st, sd = req('GET', BASE + '/api/study', h=H)
check('srs 状态已上云', wid in (sd.get('srs') or {}), 'srs 词数 %d' % len(sd.get('srs') or {}))
check('ans 记录 qid 前缀 vocab:', ('vocab:' + wid) in (sd.get('ans') or {}))
check('tags 派生英语·词汇', '英语·词汇' in (sd.get('tags') or {}))

print('\n=== 7. 原有模块未受影响 ===')
st, r = req('GET', BASE + '/api/vocab?level=primary', h=H)
check('小学词书仍可用（240 词）', st == 200 and r.get('est', {}).get('total') == 240,
      '%s 词' % r.get('est', {}).get('total'))
for path, label in [('/api/volumes', '中考听说'), ('/api/me', '账号')]:
    st, rr2 = req('GET', BASE + path, h=H)
    check('%-8s %s' % (label, path), st == 200, 'HTTP %s' % st)

print('\n=========================================')
print('  验证结果：%d 通过 / %d 失败' % (P, F))
print('=========================================')
sys.exit(1 if F else 0)
