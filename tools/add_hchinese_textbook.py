# -*- coding: utf-8 -*-
"""在 public/hchinese.html 基础上新增「📖 课本同步」Tab（人教版五册单元同步）。
改动：
  - SECTIONS 插入 textbook 板块（排在 exam 之前）
  - selectSection 支持 'textbook'（独立整幅渲染）
  - 新增 renderTextbookPage / renderTextbookShell / loadTextbookUnit 渲染器
  - init 的 trial 提示补充课本同步说明
  - 首页卡片描述补充「五册单元同步」
所有替换均断言命中次数。
"""
import io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'public', 'hchinese.html')
DST = os.path.join(ROOT, 'public', 'hchinese.html')

s = io.open(SRC, encoding='utf-8').read()
reps = []
def add(old, new, n=1):
    reps.append((old, new, n))

# 1) SECTIONS 插入 textbook
add("    { k: 'exam', t: '📋 题库组卷', modes: [] },",
    "    { k: 'textbook', t: '📖 课本同步', modes: [] },\n    { k: 'exam', t: '📋 题库组卷', modes: [] },")

# 2) selectSection 支持 textbook
add("""    if (k === 'exam' || k === 'link') {
      // 独立板块：隐藏左侧分组栏，整幅渲染
      $('#sidePane').style.display = 'none';
      $('#mainArea').style.flex = '1 1 100%';
      if (k === 'exam') renderExamPage();
      else renderLinkPage();
      return;
    }""",
    """    if (k === 'exam' || k === 'link' || k === 'textbook') {
      // 独立板块：隐藏左侧分组栏，整幅渲染
      $('#sidePane').style.display = 'none';
      $('#mainArea').style.flex = '1 1 100%';
      if (k === 'exam') renderExamPage();
      else if (k === 'textbook') renderTextbookPage();
      else renderLinkPage();
      return;
    }""")

# 3) itemsOf / renderSide 排除 textbook
add("    if (section === 'exam' || section === 'link') return;\n    const groups = curGroups();",
    "    if (section === 'exam' || section === 'link' || section === 'textbook') return;\n    const groups = curGroups();")

# 4) 键盘翻页不覆盖 textbook
add("    const navMode = (section !== 'exam' && section !== 'link' && mode === 'read');",
    "    const navMode = (section !== 'exam' && section !== 'link' && section !== 'textbook' && mode === 'read');")

# 5) trial 提示补充
add("      $('#trialNote').innerHTML = '🎁 体验模式：每板块可学习第一个分组。输入授权码或联系管理员（微信 13538237315）解锁全部内容。';",
    "      $('#trialNote').innerHTML = '🎁 体验模式：每板块可学习第一个分组，课本同步仅开放每册第 1 单元。输入授权码或联系管理员（微信 13538237315）解锁全部内容。';")

# 6) 默认落地页改为 exam（保持原样，显式断言）
add("    selectSection('exam');", "    selectSection('exam');")

# 7) 插入课本同步渲染器（在「板块：题库组卷」注释之前）
ANCHOR = "  // ================== 板块：题库组卷 =================="
TB = r'''  // ================== 板块：课本同步（人教版五册） ==================
  let TB_DATA = null;      // { books, edition, trial }
  let TB_BOOK = null;      // 当前册
  let TB_UNIT = null;      // 当前单元

  async function renderTextbookPage() {
    $('#mainArea').innerHTML = '<div class="empty">加载中…</div>';
    const r = await api('/api/htextbook');
    if (r.s !== 200) { $('#mainArea').innerHTML = '<div class="err-msg">' + (r.j.error || '加载失败，请登录后重试') + '</div>'; return; }
    TB_DATA = r.j;
    const books = TB_DATA.books || [];
    if (!books.length) { $('#mainArea').innerHTML = '<div class="empty">暂无课本数据</div>'; return; }
    const cards = books.map(b =>
      '<div class="tb-book" data-b="' + esc(b.id) + '">' +
        '<div class="tb-book-hd"><b>' + esc(b.name) + '</b><span class="tb-tag">' + esc(b.term || '') + '</span></div>' +
        '<div class="tb-book-th">' + esc(b.theme || '') + '</div>' +
        '<div class="tb-book-meta">' + (b.unitCount || 0) + ' 个单元 · 点开查看课文与同步练习</div>' +
      '</div>').join('');
    $('#mainArea').innerHTML =
      '<div class="tb-wrap">' +
        '<div class="tb-hd">📖 高中语文 · 课本同步<span class="tb-ed">' + esc(TB_DATA.edition || '') + '</span></div>' +
        '<div class="tb-tip">按教材册 → 单元 → 课文顺序同步：每单元含<b>课文清单</b>、<b>重点字词</b>、<b>必背默写</b>、<b>同步练习</b>。先选册，再选单元。</div>' +
        (TB_DATA.trial ? '<div class="tb-warn">🎁 体验模式：课本同步仅开放每册第 1 单元。输入授权码可解锁全部五册。</div>' : '') +
        '<div class="tb-books">' + cards + '</div>' +
      '</div>';
    document.querySelectorAll('.tb-book').forEach(el => el.addEventListener('click', () => loadTextbookBook(el.dataset.b)));
  }

  async function loadTextbookBook(bookId) {
    $('#mainArea').innerHTML = '<div class="empty">加载中…</div>';
    const r = await api('/api/htextbook?book=' + encodeURIComponent(bookId));
    if (r.s !== 200) { $('#mainArea').innerHTML = '<div class="err-msg">' + (r.j.error || '加载失败') + '</div>'; return; }
    TB_BOOK = r.j.book;
    const units = TB_BOOK.units || [];
    const list = units.map(u =>
      '<div class="tb-unit" data-u="' + esc(u.id) + '">' +
        '<div class="tb-unit-hd"><b>' + esc(u.title) + '</b>' + (u.theme ? '<span class="tb-unit-theme">' + esc(u.theme) + '</span>' : '') + '</div>' +
        '<div class="tb-unit-meta">' + (u.textbooks || []).length + ' 课 · 字词 ' + (u.keywords || []).length + ' · 必背 ' + (u.recite || []).length + ' · 练习 ' + (u.practice || []).length + '</div>' +
        '<div class="tb-unit-tb">' + (u.textbooks || []).map(t => esc(t.title)).join('、') + '</div>' +
      '</div>').join('');
    $('#mainArea').innerHTML =
      '<div class="tb-wrap">' +
        '<div class="tb-hd"><button class="tb-back" id="tbBack">← 返回册列表</button> ' + esc(TB_BOOK.name) + '<span class="tb-ed">' + esc(TB_BOOK.term || '') + '</span></div>' +
        '<div class="tb-tip">本册共 ' + units.length + ' 个单元，点单元查看课文清单、字词、必背与同步练习。</div>' +
        '<div class="tb-units">' + list + '</div>' +
      '</div>';
    $('#tbBack').addEventListener('click', renderTextbookPage);
    document.querySelectorAll('.tb-unit').forEach(el => el.addEventListener('click', () => loadTextbookUnit(el.dataset.u)));
  }

  async function loadTextbookUnit(unitId) {
    $('#mainArea').innerHTML = '<div class="empty">加载中…</div>';
    const r = await api('/api/htextbook?unit=' + encodeURIComponent(unitId));
    if (r.s !== 200) { $('#mainArea').innerHTML = '<div class="err-msg">' + (r.j.error || '加载失败') + '</div>'; return; }
    const u = r.j;
    TB_UNIT = u;

    const tbs = (u.textbooks || []).map((t, i) =>
      '<div class="tb-tb-item' + (t.recite ? ' recite' : '') + '">' +
        '<span class="tb-tb-idx">' + (i + 1) + '</span>' +
        '<span class="tb-tb-title">' + esc(t.title) + '</span>' +
        '<span class="tb-tb-author">' + esc(t.author || '') + '</span>' +
        (t.genre ? '<span class="tb-tb-genre">' + esc(t.genre) + '</span>' : '') +
        (t.recite ? '<span class="tb-tb-recite">📌 必背</span>' : '') +
        (t.note ? '<span class="tb-tb-note">' + esc(t.note) + '</span>' : '') +
      '</div>').join('');

    const kws = (u.keywords || []).map(k =>
      '<div class="tb-kw"><span class="tb-kw-w">' + esc(k.word) + '</span>' +
      (k.pinyin ? '<span class="tb-kw-py">' + esc(k.pinyin) + '</span>' : '') +
      '<span class="tb-kw-js">' + esc(k.jieshi || '') + '</span>' +
      '<button class="tb-kw-say" data-t="' + esc(k.word) + '">🔊</button></div>').join('');

    const rec = (u.recite || []).map(r0 =>
      '<div class="tb-rec">' +
        '<div class="tb-rec-t">' + esc(r0.title) + '<button class="tb-kw-say" data-t="' + esc((r0.lines || []).join('。')) + '">🔊 朗读</button></div>' +
        '<div class="tb-rec-l">' + (r0.lines || []).map(esc).join('<br>') + '</div>' +
      '</div>').join('');

    const prac = (u.practice || []).map((p, pi) => {
      if (p.type === 'fill') {
        return '<div class="tb-pr"><div class="tb-pr-q">' + (pi + 1) + '. ' + esc(p.stem) + '</div>' +
          '<input class="tb-pr-in" data-pi="' + pi + '" placeholder="输入答案">' +
          '<button class="tb-pr-btn" data-pi="' + pi + '">判分</button>' +
          '<span class="tb-pr-res" id="tbRes' + pi + '"></span>' +
          '<div class="tb-pr-a" id="tbAn' + pi + '">' + esc(p.analysis) + '</div></div>';
      }
      return '<div class="tb-pr"><div class="tb-pr-q">' + (pi + 1) + '. ' + esc(p.stem) + '</div>' +
        '<div class="tb-pr-opts" id="tbOp' + pi + '">' + p.options.map((o, oi) =>
          '<div class="tb-pr-o" data-pi="' + pi + '" data-oi="' + oi + '">' + esc(o) + '</div>').join('') + '</div>' +
        '<div class="tb-pr-res" id="tbRes' + pi + '"></div>' +
        '<div class="tb-pr-a" id="tbAn' + pi + '">' + esc(p.analysis) + '</div></div>';
    }).join('');

    $('#mainArea').innerHTML =
      '<div class="tb-wrap">' +
        '<div class="tb-hd"><button class="tb-back" id="tbBack">← 返回</button> ' + esc(u.title) + (u.theme ? '　<span class="tb-ed">' + esc(u.theme) + '</span>' : '') + '</div>' +

        '<div class="tb-card"><div class="tb-card-h">📚 课文清单<span class="tb-card-n">' + (u.textbooks || []).length + ' 课</span></div>' +
          '<div class="tb-tbs">' + (tbs || '<div class="tb-empty">本单元为学习活动，无课文清单</div>') + '</div></div>' +

        '<div class="tb-card"><div class="tb-card-h">🔤 重点字词<span class="tb-card-n">' + (u.keywords || []).length + ' 个</span></div>' +
          '<div class="tb-kws">' + (kws || '<div class="tb-empty">本单元无专门字词表</div>') + '</div></div>' +

        '<div class="tb-card"><div class="tb-card-h">✍️ 必背默写<span class="tb-card-n">' + (u.recite || []).length + ' 篇</span></div>' +
          '<div class="tb-recs">' + (rec || '<div class="tb-empty">本单元无背诵要求</div>') + '</div></div>' +

        '<div class="tb-card"><div class="tb-card-h">✅ 同步练习<span class="tb-card-n">' + (u.practice || []).length + ' 题</span></div>' +
          '<div class="tb-prs">' + (prac || '<div class="tb-empty">本单元暂无练习</div>') + '</div></div>' +
      '</div>';

    $('#tbBack').addEventListener('click', () => loadTextbookBook(TB_BOOK.id));

    // 朗读
    document.querySelectorAll('.tb-kw-say').forEach(b => b.addEventListener('click', () => speak(b.dataset.t)));
    // 填空判分
    (u.practice || []).forEach((p, pi) => {
      if (p.type !== 'fill') return;
      const btn = document.querySelector('.tb-pr-btn[data-pi="' + pi + '"]');
      if (!btn) return;
      btn.addEventListener('click', () => {
        const inp = document.querySelector('.tb-pr-in[data-pi="' + pi + '"]');
        const val = (inp.value || '').trim();
        const ok = val && val === String(p.answer).trim();
        const res = document.getElementById('tbRes' + pi);
        res.textContent = ok ? '✅ 正确！' : ('❌ 正确答案：' + p.answer);
        res.className = 'tb-pr-res ' + (ok ? 'ok' : 'bad');
        document.getElementById('tbAn' + pi).style.display = 'block';
      });
    });
    // 选择判分
    (u.practice || []).forEach((p, pi) => {
      if (p.type === 'fill') return;
      const box = document.getElementById('tbOp' + pi);
      if (!box) return;
      box.querySelectorAll('.tb-pr-o').forEach(o => o.addEventListener('click', () => {
        if (box.dataset.locked) return;
        box.dataset.locked = '1';
        const oi = Number(o.dataset.oi);
        const ok = oi === p.answer;
        box.querySelectorAll('.tb-pr-o').forEach(x => {
          if (Number(x.dataset.oi) === p.answer) x.classList.add('right');
          else if (x === o) x.classList.add('wrong');
        });
        const res = document.getElementById('tbRes' + pi);
        res.textContent = ok ? '✅ 正确！' : ('❌ 正确答案：' + String.fromCharCode(65 + p.answer));
        res.className = 'tb-pr-res ' + (ok ? 'ok' : 'bad');
        document.getElementById('tbAn' + pi).style.display = 'block';
      }));
    });
  }

'''
add(ANCHOR, TB + ANCHOR)

# 8) 追加课本同步 CSS
CSS_ANCHOR = "  /* —— 题库组卷 / 高考衔接 专用 —— */"
TB_CSS = """  /* —— 课本同步 —— */
  .tb-wrap { max-width:1000px; }
  .tb-hd { font-size:18px; font-weight:800; margin-bottom:10px; display:flex; align-items:center; gap:10px; flex-wrap:wrap; }
  .tb-ed { font-size:12px; font-weight:500; color:#8e44ad; background:#f5eefa; padding:3px 10px; border-radius:12px; }
  .tb-back { border:none; background:#f5eefa; color:#8e44ad; font-size:13px; font-weight:700; padding:6px 12px; border-radius:14px; cursor:pointer; }
  .tb-back:hover { background:#efe4f7; }
  .tb-tip { font-size:12.5px; color:#666; background:#fff; border:1px solid #f0e6f9; border-radius:12px; padding:10px 14px; margin-bottom:12px; line-height:1.7; }
  .tb-tip b { color:#8e44ad; }
  .tb-warn { font-size:12.5px; color:#7a5c00; background:#fffbe8; border:1px solid #f3e6b8; border-radius:12px; padding:10px 14px; margin-bottom:12px; }
  .tb-books { display:flex; gap:12px; flex-wrap:wrap; }
  .tb-book { flex:1 1 300px; background:#fff; border:1.5px solid #f0e6f9; border-radius:16px; padding:16px; cursor:pointer; transition:border-color .15s, box-shadow .15s; }
  .tb-book:hover { border-color:#8e44ad; box-shadow:0 6px 20px rgba(142,68,173,.12); }
  .tb-book-hd { display:flex; align-items:center; gap:8px; font-size:16px; font-weight:800; }
  .tb-tag { font-size:11px; font-weight:600; color:#8e44ad; background:#f5eefa; padding:2px 8px; border-radius:10px; }
  .tb-book-th { font-size:12.5px; color:#888; margin-top:6px; }
  .tb-book-meta { font-size:12px; color:#aaa; margin-top:8px; }
  .tb-units { display:flex; gap:10px; flex-direction:column; }
  .tb-unit { background:#fff; border:1.5px solid #f0e6f9; border-radius:14px; padding:13px 15px; cursor:pointer; }
  .tb-unit:hover { border-color:#8e44ad; }
  .tb-unit-hd { font-size:15px; font-weight:700; display:flex; align-items:center; gap:8px; flex-wrap:wrap; }
  .tb-unit-theme { font-size:12px; font-weight:600; color:#8e44ad; background:#f5eefa; padding:2px 9px; border-radius:10px; }
  .tb-unit-meta { font-size:12px; color:#aaa; margin-top:5px; }
  .tb-unit-tb { font-size:12.5px; color:#666; margin-top:6px; line-height:1.7; }
  .tb-card { background:#fff; border-radius:16px; padding:16px; margin-bottom:14px; box-shadow:0 4px 16px rgba(0,0,0,.05); }
  .tb-card-h { font-size:15px; font-weight:800; margin-bottom:12px; display:flex; align-items:center; gap:8px; }
  .tb-card-n { font-size:11.5px; font-weight:600; color:#8e44ad; background:#f5eefa; padding:2px 9px; border-radius:10px; }
  .tb-tbs { display:flex; flex-direction:column; gap:8px; }
  .tb-tb-item { display:flex; align-items:center; gap:8px; flex-wrap:wrap; background:#faf8fc; border-radius:10px; padding:9px 12px; font-size:13.5px; }
  .tb-tb-item.recite { background:#f5eefa; }
  .tb-tb-idx { width:20px; height:20px; border-radius:50%; background:#e0d4ec; color:#fff; font-size:11px; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
  .tb-tb-title { font-weight:700; }
  .tb-tb-author { color:#888; font-size:12.5px; }
  .tb-tb-genre { color:#8e44ad; font-size:11.5px; background:#fff; padding:1px 7px; border-radius:8px; border:1px solid #e0d4ec; }
  .tb-tb-recite { color:#b8860b; font-size:11.5px; font-weight:700; }
  .tb-tb-note { color:#aaa; font-size:11.5px; }
  .tb-kws { display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); gap:8px; }
  .tb-kw { display:flex; align-items:baseline; gap:7px; flex-wrap:wrap; background:#faf8fc; border-radius:10px; padding:9px 12px; }
  .tb-kw-w { font-size:15px; font-weight:800; }
  .tb-kw-py { font-size:12px; color:#8e44ad; }
  .tb-kw-js { font-size:12.5px; color:#666; flex:1; }
  .tb-kw-say { border:none; background:#f5eefa; color:#8e44ad; border-radius:10px; padding:2px 8px; font-size:12px; cursor:pointer; }
  .tb-recs { display:flex; flex-direction:column; gap:10px; }
  .tb-rec { background:#faf8fc; border-left:3px solid #8e44ad; border-radius:0 10px 10px 0; padding:10px 13px; }
  .tb-rec-t { font-size:14px; font-weight:700; margin-bottom:6px; display:flex; align-items:center; gap:8px; }
  .tb-rec-l { font-size:13.5px; line-height:2; color:#444; }
  .tb-prs { display:flex; flex-direction:column; gap:14px; }
  .tb-pr { border-bottom:1px solid #f4eef8; padding-bottom:12px; }
  .tb-pr:last-child { border-bottom:none; }
  .tb-pr-q { font-size:14px; font-weight:700; line-height:1.8; margin-bottom:8px; }
  .tb-pr-o { background:#faf8fc; border:1.5px solid transparent; border-radius:10px; padding:8px 12px; font-size:13.5px; cursor:pointer; margin-bottom:6px; }
  .tb-pr-o:hover { border-color:#c9a8dc; }
  .tb-pr-o.right { background:#e8f8ee; border-color:#2a8; color:#1a6b37; font-weight:700; }
  .tb-pr-o.wrong { background:#fdecec; border-color:#e23; color:#a12626; }
  .tb-pr-in { width:70%; padding:9px 12px; border:1px solid #e0d4ec; border-radius:10px; font-size:14px; }
  .tb-pr-btn { margin-left:8px; padding:9px 18px; border:none; border-radius:10px; background:#8e44ad; color:#fff; font-size:13.5px; font-weight:700; cursor:pointer; }
  .tb-pr-btn:hover { background:#7d3c98; }
  .tb-pr-res { display:inline-block; margin-left:10px; font-size:13px; font-weight:700; }
  .tb-pr-res.ok { color:#2a8; }
  .tb-pr-res.bad { color:#e23; }
  .tb-pr-a { display:none; margin-top:8px; font-size:12.5px; color:#888; background:#faf8fc; border-radius:10px; padding:9px 12px; line-height:1.8; }
  .tb-empty { font-size:12.5px; color:#aaa; padding:8px 0; }

"""
add(CSS_ANCHOR, TB_CSS + CSS_ANCHOR)

# 执行 + 断言
for i, (old, new, n) in enumerate(reps):
    cnt = s.count(old)
    if n != 0:
        assert cnt == n, "替换未命中或多次命中(#%d): 期望%d 实际%d\nOLD=%r" % (i, n, cnt, old[:70])
    s = s.replace(old, new, n)

io.open(DST, 'w', encoding='utf-8').write(s)
print("updated", DST, len(s), "bytes")
print("DONE")
