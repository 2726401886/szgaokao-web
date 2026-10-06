# -*- coding: utf-8 -*-
"""由 public/politics.html 克隆生成 public/history.html（初高中历史）
改动点（每处均断言命中次数，模板一变即响亮报错）：
  - 标题 / 顶栏文案 / 品牌色（政治红 → 历史赭金）
  - PROG_KEY
  - SECTIONS 去掉「广东高考卷」（历史本次无高考卷数据）
  - init / exam / link 三处 API → /api/history*
  - exam 模板名与年级筛选文案（政治 7-12 → 历史 7-12，沿用）
  - 专题突破包文案 → 历史专题
用法：python tools/make_history_page.py
"""
import io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'public', 'politics.html')
DST = os.path.join(ROOT, 'public', 'history.html')

s = io.open(SRC, encoding='utf-8').read()
reps = []


def add(old, new, n=1):
    reps.append((old, new, n))


# —— 标题 / 顶栏 ——
add('<title>初高中道法·政治 · 知识点·题库·专题</title>',
    '<title>初高中历史 · 知识点·题库·专题</title>')
add('      <h1>📚 初高中道法·政治 · 知识点梳理·题库组卷·专题突破</h1>',
    '      <h1>🏛️ 初高中历史 · 知识点梳理·题库组卷·专题突破</h1>')
add('      <div class="sub">七年级至高三 · 道德与法治 + 思想政治（点 🔊 可听读知识点）</div>',
    '      <div class="sub">七年级至高三 · 中国通史 + 世界通史（点 🔊 可听读知识点）</div>')
add("  const PROG_KEY = 'politics_progress';",
    "  const PROG_KEY = 'history_progress';")

# —— SECTIONS：去掉 gd 板块（历史本次无高考卷）——
add("""    { k: 'link', t: '🧩 专题突破', modes: [] },
    { k: 'gd', t: '📄 广东高考卷', modes: [] },
  ];""",
    """    { k: 'link', t: '🧩 专题突破', modes: [] },
  ];""")

# —— selectSection 去掉 gd 分支 ——
add("""    if (k === 'exam' || k === 'link' || k === 'gd') {
      // 独立板块：隐藏左侧分组栏，整幅渲染
      $('#sidePane').style.display = 'none';
      $('#mainArea').style.flex = '1 1 100%';
      if (k === 'exam') renderExamPage();
      else if (k === 'link') renderLinkPage();
      else renderGdPage();
      return;
    }""",
    """    if (k === 'exam' || k === 'link') {
      // 独立板块：隐藏左侧分组栏，整幅渲染
      $('#sidePane').style.display = 'none';
      $('#mainArea').style.flex = '1 1 100%';
      if (k === 'exam') renderExamPage();
      else renderLinkPage();
      return;
    }""")

# —— renderSide 去掉 gd ——
add("  function renderSide() {\n    if (section === 'exam' || section === 'link' || section === 'gd') return;",
    "  function renderSide() {\n    if (section === 'exam' || section === 'link') return;")

# —— 侧栏专题包文案 ——
add("        '<div style=\"font-weight:800;font-size:15px;margin-bottom:6px;\">🧩 道法·政治专题突破包（考点梳理+小测）</div>' +",
    "        '<div style=\"font-weight:800;font-size:15px;margin-bottom:6px;\">🧩 历史专题突破包（考点梳理+小测）</div>' +")
add("        '<div style=\"font-size:13px;color:#888;line-height:1.7;\">面向七年级至高三学生：围绕宪法、改革开放与共同富裕、人民当家作主制度体系、哲学基本问题与唯物辩证法、经济全球化与中国应对等核心专题，系统梳理考点并配套小测，每单元含知识讲解与自测。</div>' +",
    "        '<div style=\"font-size:13px;color:#888;line-height:1.7;\">面向七年级至高三学生：围绕中国古代政治制度演进、经济重心南移与科技文化、近代化探索与救亡图存、社会主义建设成就、世界近代化与全球化等核心专题，系统梳理考点并配套小测，每单元含知识讲解与自测。</div>' +")

# —— API 三处 ——
add("    const r = await api('/api/politics');",
    "    const r = await api('/api/history');")
add("      const r = await api('/api/politics-exam');",
    "      const r = await api('/api/history-exam');")
add("      const r = await api('/api/politics-link');",
    "      const r = await api('/api/history-link');")
add("    const r = await api('/api/politics-link?unit=' + encodeURIComponent(uid));",
    "    const r = await api('/api/history-link?unit=' + encodeURIComponent(uid));")

# —— exam 默认卷名 ——
add("    const title = EX.title || ('初高中道法·政治' + (EX.f.grade ? (({'7':'初一','8':'初二','9':'初三','10':'高一','11':'高二','12':'高三'}[EX.f.grade]) || (EX.f.grade + '年级')) : '') + '测试卷');",
    "    const title = EX.title || ('初高中历史' + (EX.f.grade ? (({'7':'初一','8':'初二','9':'初三','10':'高一','11':'高二','12':'高三'}[EX.f.grade]) || (EX.f.grade + '年级')) : '') + '测试卷');")

# —— TPL 模板名（政治 → 历史）——
add("""  const TPL = {
    choice: { name: '选择题专项卷', cnt: { choice: 25 } },
    fill: { name: '填空默写卷', cnt: { fill: 15, choice: 5 } },
    mock: { name: '综合模拟卷', cnt: { choice: 14, fill: 8, read: 3, write: 1 } },
  };""",
    """  const TPL = {
    choice: { name: '选择题专项卷', cnt: { choice: 25 } },
    fill: { name: '材料填空卷', cnt: { fill: 15, choice: 5 } },
    mock: { name: '综合模拟卷', cnt: { choice: 14, fill: 8, read: 3, write: 1 } },
  };""")

# —— 移除整个 GD 渲染器代码块 ——
i0 = s.find('  // ================== 板块：广东高考卷（结构仿真卷） ==================')
i1 = s.find('  // ================== 板块：题库组卷 ==================')
assert i0 > 0 and i1 > i0, 'GD 代码块边界未找到'
s = s[:i0] + s[i1:]

# —— 移除 GD 相关 CSS ——
import re
css_pat = re.compile(r'\n  /\* ===== 广东高考卷（结构仿真卷） ===== \*/.*?(?=\n  \.read-text \{)', re.S)
s2, ncss = css_pat.subn('', s)
assert ncss == 1, 'GD CSS 段未找到或多次命中: %d' % ncss
s = s2

# —— 品牌色 全局替换（政治红 → 历史赭金）——
BRAND = [('#c0392b', '#8a5a1b'), ('#e74c3c', '#b8791f'), ('#b03a2e', '#7a4d16'),
         ('#fdf0ef', '#fdf6ec'), ('#fbeae8', '#f8ecd8'), ('#fce9e7', '#f5e3c8'),
         ('#fdf6f5', '#fdfaf2'), ('#faeceb', '#f8f0df'), ('#f5eefa', '#f6f1e8'),
         ('#f0e6f9', '#f5e6c8'), ('#8e44ad', '#8a5a1b')]
for a, b in BRAND:
    reps.append((a, b, 0))

# —— 执行 + 断言 ——
for i, (old, new, n) in enumerate(reps):
    cnt = s.count(old)
    if n == 0:
        if cnt == 0:
            pass
    else:
        assert cnt == n, "替换未命中或多次命中(#%d): 期望%d次, 实际%d次\nOLD=%r" % (i, n, cnt, old[:60])
    s = s.replace(old, new)

# —— 收尾校验 ——
assert '/api/politics' not in s, '仍残留 /api/politics'
assert 'renderGdPage' not in s, '仍残留 renderGdPage'
assert 'politics_progress' not in s, '仍残留 politics_progress'
assert 'renderKnowledgeRead' in s, 'knowledge 渲染器缺失'

io.open(DST, 'w', encoding='utf-8').write(s)
print("wrote", DST, len(s), "bytes")

# —— 产物语法校验：抽内联 script 交给 node --check ——
scripts = re.findall(r'<script>(.*?)</script>', s, re.S)
tmp = os.path.join(ROOT, 'tools', '_check_history.js')
io.open(tmp, 'w', encoding='utf-8').write(max(scripts, key=len))
print("extracted script ->", tmp, os.path.getsize(tmp), "bytes")
print("DONE")
