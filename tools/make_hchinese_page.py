# -*- coding: utf-8 -*-
"""由 public/jchinese.html 克隆生成 public/hchinese.html（高中语文）
改动点：
  - 标题 / 顶栏文案 / 品牌色（靛蓝 #3b5bdb → 紫红 #8e44ad 系）
  - PROG_KEY：jchinese_progress → hchinese_progress
  - 3 个 API 端点：/api/jchinese[-exam|-link] → /api/hchinese[-exam|-link]
  - SECTIONS 板块标题与标签改为高中措辞
  - exam 年级筛选：初一/初二/初三 → 高一/高二/高三
  - exam 模板名「中考模拟卷」→「高考模拟卷」
  - link 文案：中考衔接 → 高考衔接
所有替换均断言命中次数，未命中即报错。
"""
import io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'public', 'jchinese.html')
DST = os.path.join(ROOT, 'public', 'hchinese.html')

s = io.open(SRC, encoding='utf-8').read()
reps = []

def add(old, new, n=1):
    reps.append((old, new, n))

# —— 标题 / 顶栏 ——
add('<title>初中语文 · 字词古诗文文言文阅读名著写作</title>',
    '<title>高中语文 · 字词古诗文文言文阅读名著写作</title>')
add('      <h1>📚 初中语文 · 字词古诗文文言文阅读名著写作</h1>',
    '      <h1>📚 高中语文 · 字词古诗文文言文阅读名著写作</h1>')
add('      <div class="sub">字词积累 · 古诗文默写赏析 · 文言文 · 现代文阅读 · 名著导读 · 写作（点 🔊 可听读）</div>',
    '      <div class="sub">字音字形词语 · 古诗文默写赏析 · 文言文 · 现代文阅读 · 名著导读 · 高考作文（点 🔊 可听读）</div>')

# —— PROG_KEY ——
add("  const PROG_KEY = 'jchinese_progress';",
    "  const PROG_KEY = 'hchinese_progress';")

# —— SECTIONS 标签改高中措辞 ——
add("    { k: 'zi', t: '🔤 字词积累', modes: [",
    "    { k: 'zi', t: '🔤 字音字形词语', modes: [")
add("    { k: 'read', t: '📝 现代文阅读', modes: [",
    "    { k: 'read', t: '📝 现代文阅读', modes: [")   # 无需改，仅占位保持结构
reps.pop()  # 移除占位
add("    { k: 'writing', t: '✍️ 写作指导', modes: [",
    "    { k: 'writing', t: '✍️ 高考作文', modes: [")
add("    { k: 'link', t: '🌉 中考衔接', modes: [] },",
    "    { k: 'link', t: '🌉 高考衔接', modes: [] },")
add("    { k: 'exam', t: '📋 题库组卷', modes: [] },\n    { k: 'link', t: '🌉 高考衔接', modes: [] },",
    "    { k: 'exam', t: '📋 题库组卷', modes: [] },\n    { k: 'link', t: '🌉 高考衔接', modes: [] },")

# —— API 端点 ×4 ——
add("    const r = await api('/api/jchinese');", "    const r = await api('/api/hchinese');")
add("      const r = await api('/api/jchinese-exam');", "      const r = await api('/api/hchinese-exam');")
add("      const r = await api('/api/jchinese-link');", "      const r = await api('/api/hchinese-link');")
add("    const r = await api('/api/jchinese-link?unit=' + encodeURIComponent(uid));",
    "    const r = await api('/api/hchinese-link?unit=' + encodeURIComponent(uid));")

# —— exam 年级筛选：初一/初二/初三 → 高一/高二/高三 ——
add("""          ['', '7', '8', '9'].map(g => '<button data-v="' + g + '" class="' + (EX.f.grade === g ? 'on' : '') + '">' + (g ? ({'7':'初一','8':'初二','9':'初三'}[g]) : '全部') + '</button>').join('') +""",
    """          ['', '10', '11', '12'].map(g => '<button data-v="' + g + '" class="' + (EX.f.grade === g ? 'on' : '') + '">' + (g ? ({'10':'高一','11':'高二','12':'高三'}[g]) : '全部') + '</button>').join('') +""")
add("""          ['7', '8', '9'].map(g => '<button data-v="' + g + '" class="' + (String(EX.f.grade) === g ? 'on' : '') + '">' + ({'7':'初一','8':'初二','9':'初三'}[g]) + '</button>').join('') +""",
    """          ['10', '11', '12'].map(g => '<button data-v="' + g + '" class="' + (String(EX.f.grade) === g ? 'on' : '') + '">' + ({'10':'高一','11':'高二','12':'高三'}[g]) + '</button>').join('') +""")

# —— exam 默认卷名：初中语文 → 高中语文（年级用高一/高二/高三）——
add("    const title = EX.title || ('初中语文' + (EX.f.grade ? (({'7':'初一','8':'初二','9':'初三'}[EX.f.grade]) || (EX.f.grade + '年级')) : '') + '测试卷');",
    "    const title = EX.title || ('高中语文' + (EX.f.grade ? (({'10':'高一','11':'高二','12':'高三'}[EX.f.grade]) || (EX.f.grade + '年级')) : '') + '测试卷');")

# —— TPL 模板名：中考模拟卷 → 高考模拟卷 ——
add("    final: { name: '中考模拟卷', cnt: { choice: 16, fill: 10, read: 4 } },",
    "    final: { name: '高考模拟卷', cnt: { choice: 16, fill: 10, read: 4 } },")

# —— link 文案：中考 → 高考 ——
add("  /* —— 题库组卷 / 中考衔接 专用 —— */",
    "  /* —— 题库组卷 / 高考衔接 专用 —— */")
add("  // ================== 板块：中考衔接包 ==================",
    "  // ================== 板块：高考衔接包 ==================")
add("        '<div style=\"font-weight:800;font-size:15px;margin-bottom:6px;\">🌉 中考语文衔接包（初中备考）</div>' +",
    "        '<div style=\"font-weight:800;font-size:15px;margin-bottom:6px;\">🌉 高考语文总复习包（高三备考）</div>' +")
add("        '<div style=\"font-size:13px;color:#888;line-height:1.7;\">面向初一至初三学生：系统梳理字音字形、词语成语、病句标点、古诗文默写赏析、文言文方法、现代文阅读模板、名著导读与中考作文升格，每单元含知识讲解与小测。</div>' +",
    "        '<div style=\"font-size:13px;color:#888;line-height:1.7;\">面向高一至高三学生：系统梳理字音字形词语、病句标点与修辞、古诗文默写赏析、文言文实词虚词与句式、论述类与实用类阅读模板、名著导读与高考作文升格，每单元含知识讲解与小测。</div>' +")

# —— trial 文案里的「6 大板块」保持；渲染器内品牌色跟随全局替换 ——

# —— 品牌色：靛蓝 → 紫红系（9 色，与 jchinese 同款位置）——
BRAND = [('#3b5bdb', '#8e44ad'), ('#5c7cfa', '#b07cc6'), ('#2f6bd6', '#7d3c98'),
         ('#eef2ff', '#f5eefa'), ('#e7ecff', '#efe4f7'), ('#eaf1ff', '#f0e6f9'),
         ('#f5f8ff', '#faf5fd'), ('#eaeefc', '#f3e9f8'), ('#eef2ff', '#f5eefa')]
seen = set()
for a, b in BRAND:
    if a in seen:
        continue
    seen.add(a)
    reps.append((a, b, 0))  # 0 = 不限定次数

# —— 执行 + 断言 ——
for i, (old, new, n) in enumerate(reps):
    cnt = s.count(old)
    if n != 0:
        assert cnt == n, "替换未命中或多次命中(#%d): 期望%d次, 实际%d次\nOLD=%r" % (i, n, cnt, old[:70])
    s = s.replace(old, new)

io.open(DST, 'w', encoding='utf-8').write(s)
print("wrote", DST, len(s), "bytes")
print("DONE")
