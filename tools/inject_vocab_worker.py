# -*- coding: utf-8 -*-
"""把 data/vocab.json 注入 worker.js，并追加 FSRS 记忆引擎 + /api/vocab 路由。

幂等：重复执行会替换锚点区间内容。
用法：python tools/inject_vocab_worker.py
"""
import io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.dirname(HERE)
WORKER = r'E:/szgaokao.cn/worker/src/worker.js'
VOCAB = os.path.join(WEB, 'data', 'vocab.json')

START = '// === VOCAB_DEFAULT_START ==='
END = '// === VOCAB_DEFAULT_END ==='
SRS_START = '// === VOCAB_SRS_ENGINE_START ==='
SRS_END = '// === VOCAB_SRS_ENGINE_END ==='

SRS_CODE = r'''
// === VOCAB_SRS_ENGINE_START ===
// —— FSRS 双成分间隔重复引擎 ——
// 借鉴墨墨 SSP-MMC 的「逐词独立拟合」思想 + FSRS 的稳定性/可提取性双成分模型。
// S(stability) 记忆强度（天），R = exp(-t/S) 可提取性。逐词独立演化，互不影响。
// 四档反馈对标墨墨：0 忘记 / 1 模糊 / 2 认识 / 3 熟知

const VOCAB_DAY = 864e5;

const VOCAB_GRADES = { 0: '忘记', 1: '模糊', 2: '认识', 3: '熟知' };

// 各学段默认新词量/日（对标各产品节奏：小额高频防积压）
function vocabDailyLimit(mod) {
  if (mod === 'kids' || mod === 'primary') return 20;
  if (mod === 'longman') return 20;
  if (mod === 'junior') return 30;
  if (mod === 'senior') return 30;
  return 40;   // ket / pet
}

function srsNewState(now) {
  // 新词：初始稳定性 0.6 天，难度中等
  return { s: 0.6, d: now, r: 0, l: 0, lv: 0, ts: now, h: 0 };
}

// 记忆可提取性：距上次复习 t 天后的记得概率
function srsRetrievability(st, ts, now) {
  if (!(st > 0)) return 0;
  const t = Math.max(0, (now - ts)) / VOCAB_DAY;
  return Math.exp(-t / st);
}

// 核心：根据四档反馈更新记忆状态
// grade: 0 忘记 / 1 模糊 / 2 认识 / 3 熟知
function srsReview(st, now) {
  const s0 = st.s > 0 ? st.s : 0.6;
  const R = srsRetrievability(s0, st.ts, now);
  const lv = st.lv || 0;

  // 难度调整：忘记/模糊拉低难度基线，熟知略微提高（更难的词反而记住说明基础牢）
  let d = st.d != null ? st.d : 5;
  if (lv === 0) d = Math.max(1, d - 0.35);
  else if (lv === 1) d = Math.max(1, d - 0.12);
  else if (lv === 3) d = Math.min(10, d + 0.15);
  else d = Math.min(10, d + 0.9 - 0.25 * R);   // 认识：记得越牢，下次间隔拉越长

  let s, lapses = st.l || 0;
  if (lv === 0) {
    // 忘记：稳定性大幅衰减，回落到易记区间，间隔重置到 10 分钟内（当天再练）
    s = Math.max(0.35, s0 * 0.28);
    lapses += 1;
  } else if (lv === 1) {
    // 模糊：几乎不增长，甚至略降
    s = Math.max(0.5, s0 * (1.0 + 0.55 * (d / 10)) * 0.92);
  } else if (lv === 2) {
    // 认识：主要增长路径，R 越高增幅越大（欲难效应：太轻松说明间隔太短）
    s = Math.max(1.0, s0 * (1 + 1.35 * (0.35 + 0.65 * (1 - R))) * (11 - d) / 8);
  } else {
    // 熟知：最大增幅，且直接跳到长间隔
    s = Math.max(1.5, s0 * (1 + 2.5 * (0.4 + 0.6 * (1 - R))) * (11 - d) / 7.5);
  }

  s = Math.min(s, 3650);                 // 上限 10 年
  const next = Math.max(0.007, s);       // 间隔（天）= 新稳定性 × 难度微调

  return {
    s: +s.toFixed(4),
    d: +(now + next * VOCAB_DAY).toFixed(0),
    r: st.r || 0,
    l: lapses,
    lv,
    ts: now,
    h: (st.h || 0) + 1
  };
}

// 到期判定：今天该复习的词（含逾期）
function srsDue(st, now) {
  return st && st.d && now >= st.d;
}

// 今日队列：到期复习词 + 新词，优先逾期久、易忘、难度高的
function vocabQueue(srsMap, words, mod, now, newLimit, reviewLimit) {
  const byId = {};
  words.forEach((w) => { byId[w.id] = w; });

  const due = [];
  for (const id in srsMap) {
    const st = srsMap[id];
    if (!byId[id]) continue;             // 只取本词书内的词
    if (srsDue(st, now)) {
      const overdue = (now - st.d) / VOCAB_DAY;
      const R = srsRetrievability(st.s, st.ts, now);
      due.push({ w: byId[id], st, overdue, R });
    }
  }
  // 逾期越久、记得率越低越优先
  due.sort((a, b) => (b.overdue - a.overdue) || (a.R - b.R));
  const review = due.slice(0, reviewLimit);

  // 新词：从未学过的
  const fresh = [];
  for (const w of words) {
    if (!srsMap[w.id]) fresh.push(w);
  }

  const nl = Math.max(0, newLimit);
  const queue = review.map((x) => ({ w: x.w, st: x.st, isNew: false, R: x.R }))
    .concat(fresh.slice(0, nl).map((w) => ({ w, st: srsNewState(now), isNew: true, R: 0 })));

  return { queue, dueTotal: due.length, newTotal: fresh.length };
}

// 词汇量估算：按记忆强度分档统计（熟词过滤，对标扇贝）
function vocabEstimate(srsMap, words, now) {
  let known = 0, learning = 0, fresh = 0, strong = 0;
  words.forEach((w) => {
    const st = srsMap[w.id];
    if (!st) { fresh += 1; return; }
    if (st.s >= 21) strong += 1;
    if (st.s >= 1) known += 1; else learning += 1;
  });
  return { total: words.length, known, learning, fresh, strong, now };
}

// —— 选干扰项：同词书同单元优先，其次同词书 ——
function vocabDistractors(word, all, n) {
  const sameUnit = all.filter((w) => w.id !== word.id && w.unitId === word.unitId);
  const sameLevel = all.filter((w) => w.id !== word.id && w.level === word.level);
  const pool = (sameUnit.length >= n ? sameUnit : (sameLevel.length >= n ? sameLevel : all.filter((w) => w.id !== word.id)));
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
'''

ROUTES_CODE = r'''
    // —— 专业英语单词记忆：词书列表 / 取词 / 评分 / 队列 / 统计 ——

    if (path === "/api/vocab" && method === "GET") {

      const user = await uidOf(request, env);
      if (!user) return err(401, "未登录或登录已失效，请重新登录");
      if (!parseDevices(user).includes(getDev({}, request))) return err(403, "当前设备未授权，请重新登录");

      const authed = modAuthed(user, "vocab");
      const lid = q.get("level");
      const now = Date.now();

      // 词汇量测试定级 / 全局统计
      if (q.get("stats")) {
        const st = await env.DB.prepare("SELECT data FROM study WHERE username = ?").bind(user.username).first();
        let d = { srs: {} };
        if (st) { try { d = JSON.parse(st.data); } catch (e) {} }
        const srsMap = d.srs || {};
        const levels = vocab_default.levels.map((lv) => {
          const ids = [];
          lv.books.forEach((b) => b.units.forEach((u) => u.words.forEach((w) => ids.push(w.id))));
          const set = {};
          ids.forEach((id) => { if (srsMap[id]) set[id] = 1; });
          const est = vocabEstimate(set, ids.map((id) => ({ id })), now);
          return { level: lv.level, title: lv.title, stage: lv.stage, count: lv.count,
                   known: est.known, learning: est.learning, fresh: est.fresh, strong: est.strong };
        });
        const total = levels.reduce((n, l) => n + l.count, 0);
        const knownAll = levels.reduce((n, l) => n + l.known, 0);
        return ok({ levels, total, known: knownAll, updated: Number(st ? st.updated : 0) || 0 });
      }

      const lv = vocab_default.levels.find((x) => x.level === lid);
      if (!lv) return ok({ levels: vocab_default.levels.map((x) => ({ level: x.level, title: x.title, stage: x.stage, count: x.count, books: x.books.length })) });

      // 汇总该 level 全部词
      const all = [];
      lv.books.forEach((b) => b.units.forEach((u) => u.words.forEach((w) => all.push(w))));

      const st = await env.DB.prepare("SELECT data FROM study WHERE username = ?").bind(user.username).first();
      let d = { srs: {} };
      if (st) { try { d = JSON.parse(st.data); } catch (e) {} }
      const srsMap = d.srs || {};

      if (q.get("word")) {
        const w = all.find((x) => x.id === q.get("word"));
        if (!w) return err(404, "单词不存在");
        const s0 = srsMap[w.id] || null;
        const R = s0 ? srsRetrievability(s0.s, s0.ts, now) : 0;
        return ok({ word: w, srs: s0, R: +R.toFixed(3), distractors: vocabDistractors(w, all, 3) });
      }

      const daily = vocabDailyLimit(lv.mod);
      const nl = Math.min(200, Math.max(0, parseInt(q.get("new") || "", 10) || daily));
      const rl = Math.min(500, Math.max(0, parseInt(q.get("review") || "", 10) || 200));
      const { queue, dueTotal, newTotal } = vocabQueue(srsMap, all, lv.mod, now, nl, rl);
      const est = vocabEstimate(srsMap, all, now);

      // 体验模式：只放开前 20 词
      const LIMIT = 20;
      const finalQueue = authed ? queue : queue.slice(0, LIMIT);
      const books = lv.books.map((b) => ({ id: b.id, title: b.title, units: b.units.length,
        count: b.units.reduce((n, u) => n + u.words.length, 0) }));

      return ok({ level: lv.level, title: lv.title, stage: lv.stage, mod: lv.mod,
        books, queue: finalQueue, dueTotal: authed ? dueTotal : Math.min(dueTotal, LIMIT),
        newTotal, est, daily, trial: !authed, limit: LIMIT });
    }

    if (path === "/api/vocab/review" && method === "POST") {

      const user = await uidOf(request, env);
      if (!user) return err(401, "未登录或登录已失效，请重新登录");
      if (!parseDevices(user).includes(getDev({}, request))) return err(403, "当前设备未授权，请重新登录");

      const b = await readBody(request);
      const wid = String(b.id || "");
      const grade = Math.max(0, Math.min(3, parseInt(b.grade, 10) || 0));
      const now = Date.now();

      const row = await env.DB.prepare("SELECT data FROM study WHERE username = ?").bind(user.username).first();
      let d = { srs: {}, ans: {}, tags: {} };
      if (row) { try { d = JSON.parse(row.data); } catch (e) {} }
      const srsMap = d.srs || {};
      const st0 = srsMap[wid] || srsNewState(now);
      const st1 = srsReview(st0, now);
      srsMap[wid] = st1;
      d.srs = srsMap;

      // 同步累加到 ans（进入错题本 / 学习报告）
      const ans = d.ans || {};
      const tags = d.tags || {};
      const qid = "vocab:" + wid;
      const q = ans[qid] || { r: 0, w: 0, lw: null, lt: 0, ts: 0, tags: [] };
      const okGrade = grade >= 2;
      if (okGrade) q.r += 1; else { q.w += 1; q.lw = grade; }
      if (b.time != null && b.time > 0) q.lt = b.time;
      q.ts = now;
      const tg = ["英语·词汇"];
      if (!q.tags.length) q.tags = tg;
      ans[qid] = q;
      const t = tags["英语·词汇"] || { wrong: 0, total: 0, last: 0 };
      t.total += 1;
      if (!okGrade) t.wrong += 1;
      t.last = now;
      tags["英语·词汇"] = t;
      d.ans = ans;
      d.tags = tags;

      const data = JSON.stringify(d);
      await env.DB.prepare("INSERT INTO study (username, data, updated) VALUES (?,?,?) ON CONFLICT(username) DO UPDATE SET data = excluded.data, updated = excluded.updated")
        .bind(user.username, data, now).run();

      return ok({ srs: st1, grade, label: VOCAB_GRADES[grade], nextIn: +(((st1.d - now) / VOCAB_DAY)).toFixed(2) });
    }
'''

def main():
    if not os.path.exists(WORKER):
        print('worker.js 不存在: ' + WORKER); sys.exit(1)
    if not os.path.exists(VOCAB):
        print('vocab.json 不存在，请先运行 build_vocab.py'); sys.exit(1)

    with io.open(VOCAB, encoding='utf-8') as f:
        vocab = json.load(f)
    payload = json.dumps(vocab, ensure_ascii=False, separators=(',', ':'))
    # 校验可解析
    json.loads(payload)

    with io.open(WORKER, encoding='utf-8') as f:
        src = f.read()

    def replace_block(text, s_tag, e_tag, body):
        pat = re.compile(re.escape(s_tag) + r'.*?' + re.escape(e_tag), re.S)
        blk = s_tag + '\n' + body + '\n' + e_tag
        if pat.search(text):
            return pat.sub(lambda m: blk, text, count=1)
        return text

    # 1) 注入词库（放在 HCHINESE_GD_DEFAULT_END 之后、worker_default 之前）
    anchor = 'var worker_default = {'
    if START not in src:
        inject = START + '\nvar vocab_default = ' + payload + '\n' + END + '\n\n'
        src = src.replace(anchor, inject + anchor, 1)
        print('词库已注入')
    else:
        src = replace_block(src, START, END, 'var vocab_default = ' + payload)
        print('词库已替换')

    # 2) 注入 SRS 引擎（放在 fetch 之前，即 worker_default 之前）
    if SRS_START not in src:
        src = src.replace(anchor, SRS_CODE + '\n' + anchor, 1)
        print('SRS 引擎已注入')
    else:
        src = replace_block(src, SRS_START, SRS_END, SRS_CODE.strip())
        print('SRS 引擎已替换')

    # 3) 注入路由（放在 return err(404,"接口不存在") 之前）
    tail = 'return err(404, "\\u63A5\\u53E3\\u4E0D\\u5B58\\u5728");'
    if '/api/vocab/review' not in src:
        if tail not in src:
            print('未找到路由插入锚点'); sys.exit(1)
        src = src.replace(tail, ROUTES_CODE + '\n' + tail, 1)
        print('vocab 路由已注入')
    else:
        print('vocab 路由已存在，跳过')

    # 4) 授权 modules 白名单加 vocab
    n1 = src.count('JSON.stringify({ kids: 1, primary: 1, middle: 1, gk: 1, math: 1 })')
    src = src.replace('JSON.stringify({ kids: 1, primary: 1, middle: 1, gk: 1, math: 1 })',
                      'JSON.stringify({ kids: 1, primary: 1, middle: 1, gk: 1, math: 1, vocab: 1 })')
    n2 = src.count('const ALL = ["kids", "primary", "middle", "gk", "math"];')
    src = src.replace('const ALL = ["kids", "primary", "middle", "gk", "math"];',
                      'const ALL = ["kids", "primary", "middle", "gk", "math", "vocab"];')
    print('授权白名单更新: activate/trial %d 处, ALL %d 处' % (n1, n2))

    with io.open(WORKER, 'w', encoding='utf-8') as f:
        f.write(src)
    print('worker.js 已更新 (%.2f MB)' % (os.path.getsize(WORKER) / 1024.0 / 1024.0))

    # 5) 语法校验
    import subprocess
    r = subprocess.run(['node', '--check', WORKER], capture_output=True, text=True)
    print('node --check: ' + ('通过' if r.returncode == 0 else '失败\n' + r.stderr[:500]))
    if r.returncode != 0:
        sys.exit(1)

if __name__ == '__main__':
    main()
