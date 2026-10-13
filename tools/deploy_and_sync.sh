#!/bin/bash
# 一键部署 + 双仓同步（szgaokao 词书更新）
#
# 网络策略：
#   - GitHub 推送：默认直连（GFW 下直连 api.github.com 通常可用）；
#     如需代理，设 GH_PROXY=http://127.0.0.1:29290 环境变量。
#   - Cloudflare 部署：GFW 下直连不通，必须经代理；用 CF_PROXY 指定
#     （默认 http://127.0.0.1:29290）。代理掉线时自动重试 3 次，
#     仍失败只报错、不阻断 GitHub 备份。
#
# 用法：bash tools/deploy_and_sync.sh
set -e

CF_PROXY="${CF_PROXY:-http://127.0.0.1:29290}"
PROJ="C:/Users/27264/WorkBuddy/2026-09-26-21-53-51"
WORKER="/e/szgaokao.cn/worker"
PY="C:/Users/27264/.workbuddy/binaries/python/versions/3.13.12/python.exe"

echo "===== 1/5 检查 Cloudflare 部署代理 ====="
# 注意：api.cloudflare.com/client/v4/* 无鉴权会返回 403（端点特性），不能用它判代理死活；
# 正确探针用 api.github.com（代理通则稳定 200，见项目经验笔记）。
code=$(curl -s -o /dev/null -x "$CF_PROXY" -w "%{http_code}" --max-time 25 https://api.github.com/ 2>/dev/null || echo 000)
DEPLOY_SKIP=0
if [ "${code:0:1}" = "2" ] || [ "${code:0:1}" = "3" ]; then
  echo "[OK] 部署代理可用（$CF_PROXY 返回 $code）"
else
  echo "[警告] 部署代理 $CF_PROXY 当前不可用（返回 $code）。本次跳过 Cloudflare 部署，直接做 GitHub 备份（线上仍由已有版本服务）。"
  DEPLOY_SKIP=1
fi

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

echo "===== 4/5 部署到 Cloudflare（最多重试 3 次） ====="
if [ "$DEPLOY_SKIP" = "1" ]; then
  echo "[跳过] 部署代理不可用，跳过 Cloudflare 部署（GitHub 备份将继续）。"
else
  cd "$WORKER"
  export HTTPS_PROXY="$CF_PROXY"
  export HTTP_PROXY="$CF_PROXY"
  export CLOUDFLARE_API_TOKEN=$(tr -d '[:space:]' < "$WORKER/.env.token")
  set +e
  DEPLOY_DONE=0
  for i in 1 2 3; do
    # 后台运行带超时保护的 wrangler；只 wait 其 PID（timeout 240s 会杀掉 wrangler 本身）。
    # 结束后清理可能残留的 node/wrangler 子进程——它们会占用日志 fd，导致前台命令挂起。
    timeout 240 ./node_modules/.bin/wrangler deploy >/tmp/wrangler.log 2>&1 &
    wp=$!
    wait $wp; rc=$?
    pkill -9 -f "bin/wrangler" 2>/dev/null
    pkill -9 -f "node_modules/.bin/esbuild" 2>/dev/null
    tail -8 /tmp/wrangler.log
    if [ "$rc" -eq 0 ]; then
      DEPLOY_DONE=1
      break
    fi
    echo "[重试 $i/3] wrangler deploy 退出码 $rc（代理抖动/卡死常见），8s 后重试…"
    sleep 8
  done
  set -e
  if [ "$DEPLOY_DONE" != "1" ]; then
    echo "[错误] Cloudflare 部署 3 次均失败，请检查代理/网络后手动重试。GitHub 备份仍会继续。"
  fi
  # 部署步骤结束，清掉代理环境变量，避免影响后续 GitHub 直连推送
  unset HTTPS_PROXY HTTP_PROXY
fi

echo "===== 5/5 双仓 GitHub 同步（直连，GH_PROXY 可覆盖） ====="
cd "$PROJ"
export PUSH_MSG="feat(vocab): 课标扩容 小学800/初中1600/高中3500 + 14套8212词 + 3500个_core TTS音频 + 课标生成流水线"
# szgaokao-web：词库、课标核心词源与工具脚本
"$PY" szgaokao-web/tools/push_files.py szgaokao-web "$PROJ/szgaokao-web" github-init \
  data/vocab.json data/vocab_ky.json data/vocab_cet4.json data/vocab_cet6.json \
  data/vocab_tem8.json data/vocab_ielts.json data/vocab_toefl.json data/vocab_oral.json \
  data/primary_core.json data/junior_core.json data/senior_core.json \
  tools/build_vocab.py tools/build_exam_books.py tools/build_exam_books2.py \
  tools/gen_word_audio.py tools/gen_curriculum.py tools/gen_core_audio.py tools/verify_core_books.py \
  2>&1 | tail -8 || echo "[警告] szgaokao-web 推送失败，可重试"
# szgaokao-worker：部署用词库
"$PY" szgaokao-web/tools/push_files.py szgaokao-worker "$WORKER" github-init \
  public/vocab.json src/worker.js public/admin.html schema.sql _mig_is_test.sql \
  2>&1 | tail -4 || echo "[警告] szgaokao-worker 词库推送失败，可重试"

echo ""
echo "===== 完成 ====="
echo "线上检查：https://szgaokao.toolshe.cn/vocab"
