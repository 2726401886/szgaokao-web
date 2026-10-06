# -*- coding: utf-8 -*-
"""高中语文「课外阅读拓展专题」（4 专题 × 20 题）端到端验证。
  A. 本地数据完整性（data/hchinese_kwd.json）：4 专题结构 / 单选答案合法 / 主观有参考答案。
  B. 线上冒烟：列表（trial 仅首专题）、单专题、鉴权 401、404、页面渲染层。
"""
import json, os, re, ssl, sys, time, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASS = FAIL = 0


def check(name, cond, detail=''):
    global PASS, FAIL
    if cond:
        PASS += 1
        print('  [PASS] %s%s' % (name, (' — ' + detail) if detail else ''))
    else:
        FAIL += 1
        print('  [FAIL] %s%s' % (name, (' — ' + detail) if detail else ''))


print('========== A. 本地数据完整性 ==========')
D = json.load(open(os.path.join(ROOT, 'data', 'hchinese_kwd.json'), encoding='utf-8'))
units = D['units']
check('共 4 个专题', len(units) == 4, '实际 %d' % len(units))
check('专题 id 唯一且齐全', [u['id'] for u in units] == ['zt1', 'zt2', 'zt3', 'zt4'])
check('notice/structure 存在', bool(D.get('notice')) and bool(D.get('structure')))
for u in units:
    qs = [q for s in u['sections'] for q in s['questions']]
    n_ch = sum(1 for q in qs if q['type'] == 'choice')
    n_sh = sum(1 for q in qs if q['type'] == 'subjective')
    total = sum(len(s['questions']) for s in u['sections'])
    bad = [q['no'] for q in qs if q['type'] == 'choice' and not (0 <= q['answer'] < len(q['options']))]
    n4 = [q['no'] for q in qs if q['type'] == 'choice' and len(q['options']) != 4]
    no_sh_ans = [q['no'] for q in qs if q['type'] == 'subjective' and not q.get('answer')]
    # 每节编号唯一
    sec_ok = all(len(s['questions']) == len(set(q['no'] for q in s['questions'])) for s in u['sections'])
    ok = (n_ch == 10 and n_sh == 10 and total == 20 and u['questionCount'] == 20
          and not bad and not n4 and not no_sh_ans and sec_ok)
    detail = '题%d 单选%d 主观%d 单选答案合法=%s 主观有答案=%s' % (total, n_ch, n_sh, not bad, not no_sh_ans)
    check('%s 结构正确（%s）' % (u['no'], u['title'][:12]), ok, detail)
print('（A 段完）')

print('\n========== B. 线上冒烟 ==========')
PROXY = os.environ.get('HTTPS_PROXY') or os.environ.get('HTTP_PROXY') or 'http://127.0.0.1:60218'
BASE = 'https://szgaokao.toolshe.cn'
opener = urllib.request.build_opener(
    urllib.request.ProxyHandler({'http': PROXY, 'https': PROXY}),
    urllib.request.HTTPSHandler(context=ssl.create_default_context()))


def req(method, url, data=None, headers=None, retry=3):
    for a in range(retry):
        body = json.dumps(data).encode() if data is not None else None
        h = {'Content-Type': 'application/json', 'User-Agent': 'e2e-hchinese-kwd'}
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


U = 'hkwd%d' % int(time.time() % 100000)
DEV = 'e2e-device-hchinese-kwd'
st, r = req('POST', BASE + '/api/register', {'username': U, 'password': 'test123456', 'device': DEV})
check('注册成功', st == 200 and r.get('token'), 'HTTP %d' % st)
H = {'Authorization': 'Bearer ' + r.get('token', ''), 'X-Device': DEV}

st, r = req('GET', BASE + '/api/hchinese-kwd', headers=H)
check('列表返回 200', st == 200, 'HTTP %d' % st)
if st == 200:
    is_trial = r.get('trial')
    n = len(r.get('units', []))
    if is_trial:
        check('trial 仅开放第 1 专题（zt1）', n == 1 and r['units'][0]['id'] == 'zt1', 'units=%d trial=%s' % (n, is_trial))
    else:
        check('全量返回 4 专题（trial_open 体验期）', n == 4, 'units=%d trial=%s' % (n, is_trial))
    if r.get('units'):
        u0 = r['units'][0]
        check('首专题为 zt1', u0.get('id') == 'zt1', '%s' % u0.get('id'))
        print('       首专题: %s %s | %s题' % (u0.get('no'), u0.get('title'), u0.get('questionCount')))

st, up = req('GET', BASE + '/api/hchinese-kwd?unit=zt1', headers=H)
check('zt1 单专题 200', st == 200 and up.get('id') == 'zt1', 'HTTP %d' % st)
if st == 200:
    qs = [q for s in up['sections'] for q in s['questions']]
    check('zt1 单专题 20 题（10单选+10主观）', len(qs) == 20 and
          sum(1 for q in qs if q['type'] == 'choice') == 10 and
          sum(1 for q in qs if q['type'] == 'subjective') == 10, '题%d' % len(qs))

st, _ = req('GET', BASE + '/api/hchinese-kwd')
check('未登录 401', st == 401, 'HTTP %d' % st)
st, _ = req('GET', BASE + '/api/hchinese-kwd?unit=nope', headers=H)
check('不存在专题 404', st == 404, 'HTTP %d' % st)

print('\n--- 页面渲染层 ---')
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36'
try:
    rq = urllib.request.Request(BASE + '/hchinese', headers={'User-Agent': UA})
    with opener.open(rq, timeout=60) as resp:
        html = resp.read().decode('utf-8', 'ignore')
    check('hchinese 页面 200', True)
    check('含「课外阅读拓展」Tab', '课外阅读拓展' in html)
    check('调用 /api/hchinese-kwd', '/api/hchinese-kwd' in html)
    check('含 renderKwdPage 渲染器', 'renderKwdPage' in html)
    check('含 openKwdUnit 点击处理器', 'openKwdUnit' in html)
    check("SECTIONS 含 k: 'kwd'", "k: 'kwd'" in html)
    check('含 .gd-box CSS', '.gd-box' in html)
except Exception as e:
    check('hchinese 页面可访问', False, str(e)[:60])

print('\n=========================================')
print('  结果：%d 通过 / %d 失败' % (PASS, FAIL))
print('=========================================')
sys.exit(1 if FAIL else 0)
