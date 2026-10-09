# -*- coding: utf-8 -*-
"""初高中物理模块端到端验证（线上）。
覆盖：/api/physics（板块+条目）/api/physics-exam（total+grade筛选+ids）/api/physics-link（单元+详情）
      /physics 页面 200 + 年级筛选含 7/8 + 首页卡片 + 鉴权 401
用法：python tools/e2e_physics.py
"""
import json, os, ssl, sys, time, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://szgaokao.toolshe.cn'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
PROXY = os.environ.get('HTTPS_PROXY') or os.environ.get('HTTP_PROXY') or 'http://127.0.0.1:60218'

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


FP = 'e2e-physics-device'
U = 'phys%d' % int(time.time() % 100000)
st, r = req('POST', BASE + '/api/register', {'username': U, 'password': 'test123456', 'device': FP})
check('注册成功', st == 200 and r.get('token'), 'HTTP %d' % st)
H = {'Authorization': 'Bearer ' + r.get('token', ''), 'X-Device': FP}

print('\n--- /api/physics 知识点 ---')
st, r = req('GET', BASE + '/api/physics', headers=H)
check('知识点接口 200', st == 200, 'HTTP %d' % st)
if st == 200:
    secs = r.get('sections', {})
    check('含 knowledge 板块', 'knowledge' in secs, str(list(secs.keys())))
    gs = secs.get('knowledge', {}).get('groups', [])
    check('分组数 >= 1', len(gs) >= 1, 'groups=%d trial=%s' % (len(gs), r.get('trial')))
    if gs:
        g = gs[0]
        check('分组含 items', isinstance(g.get('items'), list) and len(g['items']) > 0, 'items=%d' % len(g.get('items', [])))
        it = g['items'][0]
        check('知识点结构完整', all(k in it for k in ('id', 'term', 'jieshi', 'kao')), str(list(it.keys())))
        check('自测含选项与答案', bool(it.get('kao', {}).get('options')) and 'answer' in it.get('kao', {}))

print('\n--- /api/physics-exam 题库 ---')
st, r = req('GET', BASE + '/api/physics-exam', headers=H)
check('题库接口 200', st == 200, 'HTTP %d' % st)
if st == 200:
    qs = r.get('questions', [])
    check('返回题目列表', len(qs) > 0, '题数=%d trial=%s' % (len(qs), r.get('trial')))
    check('返回 topics 供筛选', len(r.get('topics', [])) > 0, 'topics=%d' % len(r.get('topics', [])))
    if qs:
        q = qs[0]
        check('题目结构完整', all(k in q for k in ('id', 'grade', 'topic', 'type', 'difficulty', 'stem')), str(list(q.keys())))
        if q['type'] == 'choice':
            check('选择题 4 选项', len(q.get('options', [])) == 4)
            check('选择题答案合法', 0 <= q.get('answer', -1) < len(q.get('options', [])))

st, r = req('GET', BASE + '/api/physics-exam?grade=8', headers=H)
check('按 grade=8（初二）筛选 200', st == 200, 'HTTP %d' % st)
if st == 200:
    gs = {q['grade'] for q in r.get('questions', [])}
    check('筛选结果均为 grade=8', gs <= {8}, 'grades=%r 题数=%d' % (sorted(gs), len(r.get('questions', []))))

st, r = req('GET', BASE + '/api/physics-exam?type=choice', headers=H)
if st == 200:
    ts = {q['type'] for q in r.get('questions', [])}
    check('按 type=choice 筛选生效', ts <= {'choice'}, 'types=%r' % sorted(ts))

st, r = req('GET', BASE + '/api/physics-exam?ids=bad', headers=H)
check('ids 非法返回 200 空数组', st == 200 and r.get('questions') == [], 'HTTP %d' % st)

print('\n--- /api/physics-link 专题包 ---')
st, r = req('GET', BASE + '/api/physics-link', headers=H)
check('专题接口 200', st == 200, 'HTTP %d' % st)
if st == 200:
    us = r.get('units', [])
    check('返回单元列表', len(us) >= 1, 'units=%d trial=%s' % (len(us), r.get('trial')))
    if us:
        u = us[0]
        check('单元结构完整', all(k in u for k in ('id', 'title', 'summary', 'points', 'quiz')), str(list(u.keys())))
        check('含讲解要点', len(u.get('points', [])) > 0, 'points=%d' % len(u.get('points', [])))
        check('含小测', len(u.get('quiz', [])) > 0, 'quiz=%d' % len(u.get('quiz', [])))
        st2, r2 = req('GET', BASE + '/api/physics-link?unit=' + u['id'], headers=H)
        check('unit 详情 200', st2 == 200 and r2.get('id') == u['id'], 'HTTP %d' % st2)

st, _ = req('GET', BASE + '/api/physics-link?unit=nope', headers=H)
check('不存在单元 404', st == 404, 'HTTP %d' % st)

print('\n--- 鉴权 ---')
st, _ = req('GET', BASE + '/api/physics')
check('未登录 401', st == 401, 'HTTP %d' % st)
st, _ = req('GET', BASE + '/api/physics-exam')
check('未登录 exam 401', st == 401, 'HTTP %d' % st)
st, _ = req('GET', BASE + '/api/physics', headers={'Authorization': 'Bearer bad', 'X-Device': FP})
check('无效 token 401', st == 401, 'HTTP %d' % st)

print('\n--- 页面 ---')
for path, kw in [('/physics', ['初高中物理', '/api/physics', "k: 'knowledge'", 'renderKnowledgeRead', "'7':'初一'", "#1e40af", '物理公式计算卷']),
                 ('/', ['mod-physics', "enterMod('physics')", './physics.html', '初高中物理'])]:
    try:
        rq = urllib.request.Request(BASE + path, headers={'User-Agent': UA})
        with opener.open(rq, timeout=60) as resp:
            html = resp.read().decode('utf-8', 'ignore')
        check('%s 页面 200' % path, True)
        for k in kw:
            check('%s 含 %s' % (path, k), k in html)
    except Exception as e:
        check('%s 页面可访问' % path, False, str(e)[:60])

print('\n=========================================')
print('  结果：%d 通过 / %d 失败' % (PASS, FAIL))
print('=========================================')
sys.exit(1 if FAIL else 0)
