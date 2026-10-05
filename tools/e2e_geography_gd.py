# -*- coding: utf-8 -*-
"""地理 广东高考真题（2021–2024）端到端验证。
两部分：
  A. 本地数据完整性（data/geography_gd.json）：4 套卷结构 / 答案合法 / 选考模块等。
  B. 线上冒烟：列表（trial 仅首套）、单卷、鉴权 401、404、页面渲染层。
"""
import json, os, re, ssl, sys, time, urllib.request, urllib.error, collections

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
D = json.load(open(os.path.join(ROOT, 'data', 'geography_gd.json'), encoding='utf-8'))
papers = D['papers']
check('共 4 套真题（2021–2024）', len(papers) == 4, '实际 %d' % len(papers))
check('年份集合正确', sorted(p['year'] for p in papers) == [2021, 2022, 2023, 2024])
check('kind=real-paper', all(p['kind'] == 'real-paper' for p in papers))
check('meta 声明「非官方标准答案」', '非官方标准答案' in (D.get('notice') or ''))

EXPECT_SUBJ = {2021: 4, 2022: 4, 2023: 3, 2024: 3}   # 含选考（二选一）的题数
EXPECT_OPT = {2021: True, 2022: True, 2023: False, 2024: False}
for p in papers:
    qs = [q for m in p['modules'] for pt in m['parts'] for q in pt['questions']]
    # 总分按「模块计分」核算：选考为二选一，模块计 10 分（非两题相加）
    total = sum(m['score'] for m in p['modules'])
    n_mc = sum(1 for q in qs if q['type'] == 'single')
    n_sub = sum(1 for q in qs if q['type'] == 'subjective')
    mod_names = [m['name'] for m in p['modules']]
    has_opt = any('选考' in n for n in mod_names)
    yrs = p['year']
    ok_total = total == 100
    ok_mc = n_mc == 16
    ok_subj = n_sub == EXPECT_SUBJ[yrs]
    ok_opt = has_opt == EXPECT_OPT[yrs]
    ok_no = [q['no'] for q in qs] == list(range(1, len(qs) + 1))
    detail = '题%d 选择%d 非选择%d 总分%d 选考=%s' % (len(qs), n_mc, n_sub, total, has_opt)
    check('%d 卷结构正确' % yrs, ok_total and ok_mc and ok_subj and ok_opt and ok_no, detail)

    # 答案合法性 + 选项无重复 + 每题4选项
    mcs = [q for q in qs if q['type'] == 'single']
    bad = [q['no'] for q in mcs if not (0 <= q['answer'] < len(q['options']))]
    dup = [q['no'] for q in mcs if len(set(q['options'])) != 4]
    n4 = [q['no'] for q in mcs if len(q['options']) != 4]
    check('%d 选择题答案/选项合法' % yrs, not (bad or dup or n4),
          'bad=%s dup=%s n4=%s' % (bad, dup, n4))
    # 答案分布：真题原卷分布，不做均衡改写，仅做「不极端」体检
    dist = collections.Counter(q['answer'] for q in mcs)
    check('%d 答案四选项均出现且不过度集中' % yrs,
          all(dist.get(i, 0) >= 1 for i in range(4)) and max(dist.values()) / len(mcs) <= 0.6,
          '分布=%s' % [dist.get(i, 0) for i in range(4)])
    # 每题有解析、图表题文字化、非选择有参考答案
    no_an = [q['no'] for q in qs if not q.get('analysis')]
    check('%d 每题均有解析' % yrs, not no_an, '缺=%s' % no_an)
    figs = [q for q in qs if q.get('figure')]
    # 2024 源自试卷图片（图表多）；2021–2023 为用户文字稿，图表按材料描述补 2–3 条。
    # 此处只要求「有图表说明且均充分文字化」，不做数量硬门槛。
    check('%d 含图表文字化说明' % yrs, len(figs) >= 2 and all(len(q['figure']) > 25 for q in figs),
          '图表题=%d' % len(figs))
    subs = [q for q in qs if q['type'] == 'subjective']
    check('%d 非选择题均有参考答案' % yrs, all(q.get('answer') for q in subs))
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
        h = {'Content-Type': 'application/json', 'User-Agent': 'e2e-geography-gd'}
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


U = 'geogd%d' % int(time.time() % 100000)
DEV = 'e2e-device-geography-gd'
st, r = req('POST', BASE + '/api/register', {'username': U, 'password': 'test123456', 'device': DEV})
check('注册成功', st == 200 and r.get('token'), 'HTTP %d' % st)
H = {'Authorization': 'Bearer ' + r.get('token', ''), 'X-Device': DEV}

st, r = req('GET', BASE + '/api/geography-gd', headers=H)
check('列表返回 200', st == 200, 'HTTP %d' % st)
check('trial 仅开放第 1 套（2024）', st == 200 and len(r.get('papers', [])) == 1 and r['papers'][0]['year'] == 2024,
      'papers=%d' % len(r.get('papers', [])))
if st == 200 and r.get('papers'):
    p0 = r['papers'][0]
    check('首套 19 题', p0.get('questionCount') == 19, '%s' % p0.get('questionCount'))
    print('       首套: %s | %s分 %s分钟 %s题' % (p0.get('title'), p0.get('totalScore'), p0.get('durationMin'), p0.get('questionCount')))

st, pp = req('GET', BASE + '/api/geography-gd?paper=gdgdz2024', headers=H)
check('2024 单卷 200', st == 200 and pp.get('id') == 'gdgdz2024', 'HTTP %d' % st)
if st == 200:
    qs = [q for m in pp['modules'] for pt in m['parts'] for q in pt['questions']]
    check('2024 单卷 19 题/100分', len(qs) == 19 and sum(q['score'] for q in qs) == 100)

st, _ = req('GET', BASE + '/api/geography-gd')
check('未登录 401', st == 401, 'HTTP %d' % st)
st, _ = req('GET', BASE + '/api/geography-gd?paper=nope', headers=H)
check('不存在试卷 404', st == 404, 'HTTP %d' % st)

print('\n--- 页面渲染层 ---')
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36'
try:
    rq = urllib.request.Request(BASE + '/geography', headers={'User-Agent': UA})
    with opener.open(rq, timeout=60) as resp:
        html = resp.read().decode('utf-8', 'ignore')
    check('geography 页面 200', True)
    check('含「广东高考卷」Tab', '广东高考卷' in html)
    check('调用 /api/geography-gd', '/api/geography-gd' in html)
    check('GD2.papers 已从接口赋值', 'GD2.papers = r.j.papers' in html)
    check('试卷卡片用 GD2.papers 渲染', 'GD2.papers.map' in html)
    check('含 openGdPaper 点击处理器', 'openGdPaper' in html)
    g = re.search(r'板块：广东高考卷（真题）.*?// ================== 板块：题库组卷', html, re.S)
    if g:
        blk = g.group(0)
        for f in ['meta', 'papers', 'cur', 'showKey', 'loaded']:
            w = len(re.findall(r'GD2\.' + f + r'\s*=', blk))
            r_ = len(re.findall(r'GD2\.' + f + r'\b(?!\s*=)', blk))
            check('GD2.%-7s 有读有写' % f, w >= 1 and r_ >= 1, '读=%d 写=%d' % (r_, w))
    css = set(re.findall(r'\.(gd2-[a-z-]+)\s*\{', html))
    used = {t for u in re.findall(r'class="(gd2-[a-z- ]+)', html) for t in u.split()}
    missing = used - css
    check('gd2-* 类名 CSS 全部已定义', not missing, '缺失=%s' % sorted(missing))
    check('页面标注「非官方标准答案」', '非官方标准答案' in html)
    check('页面标注「真题原卷」', '真题原卷' in html)
except Exception as e:
    check('geography 页面可访问', False, str(e)[:60])

print('\n=========================================')
print('  结果：%d 通过 / %d 失败' % (PASS, FAIL))
print('=========================================')
sys.exit(1 if FAIL else 0)
