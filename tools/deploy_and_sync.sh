#!/bin/bash
# 一键部署 + 双仓同步（szgaokao 词书更新）
# 前提：代理 127.0.0.1:29290 已启动
#
# 用法：bash tools/deploy_and_sync.sh
set -e

PROXY="http://127.0.0.1:29290"
PROJ="C:/Users/27264/WorkBuddy/2026-09-26-21-53-51"
WORKER="/e/szgaokao.cn/worker"
PY="C:/Users/27264/.workbuddy/binaries/python/versions/3.13.12/python.exe"
SYSPY="C:/Users/27264/AppData/Local/Programs/Python/Python310/python.exe"

echo "===== 1/5 检查代理 ====="
# 用 api.github.com 根路径探测（稳定返回 200）；只要 2xx/3xx 即认为代理可用
code=$(curl -s -o /dev/null -x $PROXY -w "%{http_code}" --max-time 25 https://api.github.com/ 2>/dev/null || echo 000)
if [ "${code:0:1}" != "2" ] && [ "${code:0:1}" != "3" ]; then
  echo "[失败] 代理 $PROXY 不可用（返回 $code）。请先启动代理客户端后重试。"
  exit 1
fi
echo "[OK] 代理可用（探测返回 $code）"

echo "===== 2/5 构建词库 ====="
cd "$PROJ/szgaokao-web"
"$PY" tools/build_vocab.py | tail -20

echo "===== 3/5 同步 vocab.json 到部署仓 ====="
"$PY" - <<'PYEOF'
import io, json, os
d = json.load(io.open('data/vocab.json', encoding='utf-8'))
dst = r'E:/szgaokao.cn/worker/public/vocab.json'
with io.open(dst, 'w', encoding='utf-8') as f:
    f.write(json.dumps(d, ensure_ascii=False, separators=(',', ':')))
print('vocab.json -> %s  %.2f MB  %d 词  %d 套词书'
      % (dst, os.path.getsize(dst) / 1024 / 1024, len(d['words']), len(d['levels'])))
PYEOF

echo "===== 4/5 部署到 Cloudflare ====="
cd "$WORKER"
export HTTPS_PROXY=$PROXY
export HTTP_PROXY=$PROXY
export CLOUDFLARE_API_TOKEN=$(tr -d '[:space:]' < "$WORKER/.env.token")
if ! bash -c './node_modules/.bin/wrangler deploy' 2>&1 | tail -8; then
  echo "[重试] 首次失败（代理抖动常见），重试一次…"
  sleep 8
  bash -c './node_modules/.bin/wrangler deploy' 2>&1 | tail -8
fi

echo "===== 5/5 双仓 GitHub 同步 ====="
cd "$PROJ"
export PUSH_MSG="feat(vocab): 14 套词书 2984 词（新增考研/四六级/六级/八级/雅思/托福/出国流水）+ 2656 个 TTS 音频"
# szgaokao-web：词库与工具脚本
"$PY" push_files.py szgaokao-web "$PROJ/szgaokao-web" github-init \
  data/vocab.json data/vocab_ky.json data/vocab_cet4.json data/vocab_cet6.json \
  data/vocab_tem8.json data/vocab_ielts.json data/vocab_toefl.json data/vocab_oral.json \
  tools/build_exam_books.py tools/build_exam_books2.py tools/gen_word_audio.py tools/build_vocab.py 2>&1 | tail -6 || echo "[警告] szgaokao-web 推送失败，可重试"
# szgaokao-worker：部署用词库
"$PY" push_files.py szgaokao-worker "$WORKER" github-init public/vocab.json 2>&1 | tail -4 || echo "[警告] szgaokao-worker 词库推送失败，可重试"

echo ""
echo "===== 完成 ====="
echo "线上检查：https://szgaokao.toolshe.cn/vocab"
