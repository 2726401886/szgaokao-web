# -*- coding: utf-8 -*-
"""由 public/chemistry.html 克隆生成 public/physics.html（初高中物理）
改动点（每处均断言命中次数）：
  - 标题 / 顶栏文案 / 品牌色（化学紫 #6d28d9 → 物理深蓝靛 #1e40af）
  - PROG_KEY
  - init / exam / link 三处 API → /api/physics*
  - exam 模板名与专题包文案
用法：python tools/make_physics_page.py
"""
import io, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'public', 'chemistry.html')
DST = os.path.join(ROOT, 'public', 'physics.html')

s = io.open(SRC, encoding='utf-8').read()
reps = []


def add(old, new, n=1):
    reps.append((old, new, n))


# —— 标题 / 顶栏 ——
add('<title>初高中化学 · 知识点·题库·专题</title>',
    '<title>初高中物理 · 知识点·题库·专题</title>')
add('      <h1>⚗️ 初高中化学 · 知识点梳理·题库组卷·专题突破</h1>',
    '      <h1>⚛️ 初高中物理 · 知识点梳理·题库组卷·专题突破</h1>')
add('      <div class="sub">九年级至高三 · 化学启蒙·必修一二·选择性必修·反应原理·有机化学（点 🔊 可听读知识点）</div>',
    '      <div class="sub">八年级至高三 · 力与运动·功与能量·电磁学（点 🔊 可听读知识点）</div>')
add("  const PROG_KEY = 'chemistry_progress';",
    "  const PROG_KEY = 'physics_progress';")

# —— 侧栏专题包文案 ——
add("        '<div style=\"font-weight:800;font-size:15px;margin-bottom:6px;\">🧪 化学专题突破包（核心概念+方程式+实验+小测）</div>' +",
    "        '<div style=\"font-weight:800;font-size:15px;margin-bottom:6px;\">⚛️ 物理专题突破包（核心概念+公式+实验+小测）</div>' +")
add("        '<div style=\"font-size:13px;color:#888;line-height:1.7;\">面向九年级至高三学生：围绕化学入门概念、酸碱盐与反应原理、物质的量计算、元素周期律与物质结构、反应原理与实验探究等核心专题，系统梳理考点并配套小测，每单元含知识讲解与自测。</div>' +",
    "        '<div style=\"font-size:13px;color:#888;line-height:1.7;\">面向八年级至高三学生：围绕受力分析与牛顿定律、匀变速与曲线运动、功与能量守恒、电场电路与磁场、实验探究与科学方法等核心专题，系统梳理考点并配套小测，每单元含知识讲解与自测。</div>' +")

# —— API 三处 ——
add("    const r = await api('/api/chemistry');",
    "    const r = await api('/api/physics');")
add("      const r = await api('/api/chemistry-exam');",
    "      const r = await api('/api/physics-exam');")
add("      const r = await api('/api/chemistry-link');",
    "      const r = await api('/api/physics-link');")
add("    const r = await api('/api/chemistry-link?unit=' + encodeURIComponent(uid));",
    "    const r = await api('/api/physics-link?unit=' + encodeURIComponent(uid));")

# —— exam 默认卷名 + 年级筛选（物理含初中，7/8 需恢复）——
# ⚠️ 页面共有 3 处 grade 映射表：TPL 筛选(721) / 科目筛选(771) / 卷名(822)，
#    三处都要补 7/8，否则初中题无法按年级筛选。全部用纯 ASCII 锚点稳定命中。
_OLD_GRADE = "{'9':'初三','10':'高一','11':'高二','12':'高三'}"
_NEW_GRADE = "{'7':'初一','8':'初二','9':'初三','10':'高一','11':'高二','12':'高三'}"
add(_OLD_GRADE, _NEW_GRADE, 3)          # 3 处映射表
add("['', '9', '10', '11', '12']", "['', '7', '8', '9', '10', '11', '12']")   # TPL 年级按钮
add("['9', '10', '11', '12']", "['7', '8', '9', '10', '11', '12']")          # 科目年级按钮
# 注：物理题库 grade 为 8/9/10/11/12（无 7），但筛选器保留 7 以覆盖初一物理起步。

# —— TPL 模板名 ——
add("    fill: { name: '化学用语填空卷', cnt: { fill: 15, choice: 5 } },",
    "    fill: { name: '物理公式计算卷', cnt: { fill: 15, choice: 5 } },")

# —— 文案全局替换（标题等散落各处）——
add('初高中化学', '初高中物理', 0)

# —— 品牌色（化学紫 → 物理深蓝靛）——
BRAND = [('#6d28d9', '#1e40af'), ('#4c1d95', '#1e3a8a'), ('#8b5cf6', '#3b82f6'),
         ('#ede9fe', '#dbeafe'), ('#ddd6fe', '#bfdbfe'), ('#f5f3ff', '#eff6ff'),
         ('#faf5ff', '#f5f9ff'), ('#f3e8ff', '#e0edff')]
for a, b in BRAND:
    reps.append((a, b, 0))

# —— 执行 + 断言 ——
for i, (old, new, n) in enumerate(reps):
    cnt = s.count(old)
    if n != 0:
        assert cnt == n, "替换未命中或多次命中(#%d): 期望%d次, 实际%d次\nOLD=%r" % (i, n, cnt, old[:60])
    s = s.replace(old, new)

# —— 收尾校验 ——
assert '/api/chemistry' not in s, '仍残留 /api/chemistry'
assert 'chemistry_progress' not in s, '仍残留 chemistry_progress'
assert 'renderKnowledgeRead' in s, 'knowledge 渲染器缺失'
assert '/api/physics' in s, 'API 未替换'

io.open(DST, 'w', encoding='utf-8').write(s)
print("wrote", DST, len(s), "bytes")

# —— 产物语法校验 ——
scripts = re.findall(r'<script>(.*?)</script>', s, re.S)
tmp = os.path.join(ROOT, 'tools', '_check_physics.js')
io.open(tmp, 'w', encoding='utf-8').write(max(scripts, key=len))
print("extracted script ->", os.path.getsize(tmp), "bytes")
print("DONE")
