# -*- coding: utf-8 -*-
"""用测试验证过的 FSRS v2 算法替换 worker.js 中的 SRS 引擎块（due/df 字段分离 + 难度回归 + grade 回写）。"""
import io, re, sys

WORKER = r'E:/szgaokao.cn/worker/src/worker.js'
S = '// === VOCAB_SRS_ENGINE_START ==='
E = '// === VOCAB_SRS_ENGINE_END ==='

NEW = r'''// === VOCAB_SRS_ENGINE_START ===
// —— FSRS 双成分间隔重复引擎 v2 ——
// 借鉴墨墨 SSP-MMC「逐词独立拟合」思想 + FSRS 稳定性(S)/可提取性(R)双成分模型。
// R = exp(-t/S)。每词独立演化，互不影响。
// 字段：s 稳定性(天) / due 到期时间戳 / df 难度(1-10) / l 累计遗忘 / lv 上次评分 / ts 上次复习 / h 复习次数
// 四档反馈对标墨墨：0 忘记 / 1 模糊 / 2 认识 / 3 熟知
// 算法经 tools/test_srs.mjs 12 项场景验证（间隔曲线 1.2→363 天，符合艾宾浩斯规律）

const VOCAB_DAY = 864e5;

const VOCAB_GRADES = { 0: '忘记', 1: '模糊', 2: '认识', 3: '熟知' };

function vocabDailyLimit(mod) {
  if (mod === 'kids' || mod === 'primary' || mod === 'longman') return 20;
  if (mod === 'junior' || mod === 'senior') return 30;
  return 40;
}

function srsNewState(now) {
  return { s: 0.6, due: now, df: 5, r: 0, l: 0, lv: -1, ts: now, h: 0 };
}

function srsRetrievability(st, ts, now) {
  if (!(st.s > 0)) return 0;
  const t = Math.max(0, now - ts) / VOCAB_DAY;
  return Math.exp(-t / st.s);
}

function srsReview(st, now, grade) {
  const s0 = st.s > 0 ? st.s : 0.6;
  const R = srsRetrievability(st, st.ts, now);
  const g = Math.max(0, Math.min(3, grade == null ? 0 : grade));

  let d = st.df != null ? st.df : 5;
  if (g === 0) d = Math.max(1, d - 0.6);
  else if (g === 1) d = Math.max(1, d - 0.25);
  else if (g === 3) d = Math.max(1, d - 0.15);
  else d = d + (5 - d) * 0.25;

  let s, lapses = st.l || 0;
  if (g === 0) { s = Math.max(0.4, s0 * 0.3); lapses += 1; }
  else if (g === 1) { s = Math.max(0.6, s0 * (1 + 0.5 * (d / 10))); }
  else if (g === 2) { s = Math.max(1.2, s0 * (1 + 1.9 * (0.45 + 0.55 * (1 - R))) * (11 - d) / 8); }
  else { s = Math.max(1.8, s0 * (1 + 3.2 * (0.5 + 0.5 * (1 - R))) * (11 - d) / 7); }

  s = Math.min(s, 3650);
  const interval = Math.max(g === 0 ? 0.007 : 0.5, s * (g === 3 ? 1.35 : 1));

  return {
    s: +s.toFixed(4),
    due: +(now + interval * VOCAB_DAY).toFixed(0),
    df: +d.toFixed(2),
    r: st.r || 0,
    l: lapses,
    lv: g,
    ts: now,
    h: (st.h || 0) + 1
  };
}

function srsDue(st, now) {
  return st && st.due && now >= st.due;
}

function vocabQueue(srsMap, words, mod, now, newLimit, reviewLimit) {
  const byId = {};
  words.forEach((w) => { byId[w.id] = w; });

  const due = [];
  for (const id in srsMap) {
    const st = srsMap[id];
    if (!byId[id]) continue;
    if (srsDue(st, now)) {
      const overdue = (now - st.due) / VOCAB_DAY;
      const R = srsRetrievability(st, st.ts, now);
      due.push({ w: byId[id], st, overdue, R });
    }
  }
  due.sort((a, b) => (b.overdue - a.overdue) || (a.R - b.R));
  const review = due.slice(0, reviewLimit);

  const fresh = [];
  for (const w of words) if (!srsMap[w.id]) fresh.push(w);

  const queue = review.map((x) => ({ w: x.w, st: x.st, isNew: false, R: +x.R.toFixed(3) }))
    .concat(fresh.slice(0, newLimit).map((w) => ({ w, st: srsNewState(now), isNew: true, R: 0 })));

  return { queue, dueTotal: due.length, newTotal: fresh.length };
}

function vocabEstimate(srsMap, words) {
  let known = 0, learning = 0, fresh = 0, strong = 0;
  words.forEach((w) => {
    const st = srsMap[w.id];
    if (!st) { fresh += 1; return; }
    if (st.s >= 21) strong += 1;
    if (st.s >= 1) known += 1; else learning += 1;
  });
  return { total: words.length, known, learning, fresh, strong };
}

function vocabDistractors(word, all, n) {
  const sameUnit = all.filter((w) => w.id !== word.id && w.unitId === word.unitId);
  const sameLevel = all.filter((w) => w.id !== word.id && w.level === word.level);
  const pool = sameUnit.length >= n ? sameUnit : (sameLevel.length >= n ? sameLevel : all.filter((w) => w.id !== word.id));
  const out = [];
  const copy = pool.slice();
  while (out.length < n && copy.length) {
    const i = Math.floor(Math.random() * copy.length);
    out.push(copy.splice(i, 1)[0]);
  }
  return out;
}
__name(vocabDailyLimit, "vocabDailyLimit");
__name(srsNewState, "srsNewState");
__name(srsRetrievability, "srsRetrievability");
__name(srsReview, "srsReview");
__name(srsDue, "srsDue");
__name(vocabQueue, "vocabQueue");
__name(vocabEstimate, "vocabEstimate");
__name(vocabDistractors, "vocabDistractors");
// === VOCAB_SRS_ENGINE_END ===
'''

def main():
    with io.open(WORKER, encoding='utf-8') as f:
        src = f.read()
    # 首次注入时漏写了 END 标记，块尾用 var worker_default = { 作为锚点
    pat = re.compile(re.escape(S) + r'.*?(?=var worker_default = \{)', re.S)
    if not pat.search(src):
        print('未找到 SRS 引擎块'); sys.exit(1)
    src = pat.sub(lambda m: NEW.rstrip() + '\n\n', src, count=1)

    # review 路由需传入 grade
    src = src.replace('const st1 = srsReview(st0, now);', 'const st1 = srsReview(st0, now, grade);')
    # 返回字段 due 而非 d
    src = src.replace('nextIn: +(((st1.d - now) / VOCAB_DAY)).toFixed(2)',
                      'nextIn: +(((st1.due - now) / VOCAB_DAY)).toFixed(2), srs: st1.s, df: st1.df')

    with io.open(WORKER, 'w', encoding='utf-8') as f:
        f.write(src)
    print('SRS 引擎已升级为 v2')

    import subprocess
    r = subprocess.run(['node', '--check', WORKER], capture_output=True, text=True)
    print('node --check: ' + ('通过' if r.returncode == 0 else '失败\n' + r.stderr[:600]))
    if r.returncode != 0:
        sys.exit(1)
    for k in ['st1 = srsReview(st0, now, grade)', 'st1.due', 'df: st1.df']:
        print(('OK  ' if k in src else 'MISS'), k)

if __name__ == '__main__':
    main()
