# -*- coding: utf-8 -*-
"""由 public/geography.html 克隆生成 public/chemistry.html（初高中化学）
改动点：
  - 标题 / 顶栏文案 / 品牌色（地理蓝绿 → 化学紫青）
  - PROG_KEY
  - init API：/api/geography → /api/chemistry
  - exam/link API 同步替换
  - **年级筛选 7-12 → 9-12**（化学从九年级开课，初中无七八年级化学）
  - 移除「📄 广东高考卷」板块（化学暂无广东真题，接口未实现，留空 Tab 会报错）
  - TPL 模板名（地理化）
  - 品牌色 全局替换
所有替换均断言命中，未命中则报错。
用法：python tools/make_chemistry_page.py
"""
import io, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'public', 'geography.html')
DST = os.path.join(ROOT, 'public', 'chemistry.html')

s = io.open(SRC, encoding='utf-8').read()
reps = []


def add(old, new, n=1):
    reps.append((old, new, n))


# —— 文案 / 标题 ——
add('<title>初高中地理 · 知识点·题库·专题</title>',
    '<title>初高中化学 · 知识点·题库·专题</title>')
add('      <h1>🌍 初高中地理 · 知识点梳理·题库组卷·专题突破</h1>',
    '      <h1>⚗️ 初高中化学 · 知识点梳理·题库组卷·专题突破</h1>')
add('      <div class="sub">七年级至高三 · 地球地图·中国地理·区域发展·大气海洋（点 🔊 可听读知识点）</div>',
    '      <div class="sub">九年级至高三 · 化学启蒙·必修一二·选择性必修·反应原理·有机化学（点 🔊 可听读知识点）</div>')
add("  const PROG_KEY = 'geography_progress';",
    "  const PROG_KEY = 'chemistry_progress';")

# —— SECTIONS：移除 gd 板块（化学暂无广东真题接口）——
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

# —— API ——
add("    const r = await api('/api/geography');",
    "    const r = await api('/api/chemistry');")
add("      const r = await api('/api/geography-exam');",
    "      const r = await api('/api/chemistry-exam');")
add("      const r = await api('/api/geography-link');",
    "      const r = await api('/api/chemistry-link');")
add("    const r = await api('/api/geography-link?unit=' + encodeURIComponent(uid));",
    "    const r = await api('/api/chemistry-link?unit=' + encodeURIComponent(uid));")

# —— 年级筛选 7-12 → 9-12（化学从九年级开课）——
add("""          ['', '7', '8', '9', '10', '11', '12'].map(g => '<button data-v="' + g + '" class="' + (EX.f.grade === g ? 'on' : '') + '">' + (g ? ({'7':'初一','8':'初二','9':'初三','10':'高一','11':'高二','12':'高三'}[g]) : '全部') + '</button>').join('') +""",
    """          ['', '9', '10', '11', '12'].map(g => '<button data-v="' + g + '" class="' + (EX.f.grade === g ? 'on' : '') + '">' + (g ? ({'9':'初三','10':'高一','11':'高二','12':'高三'}[g]) : '全部') + '</button>').join('') +""")
add("""          ['7', '8', '9', '10', '11', '12'].map(g => '<button data-v="' + g + '" class="' + (String(EX.f.grade) === g ? 'on' : '') + '">' + ({'7':'初一','8':'初二','9':'初三','10':'高一','11':'高二','12':'高三'}[g]) + '</button>').join('') +""",
    """          ['9', '10', '11', '12'].map(g => '<button data-v="' + g + '" class="' + (String(EX.f.grade) === g ? 'on' : '') + '">' + ({'9':'初三','10':'高一','11':'高二','12':'高三'}[g]) + '</button>').join('') +""")

# —— exam 默认卷名 ——
add("    const title = EX.title || ('初高中地理' + (EX.f.grade ? (({'7':'初一','8':'初二','9':'初三','10':'高一','11':'高二','12':'高三'}[EX.f.grade]) || (EX.f.grade + '年级')) : '') + '测试卷');",
    "    const title = EX.title || ('初高中化学' + (EX.f.grade ? ({'9':'初三','10':'高一','11':'高二','12':'高三'}[EX.f.grade] || (EX.f.grade + '年级')) : '') + '测试卷');")

# —— TPL 模板名（地理 → 化学） ——
add("""  const TPL = {
    choice: { name: '单项选择专项卷', cnt: { choice: 25 } },
    fill: { name: '读图填空卷', cnt: { fill: 15, choice: 5 } },
    mock: { name: '综合模拟卷', cnt: { choice: 14, fill: 8, read: 3, write: 1 } },
  };""",
    """  const TPL = {
    choice: { name: '基础概念专项卷', cnt: { choice: 25 } },
    fill: { name: '化学用语填空卷', cnt: { fill: 15, choice: 5 } },
    mock: { name: '综合模拟卷', cnt: { choice: 14, fill: 8, read: 3, write: 1 } },
  };""")

# —— link 文案（地理 → 化学） ——
add("        '<div style=\"font-weight:800;font-size:15px;margin-bottom:6px;\">🧩 地理专题突破包（核心考点+读图方法+小测）</div>' +",
    "        '<div style=\"font-weight:800;font-size:15px;margin-bottom:6px;\">🧪 化学专题突破包（核心概念+方程式+实验+小测）</div>' +")
add("        '<div style=\"font-size:13px;color:#888;line-height:1.7;\">面向七年级至高三学生：围绕地球与地图、中国四大地理区域、天气气候、地球运动、工业区位与区域发展等核心专题，系统梳理考点并配套小测，每单元含知识讲解与自测。</div>' +",
    "        '<div style=\"font-size:13px;color:#888;line-height:1.7;\">面向九年级至高三学生：围绕化学入门概念、酸碱盐与反应原理、物质的量计算、元素周期律与物质结构、反应原理与实验探究等核心专题，系统梳理考点并配套小测，每单元含知识讲解与自测。</div>' +")

# —— 移除 GD 渲染器代码块 ——
i0 = s.find('  // ================== 板块：广东高考卷（真题） ==================')
i1 = s.find('  // ================== 板块：题库组卷 ==================')
assert i0 > 0 and i1 > i0, 'GD 代码块边界未找到'
s = s[:i0] + s[i1:]

# —— 移除 GD 相关 CSS ——
css_pat = re.compile(r'\n  /\* ===== 广东高考卷（真题） ===== \*/.*?(?=\n  \.read-text \{)', re.S)
s, ncss = css_pat.subn('', s)
assert ncss == 1, 'GD CSS 段未找到或多次命中: %d' % ncss

# —— 品牌色 全局替换（地理蓝绿 → 化学紫青） ——
BRAND = [('#0e7490', '#6d28d9'), ('#0891b2', '#8b5cf6'), ('#155e75', '#4c1d95'),
         ('#ecfeff', '#f5f3ff'), ('#cffafe', '#ede9fe'), ('#e0f2fe', '#ddd6fe'),
         ('#f0fdff', '#faf5ff'), ('#e0f7fa', '#f3e8ff'), ('#eff6ff', '#f5f3ff'),
         ('#0e7490', '#6d28d9')]
for a, b in BRAND:
    reps.append((a, b, 0))  # 0 = 不限定次数

# —— 执行 + 断言 ——
for i, (old, new, n) in enumerate(reps):
    cnt = s.count(old)
    if n != 0:
        assert cnt == n, "替换未命中或多次命中(#%d): 期望%d次, 实际%d次\nOLD=%r" % (i, n, cnt, old[:60])
    s = s.replace(old, new)

# —— 收尾校验 ——
assert '/api/geography' not in s, '仍残留 /api/geography'
assert 'renderGdPage' not in s, '仍残留 renderGdPage'
assert 'geography_progress' not in s, '仍残留 geography_progress'
assert "'7', '8', '9'" not in s, '年级筛选仍含 7/8（化学应从 9 起）'
assert "'初一'" not in s and "'初二'" not in s, '年级标签仍含初一初二'

io.open(DST, 'w', encoding='utf-8').write(s)
print("wrote", DST, len(s), "bytes")
print("DONE")
