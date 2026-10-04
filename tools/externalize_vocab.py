# -*- coding: utf-8 -*-
"""把 vocab 词库从 worker.js 内联常量改为「构建时写入 public/vocab.json + 运行时经 env.ASSETS 拉取」。

动机：
1) worker.js 已 3.46MB（base64 后 4.6MB），超过代理对 GitHub API 请求体的 ~2-3MB 上限，
   导致 push_files.py / push_big_blob.py 持续伪装 401，无法同步 GitHub。
2) 词库是纯静态数据，本就该走 Assets；抽离后 worker.js 降至 ~2.0MB，可正常推送。
3) 抽离后 bundle 变小，Worker 启动更快。

用法：python tools/externalize_vocab.py
"""
import io, json, os, re, shutil, sys

WORKER = r'E:/szgaokao.cn/worker/src/worker.js'
PUB = r'E:/szgaokao.cn/worker/public'
S = '// === VOCAB_DEFAULT_START ==='
E = '// === VOCAB_DEFAULT_END ==='

# 运行时加载器：读模块级缓存，miss 时经 ASSETS 拉取
LOADER = r'''var __vocabCache = null;

// 词库为静态资源（public/vocab.json），经 ASSETS 拉取并缓存，避免打进 Worker bundle。
async function vocabData(env) {
  if (__vocabCache) return __vocabCache;
  const res = await env.ASSETS.fetch(new Request('https://internal/vocab.json'));
  if (!res.ok) throw new Error('vocab.json ' + res.status);
  __vocabCache = await res.json();
  return __vocabCache;
}
__name(vocabData, "vocabData");
'''

def main():
    with io.open(WORKER, encoding='utf-8') as f:
        src = f.read()

    i = src.find(S)
    j = src.find(E)
    if i < 0 or j < 0:
        print('未找到 VOCAB_DEFAULT 块'); sys.exit(1)

    # 1) 取出内联 JSON 并落盘为 public/vocab.json
    seg = src[i + len(S):j].strip()
    if seg.startswith('var vocab_default = '):
        payload = seg[len('var vocab_default = '):].rstrip().rstrip(';')
    else:
        payload = seg
    data = json.loads(payload)          # 校验
    vp = os.path.join(PUB, 'vocab.json')
    with io.open(vp, 'w', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False, separators=(',', ':')))
    print('已写出 %s (%.2f MB, %d 词)' % (vp, os.path.getsize(vp) / 1024.0 / 1024.0, len(data['words'])))

    # 2) 用加载器替换内联块
    src = src[:i] + S + '\n' + LOADER + E + src[j:]

    # 3) 路由内 vocab_default.levels → (await vocabData(env)).levels
    n = 0
    for old, new in [
        ('vocab_default.levels', '(await vocabData(env)).levels'),
    ]:
        n = src.count(old)
        src = src.replace(old, new)
    print('路由替换 vocab_default -> vocabData(env): %d 处' % n)

    with io.open(WORKER, 'w', encoding='utf-8') as f:
        f.write(src)
    print('worker.js: %.2f MB' % (os.path.getsize(WORKER) / 1024.0 / 1024.0))

    import subprocess
    r = subprocess.run(['node', '--check', WORKER], capture_output=True, text=True)
    print('node --check: ' + ('通过' if r.returncode == 0 else '失败\n' + r.stderr[:600]))
    if r.returncode != 0:
        sys.exit(1)
    left = src.count('vocab_default')
    print('残留 vocab_default 引用: %d %s' % (left, '(OK)' if left == 0 else '<-- 需检查'))

if __name__ == '__main__':
    main()
