# -*- coding: utf-8 -*-
"""地理 2024 广东高考真题 端到端线上验证。
重点：真题结构（19题/100分/75分钟/选择16+非选择3）、答案声明诚实性、页面渲染层。
"""
import json, os, re, ssl, sys, time, urllib.request, urllib.error

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


PASS = FAIL = 0


def check(name, cond, detail=''):
    global PASS, FAIL
    if cond:
        PASS += 1
        print('  [PASS] %s%s' % (name, (' — ' + detail) if detail else ''))
    else:
        FAIL += 1
        print('  [FAIL] %s%s' % (name, (' — ' + detail) if detail else ''))


U = 'geogd%d' % int(time.time() % 100000)
DEV = 'e2e-device-geography-gd'

print('=== 步骤1：注册 ===')
st, r = req('POST', BASE + '/api/register', {'username': U, 'password': 'test123456', 'device': DEV})
check('注册成功', st == 200 and r.get('token'), 'HTTP %d' % st)
H = {'Authorization': 'Bearer ' + r.get('token', ''), 'X-Device': DEV}

print('\n=== 步骤2：/api/geography-gd 试卷列表 ===')
st, r = req('GET', BASE + '/api/geography-gd', headers=H)
check('返回 200', st == 200, 'HTTP %d' % st)
check('kind=real-paper（真题，非仿真卷）', r.get('kind') == 'real-paper', 'kind=%s' % r.get('kind'))
check('notice 声明「非官方标准答案」', '非官方标准答案' in (r.get('notice') or ''), (r.get('notice') or '')[:50])
papers = r.get('papers', [])
check('1 套真题', len(papers) == 1, '实际 %d' % len(papers))
if papers:
    p0 = papers[0]
    check('年份 2024', p0.get('year') == 2024, 'year=%s' % p0.get('year'))
    check('满分 100', p0.get('totalScore') == 100, '%s' % p0.get('totalScore'))
    check('时长 75 分钟', p0.get('durationMin') == 75, '%s' % p0.get('durationMin'))
    check('题量 19 题', p0.get('questionCount') == 19, '%s' % p0.get('questionCount'))
    print('       %s | %s分 %s分钟 %s题' % (p0.get('title'), p0.get('totalScore'), p0.get('durationMin'), p0.get('questionCount')))
struct = r.get('structure', [])
check('结构 2 段（48+52=100）', len(struct) == 2 and sum(s.get('score', 0) for s in struct) == 100,
      '分值=%s' % [s.get('score') for s in struct])

print('\n=== 步骤3：单卷详情（真题结构校验）===')
st, pp = req('GET', BASE + '/api/geography-gd?paper=gdgdz2024', headers=H)
check('返回 200', st == 200 and pp.get('id') == 'gdgdz2024', 'HTTP %d' % st)
check('examType 为广东选择性考试', '选择性考试' in (pp.get('examType') or ''), pp.get('examType'))
check('含真题来源链接', bool(pp.get('source')) and 'eol.cn' in pp['source'], (pp.get('source') or '')[:50])
mods = pp.get('modules', [])
qs = [q for m in mods for pt in m.get('parts', []) for q in pt.get('questions', [])]
total = sum(q.get('score', 0) for q in qs)
n_mc = sum(1 for q in qs if q.get('type') == 'single')
n_sub = sum(1 for q in qs if q.get('type') == 'subjective')
check('2 个大模块', len(mods) == 2, '实际 %d' % len(mods))
check('19 题（选择16+非选择3）', len(qs) == 19 and n_mc == 16 and n_sub == 3,
      '总%d 选择%d 非选择%d' % (len(qs), n_mc, n_sub))
check('总分 100', total == 100, '实际 %d' % total)
check('题号 1-19 连续', [q['no'] for q in qs] == list(range(1, 20)),
      '题号=%s' % [q['no'] for q in qs])

print('\n=== 步骤4：选择题答案与选项合法性 ===')
mcs = [q for q in qs if q['type'] == 'single']
bad = [q['no'] for q in mcs if not (0 <= q['answer'] < len(q['options']))]
check('答案索引合法', not bad, '异常题号=%s' % bad)
dup = [q['no'] for q in mcs if len(set(q['options'])) != 4]
check('无重复选项', not dup, '异常题号=%s' % dup)
noopt = [q['no'] for q in mcs if not q.get('options') or len(q['options']) != 4]
check('每题 4 个选项', not noopt, '异常题号=%s' % noopt)
# 答案分布：真题原卷的分布由命题决定，**不得为求均衡而改动真题答案**。
# 故此处只做「不极端」体检（每项至少 1 个，避免某选项从不出现在答案里导致学生蒙题失效），
# 不施加仿真卷那种「各≥N」的均衡要求。
import collections
dist = collections.Counter(q['answer'] for q in mcs)
print('       答案分布 A/B/C/D: %s（真题原卷分布，不做均衡改写）' % [dist.get(i, 0) for i in range(4)])
check('四个选项在答案中均至少出现 1 次', all(dist.get(i, 0) >= 1 for i in range(4)),
      '分布=%s' % [dist.get(i, 0) for i in range(4)])
check('分布不过度集中（单项占比 ≤ 60%）', max(dist.values()) / len(mcs) <= 0.6,
      '最高项 %d/%d' % (max(dist.values()), len(mcs)))
check('每题均有解析', all(q.get('analysis') for q in qs))

print('\n=== 步骤5：图表题已文字化 ===')
figs = [q for q in qs if q.get('figure')]
check('含图表说明的题 ≥5 道', len(figs) >= 5, '实际 %d 道' % len(figs))
for q in figs[:3]:
    print('       第%d题图表: %s' % (q['no'], q['figure'][:56]))
check('图表说明均较长（已文字化）', all(len(q['figure']) > 30 for q in figs),
      '最短=%d 字' % min(len(q['figure']) for q in figs))

print('\n=== 步骤6：非选择题含参考答案 ===')
subs = [q for q in qs if q['type'] == 'subjective']
check('3 道非选择题', len(subs) == 3, '实际 %d' % len(subs))
check('非选择题均有参考答案', all(q.get('answer') for q in subs))
for q in subs:
    print('       第%d题(%d分) 参考答案 %d 字' % (q['no'], q['score'], len(q['answer'])))

print('\n=== 步骤7：页面渲染层 ===')
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36'
try:
    rq = urllib.request.Request(BASE + '/geography', headers={'User-Agent': UA})
    with opener.open(rq, timeout=60) as resp:
        html = resp.read().decode('utf-8', 'ignore')
    check('geography 页面 200', True, 'HTTP 200')
    check('含「广东高考卷」Tab', '广东高考卷' in html)
    check('调用 /api/geography-gd', '/api/geography-gd' in html)
    check('含 renderGdPage 渲染器', 'renderGdPage' in html)
    # 上次教训：GD2.papers 必须有赋值，否则列表空白
    check('GD2.papers 已从接口赋值', 'GD2.papers = r.j.papers' in html)
    check('试卷卡片用 GD2.papers 渲染', 'GD2.papers.map' in html)
    check('点击处理器 openGdPaper 存在', 'openGdPaper' in html)
    # 状态字段有读有写
    g = re.search(r'板块：广东高考卷（真题）.*?// ================== 板块：题库组卷', html, re.S)
    check('GD 代码块可提取', g is not None)
    if g:
        blk = g.group(0)
        for f in ['meta', 'papers', 'cur', 'showKey', 'loaded']:
            w = len(re.findall(r'GD2\.' + f + r'\s*=', blk))
            r_ = len(re.findall(r'GD2\.' + f + r'\b(?!\s*=)', blk))
            check('GD2.%-7s 有读有写' % f, w >= 1 and r_ >= 1, '读=%d 写=%d' % (r_, w))
    # CSS 类名对账
    css = set(re.findall(r'\.(gd2-[a-z-]+)\s*\{', html))
    used = {t for u in re.findall(r'class="(gd2-[a-z- ]+)', html) for t in u.split()}
    missing = used - css
    check('gd2-* 类名 CSS 全部已定义', not missing, '缺失=%s' % sorted(missing))
    # 诚实性声明必须在页面上
    check('页面标注「非官方标准答案」', '非官方标准答案' in html)
    check('页面标注「真题原卷」', '真题原卷' in html)
except Exception as e:
    check('geography 页面可访问', False, str(e)[:60])

print('\n=== 步骤8：鉴权与 404 ===')
st, _ = req('GET', BASE + '/api/geography-gd')
check('未登录返回 401', st == 401, 'HTTP %d' % st)
st, _ = req('GET', BASE + '/api/geography-gd?paper=nope', headers=H)
check('不存在试卷返回 404', st == 404, 'HTTP %d' % st)

print('\n=========================================')
print('  结果：%d 通过 / %d 失败' % (PASS, FAIL))
print('=========================================')
sys.exit(1 if FAIL else 0)
