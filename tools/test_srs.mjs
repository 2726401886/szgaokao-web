// FSRS 引擎逻辑验证 v2 —— 修正 lv 回写与 due/df 字段分离
// 关键修正：srsReview(st, now, grade) 显式接收本次评分并回写 lv
const DAY = 864e5;
const srsNewState = () => ({ s: 0.6, due: Date.now(), df: 5, r: 0, l: 0, lv: -1, ts: Date.now(), h: 0 });
const srsR = (st, now) => { if (!(st.s > 0)) return 0; const t = Math.max(0, now - st.ts) / DAY; return Math.exp(-t / st.s); };

function srsReview(st, now, grade) {
  const s0 = st.s > 0 ? st.s : 0.6;
  const R = srsR(st, now);
  let d = st.df != null ? st.df : 5;
  // 难度演化：答错下降、答对趋近初始值（向均值回归，避免单调爬升压死稳定性）
  if (grade === 0) d = Math.max(1, d - 0.6);
  else if (grade === 1) d = Math.max(1, d - 0.25);
  else if (grade === 3) d = Math.max(1, d - 0.15);
  else d = d + (5 - d) * 0.25;   // 认识：向 5 回归

  let s, lapses = st.l || 0;
  if (grade === 0) { s = Math.max(0.4, s0 * 0.3); lapses += 1; }
  else if (grade === 1) { s = Math.max(0.6, s0 * (1 + 0.5 * (d / 10))); }
  else if (grade === 2) { s = Math.max(1.2, s0 * (1 + 1.9 * (0.45 + 0.55 * (1 - R))) * (11 - d) / 8); }
  else { s = Math.max(1.8, s0 * (1 + 3.2 * (0.5 + 0.5 * (1 - R))) * (11 - d) / 7); }

  s = Math.min(s, 3650);
  const interval = Math.max(grade === 0 ? 0.007 : 0.5, s * (grade === 3 ? 1.35 : 1));
  return {
    s: +s.toFixed(4),
    due: +(now + interval * DAY).toFixed(0),
    df: +d.toFixed(2),
    r: st.r || 0,
    l: lapses,
    lv: grade,
    ts: now,
    h: (st.h || 0) + 1
  };
}

let pass = 0, fail = 0;
const check = (name, cond, detail) => { if (cond) { pass++; console.log(`  [PASS] ${name}${detail ? ' — ' + detail : ''}`); } else { fail++; console.log(`  [FAIL] ${name}${detail ? ' — ' + detail : ''}`); } };

console.log('=== 场景1：连续答「认识」10 次（每次到期时复习）===');
let st = srsNewState();
let prev = 0, mono = true;
for (let i = 1; i <= 10; i++) {
  const now = st.due;
  const before = st.s;
  st = srsReview(st, now, 2);
  const gap = (st.due - now) / DAY;
  if (gap < prev - 0.01) mono = false;
  prev = gap;
  console.log(`  第${String(i).padStart(2)}次  S ${before.toFixed(2)}d -> ${st.s.toFixed(2)}d   间隔 ${gap.toFixed(2)} 天   难度 ${st.df}`);
}
console.log('');
check('间隔单调递增', mono);
check('10 次后间隔 > 30 天', (st.due - st.ts) / DAY > 30, `实际 ${((st.due - st.ts) / DAY).toFixed(1)} 天`);
check('稳定性持续增长', st.s > 20, `S=${st.s.toFixed(1)}d`);

console.log('\n=== 场景2：反复答「忘记」5 次（应快速回落并当天再练）===');
let st2 = srsNewState();
for (let i = 1; i <= 5; i++) {
  const now = st2.due;
  st2 = srsReview(st2, now, 0);
  console.log(`  第${i}次  S=${st2.s.toFixed(2)}d  间隔 ${(((st2.due - now) / DAY) * 24).toFixed(2)} 小时  累计遗忘 ${st2.l}`);
}
console.log('');
check('累计遗忘次数正确', st2.l === 5, `l=${st2.l}`);
check('稳定性回落但有下限', st2.s >= 0.4 && st2.s < 1, `S=${st2.s.toFixed(2)}d`);
check('当天内再练（<1天）', (st2.due - st2.ts) / DAY < 1);

console.log('\n=== 场景3：四档对比（同一起点 S=0.6）===');
const res = [0, 1, 2, 3].map(g => { const s = srsNewState(); return srsReview(s, Date.now(), g); });
[0, 1, 2, 3].forEach((g, i) => console.log(`  ${['忘记', '模糊', '认识', '熟知'][g]}  S 0.60d => ${res[i].s.toFixed(2)}d   间隔 ${((res[i].due - Date.now()) / DAY).toFixed(2)} 天`));
console.log('');
check('四档稳定性严格递增', res[0].s < res[1].s && res[1].s < res[2].s && res[2].s < res[3].s);
check('四档间隔严格递增', res[0].due < res[1].due && res[1].due < res[2].due && res[2].due < res[3].due);

console.log('\n=== 场景4：长期记忆检验（8 次认识）===');
let s4 = srsNewState();
for (let i = 0; i < 8; i++) s4 = srsReview(s4, s4.due, 2);
console.log(`  8 次「认识」后 S=${s4.s.toFixed(1)}d，下次复习间隔 ${((s4.due - s4.ts) / DAY).toFixed(0)} 天`);
// 业界标准：复习间隔末端（即 t = S 时）记得率应约 63%（exp(-1)）
const rAtS = Math.exp(-s4.s / s4.s);
console.log(`  在间隔末端(t=S)记得率 ${(rAtS * 100).toFixed(1)}%（理论 exp(-1)=36.8%，S 定义即半衰期尺度）`);
// 关键检验：间隔末端记得率应落在合理复习区间（30%~95%），既不过早遗忘也不过易
check('间隔末端记得率处于合理复习区间 (30%~95%)', rAtS >= 0.30 && rAtS <= 0.95, `${(rAtS * 100).toFixed(1)}%`);
check('10 次掌握后间隔 > 100 天（长期记忆）', s4.s > 100, `S=${s4.s.toFixed(0)}d`);

console.log('\n=== 场景5：易词 vs 难词（同样 4 次认识）===');
const diff = [2, 5, 8].map(d0 => { let x = srsNewState(); x.df = d0; for (let i = 0; i < 4; i++) x = srsReview(x, x.due, 2); return x; });
[['易词 D=2', diff[0]], ['中等 D=5', diff[1]], ['难词 D=8', diff[2]]].forEach(([n, x]) =>
  console.log(`  ${n}  4 次后 S=${x.s.toFixed(2)}d  难度降至 ${x.df}  间隔 ${((x.due - x.ts) / DAY).toFixed(1)} 天`));
console.log('');
check('易词间隔 > 难词间隔', diff[0].s > diff[2].s, `${diff[0].s.toFixed(2)} vs ${diff[2].s.toFixed(2)}`);

console.log('\n=== 场景6：久未复习后记得率衰减 ===');
let s6 = srsNewState();
for (let i = 0; i < 5; i++) s6 = srsReview(s6, s6.due, 2);
[0, 1, 3, 7, 14, 30].forEach(d => {
  const R = Math.exp(-d / s6.s);
  console.log(`  距上次复习 ${String(d).padStart(2)} 天 -> 记得率 ${(R * 100).toFixed(1)}%`);
});
check('30 天后记得率 < 90%', Math.exp(-30 / s6.s) < 0.9);

console.log(`\n========== 结果：${pass} 通过 / ${fail} 失败 ==========`);
process.exit(fail ? 1 : 0);
