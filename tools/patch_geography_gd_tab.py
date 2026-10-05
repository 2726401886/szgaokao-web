# -*- coding: utf-8 -*-
"""geography.html 增加「📄 广东高考卷」板块（2024 真题）。
渲染器逻辑参照 politics.html 的 GD 板块，样式改地理蓝绿主色。
改动点（全部断言命中）：
  1) CSS 追加 gd2-* 样式（蓝绿 #0e7490 系）
  2) SECTIONS 新增 { k:'gd' }
  3) selectSection 走整幅渲染分支
  4) renderSide 跳过 gd
  5) 插入 GD 渲染器（含 figure 图表文字描述的展示）
  6) 「返回首页」链接保持不变
用法：python tools/patch_geography_gd_tab.py
"""
import io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, 'public', 'geography.html')

s = io.open(HTML, encoding='utf-8').read()
reps = []


def add(old, new, n=1):
    reps.append((old, new, n))


# ---------- 1) CSS ----------
CSS_ANCHOR = "  .read-text { font-size:15px;"
GD_CSS = """  /* ===== 广东高考卷（真题） ===== */
  .gd2-wrap { max-width:1000px; }
  .gd2-hd { font-size:18px; font-weight:800; margin-bottom:10px; display:flex; align-items:center; gap:10px; flex-wrap:wrap; }
  .gd2-back { border:none; background:#ecfeff; color:#0e7490; font-size:13px; font-weight:700; padding:6px 12px; border-radius:14px; cursor:pointer; }
  .gd2-ed { font-size:12px; font-weight:500; color:#0e7490; background:#ecfeff; padding:3px 10px; border-radius:12px; }
  .gd2-warn { font-size:12.5px; color:#7a5c00; background:#fffbe8; border:1px solid #f3e6b8; border-radius:12px; padding:10px 14px; margin-bottom:12px; line-height:1.8; }
  .gd2-tip { font-size:12.5px; color:#1a56db; background:#eff6ff; border:1px solid #c9d6ff; border-radius:12px; padding:10px 14px; margin-bottom:12px; line-height:1.8; }
  .gd2-st-h { font-size:14px; font-weight:800; margin:14px 0 8px; }
  .gd2-cards { display:flex; gap:12px; flex-wrap:wrap; }
  .gd2-card { flex:1 1 290px; background:#fff; border:1.5px solid #cffafe; border-radius:14px; padding:14px; cursor:pointer; display:flex; gap:12px; align-items:center; }
  .gd2-card:hover { border-color:#0e7490; box-shadow:0 6px 20px rgba(14,116,144,.12); }
  .gd2-card-y { font-size:20px; font-weight:800; color:#0e7490; background:#ecfeff; border-radius:12px; padding:10px 12px; }
  .gd2-card-b { flex:1; }
  .gd2-card-t { font-size:14.5px; font-weight:700; }
  .gd2-card-m { font-size:12px; color:#999; margin-top:4px; }
  .gd2-card-go { font-size:12px; color:#0e7490; font-weight:700; white-space:nowrap; }
  .gd2-paper { background:#fff; border-radius:16px; padding:20px 18px; box-shadow:0 4px 16px rgba(0,0,0,.05); }
  .gd2-p-hd { text-align:center; border-bottom:2px solid #0e7490; padding-bottom:12px; margin-bottom:16px; }
  .gd2-p-name { font-size:19px; font-weight:800; }
  .gd2-p-meta { font-size:12.5px; color:#666; margin-top:6px; }
  .gd2-mod { margin-bottom:20px; }
  .gd2-mod-h { font-size:15.5px; font-weight:800; margin-bottom:6px; }
  .gd2-mod-sc { font-size:12px; font-weight:600; color:#0e7490; background:#ecfeff; padding:2px 9px; border-radius:10px; margin-left:8px; }
  .gd2-mod-note { font-size:11.5px; color:#999; margin-bottom:8px; }
  .gd2-part { margin:12px 0 12px 12px; }
  .gd2-part-h { font-size:13.5px; font-weight:700; color:#444; margin-bottom:6px; }
  .gd2-q { margin:12px 0 12px 4px; }
  .gd2-q-h { font-size:14px; line-height:1.8; margin-bottom:6px; }
  .gd2-q-sc { font-size:11.5px; color:#999; margin-left:6px; }
  .gd2-fig { font-size:12.5px; color:#555; background:#f0fdff; border:1px dashed #a5d8e6; border-radius:10px; padding:9px 11px; margin:6px 0; line-height:1.8; }
  .gd2-fig b { color:#0e7490; }
  .gd2-opt { display:block; padding:7px 10px; border:1.5px solid #eee; border-radius:10px; margin:5px 0; cursor:pointer; font-size:13.5px; line-height:1.7; }
  .gd2-opt:hover { border-color:#7fc7d9; background:#f6feff; }
  .gd2-opt.locked { cursor:default; }
  .gd2-opt.right { border-color:#2a8; background:#eefaf5; }
  .gd2-opt.wrong { border-color:#e23; background:#fdeeee; }
  .gd2-opt.picked { border-color:#0e7490; background:#ecfeff; }
  .gd2-res { font-size:12.5px; margin-top:5px; line-height:1.7; }
  .gd2-res.ok { color:#2a8; }
  .gd2-res.bad { color:#e23; }
  .gd2-ans { background:#f8f9fc; border:1px solid #eceef3; border-radius:10px; padding:9px 11px; font-size:12.5px; color:#444; line-height:1.8; margin-top:6px; white-space:pre-wrap; }
"""
add(CSS_ANCHOR, GD_CSS + CSS_ANCHOR)

# ---------- 2) SECTIONS ----------
add("""    { k: 'link', t: '🧩 专题突破', modes: [] },
  ];""",
    """    { k: 'link', t: '🧩 专题突破', modes: [] },
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

# ---------- 5) GD 渲染器 ----------
GD_ANCHOR = "  // ================== 板块：题库组卷 =================="
GD_JS = r'''  // ================== 板块：广东高考卷（真题） ==================
  let GD2 = { loaded: false, meta: null, papers: [], cur: null, showKey: {} };

  async function renderGdPage() {
    $('#mainArea').innerHTML = '<div class="gd2-wrap"><div class="empty">加载中…</div></div>';
    if (!GD2.loaded) {
      const r = await api('/api/geography-gd');
      if (r.s !== 200) { $('#mainArea').innerHTML = '<div class="empty">加载失败，请稍后重试</div>'; return; }
      GD2.loaded = true; GD2.meta = r.j; GD2.papers = r.j.papers || [];
    }
    renderGdList();
  }

  function renderGdList() {
    const m = GD2.meta;
    $('#mainArea').innerHTML =
      '<div class="gd2-wrap">' +
        '<div class="gd2-hd">📄 广东省高考地理 · 真题练习<span class="gd2-ed">真题原卷</span></div>' +
        (m.notice ? '<div class="gd2-warn">⚠️ ' + esc(m.notice.replace(/\*\*/g, '')) + '</div>' : '') +
        '<div class="gd2-tip">本卷为广东省普通高中学业水平选择性考试真题，<b>题干与选项为真题原文</b>，图表已转为文字描述。<b>答案为参考解析，非官方标准答案</b>，建议配合官方答案册核对。</div>' +
        '<div class="gd2-st-h">📋 试卷结构</div>' +
        '<div class="gd2-cards" style="margin-bottom:16px;">' +
          m.structure.map(st => '<div class="gd2-card" style="cursor:default;"><div class="gd2-card-y" style="font-size:13px;">' + st.score + '</div>' +
            '<div class="gd2-card-b"><div class="gd2-card-t">' + esc(st.name) + '</div><div class="gd2-card-m">' + esc(st.detail) + '</div></div></div>').join('') +
        '</div>' +
        '<div class="gd2-st-h">📚 可选试卷（' + GD2.papers.length + ' 套）</div>' +
        '<div class="gd2-cards">' +
          GD2.papers.map(p => '<div class="gd2-card" data-p="' + p.id + '"><div class="gd2-card-y">' + p.year + '</div>' +
            '<div class="gd2-card-b"><div class="gd2-card-t">' + esc(p.title) + '</div>' +
            '<div class="gd2-card-m">' + p.totalScore + '分 · ' + p.durationMin + '分钟 · ' + p.questionCount + '题' + (p.theme ? ' · ' + esc(p.theme) : '') + '</div></div>' +
            '<div class="gd2-card-go">开始 →</div></div>').join('') +
        '</div>' +
      '</div>';
    document.querySelectorAll('.gd2-card[data-p]').forEach(el => el.addEventListener('click', () => openGdPaper(el.dataset.p)));
  }

  async function openGdPaper(pid) {
    $('#mainArea').innerHTML = '<div class="gd2-wrap"><div class="empty">加载中…</div></div>';
    const r = await api('/api/geography-gd?paper=' + encodeURIComponent(pid));
    if (r.s !== 200) { $('#mainArea').innerHTML = '<div class="empty">试卷加载失败</div>'; return; }
    GD2.cur = r.j;
    GD2.showKey = {};
    renderGdPaper();
  }

  function renderGdPaper() {
    const p = GD2.cur;
    const body = p.modules.map(m =>
      '<div class="gd2-mod"><div class="gd2-mod-h">' + esc(m.name) + '<span class="gd2-mod-sc">' + m.score + '分</span></div>' +
      '<div class="gd2-mod-note">' + esc(m.note || '') + '</div>' +
      m.parts.map(pt =>
        '<div class="gd2-part">' + (m.parts.length > 1 ? '<div class="gd2-part-h">' + esc(pt.name) + '（' + pt.score + '分）</div>' : '') +
        pt.questions.map(q => renderGdQuestion(q)).join('') +
        '</div>').join('') +
      '</div>').join('');
    $('#mainArea').innerHTML =
      '<div class="gd2-wrap">' +
        '<div class="gd2-hd"><button class="gd2-back" id="gdBack">← 返回试卷列表</button><span class="gd2-ed">真题原卷</span></div>' +
        '<div class="gd2-paper">' +
          '<div class="gd2-p-hd"><div class="gd2-p-name">' + esc(p.title) + '</div>' +
            '<div class="gd2-p-meta">' + esc(p.examType) + ' · 满分 ' + p.totalScore + ' 分 · 考试时间 ' + p.durationMin + ' 分钟</div></div>' +
          '<div class="gd2-warn">⚠️ ' + esc(p.notice.replace(/\*\*/g, '')) + '</div>' +
          body +
        '</div>' +
      '</div>';
    $('#gdBack').addEventListener('click', renderGdList);
    bindGdQuestions();
  }

  function renderGdQuestion(q) {
    const key = 'gd2' + q.no;
    const fig = q.figure ? '<div class="gd2-fig"><b>【图表说明】</b>' + esc(q.figure) + '</div>' : '';
    if (q.type === 'single') {
      return '<div class="gd2-q" data-q="' + key + '"><div class="gd2-q-h"><b>' + q.no + '.</b> ' + esc(q.stem) + '<span class="gd2-q-sc">（' + q.score + '分）</span></div>' +
        fig +
        q.options.map((o, oi) => '<div class="gd2-opt" data-o="' + oi + '">' + 'ABCD'[oi] + '. ' + esc(o) + '</div>').join('') +
        '<div class="gd2-res" id="r-' + key + '"></div><div class="gd2-ans" id="a-' + key + '" style="display:none"></div></div>';
    }
    return '<div class="gd2-q" data-q="' + key + '"><div class="gd2-q-h"><b>' + q.no + '.</b> ' + esc(q.stem) + '<span class="gd2-q-sc">（' + q.score + '分）</span></div>' +
      fig +
      '<div class="gd2-ans" id="a-' + key + '">' + esc(q.answer) + '</div>' +
      '<div class="gd2-res" id="r-' + key + '"></div></div>';
  }

  function bindGdQuestions() {
    const p = GD2.cur;
    if (!p) return;
    const all = {};
    p.modules.forEach(m => m.parts.forEach(pt => pt.questions.forEach(q => { all['gd2' + q.no] = q; })));
    Object.keys(all).forEach(key => {
      const q = all[key];
      if (q.type !== 'single') return;
      const box = document.querySelector('.gd2-q[data-q="' + key + '"]');
      if (!box) return;
      const picked = [];
      box.querySelectorAll('.gd2-opt').forEach(el => el.addEventListener('click', () => {
        if (GD2.showKey[key]) return;
        const oi = Number(el.dataset.o);
        if (picked.length && picked[0] === oi) return;
        picked.length = 0; picked.push(oi);
        box.querySelectorAll('.gd2-opt').forEach(x => x.classList.remove('picked'));
        box.querySelector('.gd2-opt[data-o="' + oi + '"]').classList.add('picked');
        judgeGd(key, q, box, picked);
      }));
    });
  }

  function judgeGd(key, q, box, picked) {
    if (GD2.showKey[key]) return;
    GD2.showKey[key] = true;
    const ok = picked.length === 1 && picked[0] === q.answer;
    box.querySelectorAll('.gd2-opt').forEach(x => {
      x.classList.add('locked');
      const oi = Number(x.dataset.o);
      if (oi === q.answer) x.classList.add('right');
      else if (picked.indexOf(oi) >= 0) x.classList.add('wrong');
    });
    const res = document.getElementById('r-' + key);
    const ans = document.getElementById('a-' + key);
    res.className = 'gd2-res ' + (ok ? 'ok' : 'bad');
    res.textContent = ok ? '✅ 回答正确' : '❌ 回答错误，正确答案：' + 'ABCD'[q.answer];
    if (ans && q.analysis) { ans.style.display = ''; ans.textContent = '【参考解析】' + q.analysis; }
  }

'''
add(GD_ANCHOR, GD_JS + GD_ANCHOR)

# ---------- 执行 + 断言 ----------
for i, (old, new, n) in enumerate(reps):
    cnt = s.count(old)
    assert cnt == n, "替换未命中或多次命中(#%d): 期望%d次, 实际%d次\nOLD=%r" % (i, n, cnt, old[:60])
    s = s.replace(old, new)

# ---------- 收尾校验 ----------
assert '/api/politics' not in s, '残留 politics API'
assert 'renderGdPage' in s, 'GD 渲染器未插入'
assert "GD2.papers = r.j.papers" in s, 'GD2.papers 未赋值（会导致列表空白）'

io.open(HTML, 'w', encoding='utf-8').write(s)
print("patched", HTML, len(s), "bytes")
print("DONE")
