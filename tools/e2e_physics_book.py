# -*- coding: utf-8 -*-
"""物理·课本同步 端到端验证（线上）。
覆盖：
  /api/physics-book           册列表（trial 仅每册第 1 章）
  /api/physics-book?book=     单册（trial 仅第 1 章）
  /api/physics-book?chapter=  单章
  /api/physics-book?section=  单节（≥10 题，题型/答案结构合法）
  鉴权 401 / 404 / /physics 页面含「课本同步」
用法：HTTPS_PROXY=http://127.0.0.1:65428 python tools/e2e_physics_book.py
"""
import json, os, ssl, sys, time, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://szgaokao.toolshe.cn'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
PROXY = os.environ.get('HTTPS_PROXY') or os.environ.get('HTTP_PROXY') or 'http://127.0.0.1:65428'

PASS = FAIL = 0


def check(name, cond, detail=''):
    global PASS, FAIL
    if cond:
        PASS += 1
        print('  [PASS] %s%s' % (name, (' — ' + detail) if detail else ''))
    else:
        FAIL += 1
        print('  [FAIL] %s%s' % (name, (' — ' + detail) if detail else ''))


opener = urllib.request.build_opener(
    urllib.request.ProxyHandler({'http': PROXY, 'https': PROXY}),
    urllib.request.HTTPSHandler(context=ssl.create_default_context()))


def req(method, url, data=None, headers=None, retry=3):
    for a in range(retry):
        body = json.dumps(data).encode() if data is not None else None
        h = {'Content-Type': 'application/json', 'User-Agent': UA}
        if headers:
            h.update(headers)
        try:
            r = urllib.request.Request(url, data=body, method=method, headers=h)
            with opener.open(r, timeout=60) as resp:
                return resp.status, json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            try:
                return e.code, json.loads(e.read().decode())
            except Exception:
                return e.code, {}
        except Exception as e:
            if a < retry - 1:
                time.sleep(2)
                continue
            return 0, {'error': str(e)}


FP = 'e2e-physics-book-device'
U = 'pbook%d' % int(time.time() % 100000)
st, r = req('POST', BASE + '/api/register', {'username': U, 'password': 'test123456', 'device': FP})
check('注册成功', st == 200 and r.get('token'), 'HTTP %d' % st)
H = {'Authorization': 'Bearer ' + r.get('token', ''), 'X-Device': FP}

print('\n--- /api/physics-book 册列表（trial） ---')
st, r = req('GET', BASE + '/api/physics-book', headers=H)
check('册列表 200', st == 200, 'HTTP %d' % st)
if st == 200:
    books = r.get('books', [])
    trial = r.get('trial')
    check('返回 6 册', len(books) == 6, 'books=%d trial=%s' % (len(books), trial))
    check('edition 字段存在', bool(r.get('edition')), r.get('edition', '')[:20])
    check('trial 字段为布尔', isinstance(trial, bool), 'trial=%s' % trial)
    if books:
        b0 = books[0]
        check('册结构字段完整', all(k in b0 for k in ('id', 'name', 'term', 'chapterCount', 'sectionCount')), str(list(b0.keys())))
        # trial 模式每册仅 1 章；授权模式返回全部章（>=1）
        if trial:
            check('trial 每册仅 1 章', b0.get('chapterCount') == 1, 'chapterCount=%s' % b0.get('chapterCount'))
        else:
            check('授权模式返回全部章（>=1）', b0.get('chapterCount', 0) >= 1, 'chapterCount=%s' % b0.get('chapterCount'))
        check('sectionCount>=1', b0.get('sectionCount', 0) >= 1, 'sectionCount=%s' % b0.get('sectionCount'))

print('\n--- ?book= 单册（trial 仅第 1 章） ---')
st, r = req('GET', BASE + '/api/physics-book?book=pb9', headers=H)
check('单册 200', st == 200, 'HTTP %d' % st)
if st == 200:
    bk = r.get('book', {})
    check('册 id 正确', bk.get('id') == 'pb9', bk.get('id'))
    chs = bk.get('chapters', [])
    if r.get('trial'):
        check('trial 单册仅 1 章', len(chs) == 1, 'chapters=%d' % len(chs))
    else:
        check('授权模式返回全部章（>=1）', len(chs) >= 1, 'chapters=%d' % len(chs))
    if chs:
        check('章含 sections', len(chs[0].get('sections', [])) >= 1, 'sections=%d' % len(chs[0].get('sections', [])))

print('\n--- ?chapter= 单章 ---')
# 先取一个真实 chapter id：从单册里拿
st0, r0 = req('GET', BASE + '/api/physics-book?book=pb8s', headers=H)
cid = r0.get('book', {}).get('chapters', [{}])[0].get('id') if st0 == 200 else None
if cid:
    st, r = req('GET', BASE + '/api/physics-book?chapter=' + cid, headers=H)
    check('单章 200', st == 200, 'HTTP %d' % st)
    if st == 200:
        ch = r.get('chapter', {})
        check('章含 id/title/sections', all(k in ch for k in ('id', 'title', 'sections')), str(list(ch.keys())))
        check('章含若干节', len(ch.get('sections', [])) >= 1, 'sections=%d' % len(ch.get('sections', [])))
        # 取第一节 id 验证 section 接口
        sid = ch.get('sections', [{}])[0].get('id')
else:
    st, r, sid = 0, {}, None

print('\n--- ?section= 单节（核心：≥10 题，结构合法） ---')
if not sid:
    # 退路：直接猜一个已知 id
    sid = 'pb8s_c1s1'
st, r = req('GET', BASE + '/api/physics-book?section=' + sid, headers=H)
check('单节 200', st == 200, 'HTTP %d' % st)
if st == 200:
    sec = r.get('section', {})
    check('节含 id/title/points/questions', all(k in sec for k in ('id', 'title', 'points', 'questions')), str(list(sec.keys())))
    qs = sec.get('questions', [])
    check('每节 >= 10 题', len(qs) >= 10, '题数=%d' % len(qs))
    check('考点 points >= 1', len(sec.get('points', [])) >= 1, 'points=%d' % len(sec.get('points', [])))
    # 逐题校验结构
    types = {}
    ok_struct = True
    for q in qs:
        t = q.get('type'); types[t] = types.get(t, 0) + 1
        if t in ('choice_single',):
            if not (isinstance(q.get('options'), list) and len(q.get('options', [])) >= 2 and isinstance(q.get('answer'), int) and 0 <= q['answer'] < len(q['options'])):
                ok_struct = False
        elif t == 'choice_multi':
            if not (isinstance(q.get('options'), list) and isinstance(q.get('answer'), list) and all(isinstance(x, int) for x in q['answer'])):
                ok_struct = False
        elif t in ('fill', 'drawing', 'calculation', 'short'):
            if not (isinstance(q.get('answer'), str) and q.get('answer') != ''):
                ok_struct = False
        elif t == 'experiment':
            if not (isinstance(q.get('sub'), list) or q.get('analysis')):
                ok_struct = False
        if 'analysis' not in q or 'stem' not in q or 'kaodian' not in q:
            ok_struct = False
    check('全部题目结构合法', ok_struct, '题型分布=%s' % types)
    check('题型贴合中高考（含选择/填空/计算/简答/实验等）', any(k in types for k in ('choice_single', 'fill', 'calculation', 'short', 'experiment', 'choice_multi')), str(types))

print('\n--- 404 / 401 ---')
st, _ = req('GET', BASE + '/api/physics-book?section=nope', headers=H)
check('不存在节 404', st == 404, 'HTTP %d' % st)
st, _ = req('GET', BASE + '/api/physics-book')
check('未登录 401', st == 401, 'HTTP %d' % st)
st, _ = req('GET', BASE + '/api/physics-book', headers={'Authorization': 'Bearer bad', 'X-Device': FP})
check('无效 token 401', st == 401, 'HTTP %d' % st)

print('\n--- /physics 页面 ---')
try:
    rq = urllib.request.Request(BASE + '/physics', headers={'User-Agent': UA})
    with opener.open(rq, timeout=60) as resp:
        html = resp.read().decode('utf-8', 'ignore')
    check('/physics 页面 200', True)
    for k in ['课本同步', 'renderBookPage', '📗 课本同步']:
        check('/physics 含 %s' % k, k in html)
except Exception as e:
    check('/physics 页面可访问', False, str(e)[:60])

print('\n==== 结果：PASS=%d FAIL=%d ====' % (PASS, FAIL))
sys.exit(1 if FAIL else 0)
