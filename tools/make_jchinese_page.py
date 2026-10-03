# -*- coding: utf-8 -*-
"""由 public/chinese.html 克隆生成 public/jchinese.html（初中语文）
改动点：
  - 标题 / 顶栏文案 / 品牌色（绿→蓝靛）
  - PROG_KEY
  - SECTIONS：4 学习板块 → 6 板块（字词/古诗文/文言文/现代文/名著/写作）+ exam + link
  - init API：/api/chinese → /api/jchinese
  - itemsOf / renderMain 分发
  - 增：renderZiRead 释义行、renderGuwenRead / renderClassicRead / renderWritingRead
  - exam：年级筛选项 1-6 → 初一/初二/初三；模板改名；默认卷名 初中语文
  - link：/api/chinese-link → /api/jchinese-link；文案 小升初→中考
  - 键盘翻页 navMode 泛化
所有替换均断言命中，未命中则报错。
"""
import io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'public', 'chinese.html')
DST = os.path.join(ROOT, 'public', 'jchinese.html')

s = io.open(SRC, encoding='utf-8').read()
reps = []

def add(old, new, n=1):
    reps.append((old, new, n))

# —— 文案 / 标题 / 品牌 ——
add('<title>小学语文 · 拼音识字古诗阅读</title>',
    '<title>初中语文 · 字词古诗文文言文阅读名著写作</title>')
add('      <h1>📚 小学语文 · 拼音识字古诗阅读</h1>',
    '      <h1>📚 初中语文 · 字词古诗文文言文阅读名著写作</h1>')
add('      <div class="sub">汉语拼音 · 识字写字 · 古诗文积累 · 阅读理解（点 🔊 可听读）</div>',
    '      <div class="sub">字词积累 · 古诗文默写赏析 · 文言文 · 现代文阅读 · 名著导读 · 写作（点 🔊 可听读）</div>')
add("  const PROG_KEY = 'chinese_progress';",
    "  const PROG_KEY = 'jchinese_progress';")

# —— SECTIONS 4→6 ——
OLD_SECTIONS = """  const SECTIONS = [
    { k: 'pinyin', t: '🔤 汉语拼音', modes: [
        { k: 'read', t: '📖 认读' }, { k: 'quiz', t: '🎯 辨析' } ] },
    { k: 'zi', t: '✍️ 识字写字', modes: [
        { k: 'read', t: '📖 认读' }, { k: 'spell', t: '✍️ 看拼音写汉字' }, { k: 'pick', t: '🔍 选拼音' } ] },
    { k: 'poem', t: '📜 古诗文', modes: [
        { k: 'read', t: '📖 诵读' }, { k: 'link', t: '🔗 接句' }, { k: 'who', t: '🧠 作者朝代' } ] },
    { k: 'read', t: '📝 阅读理解', modes: [
        { k: 'do', t: '✏️ 答题' } ] },
    { k: 'exam', t: '📋 题库组卷', modes: [] },
    { k: 'link', t: '🌉 小升初衔接', modes: [] },
  ];"""
NEW_SECTIONS = """  const SECTIONS = [
    { k: 'zi', t: '🔤 字词积累', modes: [
        { k: 'read', t: '📖 认读' }, { k: 'pick', t: '🔍 选拼音' } ] },
    { k: 'poem', t: '📜 古诗文', modes: [
        { k: 'read', t: '📖 诵读' }, { k: 'link', t: '🔗 接句' }, { k: 'who', t: '🧠 作者朝代' } ] },
    { k: 'guwen', t: '📿 文言文', modes: [
        { k: 'read', t: '📖 精讲+考点' } ] },
    { k: 'read', t: '📝 现代文阅读', modes: [
        { k: 'do', t: '✏️ 答题' } ] },
    { k: 'classic', t: '📚 名著导读', modes: [
        { k: 'read', t: '📖 导读+考点' } ] },
    { k: 'writing', t: '✍️ 写作指导', modes: [
        { k: 'read', t: '📖 范文赏析' } ] },
    { k: 'exam', t: '📋 题库组卷', modes: [] },
    { k: 'link', t: '🌉 中考衔接', modes: [] },
  ];"""
add(OLD_SECTIONS, NEW_SECTIONS)

# —— init API ——
add("    const r = await api('/api/chinese');",
    "    const r = await api('/api/jchinese');")

# —— itemsOf ——
OLD_ITEMS = """  function itemsOf(g) {
    if (section === 'pinyin') return g.items || [];
    if (section === 'zi') return g.words || [];
    if (section === 'poem') return g.poems || [];
    if (section === 'read') return g.passages || [];
    return [];
  }"""
NEW_ITEMS = """  function itemsOf(g) {
    if (section === 'zi') return g.words || [];
    if (section === 'poem') return g.poems || [];
    if (section === 'guwen') return g.passages || [];
    if (section === 'read') return g.passages || [];
    if (section === 'classic') return g.books || [];
    if (section === 'writing') return g.topics || [];
    return [];
  }"""
add(OLD_ITEMS, NEW_ITEMS)

# —— renderMain 分发 ——
OLD_RM = """  function renderMain() {
    const card = $('#modeCard');
    if (section === 'pinyin') {      if (mode === 'read') renderPyRead(card);
      else renderPyQuiz(card);
    } else if (section === 'zi') {
      if (mode === 'read') renderZiRead(card);
      else if (mode === 'spell') renderZiSpell(card);
      else renderZiPick(card);
    } else if (section === 'poem') {
      if (mode === 'read') renderPoemRead(card);
      else if (mode === 'link') renderPoemLink(card);
      else renderPoemWho(card);
    } else if (section === 'read') {
      renderReadDo(card);
    }
  }"""
NEW_RM = """  function renderMain() {
    const card = $('#modeCard');
    if (section === 'zi') {
      if (mode === 'read') renderZiRead(card);
      else renderZiPick(card);
    } else if (section === 'poem') {
      if (mode === 'read') renderPoemRead(card);
      else if (mode === 'link') renderPoemLink(card);
      else renderPoemWho(card);
    } else if (section === 'guwen') {
      renderGuwenRead(card);
    } else if (section === 'read') {
      renderReadDo(card);
    } else if (section === 'classic') {
      renderClassicRead(card);
    } else if (section === 'writing') {
      renderWritingRead(card);
    }
  }"""
add(OLD_RM, NEW_RM)

# —— renderZiRead 增加释义行 ——
add("        '<div class=\"jx\">例句：' + esc(w.juxing) + '</div>' +",
    "        '<div class=\"jx\">例句：' + esc(w.juxing) + '</div>' + (w.jieshi ? '<div class=\"jx\">释义：' + esc(w.jieshi) + '</div>' : '') +")

# —— 插入三个新课型渲染器（在题库组卷注释之前）——
ANCHOR = "  // ================== 板块：题库组卷 =================="
NEW_RENDERERS = r'''  // ===== 文言文：精讲 + 考点 =====
  function renderGuwenRead(card) {
    const ps = itemsOf(curGroup); const p = ps[idx]; const total = ps.length;
    const mc = masteredCount(section, ps.map(x => x.id));
    const zhushi = Object.keys(p.zhushi || {}).map(k => '<span class="pill" style="background:#eef2ff;color:#3b5bdb;">' + esc(k) + '</span> ' + esc(p.zhushi[k])).join('；');
    const kao = (p.kaodian || []).map((q, qi) => {
      return '<div style="margin-top:12px;"><div class="qtext">' + (qi + 1) + '. ' + esc(q.q) + '</div>' +
        '<div id="gbox-' + qi + '">' + q.options.map((o, oi) => '<div class="opt" data-q="' + qi + '" data-o="' + oi + '">' + esc(o) + '</div>').join('') +
        '<div class="result" id="gRes-' + qi + '"></div></div>';
    }).join('');
    card.innerHTML =
      '<div class="group-title">' + curGroup.title + ' · 第 ' + (idx + 1) + ' / ' + total + ' · 已掌握 ' + mc + '/' + total + '</div>' +
      '<div style="font-weight:700;font-size:15px;margin-bottom:6px;">📿 《' + esc(p.title) + '》　<span style="font-size:12px;color:#888;">' + esc(p.source || '') + '</span></div>' +
      '<div class="read-text">' + p.lines.map(l => esc(l)).join('<br>') + '</div>' +
      (zhushi ? '<div class="notes">📖 词语注释：' + zhushi + '</div>' : '') +
      (p.fanyi ? '<div class="notes" style="background:#f5f8ff;">🔁 参考译文：' + esc(p.fanyi) + '</div>' : '') +
      (kao ? '<div style="margin-top:14px;font-weight:700;">📝 考点自测：</div>' + kao : '') +
      '<div class="play-row"><button class="play" id="playBtn">🔊 朗读原文</button></div>' +
      '<div class="prog-bar"><i style="width:' + ((idx + 1) / total * 100) + '%"></i></div>' +
      '<div class="prog-txt">' + (idx + 1) + ' / ' + total + '</div>' +
      '<div class="navbtns"><button id="prevBtn" ' + (idx === 0 ? 'disabled' : '') + '>← 上一篇</button><button id="markBtn">✅ 标记掌握</button><button id="nextBtn" class="primary" ' + (idx >= total - 1 ? 'disabled' : '') + '>下一篇 →</button></div>';
    $('#playBtn').addEventListener('click', () => speak(p.lines.join(' ')));
    $('#markBtn').addEventListener('click', () => markMastered(section, p.id));
    (p.kaodian || []).forEach((q, qi) => {
      const box = $('#gbox-' + qi);
      box.querySelectorAll('.opt').forEach(el => el.addEventListener('click', () => {
        if (el.classList.contains('locked')) return;
        box.querySelectorAll('.opt').forEach(x => x.classList.add('locked'));
        const ok = Number(el.dataset.o) === q.answer;
        if (ok) { el.classList.add('right'); markMastered(section, p.id); } else { el.classList.add('wrong'); box.querySelectorAll('.opt').forEach(x => { if (Number(x.dataset.o) === q.answer) x.classList.add('right'); }); }
        $('#gRes-' + qi).textContent = ok ? '✅ 正确！' : '❌ 正确答案：' + q.options[q.answer];
        $('#gRes-' + qi).className = 'result ' + (ok ? 'ok' : 'bad');
      }));
    });
    bindNav(total);
  }

  // ===== 名著导读：导读 + 考点 =====
  function renderClassicRead(card) {
    const bs = itemsOf(curGroup); const b = bs[idx]; const total = bs.length;
    const mc = masteredCount(section, bs.map(x => x.id));
    const renwu = (b.renwu || []).map(r => '<span class="pill" style="background:#eef2ff;color:#3b5bdb;">' + esc(r) + '</span>').join(' ');
    const kao = (b.kaodian || []).map((q, qi) => {
      return '<div style="margin-top:12px;"><div class="qtext">' + (qi + 1) + '. ' + esc(q.q) + '</div>' +
        '<div id="cbox-' + qi + '">' + q.options.map((o, oi) => '<div class="opt" data-q="' + qi + '" data-o="' + oi + '">' + esc(o) + '</div>').join('') +
        '<div class="result" id="cRes-' + qi + '"></div></div>';
    }).join('');
    card.innerHTML =
      '<div class="group-title">' + curGroup.title + ' · 第 ' + (idx + 1) + ' / ' + total + ' · 已掌握 ' + mc + '/' + total + '</div>' +
      '<div class="hero" style="text-align:left;padding:14px;">' +
        '<div class="big" style="font-size:26px;color:#3b5bdb;">《' + esc(b.title) + '》</div>' +
        '<div class="ph">作者：' + esc(b.author) + '　' + esc(b.period || '') + '</div>' +
        '<div class="jx" style="margin-top:10px;line-height:1.8;">' + esc(b.jianjie) + '</div>' +
        (renwu ? '<div style="margin-top:10px;font-size:13px;color:#666;">主要人物：' + renwu + '</div>' : '') +
      '</div>' +
      (kao ? '<div style="margin-top:14px;font-weight:700;">📝 考点自测：</div>' + kao : '') +
      '<div class="play-row"><button class="play" id="playBtn">🔊 朗读简介</button></div>' +
      '<div class="prog-bar"><i style="width:' + ((idx + 1) / total * 100) + '%"></i></div>' +
      '<div class="prog-txt">' + (idx + 1) + ' / ' + total + '</div>' +
      '<div class="navbtns"><button id="prevBtn" ' + (idx === 0 ? 'disabled' : '') + '>← 上一本</button><button id="markBtn">✅ 标记掌握</button><button id="nextBtn" class="primary" ' + (idx >= total - 1 ? 'disabled' : '') + '>下一本 →</button></div>';
    $('#playBtn').addEventListener('click', () => speak(b.title + '，' + b.jianjie));
    $('#markBtn').addEventListener('click', () => markMastered(section, b.id));
    (b.kaodian || []).forEach((q, qi) => {
      const box = $('#cbox-' + qi);
      box.querySelectorAll('.opt').forEach(el => el.addEventListener('click', () => {
        if (el.classList.contains('locked')) return;
        box.querySelectorAll('.opt').forEach(x => x.classList.add('locked'));
        const ok = Number(el.dataset.o) === q.answer;
        if (ok) { el.classList.add('right'); markMastered(section, b.id); } else { el.classList.add('wrong'); box.querySelectorAll('.opt').forEach(x => { if (Number(x.dataset.o) === q.answer) x.classList.add('right'); }); }
        $('#cRes-' + qi).textContent = ok ? '✅ 正确！' : '❌ 正确答案：' + q.options[q.answer];
        $('#cRes-' + qi).className = 'result ' + (ok ? 'ok' : 'bad');
      }));
    });
    bindNav(total);
  }

  // ===== 写作指导：要求 + 思路 + 范文 =====
  function renderWritingRead(card) {
    const ts = itemsOf(curGroup); const t = ts[idx]; const total = ts.length;
    const mc = masteredCount(section, ts.map(x => x.id));
    const silu = (t.silu || []).map(s => '<li style="margin:6px 0;line-height:1.8;">' + esc(s) + '</li>').join('');
    card.innerHTML =
      '<div class="group-title">' + curGroup.title + ' · 第 ' + (idx + 1) + ' / ' + total + ' · 已掌握 ' + mc + '/' + total + '</div>' +
      '<div class="card" style="margin-bottom:14px;">' +
        '<div style="font-weight:800;font-size:16px;color:#3b5bdb;">✍️ ' + esc(t.title) + '　<span class="pill" style="background:#eef2ff;color:#3b5bdb;">' + esc(t.tixing || '') + '</span></div>' +
        '<div style="margin-top:10px;font-size:14px;line-height:1.9;"><b>题目要求：</b>' + esc(t.yaoqiu) + '</div>' +
      '</div>' +
      (silu ? '<div class="card" style="margin-bottom:14px;"><div style="font-weight:800;font-size:14px;color:#3b5bdb;margin-bottom:8px;">💡 写作思路</div><ol style="padding-left:20px;color:#444;font-size:14px;">' + silu + '</ol></div>' : '') +
      (t.fanwen ? '<div class="card"><div style="font-weight:800;font-size:14px;color:#3b5bdb;margin-bottom:8px;">📄 范文示例</div><div class="read-text" style="line-height:2;">' + esc(t.fanwen) + '</div></div>' : '') +
      '<div class="play-row"><button class="play" id="playBtn">🔊 朗读范文</button></div>' +
      '<div class="prog-bar"><i style="width:' + ((idx + 1) / total * 100) + '%"></i></div>' +
      '<div class="prog-txt">' + (idx + 1) + ' / ' + total + '</div>' +
      '<div class="navbtns"><button id="prevBtn" ' + (idx === 0 ? 'disabled' : '') + '>← 上一篇</button><button id="markBtn">✅ 标记掌握</button><button id="nextBtn" class="primary" ' + (idx >= total - 1 ? 'disabled' : '') + '>下一篇 →</button></div>';
    $('#playBtn').addEventListener('click', () => speak(t.fanwen || t.title));
    $('#markBtn').addEventListener('click', () => markMastered(section, t.id));
    bindNav(total);
  }

'''
add(ANCHOR, NEW_RENDERERS + ANCHOR)

# —— exam API ——
add("      const r = await api('/api/chinese-exam');",
    "      const r = await api('/api/jchinese-exam');")

# —— exam 年级筛选（小学 1-6 → 初中 初一/初二/初三）——
OLD_GRADE = """          ['', '1', '2', '3', '4', '5', '6'].map(g => '<button data-v="' + g + '" class="' + (EX.f.grade === g ? 'on' : '') + '">' + (g ? g + '年级' : '全部') + '</button>').join('') +"""
NEW_GRADE = """          ['', '7', '8', '9'].map(g => '<button data-v="' + g + '" class="' + (EX.f.grade === g ? 'on' : '') + '">' + (g ? ({'7':'初一','8':'初二','9':'初三'}[g]) : '全部') + '</button>').join('') +"""
add(OLD_GRADE, NEW_GRADE)

# —— renderTpl 年级 ——
OLD_TPL_GRADE = """          ['1', '2', '3', '4', '5', '6'].map(g => '<button data-v="' + g + '" class="' + (String(EX.f.grade) === g ? 'on' : '') + '">' + g + '年级</button>').join('') +"""
NEW_TPL_GRADE = """          ['7', '8', '9'].map(g => '<button data-v="' + g + '" class="' + (String(EX.f.grade) === g ? 'on' : '') + '">' + ({'7':'初一','8':'初二','9':'初三'}[g]) + '</button>').join('') +"""
add(OLD_TPL_GRADE, NEW_TPL_GRADE)

# —— TPL 模板定义 ——
OLD_TPL = """  const TPL = {
    basics: { name: '基础积累卷', cnt: { choice: 20, fill: 8 } },
    poem: { name: '古诗文专练卷', cnt: { fill: 12, choice: 8 } },
    read: { name: '阅读专项卷', cnt: { read: 6, choice: 6 } },
    final: { name: '小升初模拟卷', cnt: { choice: 16, fill: 10, read: 4, write: 1 } },
  };"""
NEW_TPL = """  const TPL = {
    basics: { name: '基础积累卷', cnt: { choice: 20, fill: 10 } },
    poem: { name: '古诗文专练卷', cnt: { fill: 12, choice: 8 } },
    read: { name: '阅读专项卷', cnt: { read: 6, choice: 6 } },
    final: { name: '中考模拟卷', cnt: { choice: 16, fill: 10, read: 4 } },
  };"""
add(OLD_TPL, NEW_TPL)

# —— exam 默认卷名 ——
add("    const title = EX.title || ('小学语文' + (EX.f.grade ? EX.f.grade + '年级' : '') + '测试卷');",
    "    const title = EX.title || ('初中语文' + (EX.f.grade ? (({'7':'初一','8':'初二','9':'初三'}[EX.f.grade]) || (EX.f.grade + '年级')) : '') + '测试卷');")

# —— link API ×2 ——
add("      const r = await api('/api/chinese-link');",
    "      const r = await api('/api/jchinese-link');")
add("    const r = await api('/api/chinese-link?unit=' + encodeURIComponent(uid));",
    "    const r = await api('/api/jchinese-link?unit=' + encodeURIComponent(uid));")

# —— link 文案 小升初→中考 ——
add("        '<div style=\"font-weight:800;font-size:15px;margin-bottom:6px;\">🌉 小升初语文衔接包（初中预备）</div>' +",
    "        '<div style=\"font-weight:800;font-size:15px;margin-bottom:6px;\">🌉 中考语文衔接包（初中备考）</div>' +")
add("        '<div style=\"font-size:13px;color:#888;line-height:1.7;\">面向六年级毕业、即将升入初中的学生：提前预习初中文言文、必背古诗文、阅读答题方法、记叙文写作、语法基础与名著导读，每单元含知识讲解与小测。</div>' +",
    "        '<div style=\"font-size:13px;color:#888;line-height:1.7;\">面向初一至初三学生：系统梳理字音字形、词语成语、病句标点、古诗文默写赏析、文言文方法、现代文阅读模板、名著导读与中考作文升格，每单元含知识讲解与小测。</div>' +")

# —— 键盘翻页 navMode 泛化 ——
add("    const navMode = (section === 'read') || (section === 'poem' && mode === 'read') || (section === 'zi' && mode === 'read') || (section === 'pinyin' && mode === 'read');",
    "    const navMode = (section !== 'exam' && section !== 'link' && mode === 'read');")

# —— 品牌色 全局替换 ——
BRAND = [('#1aa179', '#3b5bdb'), ('#33c79e', '#5c7cfa'), ('#1a9e5c', '#2f6bd6'),
         ('#eefaf5', '#eef2ff'), ('#e6f7f1', '#e7ecff'), ('#e8f8ee', '#eaf1ff'),
         ('#f6fbf9', '#f5f8ff'), ('#eef4f1', '#eaeefc'), ('#2a8', '#2f6bd6')]
for a, b in BRAND:
    reps.append((a, b, 0))  # 0 = 不限定次数

# —— 执行 + 断言 ——
for i, (old, new, n) in enumerate(reps):
    cnt = s.count(old)
    if n == 0:
        if cnt == 0:
            # 品牌色允许 0（某些值可能不存在），但仅当确实是品牌色时才放宽
            pass
    else:
        assert cnt == n, "替换未命中或多次命中(#%d): 期望%d次, 实际%d次\nOLD=%r" % (i, n, cnt, old[:60])
    s = s.replace(old, new)

io.open(DST, 'w', encoding='utf-8').write(s)
print("wrote", DST, len(s), "bytes")
print("DONE")
