# -*- coding: utf-8 -*-
"""多文件推送到 GitHub（GFW 下用 REST API 绕过 git push）。
与 push_big_blob.py 同源思路，但支持一次提交多个文件，且用 base_tree
保留仓库其余文件 —— 只更新给定路径，不会误删仓库里其它文件。
用法：python tools/push_files.py <repo> <local_dir> <branch> <file1> [file2 ...]
  repo       : GitHub 仓库名（用户名固定 2726401886）
  local_dir  : 本地根目录，file* 相对此目录
  branch     : 目标分支
  file*      : 要推送的文件（相对 local_dir 的路径）
"""
import base64
import io
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.request

PAT = open(r'C:/Users/27264/WorkBuddy/2026-09-26-21-53-51/github-tak.txt').read().strip()
REPO = sys.argv[1]
LOCAL_DIR = sys.argv[2]
BRANCH = sys.argv[3]
FILES = sys.argv[4:]
API = 'https://api.github.com/repos/2726401886/%s' % REPO
PROXY = 'http://127.0.0.1:29290'
# GitHub 直连通常可用；大文件（如 vocab.json 5.5MB）经代理上传易 401/404 失败，
# 故直连优先、代理兜底。
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
            # 401/5xx 视为网络抖动或瞬时限流，退避重试
            if e.code in (401, 403, 502, 503, 504) and a < 5:
                wait = 5 * (a + 1)
                print('   %s 第%d次失败(%d)，%d秒后重试' % (url.split('/')[-1], a + 1, e.code, wait))
                time.sleep(wait)
                continue
            return e.code, {'error': detail}
        except Exception as ex:
            last = (0, str(ex))
            if a < 5:
                wait = 5 * (a + 1)
                print('   %s 第%d次异常(%s)，%d秒后重试' % (url.split('/')[-1], a + 1, str(ex)[:60], wait))
                time.sleep(wait)
                continue
            return 0, {'error': str(ex)}
    return last if last else (0, {})


if not FILES:
    print('没有要推送的文件')
    sys.exit(1)

# 1) 取基准 tree（保留仓库其余文件，避免误删）
st, ref = req('GET', API + '/git/ref/heads/' + BRANCH)
if st != 200:
    print('ref 获取失败', st, ref)
    sys.exit(1)
base_commit = ref['object']['sha']
st, c = req('GET', API + '/git/commits/' + base_commit)
base_tree = c['tree']['sha']
print('base commit %s  tree %s' % (base_commit[:10], base_tree[:10]))

# 2) 逐个文件建 blob
tree_entries = []
for rel in FILES:
    local = os.path.join(LOCAL_DIR, rel)
    if not os.path.isfile(local):
        print('   ! 跳过不存在的文件: %s' % local)
        continue
    with io.open(local, 'rb') as f:
        content = f.read()
    b64 = base64.b64encode(content).decode()
    st, b = req('POST', API + '/git/blobs', {'content': b64, 'encoding': 'base64'})
    if st != 201:
        print('   ! blob 失败 %s: %s' % (rel, b))
        sys.exit(1)
    tree_entries.append({'path': rel, 'mode': '100644', 'type': 'blob', 'sha': b['sha']})
    print('   blob ok %s  %d B  %s' % (rel, len(content), b['sha'][:10]))

if not tree_entries:
    print('没有有效文件可推送')
    sys.exit(1)

# 3) 在 base_tree 基础上建新 tree（只覆盖给定路径，其余保留）
st, t = req('POST', API + '/git/trees', {'base_tree': base_tree, 'tree': tree_entries})
if st != 201:
    print('tree 失败', st, t)
    sys.exit(1)
new_tree = t['sha']

# 4) 提交
msg = os.environ.get('PUSH_MSG', 'chore: update files via push_files.py')
st, cm = req('POST', API + '/git/commits', {'message': msg, 'tree': new_tree, 'parents': [base_commit]})
if st != 201:
    print('commit 失败', st, cm)
    sys.exit(1)
new_commit = cm['sha']

# 5) 更新分支引用
st, u = req('PATCH', API + '/git/refs/heads/' + BRANCH, {'sha': new_commit, 'force': False})
if st != 200:
    print('ref 更新失败（非快进？）', st, u)
    sys.exit(2)
print('PUSHED %s %s -> %s  (%d 文件)' % (REPO, BRANCH, new_commit[:10], len(tree_entries)))
