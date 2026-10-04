# -*- coding: utf-8 -*-
"""诊断 primary 词书队列返回 0 的问题（带重试，区分真实缺陷与代理抖动）"""
import json, ssl, time, urllib.request, urllib.error

PROXY = 'http://127.0.0.1:29290'
BASE = 'https://szgaokao.toolshe.cn'
SECRET = 'eqD7tVejuzbWmFg6'
opener = urllib.request.build_opener(
    urllib.request.ProxyHandler({'http': PROXY, 'https': PROXY}),
    urllib.request.HTTPSHandler(context=ssl.create_default_context()))

def req(method, url, data=None, headers=None, retry=3):
    for a in range(retry):
        body = json.dumps(data).encode() if data is not None else None
        h = {'Content-Type': 'application/json', 'User-Agent': 'diag'}
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

U = 'vdiag%d' % int(time.time() % 100000)
DEV = 'diag-device-vocab'

st, r = req('POST', BASE + '/api/register', {'username': U, 'password': 'test123456', 'device': DEV})
TOKEN = r.get('token', '')
st, r = req('POST', BASE + '/api/admin/login', {'secret': SECRET})
AT = r.get('token', '')
req('POST', BASE + '/api/admin/users/grant', {'username': U, 'plan': 'permanent', 'modules': ['vocab']},
    {'Authorization': 'Bearer ' + AT})
st, r = req('POST', BASE + '/api/login', {'username': U, 'password': 'test123456', 'device': DEV})
TOKEN = r.get('token', '')
H = {'Authorization': 'Bearer ' + TOKEN, 'X-Device': DEV}

print('=== 各词书首次取词（连打 3 次看重试稳定性）===')
for lv in ['primary', 'primary', 'primary', 'kids', 'primary']:
    st, rr = req('GET', BASE + '/api/vocab?level=' + lv, headers=H)
    if st == 200:
        print('  %-8s HTTP200  队列 %-3d  待复习 %-3d 新词池 %-4d  est.total %d' % (
            lv, len(rr.get('queue', [])), rr.get('dueTotal', 0), rr.get('newTotal', 0),
            rr.get('est', {}).get('total', 0)))
    else:
        print('  %-8s HTTP%s  %s' % (lv, st, json.dumps(rr, ensure_ascii=False)[:200]))

print('\n=== 学 1 个词后再取（复现 e2e 步骤12 场景）===')
st, rr = req('GET', BASE + '/api/vocab?level=primary', headers=H)
w = rr['queue'][0]['w']
print('  学: %s (%s)' % (w['word'], w['id']))
req('POST', BASE + '/api/vocab/review', {'id': w['id'], 'grade': 2}, headers=H)
for i in range(3):
    st, rr = req('GET', BASE + '/api/vocab?level=primary', headers=H)
    if st == 200:
        est = rr.get('est', {})
        print('  第%d次 HTTP200  队列 %-3d  新词池 %-4d  est: total %d fresh %d known %d' % (
            i + 1, len(rr.get('queue', [])), rr.get('newTotal', 0),
            est.get('total', 0), est.get('fresh', 0), est.get('known', 0)))
    else:
        print('  第%d次 HTTP%s  %s' % (i + 1, st, json.dumps(rr, ensure_ascii=False)[:300]))

print('\n=== 显式传 new 参数 ===')
for nv in ['', '&new=20', '&new=5', '&new=0']:
    st, rr = req('GET', BASE + '/api/vocab?level=primary' + nv, headers=H)
    q = len(rr.get('queue', [])) if st == 200 else -1
    nt = rr.get('newTotal', -1) if st == 200 else -1
    print('  %-10s HTTP%s 队列 %-3d 新词池 %d' % (nv or '(默认)', st, q, nt))
