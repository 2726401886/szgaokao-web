# -*- coding: utf-8 -*-
"""化学模块端到端线上验证。
重点：三接口数据形状 + 化学特有回归（年级筛选须为 9-12，初中无七八年级化学）
     + 页面渲染层（状态字段审计 + CSS 类名对账）。
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
        h = {'Content-Type': 'application/json', 'User-Agent': 'e2e-chemistry'}
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


U = 'chemtest%d' % int(time.time() % 100000)
DEV = 'e2e-device-chemistry'

print('=== 步骤1：注册 ===')
st, r = req('POST', BASE + '/api/register', {'username': U, 'password': 'test123456', 'device': DEV})
check('注册成功', st == 200 and r.get('token'), 'HTTP %d' % st)
H = {'Authorization': 'Bearer ' + r.get('token', ''), 'X-Device': DEV}

print('\n=== 步骤2：/api/chemistry 知识点 ===')
st, r = req('GET', BASE + '/api/chemistry', headers=H)
check('返回 200', st == 200, 'HTTP %d' % st)
groups = (r.get('sections') or {}).get('knowledge', {}).get('groups', [])
check('5 个学段分组', len(groups) == 5, '实际 %d' % len(groups))
ti = sum(len(g.get('items', [])) for g in groups)
check('44 个知识点', ti == 44, '实际 %d' % ti)
tags = [g.get('grade_tag') for g in groups]
check('学段标签 初三~高二', tags == ['初三', '高一', '高一', '高二', '高二'], 'tags=%s' % tags)
for g in groups:
    print('       %-4s %s (%d项)' % (g['id'], g['title'], len(g.get('items', []))))
bad = [it['id'] for g in groups for it in g.get('items', []) if not (0 <= it['kao']['answer'] < len(it['kao']['options']))]
check('知识点自测答案索引合法', not bad, '异常=%s' % bad[:5])
check('知识点含 term/jieshi/kao', all('term' in it and 'jieshi' in it and 'kao' in it
                              for g in groups for it in g.get('items', [])))

print('\n=== 步骤3：/api/chemistry-exam 题库 ===')
st, r = req('GET', BASE + '/api/chemistry-exam', headers=H)
check('返回 200', st == 200, 'HTTP %d' % st)
qs = r.get('questions', [])
check('46 题', len(qs) == 46, '实际 %d' % len(qs))
check('total=46', r.get('total') == 46, 'total=%s' % r.get('total'))
check('topics 列表非空', isinstance(r.get('topics'), list) and len(r['topics']) > 20, 'topics=%d' % len(r.get('topics', [])))
grades = set(q.get('grade') for q in qs)
check('年级取值仅 9-12（化学从九年级开课）', grades == set([9, 10, 11, 12]), 'grades=%s' % sorted(grades))
types = set(q.get('type') for q in qs)
check('题型覆盖 choice/fill/read/write', types >= {'choice', 'fill', 'read', 'write'}, 'types=%s' % types)
bad = [q['id'] for q in qs
       if (q['type'] == 'choice' and not (0 <= q['answer'] < len(q['options'])))
       or (q['type'] == 'choice' and len(set(q['options'])) != 4)
       or (q['type'] == 'read' and any(not (0 <= s['answer'] < len(s['options'])) for s in q.get('questions', [])))]
check('答案索引合法且选项不重复', not bad, '异常=%s' % bad[:5])
import collections
dist = collections.Counter(q['answer'] for q in qs if q['type'] == 'choice')
print('       单选答案分布 A/B/C/D: %s' % [dist.get(i, 0) for i in range(4)])
check('答案分布均衡（各≥8）', all(dist.get(i, 0) >= 8 for i in range(4)),
      '分布=%s' % [dist.get(i, 0) for i in range(4)])
check('每题均有解析', all(q.get('analysis') for q in qs))

print('\n=== 步骤4：按年级筛选（化学关键回归：应只有 9-12 有题）===')
for g, lbl in [(9, '初三'), (10, '高一'), (11, '高二'), (12, '高三')]:
    st, rr = req('GET', BASE + '/api/chemistry-exam?grade=%d' % g, headers=H)
    n = len(rr.get('questions', []))
    check('grade=%d(%s) 筛选非空' % (g, lbl), st == 200 and n > 0, '%d 题' % n)
for g in (7, 8):
    st, rr = req('GET', BASE + '/api/chemistry-exam?grade=%d' % g, headers=H)
    n = len(rr.get('questions', []))
    check('grade=%d 返回 0 题（初中不开化学）' % g, n == 0, '%d 题' % n)

print('\n=== 步骤5：/api/chemistry-link 专题包 ===')
st, r = req('GET', BASE + '/api/chemistry-link', headers=H)
check('返回 200', st == 200, 'HTTP %d' % st)
units = r.get('units', [])
check('5 个专题单元', len(units) == 5, '实际 %d' % len(units))
ids = [u.get('id') for u in units]
check('单元 id 为 cl1~cl5', ids == ['cl1', 'cl2', 'cl3', 'cl4', 'cl5'], 'ids=%s' % ids)
st, u1 = req('GET', BASE + '/api/chemistry-link?unit=cl3', headers=H)
check('单单元详情 200', st == 200 and u1.get('id') == 'cl3', 'HTTP %d' % st)
check('含 points(3) 与 quiz(3)', len(u1.get('points', [])) == 3 and len(u1.get('quiz', [])) == 3,
      'points=%d quiz=%d' % (len(u1.get('points', [])), len(u1.get('quiz', []))))
st, _ = req('GET', BASE + '/api/chemistry-link?unit=cl999', headers=H)
check('不存在单元返回 404', st == 404, 'HTTP %d' % st)

print('\n=== 步骤6：页面渲染层 ===')
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36'
try:
    rq = urllib.request.Request(BASE + '/chemistry', headers={'User-Agent': UA})
    with opener.open(rq, timeout=60) as resp:
        html = resp.read().decode('utf-8', 'ignore')
    check('chemistry 页面 200', True, 'HTTP 200')
    check('含「知识点梳理」板块', '知识点梳理' in html)
    check('含「题库组卷」板块', '题库组卷' in html)
    check('含「专题突破」板块', '专题突破' in html)
    check('调用 /api/chemistry', '/api/chemistry' in html)
    check('调用 /api/chemistry-exam', '/api/chemistry-exam' in html)
    check('调用 /api/chemistry-link', '/api/chemistry-link' in html)
    check('含 renderKnowledgeRead 渲染器', 'renderKnowledgeRead' in html)
    check('PROG_KEY 为 chemistry_progress', 'chemistry_progress' in html)
    # init 赋值
    check('init 已将接口数据赋给 DATA', re.search(r'DATA\s*=\s*r\.j', html) is not None)
    m = re.search(r'function itemsOf\(g\) \{.*?\}', html, re.S)
    check('itemsOf 返回 g.items', bool(m) and 'g.items' in m.group(0))
    # 化学关键回归：年级筛选必须是 9-12，不得含 7/8 与初一初二
    check('年级筛选为 9-12（不含初一初二）', "'9', '10', '11', '12'" in html)
    check('无初一/初二标签', "'初一'" not in html and "'初二'" not in html)
    check('年级标签为 初三/高一/高二/高三', all(x in html for x in ['初三', '高一', '高二', '高三']))
    # 无地理/政治残留
    check('无 /api/geography 残留', '/api/geography' not in html)
    check('无 geography_progress 残留', 'geography_progress' not in html)
    check('无 renderGdPage 残留（化学无广东卷）', 'renderGdPage' not in html)
    # CSS 类名对账
    css = set(re.findall(r'\.([a-z][a-z0-9-]*)\s*\{', html))
    used = {t for u in re.findall(r'class="([a-z][a-z0-9 -]*)"', html) for t in u.split()}
    skip = {'on', 'ok', 'off', 'locked', 'right', 'wrong', 'picked', 'trial', 'empty', 'hide', 'active', 'card', 'msg', 'err'}
    missing = sorted(x for x in used - css - skip if '-' in x)
    check('CSS 类名全部已定义', not missing, '缺失=%s' % missing)
    # 无未定义关键函数
    defs = set(re.findall(r'function (\w+)\s*\(', html))
    calls = set(re.findall(r'\b(\w+)\s*\(', html))
    builtin = {'if', 'for', 'while', 'switch', 'catch', 'return', 'function', 'String', 'Number', 'Array',
               'Object', 'Math', 'JSON', 'parseInt', 'parseFloat', 'encodeURIComponent', 'isNaN',
               'setTimeout', 'fetch', 'Promise', 'Boolean'}
    undef = sorted(x for x in calls - defs - builtin
                   if re.match(r'^(render|load|open|bind|judge|mark|speak|nav|esc|api|mastered|init|build|select)', x))
    check('无「调用但未定义」的关键函数', not undef, '未定义=%s' % undef)
except Exception as e:
    check('chemistry 页面可访问', False, str(e)[:60])

print('\n=== 步骤7：首页含化学卡片 ===')
try:
    rq = urllib.request.Request(BASE + '/', headers={'User-Agent': UA})
    with opener.open(rq, timeout=60) as resp:
        home = resp.read().decode('utf-8', 'ignore')
    check('首页 200', True, 'HTTP 200')
    check('含 mod-chemistry 卡片', 'mod-chemistry' in home)
    check('含 go-chemistry 按钮', 'go-chemistry' in home)
    check('MODINFO 含 chemistry.html', 'chemistry.html' in home)
    check("forEach 含 'chemistry'", "'chemistry']" in home)
    check('hint 含化学体验说明', '初高中化学每个板块第 1 组' in home)
except Exception as e:
    check('首页可访问', False, str(e)[:60])

print('\n=== 步骤8：鉴权 ===')
st, _ = req('GET', BASE + '/api/chemistry')
check('未登录返回 401', st == 401, 'HTTP %d' % st)

print('\n=========================================')
print('  结果：%d 通过 / %d 失败' % (PASS, FAIL))
print('=========================================')
sys.exit(1 if FAIL else 0)
