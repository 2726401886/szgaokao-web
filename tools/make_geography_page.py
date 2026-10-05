# -*- coding: utf-8 -*-
"""由 public/politics.html 克隆生成 public/geography.html（初高中地理）
改动点：
  - 标题 / 顶栏文案 / 品牌色（红 → 地理蓝绿）
  - PROG_KEY
  - 移除「📄 广东高考卷」板块（地理无广东卷数据）
  - init API：/api/politics → /api/geography
  - exam/link API 同步替换
  - 品牌色 全局替换
所有替换均断言命中，未命中则报错。
用法：python tools/make_geography_page.py
"""
import io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'public', 'politics.html')
DST = os.path.join(ROOT, 'public', 'geography.html')

s = io.open(SRC, encoding='utf-8').read()
reps = []


def add(old, new, n=1):
    reps.append((old, new, n))


# —— 文案 / 标题 / 品牌 ——
add('<title>初高中道法·政治 · 知识点·题库·专题</title>',
    '<title>初高中地理 · 知识点·题库·专题</title>')
add('      <h1>📚 初高中道法·政治 · 知识点梳理·题库组卷·专题突破</h1>',
    '      <h1>🌍 初高中地理 · 知识点梳理·题库组卷·专题突破</h1>')
add('      <div class="sub">七年级至高三 · 道德与法治 + 思想政治（点 🔊 可听读知识点）</div>',
    '      <div class="sub">七年级至高三 · 地球地图·中国地理·区域发展·大气海洋（点 🔊 可听读知识点）</div>')
add("  const PROG_KEY = 'politics_progress';",
    "  const PROG_KEY = 'geography_progress';")

# —— SECTIONS：移除 gd 板块 ——
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

add("        '<div style=\"font-weight:800;font-size:15px;margin-bottom:6px;\">🧩 道法·政治专题突破包（考点梳理+小测）</div>' +",
    "        '<div style=\"font-weight:800;font-size:15px;margin-bottom:6px;\">🧩 地理专题突破包（核心考点+读图方法+小测）</div>' +")
add("        '<div style=\"font-size:13px;color:#888;line-height:1.7;\">面向七年级至高三学生：围绕宪法、改革开放与共同富裕、人民当家作主制度体系、哲学基本问题与唯物辩证法、经济全球化与中国应对等核心专题，系统梳理考点并配套小测，每单元含知识讲解与自测。</div>' +",
    "        '<div style=\"font-size:13px;color:#888;line-height:1.7;\">面向七年级至高三学生：围绕地球与地图、中国四大地理区域、天气气候、地球运动、工业区位与区域发展等核心专题，系统梳理考点并配套小测，每单元含知识讲解与自测。</div>' +")

# —— API 三处 ——
add("    const r = await api('/api/politics');",
    "    const r = await api('/api/geography');")
add("      const r = await api('/api/politics-exam');",
    "      const r = await api('/api/geography-exam');")
add("      const r = await api('/api/politics-link');",
    "      const r = await api('/api/geography-link');")
add("    const r = await api('/api/politics-link?unit=' + encodeURIComponent(uid));",
    "    const r = await api('/api/geography-link?unit=' + encodeURIComponent(uid));")

# —— exam 默认卷名 ——
add("    const title = EX.title || ('初高中道法·政治' + (EX.f.grade ? (({'7':'初一','8':'初二','9':'初三','10':'高一','11':'高二','12':'高三'}[EX.f.grade]) || (EX.f.grade + '年级')) : '') + '测试卷');",
    "    const title = EX.title || ('初高中地理' + (EX.f.grade ? (({'7':'初一','8':'初二','9':'初三','10':'高一','11':'高二','12':'高三'}[EX.f.grade]) || (EX.f.grade + '年级')) : '') + '测试卷');")

# —— TPL 模板名（政治术语 → 地理） ——
add("""  const TPL = {
    choice: { name: '选择题专项卷', cnt: { choice: 25 } },
    fill: { name: '填空默写卷', cnt: { fill: 15, choice: 5 } },
    mock: { name: '综合模拟卷', cnt: { choice: 14, fill: 8, read: 3, write: 1 } },
  };""",
    """  const TPL = {
    choice: { name: '单项选择专项卷', cnt: { choice: 25 } },
    fill: { name: '读图填空卷', cnt: { fill: 15, choice: 5 } },
    mock: { name: '综合模拟卷', cnt: { choice: 14, fill: 8, read: 3, write: 1 } },
  };""")

# —— 移除整个 GD 渲染器代码块 ——
i0 = s.find('  // ================== 板块：广东高考卷（结构仿真卷） ==================')
i1 = s.find('  // ================== 板块：题库组卷 ==================')
assert i0 > 0 and i1 > i0, 'GD 代码块边界未找到'
s = s[:i0] + s[i1:]

# —— 移除 GD 相关 CSS（含 gd-wrap 到 gd-tip 的整段） ——
import re
css_pat = re.compile(r'\n  /\* ===== 广东高考卷（结构仿真卷） ===== \*/.*?(?=\n  \.read-text \{)', re.S)
s2, ncss = css_pat.subn('', s)
assert ncss == 1, 'GD CSS 段未找到或多次命中: %d' % ncss
s = s2

# —— 品牌色 全局替换（红 → 地理蓝绿） ——
BRAND = [('#c0392b', '#0e7490'), ('#e74c3c', '#0891b2'), ('#b03a2e', '#155e75'),
         ('#fdf0ef', '#ecfeff'), ('#fbeae8', '#e0f2fe'), ('#fce9e7', '#cffafe'),
         ('#fdf6f5', '#f0fdff'), ('#faeceb', '#e0f7fa'), ('#f5eefa', '#eff6ff'),
         ('#f0e6f9', '#cffafe'), ('#8e44ad', '#0e7490')]
for a, b in BRAND:
    reps.append((a, b, 0))  # 0 = 不限定次数

# —— 执行 + 断言 ——
for i, (old, new, n) in enumerate(reps):
    cnt = s.count(old)
    if n == 0:
        if cnt == 0:
            pass
    else:
        assert cnt == n, "替换未命中或多次命中(#%d): 期望%d次, 实际%d次\nOLD=%r" % (i, n, cnt, old[:60])
    s = s.replace(old, new)

# —— 收尾校验：不得残留 politics / gd 引用 ——
assert '/api/politics' not in s, '仍残留 /api/politics'
assert 'renderGdPage' not in s, '仍残留 renderGdPage'
assert 'politics_progress' not in s, '仍残留 politics_progress'

io.open(DST, 'w', encoding='utf-8').write(s)
print("wrote", DST, len(s), "bytes")
print("DONE")
