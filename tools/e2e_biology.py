# -*- coding: utf-8 -*-
"""线上 E2E：注册试用账号 -> 登录 -> 验证 4 个 biology 端点 + 页面"""
import os, sys, json, urllib.request, urllib.error

# 走工作区代理
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:58070'
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:58070'

BASE = 'https://szgaokao.toolshe.cn'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
DEV = 'e2ebio-%d' % os.getpid()
USER = 'bio_e2e_%d' % os.getpid()
PW = 'Bio123456'

def call(path, token='', method='GET', body=None):
    url = BASE + path
    headers = {'User-Agent': UA, 'X-Device': DEV, 'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = token
    data = json.dumps(body).encode('utf-8') if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode('utf-8'))
        except Exception:
            return e.code, {'error': e.reason}

print('== 注册试用账号 ==')
s, j = call('/api/register', method='POST', body={'username': USER, 'password': PW})
print('register', s, j.get('token') and 'token-ok' or j)
assert s == 200 and j.get('token'), '注册失败: %r' % j
TOKEN = j['token']

print('== 登录 ==')
s, j = call('/api/login', method='POST', body={'username': USER, 'password': PW})
print('login', s, j.get('token') and 'token-ok' or j)
assert s == 200 and j.get('token'), '登录失败'
TOKEN = j['token']

print('== /api/biology-book (trial) ==')
s, j = call('/api/biology-book', token=TOKEN)
print('  status', s, '| keys', list(j.keys()))
if 'books' in j:
    print('  册数', len(j['books']), '| edition', j.get('edition'), '| trial', j.get('trial'))
    for b in j['books']:
        print('   -', b['id'], b['name'], '章', b.get('chapterCount'), '节', b.get('sectionCount'))
assert s == 200 and j.get('books'), 'biology-book 异常: %r' % j

print('== /api/biology-knowledge (trial) ==')
s, j = call('/api/biology-knowledge', token=TOKEN)
print('  status', s, '| keys', list(j.keys()), '| trial', j.get('trial'))
assert s == 200 and j.get('books'), 'biology-knowledge 异常: %r' % j

print('== /api/biology-exam (trial, 仅前 5 题) ==')
s, j = call('/api/biology-exam', token=TOKEN)
print('  status', s, '| 返回题数', len(j.get('questions', [])), '| total', j.get('total'), '| trial', j.get('trial'))
assert s == 200 and j.get('questions') and j['total'] > 5, 'biology-exam 异常: %r' % j

print('== /api/biology-link (trial, 仅第 1 单元) ==')
s, j = call('/api/biology-link', token=TOKEN)
print('  status', s, '| 单元数', len(j.get('units', [])), '| trial', j.get('trial'))
assert s == 200 and j.get('units') and len(j['units']) == 1, 'biology-link 异常: %r' % j

print('== 页面 /biology.html ==')
s, j = call('/biology.html', token=TOKEN)
print('  biology.html status', s, type(j) if not isinstance(j, dict) else 'html')

print('== 首页含 biology 卡片 ==')
s, j = call('/', token=TOKEN)
html = j if isinstance(j, str) else ''
print('  index status', s, '| mod-biology 出现', ('mod-biology' in html), '| 生物文案', ('初高中生物' in html))

print('\nE2E ALL PASS')
