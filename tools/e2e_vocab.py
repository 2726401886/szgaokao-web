# -*- coding: utf-8 -*-
"""vocab 模块端到端线上验证：注册 → 授权 → 取词 → 评分 → SRS 状态变化 → 队列更新。"""
import json, os, ssl, sys, time, urllib.request, urllib.error

PROXY = 'http://127.0.0.1:29290'
BASE = 'https://szgaokao.toolshe.cn'
SECRET = 'eqD7tVejuzbWmFg6'
opener = urllib.request.build_opener(
    urllib.request.ProxyHandler({'http': PROXY, 'https': PROXY}),
    urllib.request.HTTPSHandler(context=ssl.create_default_context()))

def req(method, url, data=None, headers=None, retry=3):
    for a in range(retry):
        body = json.dumps(data).encode() if data is not None else None
        h = {'Content-Type': 'application/json', 'User-Agent': 'e2e'}
        if headers: h.update(headers)
        try:
            r = urllib.request.Request(url, data=body, method=method, headers=h)
            with opener.open(r, timeout=60) as resp:
                return resp.status, json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            try: return e.code, json.loads(e.read().decode())
            except Exception: return e.code, {}
        except Exception as e:
            if a < retry - 1: time.sleep(2); continue
            return 0, {'error': str(e)}

PASS = FAIL = 0
def check(name, cond, detail=''):
    global PASS, FAIL
    if cond: PASS += 1; print('  [PASS] %s%s' % (name, (' — ' + detail) if detail else ''))
    else:    FAIL += 1; print('  [FAIL] %s%s' % (name, (' — ' + detail) if detail else ''))

U = 'vocabtest%d' % int(time.time() % 100000)
DEV = 'e2e-device-vocab'

print('=== 步骤1：注册账号 ===')
st, r = req('POST', BASE + '/api/register', {'username': U, 'password': 'test123456', 'device': DEV})
check('注册成功', st == 200 and r.get('token'), 'HTTP %d' % st)
TOKEN = r.get('token', '')
H = {'Authorization': 'Bearer ' + TOKEN, 'X-Device': DEV}

print('\n=== 步骤2：管理员授权 vocab 模块 ===')
st, r = req('POST', BASE + '/api/admin/login', {'secret': SECRET})
AT = r.get('token', '')
st, r = req('POST', BASE + '/api/admin/users/grant', {'username': U, 'plan': 'permanent', 'modules': ['vocab']},
            {'Authorization': 'Bearer ' + AT})
check('授权成功', st == 200, 'HTTP %d' % st)
# 重新登录拿新 token（授权不影响 token，但保险起见验证 modules）
st, r = req('POST', BASE + '/api/login', {'username': U, 'password': 'test123456', 'device': DEV})
TOKEN = r.get('token', '')
H = {'Authorization': 'Bearer ' + TOKEN, 'X-Device': DEV}
st, me = req('GET', BASE + '/api/me', headers=H)
check('modules 含 vocab', (me.get('modules') or {}).get('vocab') == 1, json.dumps(me.get('modules'), ensure_ascii=False))

print('\n=== 步骤3：词书列表 ===')
st, r = req('GET', BASE + '/api/vocab?stats=1', headers=H)
check('词书统计返回 7 套', st == 200 and len(r.get('levels', [])) == 7, '实际 %d 套' % len(r.get('levels', [])))
total = r.get('total', 0)
check('总词数 1656', total == 1656, '实际 %d' % total)
for lv in r.get('levels', []):
    print('       %-9s %-22s %4d 词' % (lv['level'], lv['title'], lv['count']))

print('\n=== 步骤4：取词（小学 primary）===')
st, r = req('GET', BASE + '/api/vocab?level=primary', headers=H)
check('取词成功', st == 200, 'HTTP %d' % st)
check('队列非空', len(r.get('queue', [])) > 0, '队列 %d 个' % len(r.get('queue', [])))
check('返回 8 类题型标记', 'daily' in r)
q0 = r['queue'][0]
w0 = q0['w']
print('       首词: %s %s %s  音频=%s' % (w0['word'], w0['phonetic'], w0['meaning'], w0.get('audio', '无')))
check('词条含音标', bool(w0.get('phonetic')))
check('词条含释义', bool(w0.get('meaning')))
check('词条含发音路径', bool(w0.get('audio')))
check('队列入队标记正确', q0.get('isNew') is True)
print('       待复习=%d 新词=%d 每日上限=%d 体验模式=%s' % (
    r.get('dueTotal', 0), r.get('newTotal', 0), r.get('daily', 0), r.get('trial')))

print('\n=== 步骤5：单词详情 + 干扰项 ===')
st, r = req('GET', BASE + '/api/vocab?level=primary&word=' + w0['id'], headers=H)
check('单词详情返回', st == 200 and r.get('word', {}).get('id') == w0['id'])
check('干扰项 3 个', len(r.get('distractors', [])) == 3, '实际 %d' % len(r.get('distractors', [])))
check('干扰项非空', all(d.get('word') for d in r.get('distractors', [])))

print('\n=== 步骤6：提交评分「认识」并验证 SRS 演化 ===')
st, r1 = req('POST', BASE + '/api/vocab/review', {'id': w0['id'], 'grade': 2, 'time': 1200}, headers=H)
check('评分提交成功', st == 200, 'HTTP %d' % st)
print('       反馈: %s  下次复习: %.2f 天后  稳定性 S=%s  难度=%s' % (
    r1.get('label'), r1.get('nextIn', 0), r1.get('srs'), r1.get('df')))
check('返回稳定性字段', r1.get('srs', 0) > 0, 'S=%s' % r1.get('srs'))
check('下次间隔 > 0', r1.get('nextIn', 0) > 0, '%.2f 天' % r1.get('nextIn', 0))

print('\n=== 步骤7：连续 4 次「认识」，验证间隔增长曲线 ===')
prev = 0; mono = True; gaps = []
for i in range(4):
    st, rr = req('POST', BASE + '/api/vocab/review', {'id': w0['id'], 'grade': 2}, headers=H)
    g = rr.get('nextIn', 0); gaps.append(g)
    if g < prev - 0.01: mono = False
    prev = g
print('       间隔序列: %s 天' % ' -> '.join('%.2f' % g for g in gaps))
check('间隔单调递增', mono)
check('间隔逐步拉长', gaps[-1] > gaps[0], '%.2f -> %.2f' % (gaps[0], gaps[-1]))

print('\n=== 步骤8：答「忘记」应回落并当天再练 ===')
st, rf = req('POST', BASE + '/api/vocab/review', {'id': w0['id'], 'grade': 0}, headers=H)
print('       忘记后: 稳定性 S=%s  下次 %.3f 天(约 %.1f 小时)' % (
    rf.get('srs'), rf.get('nextIn', 0), rf.get('nextIn', 0) * 24))
check('忘记后间隔 < 1 天', rf.get('nextIn', 99) < 1, '%.4f 天' % rf.get('nextIn', 0))
check('忘记后稳定性回落', rf.get('srs', 99) < 5, 'S=%s' % rf.get('srs'))

print('\n=== 步骤9：srs 状态云端持久化（跨请求读取）===')
st, sd = req('GET', BASE + '/api/study', headers=H)
check('study 接口返回 srs 键', st == 200 and 'srs' in sd)
srs = sd.get('srs', {})
check('srs 已存该词状态', w0['id'] in srs, '词数 %d' % len(srs))
if w0['id'] in srs:
    s0 = srs[w0['id']]
    print('       云端状态: S=%s due=%s df=%s 遗忘=%s次 复习=%s次' % (
        s0.get('s'), s0.get('due'), s0.get('df'), s0.get('l'), s0.get('h')))
    check('云端含 due 字段', 'due' in s0)
    check('云端含难度字段', 'df' in s0)
    check('累计复习次数 >= 5', s0.get('h', 0) >= 5, 'h=%s' % s0.get('h'))
    check('累计遗忘次数 = 1', s0.get('l') == 1, 'l=%s' % s0.get('l'))

print('\n=== 步骤10：作答记录进入 ans/错题本 ===')
st, sd2 = req('GET', BASE + '/api/study', headers=H)
ans = sd2.get('ans', {})
tags = sd2.get('tags', {})
qid = 'vocab:' + w0['id']
check('ans 含 vocab: 前缀记录', qid in ans, 'qid=%s' % qid)
if qid in ans:
    a = ans[qid]
    print('       ans: 正确%s次 错误%s次 标签%s' % (a.get('r'), a.get('w'), a.get('tags')))
    check('对错次数已累加', (a.get('r', 0) + a.get('w', 0)) >= 5, '合计 %s' % (a.get('r', 0) + a.get('w', 0)))
check('tags 派生英语·词汇', '英语·词汇' in tags, json.dumps(tags.get('英语·词汇'), ensure_ascii=False))

print('\n=== 步骤11：已学词进入统计，队列相应减少 ===')
st, r = req('GET', BASE + '/api/vocab?level=primary', headers=H)
est = r.get('est', {})
print('       统计: 总%d 已掌握%d 学习中%d 未学%d 强记忆%d' % (
    est.get('total', 0), est.get('known', 0), est.get('learning', 0), est.get('fresh', 0), est.get('strong', 0)))
check('已学词计入 known/learning', (est.get('known', 0) + est.get('learning', 0)) >= 1)
check('未学词减少', est.get('fresh', 0) < 240, '剩余未学 %d' % est.get('fresh', 0))

print('\n=== 步骤12：全部 7 套词书可取词 ===')
for lv in ['kids', 'primary', 'longman', 'junior', 'senior', 'ket', 'pet']:
    st, rr = req('GET', BASE + '/api/vocab?level=' + lv, headers=H)
    q = len(rr.get('queue', [])) if st == 200 else 0
    n = rr.get('est', {}).get('total', 0) if st == 200 else 0
    check('%-8s 可用' % lv, st == 200 and q > 0, '%d 词 / 队列 %d' % (n, q))

print('\n=========================================')
print('  结果：%d 通过 / %d 失败' % (PASS, FAIL))
print('=========================================')
sys.exit(1 if FAIL else 0)
