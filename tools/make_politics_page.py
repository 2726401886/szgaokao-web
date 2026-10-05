# -*- coding: utf-8 -*-
"""由 public/chinese.html 克隆生成 public/politics.html（初高中道法·政治）
改动点：
  - 标题 / 顶栏文案 / 品牌色（绿 → 红）
  - PROG_KEY
  - SECTIONS：4 学习板块 + exam + link → 3 板块（knowledge / exam / link）
  - init API：/api/chinese → /api/politics
  - itemsOf / renderMain 仅分发 knowledge（自定义 renderKnowledgeRead）
  - 插入 renderKnowledgeRead：知识点（term + jieshi + 自测 kao）
  - exam：年级筛选项 1-6 → 初一/初二/初三/高一/高二/高三；模板改名；默认卷名
  - link：/api/chinese-link → /api/politics-link；文案 小升初衔接 → 专题突破；单元数 8→5
  - 键盘翻页 navMode 泛化
所有替换均断言命中，未命中则报错。
"""
import io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'public', 'chinese.html')
DST = os.path.join(ROOT, 'public', 'politics.html')

s = io.open(SRC, encoding='utf-8').read()
reps = []

def add(old, new, n=1):
    reps.append((old, new, n))

# —— 文案 / 标题 / 品牌 ——
add('<title>小学语文 · 拼音识字古诗阅读</title>',
    '<title>初高中道法·政治 · 知识点·题库·专题</title>')
add('      <h1>📚 小学语文 · 拼音识字古诗阅读</h1>',
    '      <h1>📚 初高中道法·政治 · 知识点梳理·题库组卷·专题突破</h1>')
add('      <div class="sub">汉语拼音 · 识字写字 · 古诗文积累 · 阅读理解（点 🔊 可听读）</div>',
    '      <div class="sub">七年级至高三 · 道德与法治 + 思想政治（点 🔊 可听读知识点）</div>')
add("  const PROG_KEY = 'chinese_progress';",
    "  const PROG_KEY = 'politics_progress';")

# —— SECTIONS 4学习+exam+link → 3 板块 ——
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
    { k: 'knowledge', t: '📘 知识点梳理', modes: [
        { k: 'read', t: '📖 学习' } ] },
    { k: 'exam', t: '📋 题库组卷', modes: [] },
    { k: 'link', t: '🧩 专题突破', modes: [] },
  ];"""
add(OLD_SECTIONS, NEW_SECTIONS)

# —— init API ——
add("    const r = await api('/api/chinese');",
    "    const r = await api('/api/politics');")

# —— itemsOf ——
OLD_ITEMS = """  function itemsOf(g) {
    if (section === 'pinyin') return g.items || [];
    if (section === 'zi') return g.words || [];
    if (section === 'poem') return g.poems || [];
    if (section === 'read') return g.passages || [];
    return [];
  }"""
NEW_ITEMS = """  function itemsOf(g) {
    if (section === 'knowledge') return g.items || [];
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
    if (section === 'knowledge') {
      renderKnowledgeRead(card);
    }
  }"""
add(OLD_RM, NEW_RM)

# —— 插入知识点渲染器（在题库组卷注释之前）——
ANCHOR = "  // ================== 板块：题库组卷 =================="
NEW_RENDERERS = r'''  // ===== 知识点梳理：术语 + 讲解 + 自测 =====
  function renderKnowledgeRead(card) {
    const its = itemsOf(curGroup); const it = its[idx]; const total = its.length;
    const mc = masteredCount(section, its.map(x => x.id));
    const kao = it.kao;
    const quizHtml = kao ? (
      '<div style="margin-top:16px;padding:14px;background:#fafcff;border-radius:12px;border:1.5px solid #eef4f1;">' +
        '<div style="font-weight:700;font-size:14px;color:#b8860b;margin-bottom:8px;">🧠 自测：' + esc(kao.q) + '</div>' +
        '<div id="kbox">' + kao.options.map((o, oi) => '<div class="opt" data-o="' + oi + '">' + L(oi) + '. ' + esc(o) + '</div>').join('') +
        '<div class="result" id="kRes"></div></div>' +
      '</div>'
    ) : '';
    card.innerHTML =
      '<div class="group-title">' + curGroup.title + ' · 第 ' + (idx + 1) + ' / ' + total + ' · 已掌握 ' + mc + '/' + total + '</div>' +
      '<div class="card" style="margin-bottom:14px;">' +
        '<div class="hero" style="padding:6px 0 10px;"><div class="big" style="font-size:30px;color:var(--brand);">' + esc(it.term) + '</div></div>' +
        '<div class="read-text" style="font-size:15px;line-height:2;">' + esc(it.jieshi) + '</div>' +
      '</div>' +
      quizHtml +
      '<div class="play-row"><button class="play" id="playBtn">🔊 朗读知识点</button></div>' +
      '<div class="prog-bar"><i style="width:' + ((idx + 1) / total * 100) + '%"></i></div>' +
      '<div class="prog-txt">' + (idx + 1) + ' / ' + total + '</div>' +
      '<div class="navbtns"><button id="prevBtn" ' + (idx === 0 ? 'disabled' : '') + '>← 上一个</button>' +
        '<button id="markBtn">✅ 标记掌握</button>' +
        '<button id="nextBtn" class="primary" ' + (idx >= total - 1 ? 'disabled' : '') + '>下一个 →</button></div>';
    $('#playBtn').addEventListener('click', () => speak(it.term + '。' + it.jieshi));
    $('#markBtn').addEventListener('click', () => markMastered(section, it.id));
    if (kao) {
      const box = $('#kbox');
      box.querySelectorAll('.opt').forEach(el => el.addEventListener('click', () => {
        if (el.classList.contains('locked')) return;
        box.querySelectorAll('.opt').forEach(x => x.classList.add('locked'));
        const oi = Number(el.dataset.o); const ok = oi === kao.answer;
        if (ok) { el.classList.add('right'); markMastered(section, it.id); }
        else { el.classList.add('wrong'); box.querySelectorAll('.opt').forEach(x => { if (Number(x.dataset.o) === kao.answer) x.classList.add('right'); }); }
        $('#kRes').textContent = ok ? '✅ 正确！' : '❌ 正确答案：' + L(kao.answer) + '. ' + kao.options[kao.answer];
        $('#kRes').className = 'result ' + (ok ? 'ok' : 'bad');
      }));
    }
    bindNav(total);
  }

'''
add(ANCHOR, NEW_RENDERERS + ANCHOR)

# —— exam API ——
add("      const r = await api('/api/chinese-exam');",
    "      const r = await api('/api/politics-exam');")

# —— exam 年级筛选（小学 1-6 → 初高中 初一~高三）——
OLD_GRADE = """          ['', '1', '2', '3', '4', '5', '6'].map(g => '<button data-v="' + g + '" class="' + (EX.f.grade === g ? 'on' : '') + '">' + (g ? g + '年级' : '全部') + '</button>').join('') +"""
NEW_GRADE = """          ['', '7', '8', '9', '10', '11', '12'].map(g => '<button data-v="' + g + '" class="' + (EX.f.grade === g ? 'on' : '') + '">' + (g ? ({'7':'初一','8':'初二','9':'初三','10':'高一','11':'高二','12':'高三'}[g]) : '全部') + '</button>').join('') +"""
add(OLD_GRADE, NEW_GRADE)

# —— TPL 年级筛选 ——
OLD_TPL_GRADE = """          ['1', '2', '3', '4', '5', '6'].map(g => '<button data-v="' + g + '" class="' + (String(EX.f.grade) === g ? 'on' : '') + '">' + g + '年级</button>').join('') +"""
NEW_TPL_GRADE = """          ['7', '8', '9', '10', '11', '12'].map(g => '<button data-v="' + g + '" class="' + (String(EX.f.grade) === g ? 'on' : '') + '">' + ({'7':'初一','8':'初二','9':'初三','10':'高一','11':'高二','12':'高三'}[g]) + '</button>').join('') +"""
add(OLD_TPL_GRADE, NEW_TPL_GRADE)

# —— TPL 模板定义 ——
OLD_TPL = """  const TPL = {
    basics: { name: '基础积累卷', cnt: { choice: 20, fill: 8 } },
    poem: { name: '古诗文专练卷', cnt: { fill: 12, choice: 8 } },
    read: { name: '阅读专项卷', cnt: { read: 6, choice: 6 } },
    final: { name: '小升初模拟卷', cnt: { choice: 16, fill: 10, read: 4, write: 1 } },
  };"""
NEW_TPL = """  const TPL = {
    choice: { name: '选择题专项卷', cnt: { choice: 25 } },
    fill: { name: '填空默写卷', cnt: { fill: 15, choice: 5 } },
    mock: { name: '综合模拟卷', cnt: { choice: 14, fill: 8, read: 3, write: 1 } },
  };"""
add(OLD_TPL, NEW_TPL)

# —— exam 默认卷名 ——
add("    const title = EX.title || ('小学语文' + (EX.f.grade ? EX.f.grade + '年级' : '') + '测试卷');",
    "    const title = EX.title || ('初高中道法·政治' + (EX.f.grade ? (({'7':'初一','8':'初二','9':'初三','10':'高一','11':'高二','12':'高三'}[EX.f.grade]) || (EX.f.grade + '年级')) : '') + '测试卷');")

# —— link API ×2 ——
add("      const r = await api('/api/chinese-link');",
    "      const r = await api('/api/politics-link');")
add("    const r = await api('/api/chinese-link?unit=' + encodeURIComponent(uid));",
    "    const r = await api('/api/politics-link?unit=' + encodeURIComponent(uid));")

# —— link 体验提示单元数 8→5 ——
add("'<div class=\"trial-note\" style=\"display:block;margin-bottom:12px;\">🎁 体验模式：衔接包仅开放第 1 单元。输入授权码或联系管理员（微信 13538237315）解锁全部 8 个单元。</div>' : '';",
    "'<div class=\"trial-note\" style=\"display:block;margin-bottom:12px;\">🎁 体验模式：专题包仅开放第 1 单元。输入授权码或联系管理员（微信 13538237315）解锁全部 5 个单元。</div>' : '';")

# —— link 文案 小升初衔接 → 专题突破 ——
add("        '<div style=\"font-weight:800;font-size:15px;margin-bottom:6px;\">🌉 小升初语文衔接包（初中预备）</div>' +",
    "        '<div style=\"font-weight:800;font-size:15px;margin-bottom:6px;\">🧩 道法·政治专题突破包（考点梳理+小测）</div>' +")
add("        '<div style=\"font-size:13px;color:#888;line-height:1.7;\">面向六年级毕业、即将升入初中的学生：提前预习初中文言文、必背古诗文、阅读答题方法、记叙文写作、语法基础与名著导读，每单元含知识讲解与小测。</div>' +",
    "        '<div style=\"font-size:13px;color:#888;line-height:1.7;\">面向七年级至高三学生：围绕宪法、改革开放与共同富裕、人民当家作主制度体系、哲学基本问题与唯物辩证法、经济全球化与中国应对等核心专题，系统梳理考点并配套小测，每单元含知识讲解与自测。</div>' +")

# —— 键盘翻页 navMode 泛化 ——
add("    const navMode = (section === 'read') || (section === 'poem' && mode === 'read') || (section === 'zi' && mode === 'read') || (section === 'pinyin' && mode === 'read');",
    "    const navMode = (section === 'knowledge' && mode === 'read');")

# —— 品牌色 全局替换（绿 → 红）——
BRAND = [('#1aa179', '#c0392b'), ('#33c79e', '#e74c3c'), ('#1a9e5c', '#b03a2e'),
         ('#eefaf5', '#fdf0ef'), ('#e6f7f1', '#fbeae8'), ('#e8f8ee', '#fce9e7'),
         ('#f6fbf9', '#fdf6f5'), ('#eef4f1', '#faeceb'), ('#2a8', '#b03a2e')]
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
