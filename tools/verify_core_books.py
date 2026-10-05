# -*- coding: utf-8 -*-
"""课标三层级扩容上线验证：确认小学800/初中1600/高中3500 三套词书、音频、FSRS 均线上可用。

用法：python tools/verify_core_books.py   （默认直连，VOCAB_PROXY=1 走代理）
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
DEV = 'verify-core-dev'
st, r = req('POST', BASE + '/api/register', {'username': U, 'password': 'test123456', 'device': DEV, 'is_test': True})
T = r.get('token', '')
st, r = req('POST', BASE + '/api/admin/login', {'secret': SECRET})
AT = r.get('token', '')
req('POST', BASE + '/api/admin/users/grant',
    {'username': U, 'plan': 'permanent', 'modules': ['vocab']},
    {'Authorization': 'Bearer ' + AT})
st, r = req('POST', BASE + '/api/login', {'username': U, 'password': 'test123456', 'device': DEV})
T = r.get('token', '')
H = {'Authorization': 'Bearer ' + T, 'X-Device': DEV}

print('\n=== 1. 词书总览（应 14 套 / 8212 词）===')
st, r = req('GET', BASE + '/api/vocab?stats=1', h=H)
check('统计接口可用', st == 200, 'HTTP %s' % st)
levels = r.get('levels', [])
total = r.get('total', 0)
check('总词数 = 8212', total == 8212, '实际 %s' % total)
have = {l['level']: l['count'] for l in levels}
TARGETS = {'primary': 800, 'junior': 1600, 'senior': 3500}
for lv, n in TARGETS.items():
    check('%s 词书 = %d' % (lv, n), have.get(lv) == n,
          '实际 %s' % have.get(lv, '缺失'))

print('\n=== 2. 三套词书逐套取词（验队列可用）===')
for lv in ['primary', 'junior', 'senior']:
    st, rr = req('GET', BASE + '/api/vocab?level=' + lv, h=H)
    q = rr.get('queue', []) if st == 200 else []
    n = rr.get('est', {}).get('total', 0) if st == 200 else 0
    check('%-8s 取词' % lv, st == 200 and len(q) > 0,
          '%d 词 / 队列 %d / 每日上限 %d' % (n, len(q), rr.get('daily', 0)))

print('\n=== 3. 词条字段完整性（音标/释义/音频）===')
for lv in ['primary', 'junior', 'senior']:
    wid = {'primary': 'p_0001', 'junior': 'j_0001', 'senior': 's_0001'}[lv]
    st, rr = req('GET', BASE + '/api/vocab?level=' + lv + '&word=' + wid, h=H)
    w = rr.get('word', {}) if st == 200 else {}
    check('%-8s 首词字段完整' % lv,
          bool(w.get('word')) and bool(w.get('phonetic')) and bool(w.get('meaning')) and bool(w.get('audio')),
          '%s %s %s' % (w.get('word'), w.get('phonetic'), w.get('meaning')))

print('\n=== 4. 核心音频真实可访问（每套抽验首词 _core 音频）===')
for lv, wid in [('primary', 'p_0001'), ('junior', 'j_0001'), ('senior', 's_0001')]:
    st, rr = req('GET', BASE + '/api/vocab?level=' + lv + '&word=' + wid, h=H)
    w = rr.get('word', {}) if st == 200 else {}
    url = BASE + w.get('audio', '') if w.get('audio') else ''
    if not url:
        check('%-8s 音频' % lv, False, '无 audio 路径'); continue
    try:
        rq = urllib.request.Request(url, headers={'User-Agent': 'verify'})
        with op.open(rq, timeout=45) as x:
            b = x.read(2048)
            ok = x.status == 200 and len(b) > 0 and b[0] == 0xFF
            check('%-8s %s' % (lv, w.get('word')), ok,
                  'HTTP %s  %sB  帧头 %s' % (x.status, x.headers.get('Content-Length', '0'), b[:2].hex()))
    except Exception as e:
        check('%-8s 音频' % lv, False, str(e)[:50])

print('\n=== 5. FSRS 引擎对课标词书生效 ===')
st, rr = req('GET', BASE + '/api/vocab?level=primary&word=p_0001', h=H)
wid = rr['word']['id']
prev = 0; mono = True; gaps = []
for i in range(3):
    st, r3 = req('POST', BASE + '/api/vocab/review', {'id': wid, 'grade': 2, 'time': 900}, h=H)
    g = r3.get('nextIn', 0); gaps.append(g)
    if g < prev - 0.01: mono = False
    prev = g
print('       间隔序列: %s 天' % ' -> '.join('%.2f' % g for g in gaps))
check('评分提交成功', st == 200)
check('间隔单调递增（FSRS 生效）', mono, 'SRS 未按记忆曲线拉长' if not mono else '')
check('间隔逐步拉长', gaps[-1] > gaps[0], '%.2f -> %.2f 天' % (gaps[0], gaps[-1]))
st, rf = req('POST', BASE + '/api/vocab/review', {'id': wid, 'grade': 0}, h=H)
check('「忘记」后当天再练', rf.get('nextIn', 99) < 1, '%.3f 天' % rf.get('nextIn', 0))

print('\n=== 6. 云端持久化与错题本 ===')
st, sd = req('GET', BASE + '/api/study', h=H)
check('srs 状态已上云', wid in (sd.get('srs') or {}), 'srs 词数 %d' % len(sd.get('srs') or {}))
check('ans 记录 qid 前缀 vocab:', ('vocab:' + wid) in (sd.get('ans') or {}))
check('tags 派生英语·词汇', '英语·词汇' in (sd.get('tags') or {}))

print('\n=== 7. 原有模块未受影响 ===')
for lv, n in [('kids', 120), ('longman', 384), ('cet4', 295), ('ielts', 174)]:
    st, rr = req('GET', BASE + '/api/vocab?level=' + lv, h=H)
    t = rr.get('est', {}).get('total', 0) if st == 200 else -1
    check('%-8s 仍可用（%d 词）' % (lv, n), st == 200 and t == n, '%s 词' % t)

print('\n=========================================')
print('  验证结果：%d 通过 / %d 失败' % (P, F))
print('=========================================')
sys.exit(1 if F else 0)
