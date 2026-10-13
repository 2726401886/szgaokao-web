# -*- coding: utf-8 -*-
"""大文件 blob 上传：GitHub Contents/Blobs API 对 MB 级文件易 401。
策略：分块不可行（blob API 不支持分片），改为：
  1) 压缩后尝试（worker.js 是 JSON 密集型，gzip 后可能 <1MB，但 blob API 收原始内容）
  2) 多次重试 + 延长超时（401 多为代理对大 body 的截断，重试即可）
用法：python tools/push_big_blob.py <repo> <local_file> <branch> <repo_path>
"""
import base64, io, json, os, ssl, sys, time, urllib.request, urllib.error

PAT = open(r'C:/Users/27264/WorkBuddy/2026-09-26-21-53-51/github-tak.txt').read().strip()
REPO = sys.argv[1]
LOCAL = sys.argv[2]
BRANCH = sys.argv[3]
REPO_PATH = sys.argv[4]
API = 'https://api.github.com/repos/2726401886/%s' % REPO
PROXY = 'http://127.0.0.1:29290'
# GitHub 直连通常可用；大文件经代理上传易 401/404 失败，故直连优先、代理兜底。
direct_opener = urllib.request.build_opener(
    urllib.request.HTTPSHandler(context=ssl.create_default_context()))
proxy_opener = urllib.request.build_opener(
    urllib.request.ProxyHandler({'http': PROXY, 'https': PROXY}),
    urllib.request.HTTPSHandler(context=ssl.create_default_context()))

def req(method, url, data=None, timeout=300):
    body = json.dumps(data).encode() if data is not None else None
    r = urllib.request.Request(url, data=body, method=method, headers={
        'Authorization': 'Bearer ' + PAT, 'User-Agent': 'workbuddy',
        'Content-Type': 'application/json', 'Accept': 'application/vnd.github+json'})
    last = None
    openers = [direct_opener, proxy_opener]  # 直连优先，失败后切代理
    for a in range(6):
        op = openers[0] if a < 3 else openers[1]
        try:
            with op.open(r, timeout=timeout) as resp:
                return resp.status, json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            detail = e.read().decode()[:300]
            last = (e.code, detail)
            # 401/5xx 视为代理抖动或瞬时限流，退避重试
            if e.code in (401, 403, 502, 503, 504) and a < 5:
                wait = 5 * (a + 1)
                print('   %s 第%d次失败(%d)，%d秒后重试' % (REPO_PATH, a + 1, e.code, wait))
                time.sleep(wait); continue
            return e.code, {'error': detail}
        except Exception as ex:
            last = (0, str(ex))
            if a < 5:
                wait = 5 * (a + 1)
                print('   %s 第%d次异常(%s)，%d秒后重试' % (REPO_PATH, a + 1, str(ex)[:60], wait))
                time.sleep(wait); continue
            return 0, {'error': str(ex)}
    return last if last else (0, {})

with io.open(LOCAL, 'rb') as f:
    content = f.read()
print('本地文件 %s  (%.2f MB)' % (LOCAL, len(content) / 1024.0 / 1024.0))
b64 = base64.b64encode(content).decode()
print('base64 后 %.2f MB' % (len(b64) / 1024.0 / 1024.0))

st, ref = req('GET', API + '/git/ref/heads/' + BRANCH)
if st != 200:
    print('ref 获取失败', st, ref); sys.exit(1)
base_commit = ref['object']['sha']
st, c = req('GET', API + '/git/commits/' + base_commit)
base_tree = c['tree']['sha']
print('base commit %s  tree %s' % (base_commit[:10], base_tree[:10]))

st, b = req('POST', API + '/git/blobs', {'content': b64, 'encoding': 'base64'})
if st != 201:
    print('blob 失败', st, b); sys.exit(1)
print('blob ok  %s  %d B  %s' % (REPO_PATH, len(content), b['sha'][:10]))

st, t = req('POST', API + '/git/trees', {'base_tree': base_tree, 'tree': [
    {'path': REPO_PATH, 'mode': '100644', 'type': 'blob', 'sha': b['sha']}]})
if st != 201:
    print('tree 失败', st, t); sys.exit(1)
new_tree = t['sha']
print('new tree %s' % new_tree[:10])

msg = os.environ.get('PUSH_MSG', 'chore: update large file via push_big_blob.py')
st, cm = req('POST', API + '/git/commits', {'message': msg, 'tree': new_tree, 'parents': [base_commit]})
if st != 201:
    print('commit 失败', st, cm); sys.exit(1)
new_commit = cm['sha']
print('new commit %s' % new_commit[:10])

st, u = req('PATCH', API + '/git/refs/heads/' + BRANCH, {'sha': new_commit, 'force': False})
if st != 200:
    print('ref 更新失败（非快进？）', st, u); sys.exit(2)
print('PUSHED %s %s -> %s' % (REPO, BRANCH, new_commit[:10]))
