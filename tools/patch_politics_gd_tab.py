# -*- coding: utf-8 -*-
"""politics.html 增加「📄 广东高考卷」板块（结构仿真卷，红色品牌调）。
改动点（全部断言命中）：
  1) CSS：追加 gd-* 样式（红品牌 #c0392b）
  2) SECTIONS：新增 { k:'gd' }
  3) selectSection：'gd' 走独立整幅渲染分支
  4) renderSide：gd 板块跳过侧栏
  5) 新增 GD 渲染器（试卷列表 + 整卷作答，支持单选/多选/主观题）
用法：python tools/patch_politics_gd_tab.py
"""
import io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, 'public', 'politics.html')

s = io.open(HTML, encoding='utf-8').read()
reps = []


def add(old, new, n=1):
    reps.append((old, new, n))


# ---------- 1) CSS ----------
CSS_ANCHOR = "  .read-text { font-size:15px;"
GD_CSS = """  /* ===== 广东高考卷（结构仿真卷） ===== */
  .gd-wrap { max-width:1000px; }
  .gd-hd { font-size:18px; font-weight:800; margin-bottom:10px; display:flex; align-items:center; gap:10px; flex-wrap:wrap; }
  .gd-back { border:none; background:#fdf0ef; color:#c0392b; font-size:13px; font-weight:700; padding:6px 12px; border-radius:14px; cursor:pointer; }
  .gd-st-h { font-size:14px; font-weight:800; margin:14px 0 8px; }
  .gd-ed { font-size:12px; font-weight:500; color:#c0392b; background:#fdf0ef; padding:3px 10px; border-radius:12px; }
  .gd-warn { font-size:12.5px; color:#7a5c00; background:#fffbe8; border:1px solid #f3e6b8; border-radius:12px; padding:10px 14px; margin-bottom:12px; line-height:1.8; }
  .gd-cards { display:flex; gap:12px; flex-wrap:wrap; }
  .gd-card { flex:1 1 290px; background:#fff; border:1.5px solid #f7dedb; border-radius:14px; padding:14px; cursor:pointer; display:flex; gap:12px; align-items:center; }
  .gd-card:hover { border-color:#c0392b; box-shadow:0 6px 20px rgba(192,57,43,.12); }
  .gd-card-y { font-size:20px; font-weight:800; color:#c0392b; background:#fdf0ef; border-radius:12px; padding:10px 12px; }
  .gd-card-b { flex:1; }
  .gd-card-t { font-size:14.5px; font-weight:700; }
  .gd-card-m { font-size:12px; color:#999; margin-top:4px; }
  .gd-card-go { font-size:12px; color:#c0392b; font-weight:700; white-space:nowrap; }
  .gd-paper { background:#fff; border-radius:16px; padding:20px 18px; box-shadow:0 4px 16px rgba(0,0,0,.05); }
  .gd-p-hd { text-align:center; border-bottom:2px solid #c0392b; padding-bottom:12px; margin-bottom:16px; }
  .gd-p-name { font-size:19px; font-weight:800; }
  .gd-p-meta { font-size:12.5px; color:#666; margin-top:6px; }
  .gd-mod { margin-bottom:20px; }
  .gd-mod-h { font-size:15.5px; font-weight:800; margin-bottom:6px; }
  .gd-mod-sc { font-size:12px; font-weight:600; color:#c0392b; background:#fdf0ef; padding:2px 9px; border-radius:10px; margin-left:8px; }
  .gd-mod-note { font-size:11.5px; color:#999; margin-bottom:8px; }
  .gd-part { margin:12px 0 12px 12px; }
  .gd-part-h { font-size:13.5px; font-weight:700; color:#444; margin-bottom:6px; }
  .gd-q { margin:12px 0 12px 4px; }
  .gd-q-h { font-size:14px; line-height:1.8; margin-bottom:6px; }
  .gd-q-sc { font-size:11.5px; color:#999; margin-left:6px; }
  .gd-opt { display:block; padding:7px 10px; border:1.5px solid #eee; border-radius:10px; margin:5px 0; cursor:pointer; font-size:13.5px; line-height:1.7; }
  .gd-opt:hover { border-color:#e5a09a; background:#fdf7f6; }
  .gd-opt.locked { cursor:default; }
  .gd-opt.right { border-color:#2a8; background:#eefaf5; }
  .gd-opt.wrong { border-color:#e23; background:#fdeeee; }
  .gd-opt.picked { border-color:#c0392b; background:#fdf0ef; }
  .gd-res { font-size:12.5px; margin-top:5px; line-height:1.7; }
  .gd-res.ok { color:#2a8; }
  .gd-res.bad { color:#e23; }
  .gd-ans { background:#f8f9fc; border:1px solid #eceef3; border-radius:10px; padding:9px 11px; font-size:12.5px; color:#444; line-height:1.8; margin-top:6px; white-space:pre-wrap; }
  .gd-tip { font-size:12.5px; color:#1a56db; background:#eef2ff; border:1px solid #c9d6ff; border-radius:12px; padding:10px 14px; margin-bottom:12px; }
"""
add(CSS_ANCHOR, GD_CSS + CSS_ANCHOR)

# ---------- 2) SECTIONS ----------
add("""    { k: 'exam', t: '📋 题库组卷', modes: [] },
    { k: 'link', t: '🧩 专题突破', modes: [] },
  ];""",
    """    { k: 'exam', t: '📋 题库组卷', modes: [] },
    { k: 'link', t: '🧩 专题突破', modes: [] },
    { k: 'gd', t: '📄 广东高考卷', modes: [] },
  ];""")

# ---------- 3) selectSection 分支 ----------
add("""    if (k === 'exam' || k === 'link') {
      // 独立板块：隐藏左侧分组栏，整幅渲染
      $('#sidePane').style.display = 'none';
      $('#mainArea').style.flex = '1 1 100%';
      if (k === 'exam') renderExamPage();
      else renderLinkPage();
      return;
    }""",
    """    if (k === 'exam' || k === 'link' || k === 'gd') {
      // 独立板块：隐藏左侧分组栏，整幅渲染
      $('#sidePane').style.display = 'none';
      $('#mainArea').style.flex = '1 1 100%';
      if (k === 'exam') renderExamPage();
      else if (k === 'link') renderLinkPage();
      else renderGdPage();
      return;
    }""")

# ---------- 4) renderSide 跳过 ----------
add("  function renderSide() {\n    if (section === 'exam' || section === 'link') return;",
    "  function renderSide() {\n    if (section === 'exam' || section === 'link' || section === 'gd') return;")

# ---------- 5) GD 渲染器（插在 link 板块注释之前）----------
GD_ANCHOR = "  // ================== 板块：题库组卷 =================="
GD_JS = r'''  // ================== 板块：广东高考卷（结构仿真卷） ==================
  let GD = { loaded: false, meta: null, papers: [], cur: null, showKey: {} };

  async function renderGdPage() {
    $('#mainArea').innerHTML = '<div class="gd-wrap"><div class="empty">加载中…</div></div>';
    if (!GD.loaded) {
      const r = await api('/api/politics-gd');
      if (r.s !== 200) { $('#mainArea').innerHTML = '<div class="empty">加载失败，请稍后重试</div>'; return; }
      GD.loaded = true; GD.meta = r.j; GD.papers = r.j.papers || [];
    }
    renderGdList();
  }

  function renderGdList() {
    const m = GD.meta;
    $('#mainArea').innerHTML =
      '<div class="gd-wrap">' +
        '<div class="gd-hd">📄 广东省高考思想政治 · 结构仿真卷<span class="gd-ed">非真题原卷</span></div>' +
        (m.notice ? '<div class="gd-warn">⚠️ ' + esc(m.notice.replace(/\*\*/g, '')) + '</div>' : '') +
        '<div class="gd-tip">本套卷题型、题量、分值与广东卷一致（单选16×3分 + 多选4×6分 + 主观28分 = 100分/75分钟）；材料为自编，时政取公开宏观事实。用于考前结构与节奏训练，不可当真题原卷引用。</div>' +
        '<div class="gd-st-h" style="font-size:14px;font-weight:800;margin:14px 0 8px;">📋 试卷结构</div>' +
        '<div class="gd-cards" style="margin-bottom:16px;">' +
          m.structure.map(st => '<div class="gd-card" style="cursor:default;"><div class="gd-card-y" style="font-size:13px;">' + st.score + '</div>' +
            '<div class="gd-card-b"><div class="gd-card-t">' + esc(st.name) + '</div><div class="gd-card-m">' + esc(st.detail) + '</div></div></div>').join('') +
        '</div>' +
        '<div class="gd-st-h" style="font-size:14px;font-weight:800;margin:14px 0 8px;">📚 可选试卷（' + GD.papers.length + ' 套）</div>' +
        '<div class="gd-cards">' +
          GD.papers.map(p => '<div class="gd-card" data-p="' + p.id + '"><div class="gd-card-y">' + p.year + '</div>' +
            '<div class="gd-card-b"><div class="gd-card-t">' + esc(p.title) + '</div>' +
            '<div class="gd-card-m">' + p.totalScore + '分 · ' + p.durationMin + '分钟 · ' + p.questionCount + '题' + (p.theme ? ' · ' + esc(p.theme) : '') + '</div></div>' +
            '<div class="gd-card-go">开始 →</div></div>').join('') +
        '</div>' +
      '</div>';
    document.querySelectorAll('.gd-card[data-p]').forEach(el => el.addEventListener('click', () => openGdPaper(el.dataset.p)));
  }

  async function openGdPaper(pid) {
    $('#mainArea').innerHTML = '<div class="gd-wrap"><div class="empty">加载中…</div></div>';
    const r = await api('/api/politics-gd?paper=' + encodeURIComponent(pid));
    if (r.s !== 200) { $('#mainArea').innerHTML = '<div class="empty">试卷加载失败</div>'; return; }
    GD.cur = r.j;
    GD.showKey = {};
    renderGdPaper();
  }

  function gdAnswerText(q) {
    if (q.type === 'multiple') return q.answer.map(i => 'ABCD'[i]).join('');
    if (q.type === 'single') return 'ABCD'[q.answer];
    return q.answer;
  }

  function renderGdPaper() {
    const p = GD.cur;
    const body = p.modules.map(m =>
      '<div class="gd-mod"><div class="gd-mod-h">' + esc(m.name) + '<span class="gd-mod-sc">' + m.score + '分</span></div>' +
      '<div class="gd-mod-note">' + esc(m.note || '') + '</div>' +
      m.parts.map(pt =>
        '<div class="gd-part">' + (m.parts.length > 1 ? '<div class="gd-part-h">' + esc(pt.name) + '（' + pt.score + '分）</div>' : '') +
        pt.questions.map(q => renderGdQuestion(q)).join('') +
        '</div>').join('') +
      '</div>').join('');
    $('#mainArea').innerHTML =
      '<div class="gd-wrap">' +
        '<div class="gd-hd"><button class="gd-back" id="gdBack">← 返回试卷列表</button><span class="gd-ed">非真题原卷</span></div>' +
        '<div class="gd-paper">' +
          '<div class="gd-p-hd"><div class="gd-p-name">' + esc(p.title) + '</div>' +
            '<div class="gd-p-meta">' + esc(p.examType) + ' · 满分 ' + p.totalScore + ' 分 · 考试时间 ' + p.durationMin + ' 分钟' + (p.theme ? ' · ' + esc(p.theme) : '') + '</div></div>' +
          '<div class="gd-warn">⚠️ ' + esc(p.notice.replace(/\*\*/g, '')) + '</div>' +
          body +
        '</div>' +
      '</div>';
    $('#gdBack').addEventListener('click', renderGdList);
    bindGdQuestions();
  }

  function renderGdQuestion(q) {
    const key = 'gd' + q.no;
    if (q.type === 'single' || q.type === 'multiple') {
      return '<div class="gd-q" data-q="' + key + '"><div class="gd-q-h"><b>' + q.no + '.</b> ' + esc(q.stem) + '<span class="gd-q-sc">（' + q.score + '分' + (q.type === 'multiple' ? '，多选' : '') + '）</span></div>' +
        q.options.map((o, oi) => '<div class="gd-opt" data-o="' + oi + '">' + 'ABCD'[oi] + '. ' + esc(o) + '</div>').join('') +
        '<div class="gd-res" id="r-' + key + '"></div><div class="gd-ans" id="a-' + key + '" style="display:none"></div></div>';
    }
    return '<div class="gd-q" data-q="' + key + '"><div class="gd-q-h"><b>' + q.no + '.</b> ' + esc(q.stem) + '<span class="gd-q-sc">（' + q.score + '分）</span></div>' +
      '<div class="gd-ans" id="a-' + key + '">' + esc(q.answer) + '</div>' +
      '<div class="gd-res" id="r-' + key + '"></div></div>';
  }

  function bindGdQuestions() {
    const p = GD.cur;
    if (!p) return;
    const all = {};
    p.modules.forEach(m => m.parts.forEach(pt => pt.questions.forEach(q => { all['gd' + q.no] = q; })));
    Object.keys(all).forEach(key => {
      const q = all[key];
      if (q.type !== 'single' && q.type !== 'multiple') return;
      const box = document.querySelector('.gd-q[data-q="' + key + '"]');
      if (!box) return;
      const picked = [];
      box.querySelectorAll('.gd-opt').forEach(el => el.addEventListener('click', () => {
        if (GD.showKey[key]) return;
        const oi = Number(el.dataset.o);
        if (q.type === 'single') {
          picked.length = 0; picked.push(oi);
        } else {
          const k = picked.indexOf(oi);
          if (k >= 0) picked.splice(k, 1); else picked.push(oi);
        }
        box.querySelectorAll('.gd-opt').forEach(x => x.classList.remove('picked'));
        picked.forEach(x => box.querySelector('.gd-opt[data-o="' + x + '"]').classList.add('picked'));
        if (q.type === 'single' || picked.length >= 2) judgeGd(key, q, box, picked);
      }));
    });
  }

  function judgeGd(key, q, box, picked) {
    if (GD.showKey[key]) return;
    GD.showKey[key] = true;
    const ok = q.type === 'single'
      ? (picked.length === 1 && picked[0] === q.answer)
      : (picked.length === q.answer.length && picked.every(x => q.answer.indexOf(x) >= 0));
    box.querySelectorAll('.gd-opt').forEach(x => {
      x.classList.add('locked');
      const oi = Number(x.dataset.o);
      const isAns = q.type === 'single' ? oi === q.answer : q.answer.indexOf(oi) >= 0;
      if (isAns) x.classList.add('right');
      else if (picked.indexOf(oi) >= 0) x.classList.add('wrong');
    });
    const res = document.getElementById('r-' + key);
    const ans = document.getElementById('a-' + key);
    res.className = 'gd-res ' + (ok ? 'ok' : 'bad');
    res.textContent = ok ? '✅ 回答正确' : '❌ 回答错误，正确答案：' + gdAnswerText(q);
    if (ans && q.analysis) { ans.style.display = ''; ans.textContent = '解析：' + q.analysis; }
  }

'''
add(GD_ANCHOR, GD_JS + GD_ANCHOR)

# ---------- 执行 + 断言 ----------
for i, (old, new, n) in enumerate(reps):
    cnt = s.count(old)
    assert cnt == n, "替换未命中或多次命中(#%d): 期望%d次, 实际%d次\nOLD=%r" % (i, n, cnt, old[:70])
    s = s.replace(old, new)

io.open(HTML, 'w', encoding='utf-8').write(s)
print("patched", HTML, len(s), "bytes")
print("DONE")
