# -*- coding: utf-8 -*-
"""politics 广东高考仿真卷 端到端线上验证。
覆盖：/api/politics-gd 列表 + 单卷详情 + 结构/题量/分值校验 + 页面含 GD Tab。
"""
import json, os, ssl, sys, time, urllib.request, urllib.error

PROXY = os.environ.get('HTTPS_PROXY') or os.environ.get('HTTP_PROXY') or 'http://127.0.0.1:60218'
BASE = 'https://szgaokao.toolshe.cn'
opener = urllib.request.build_opener(
    urllib.request.ProxyHandler({'http': PROXY, 'https': PROXY}),
    urllib.request.HTTPSHandler(context=ssl.create_default_context()))


def req(method, url, data=None, headers=None, retry=3):
    for a in range(retry):
        body = json.dumps(data).encode() if data is not None else None
        h = {'Content-Type': 'application/json', 'User-Agent': 'e2e-politics-gd'}
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


PASS = FAIL = 0


def check(name, cond, detail=''):
    global PASS, FAIL
    if cond:
        PASS += 1
        print('  [PASS] %s%s' % (name, (' — ' + detail) if detail else ''))
    else:
        FAIL += 1
        print('  [FAIL] %s%s' % (name, (' — ' + detail) if detail else ''))


U = 'gdpol%d' % int(time.time() % 100000)
DEV = 'e2e-device-politics-gd'

print('=== 步骤1：注册（平台自动授予 primary）===')
st, r = req('POST', BASE + '/api/register', {'username': U, 'password': 'test123456', 'device': DEV})
check('注册成功', st == 200 and r.get('token'), 'HTTP %d' % st)
TOKEN = r.get('token', '')
H = {'Authorization': 'Bearer ' + TOKEN, 'X-Device': DEV}

print('\n=== 步骤2：/api/politics-gd 试卷列表 ===')
st, r = req('GET', BASE + '/api/politics-gd', headers=H)
check('返回 200', st == 200, 'HTTP %d' % st)
check('kind=structural-mock（标注非真题）', r.get('kind') == 'structural-mock', 'kind=%s' % r.get('kind'))
check('notice 含「非高考真题原卷」', '非高考真题原卷' in (r.get('notice') or ''), (r.get('notice') or '')[:40])
check('region=广东省', r.get('region') == '广东省', r.get('region'))
papers = r.get('papers', [])
check('共 5 套', len(papers) == 5, '实际 %d 套' % len(papers))
years = [p.get('year') for p in papers]
check('年份 2021-2025', years == [2021, 2022, 2023, 2024, 2025], 'years=%s' % years)
st_struct = r.get('structure', [])
check('结构含 3 大题型', len(st_struct) == 3, '实际 %d' % len(st_struct))
check('结构分值 48+24+28=100', sum(s.get('score', 0) for s in st_struct) == 100,
      '分值=%s' % [s.get('score') for s in st_struct])
for p in papers:
    print('       %d | %s分 %s分钟 %s题 | %s' % (p['year'], p['totalScore'], p['durationMin'], p['questionCount'], p.get('theme') or ''))

print('\n=== 步骤3：单卷详情（逐套校验结构）===')
for p in papers:
    st, pp = req('GET', BASE + '/api/politics-gd?paper=' + p['id'], headers=H)
    ok200 = st == 200 and pp.get('id') == p['id']
    mods = pp.get('modules', [])
    qs = [q for m in mods for pt in m.get('parts', []) for q in pt.get('questions', [])]
    total = sum(q.get('score', 0) for q in qs)
    n_single = sum(1 for q in qs if q.get('type') == 'single')
    n_multi = sum(1 for q in qs if q.get('type') == 'multiple')
    n_sub = sum(1 for q in qs if q.get('type') == 'subjective')
    good = (ok200 and len(mods) == 3 and len(qs) == 23 and total == 100
            and n_single == 16 and n_multi == 4 and n_sub == 3)
    check('%d 卷：3模块/23题/100分(单16多4主3)' % p['year'], good,
          '模块%d 题%d 分%d 单%d 多%d 主%d' % (len(mods), len(qs), total, n_single, n_multi, n_sub))
    # 答案合法性
    bad = []
    for q in qs:
        if q['type'] == 'single' and not (0 <= q.get('answer', -1) < len(q.get('options', []))):
            bad.append(q['no'])
        if q['type'] == 'multiple':
            a = q.get('answer') or []
            if not (isinstance(a, list) and 2 <= len(a) <= 4 and all(0 <= x < 4 for x in a)):
                bad.append(q['no'])
    check('%d 卷：答案索引合法' % p['year'], not bad, '异常题号=%s' % bad)

print('\n=== 步骤4：多选题答案可渲染性（多选答案须为字母组合）===')
st, pp = req('GET', BASE + '/api/politics-gd?paper=gdzz2024', headers=H)
qs = [q for m in pp.get('modules', []) for pt in m.get('parts', []) for q in pt.get('questions', [])]
multis = [q for q in qs if q['type'] == 'multiple']
check('2024 含 4 道多选', len(multis) == 4, '实际 %d' % len(multis))
for q in multis:
    letters = ''.join('ABCD'[i] for i in q['answer'])
    check('  第%d题答案 %s 可渲染' % (q['no'], letters), len(letters) == len(q['answer']))

print('\n=== 步骤5：主观题含参考答案与解析 ===')
subs = [q for q in qs if q['type'] == 'subjective']
check('2024 含 3 道主观题', len(subs) == 3, '实际 %d' % len(subs))
check('主观题均有参考答案', all(q.get('answer') for q in subs))
check('主观题均有解析', all(q.get('analysis') for q in subs))

print('\n=== 步骤6：页面含 GD Tab 与接口调用 ===')
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36'
try:
    rq = urllib.request.Request(BASE + '/politics', headers={'User-Agent': UA})
    with opener.open(rq, timeout=60) as resp:
        html = resp.read().decode('utf-8', 'ignore')
    check('politics 页面 200', True, 'HTTP 200')
    check('含「广东高考卷」Tab', '广东高考卷' in html)
    check('含 /api/politics-gd 调用', '/api/politics-gd' in html)
    check('含 renderGdPage 渲染器', 'renderGdPage' in html)
    check('含 gd- 样式类', 'gd-paper' in html)
except Exception as e:
    check('politics 页面可访问', False, str(e)[:60])

print('\n=== 步骤7：不存在的卷返回 404 ===')
st, _ = req('GET', BASE + '/api/politics-gd?paper=gdzz9999', headers=H)
check('不存在的卷返回 404', st == 404, 'HTTP %d' % st)

print('\n=========================================')
print('  结果：%d 通过 / %d 失败' % (PASS, FAIL))
print('=========================================')
sys.exit(1 if FAIL else 0)
