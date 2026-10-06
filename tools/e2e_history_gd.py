# -*- coding: utf-8 -*-
"""初高中历史「广东高考卷」（结构仿真卷）端到端验证。
A. 本地数据完整性（data/history_gd.json）：6 套卷 / 16 单选 + 4 主观 / 100 分 / 答案合法 / 非真题声明
B. 线上冒烟：列表（trial 仅首套）、单卷、401、404、页面渲染层
用法：python tools/e2e_history_gd.py
"""
import collections, json, os, re, ssl, sys, time, urllib.request, urllib.error

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
D = json.load(open(os.path.join(ROOT, 'data', 'history_gd.json'), encoding='utf-8'))
papers = D['papers']
check('共 6 套仿真卷（2021–2026）', len(papers) == 6, '实际 %d' % len(papers))
check('年份集合正确', sorted(p['year'] for p in papers) == [2021, 2022, 2023, 2024, 2025, 2026])
check('kind=structural-mock', all(p['kind'] == 'structural-mock' for p in papers))
check('声明「非高考真题原卷」', '非高考真题原卷' in (D.get('notice') or ''))
check('声明「结构仿真卷」', '结构仿真卷' in (D.get('notice') or ''))
check('examType 为广东新高考I卷', '广东' in (D.get('examType') or ''), D.get('examType'))

for p in papers:
    qs = [q for m in p['modules'] for pt in m['parts'] for q in pt['questions']]
    singles = [q for q in qs if q['type'] == 'single']
    subs = [q for q in qs if q['type'] == 'subjective']
    total = sum(m['score'] for m in p['modules'])
    nos = [q['no'] for q in qs]
    bad = [q['no'] for q in singles if not (0 <= q['answer'] < len(q['options']))]
    n4 = [q['no'] for q in singles if len(q['options']) != 4]
    dup = [q['no'] for q in singles if len(set(q['options'])) != 4]
    no_ans = [q['no'] for q in subs if not q.get('answer')]
    no_ana = [q['no'] for q in qs if not q.get('analysis')]
    ok = (total == 100 and len(singles) == 16 and len(subs) == 4
          and nos == list(range(1, 21)) and not (bad or n4 or dup or no_ans or no_ana)
          and p['totalScore'] == 100 and p['durationMin'] == 75)
    d = collections.Counter(q['answer'] for q in singles)
    detail = '题%d 单选%d 主观%d 总分%d 时长%d 答案分布%s' % (
        len(qs), len(singles), len(subs), total, p['durationMin'], [d.get(i, 0) for i in range(4)])
    check('%d 卷结构正确（%s）' % (p['year'], p.get('theme', '')[:10]), ok, detail)
print('（A 段完）')

print('\n========== B. 线上冒烟 ==========')
PROXY = os.environ.get('HTTPS_PROXY') or os.environ.get('HTTP_PROXY') or 'http://127.0.0.1:60218'
BASE = 'https://szgaokao.toolshe.cn'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
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


U = 'hgd%d' % int(time.time() % 100000)
DEV = 'e2e-device-history-gd'
st, r = req('POST', BASE + '/api/register', {'username': U, 'password': 'test123456', 'device': DEV})
check('注册成功', st == 200 and r.get('token'), 'HTTP %d' % st)
H = {'Authorization': 'Bearer ' + r.get('token', ''), 'X-Device': DEV}

st, r = req('GET', BASE + '/api/history-gd', headers=H)
check('列表返回 200', st == 200, 'HTTP %d' % st)
if st == 200:
    is_trial = r.get('trial')
    n = len(r.get('papers', []))
    if is_trial:
        check('trial 仅开放第 1 套（2026）', n == 1 and r['papers'][0]['year'] == 2026,
              'papers=%d trial=%s' % (n, is_trial))
    else:
        check('全量返回 6 套（trial_open 体验期）', n == 6, 'papers=%d trial=%s' % (n, is_trial))
    check('返回 structure 供页面展示', len(r.get('structure', [])) > 0, 'structure=%d' % len(r.get('structure', [])))
    if r.get('papers'):
        p0 = r['papers'][0]
        check('首套为 2026', p0.get('year') == 2026, '%s' % p0.get('year'))
        check('列表项含 100分/75分钟/20题', p0.get('totalScore') == 100 and p0.get('durationMin') == 75 and p0.get('questionCount') == 20,
              '%s分 %s分钟 %s题' % (p0.get('totalScore'), p0.get('durationMin'), p0.get('questionCount')))
        print('       首套: %s | %s' % (p0.get('title'), p0.get('theme')))

st, pp = req('GET', BASE + '/api/history-gd?paper=hgdz2026', headers=H)
check('2026 单卷 200', st == 200 and pp.get('id') == 'hgdz2026', 'HTTP %d' % st)
if st == 200:
    qs = [q for m in pp['modules'] for pt in m['parts'] for q in pt['questions']]
    check('2026 单卷 20 题（16单选+4主观）', len(qs) == 20 and
          sum(1 for q in qs if q['type'] == 'single') == 16 and
          sum(1 for q in qs if q['type'] == 'subjective') == 4, '题%d' % len(qs))
    check('2026 单卷 100 分', sum(m['score'] for m in pp['modules']) == 100)
    check('2026 单卷含参考答案（非选择题）', all(q.get('answer') for q in qs if q['type'] == 'subjective'))

st, _ = req('GET', BASE + '/api/history-gd')
check('未登录 401', st == 401, 'HTTP %d' % st)
st, _ = req('GET', BASE + '/api/history-gd?paper=nope', headers=H)
check('不存在试卷 404', st == 404, 'HTTP %d' % st)

print('\n--- 页面渲染层 ---')
try:
    rq = urllib.request.Request(BASE + '/history', headers={'User-Agent': UA})
    with opener.open(rq, timeout=60) as resp:
        html = resp.read().decode('utf-8', 'ignore')
    check('history 页面 200', True)
    check('含「广东高考卷」Tab', '广东高考卷' in html)
    check('调用 /api/history-gd', '/api/history-gd' in html)
    check('GD2→GD.papers 已从接口赋值', 'GD.papers = r.j.papers' in html)
    check('试卷卡片用 GD.papers 渲染', 'GD.papers.map' in html)
    check('含 openGdPaper 点击处理器', 'openGdPaper' in html)
    check('含 renderGdQuestion 渲染器', 'renderGdQuestion' in html)
    for f in ['meta', 'papers', 'cur', 'showKey', 'loaded']:
        w = len(re.findall(r'GD\.' + f + r'\s*=', html))
        r_ = len(re.findall(r'GD\.' + f + r'\b(?!\s*=)', html))
        check('GD.%-8s 有读有写' % f, w >= 1 and r_ >= 1, '读=%d 写=%d' % (r_, w))
    css = set(re.findall(r'\.(gd-[a-z-]+)\s*\{', html))
    used = {t for u in re.findall(r'class="(gd-[a-z- ]+)', html) for t in u.split()}
    # ok/bad/right/wrong/picked/locked 为 .gd-x.y 复合修饰类，不计缺失
    missing = {t for t in used if t.startswith('gd-')} - css
    check('gd-* 类名 CSS 全部已定义', not missing, '缺失=%s' % sorted(missing))
    check('页面标注「非真题原卷」', '非真题原卷' in html)
except Exception as e:
    check('history 页面可访问', False, str(e)[:60])

print('\n=========================================')
print('  结果：%d 通过 / %d 失败' % (PASS, FAIL))
print('=========================================')
sys.exit(1 if FAIL else 0)
