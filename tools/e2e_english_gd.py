# -*- coding: utf-8 -*-
"""广东高考英语真题（2021–2026）端到端验证。
两部分：
  A. 本地数据完整性（data/english_gd.json）：6 套卷结构 / 题型统计 / 答案合法 / 非官方声明。
  B. 线上冒烟：列表（trial 仅首套）、单卷、鉴权 401、404、页面渲染层。
  说明：2021–2024 为官方原版真题原文；2025–2026 为考生回忆整理版（均非官方标准答案，听力无音频）。
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
D = json.load(open(os.path.join(ROOT, 'data', 'english_gd.json'), encoding='utf-8'))
papers = D['papers']
check('共 6 套真题（2021–2026）', len(papers) == 6, '实际 %d' % len(papers))
check('年份集合正确', sorted(p['year'] for p in papers) == [2021, 2022, 2023, 2024, 2025, 2026])
check('顶层 kind=real-paper', D.get('kind') == 'real-paper')
check('meta 声明「非官方标准答案」', '非官方标准答案' in (D.get('notice') or ''))
check('meta 声明「听力无音频」', '听力无音频' in (D.get('notice') or ''))

EXPECT_KIND = {2021: 'real-paper', 2022: 'real-paper', 2023: 'real-paper', 2024: 'real-paper', 2025: 'recalled', 2026: 'recalled'}
for p in papers:
    qs = [q for m in p['modules'] for pt in m['parts'] for q in pt['questions']]
    n_listen = sum(1 for q in qs if q['type'] == 'listen')
    n_essay = sum(1 for q in qs if q['type'] == 'essay')
    n_seven = sum(1 for m in p['modules'] for pt in m['parts'] for q in pt['questions'] if '七选五' in pt['name'])
    n_single = sum(1 for q in qs if q['type'] == 'single')
    n_fill = sum(1 for q in qs if q['type'] == 'fill')
    bad = []
    for q in qs:
        if q['type'] == 'listen':
            if not (0 <= q['answer'] <= 2): bad.append(('listen', q['no'], q['answer']))
            if q['options'] and not (0 <= q['answer'] < len(q['options'])): bad.append(('listenOpt', q['no']))
        if q['type'] == 'single' and q['options']:
            if not (0 <= q['answer'] < len(q['options'])): bad.append(('singleOpt', q['no'], q['answer'], len(q['options'])))
    ok_total = p['totalScore'] == 150
    ok_dur = p['durationMin'] == 120
    ok_types = (n_listen == 20 and n_seven == 5 and n_essay == 2)
    ok_no = len(qs) == len(set(q['no'] for q in qs))
    ok_kind = p['kind'] == EXPECT_KIND[p['year']]
    detail = '题%d 听力%d 单选%d 七选五%d 填空%d 写作%d 总分%d 时长%d kind=%s' % (
        len(qs), n_listen, n_single, n_seven, n_fill, n_essay, p['totalScore'], p['durationMin'], p['kind'])
    check('%d 卷结构正确' % p['year'], ok_total and ok_dur and ok_types and ok_no and ok_kind and not bad, detail)

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
        h = {'Content-Type': 'application/json', 'User-Agent': 'e2e-english-gd'}
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


U = 'engd%d' % int(time.time() % 100000)
DEV = 'e2e-device-english-gd'
st, r = req('POST', BASE + '/api/register', {'username': U, 'password': 'test123456', 'device': DEV})
check('注册成功', st == 200 and r.get('token'), 'HTTP %d' % st)
H = {'Authorization': 'Bearer ' + r.get('token', ''), 'X-Device': DEV}

st, r = req('GET', BASE + '/api/english-gd', headers=H)
check('列表返回 200', st == 200, 'HTTP %d' % st)
if st == 200:
    is_trial = r.get('trial')
    n = len(r.get('papers', []))
    if is_trial:
        check('trial 仅开放第 1 套（2026）', n == 1 and r['papers'][0]['year'] == 2026, 'papers=%d trial=%s' % (n, is_trial))
    else:
        check('全量返回 6 套（trial_open 体验期）', n == 6, 'papers=%d trial=%s' % (n, is_trial))
    if r.get('papers'):
        p0 = r['papers'][0]
        check('首套为 2026', p0.get('year') == 2026, '%s' % p0.get('year'))
        print('       首套: %s | %s分 %s分钟 %s题 kind=%s trial=%s' % (
            p0.get('title'), p0.get('totalScore'), p0.get('durationMin'), p0.get('questionCount'), p0.get('kind'), is_trial))

st, pp = req('GET', BASE + '/api/english-gd?paper=gdeng2026', headers=H)
check('2026 单卷 200', st == 200 and pp.get('id') == 'gdeng2026', 'HTTP %d' % st)
if st == 200:
    qs = [q for m in pp['modules'] for pt in m['parts'] for q in pt['questions']]
    check('2026 单卷 150分/题数>0', pp['totalScore'] == 150 and len(qs) > 0, '总分=%s 题=%s' % (pp.get('totalScore'), len(qs)))
    check('2026 单卷 含 七选五 5 题', any('七选五' in pt['name'] for m in pp['modules'] for pt in m['parts']) and
          sum(1 for m in pp['modules'] for pt in m['parts'] for q in pt['questions'] if '七选五' in pt['name']) == 5)

st, _ = req('GET', BASE + '/api/english-gd')
check('未登录 401', st == 401, 'HTTP %d' % st)
st, _ = req('GET', BASE + '/api/english-gd?paper=nope', headers=H)
check('不存在试卷 404', st == 404, 'HTTP %d' % st)

print('\n--- 页面渲染层 ---')
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36'
try:
    rq = urllib.request.Request(BASE + '/english-gd', headers={'User-Agent': UA})
    with opener.open(rq, timeout=60) as resp:
        html = resp.read().decode('utf-8', 'ignore')
    check('english-gd 页面 200', True)
    check('含「广东高考英语」标题', '广东高考英语' in html)
    check('调用 /api/english-gd', '/api/english-gd' in html)
    check('EG.papers 已从接口赋值', 'EG.papers = r.j.papers' in html)
    check('试卷卡片用 EG.papers 渲染', 'EG.papers.map' in html)
    check('含 openPaper 点击处理器', 'openPaper' in html)
    check('含 renderQuestion 渲染器', 'renderQuestion' in html)
    check('含 revealEg 展开（填空/范文）', 'revealEg' in html)
    for f in ['meta', 'papers', 'cur', 'showKey']:
        w = len(re.findall(r'EG\.' + f + r'\s*=', html))
        r_ = len(re.findall(r'EG\.' + f + r'\b(?!\s*=)', html))
        check('EG.%-8s 有读有写' % f, w >= 1 and r_ >= 1, '读=%d 写=%d' % (r_, w))
    css = set(re.findall(r'\.(gd2-[a-z-]+)\s*\{', html))
    used = {t for u in re.findall(r'class="(gd2-[a-z- ]+)', html) for t in u.split()}
    # 仅校验 gd2- 前缀类名；ok/bad/picked/locked 等为 .gd2-x.y 复合修饰类，不计缺失
    missing = {t for t in used if t.startswith('gd2-')} - css
    check('gd2-* 类名 CSS 全部已定义', not missing, '缺失=%s' % sorted(missing))
    check('页面标注「非官方标准答案」', '非官方标准答案' in html)
    check('页面标注「听力无音频」', '听力无音频' in html)
except Exception as e:
    check('english-gd 页面可访问', False, str(e)[:60])

print('\n=========================================')
print('  结果：%d 通过 / %d 失败' % (PASS, FAIL))
print('=========================================')
sys.exit(1 if FAIL else 0)
