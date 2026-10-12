# -*- coding: utf-8 -*-
"""由 public/physics.html 克隆生成 public/biology.html（初高中生物）
改动点（每处均断言命中次数）：
  - 标题 / 顶栏文案
  - PROG_KEY
  - 4 处 API → /api/biology*
  - 课本同步 / 知识点梳理 硬编码标题里的「物理」→「生物」
  - “全部六册”→“全部四册” / 每节题量文案
  - 品牌色（物理深蓝靛 → 生物深绿）
用法：python tools/make_biology_page.py
"""
import io, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'public', 'physics.html')
DST = os.path.join(ROOT, 'public', 'biology.html')

s = io.open(SRC, encoding='utf-8').read()
reps = []


def add(old, new, n=1):
    reps.append((old, new, n))


# —— 标题 / 顶栏 ——
add('<title>初高中物理 · 知识点·题库·专题</title>',
    '<title>初高中生物 · 知识点·题库·专题</title>')
add('      <h1>⚛️ 初高中物理 · 知识点梳理·题库组卷·专题突破</h1>',
    '      <h1>🌿 初高中生物 · 知识点梳理·题库组卷·专题突破</h1>')
add('      <div class="sub">八年级至高三 · 力与运动·功与能量·电磁学（点 🔊 可听读知识点）</div>',
    '      <div class="sub">七年级至高三 · 细胞·遗传·生态·动物与菌类（覆盖人教版初高中）｜教研团队 23年行业执业经验</div>')
add("  const PROG_KEY = 'physics_progress';",
    "  const PROG_KEY = 'biology_progress';")

# —— 4 处 API（前缀替换，覆盖带 query 的变体）——
# 不带收尾引号，匹配 api('/api/physics-book 即可覆盖 ?book/?chapter/?section 变体
# physics.html 中各前缀出现次数：book=4, knowledge=4, exam=1, link=2
add("api('/api/physics-book", "api('/api/biology-book", 4)
add("api('/api/physics-knowledge", "api('/api/biology-knowledge", 4)
add("api('/api/physics-exam", "api('/api/biology-exam", 1)
add("api('/api/physics-link", "api('/api/biology-link", 2)

# —— 硬编码标题里的「物理」→「生物」——
add('⚛️ 物理 · 课本同步', '🌿 生物 · 课本同步', 1)
add('📘 物理 · 知识点梳理', '📘 生物 · 知识点梳理', 1)
add("('初高中物理' +", "('初高中生物' +", 1)  # 题库默认卷名前缀

# —— 册数 / 每节题量文案 ——
add('全部六册', '全部四册', 2)
add('每节不少于 10 题，题型贴合中高考', '每节含同步练习，题型贴合中高考', 1)
add('每节不少于 12 题，题型贴合中高考真题', '每节含中高考题型练习', 1)

# —— 品牌色（物理深蓝靛 → 生物深绿）——
BRAND = [
    ('#1e40af', '#15803d'), ('#1e3a8a', '#14532d'), ('#3b82f6', '#22c55e'), ('#3b6fe0', '#16a34a'),
    ('#dbeafe', '#dcfce7'), ('#bfdbfe', '#bbf7d0'), ('#e0edff', '#e7f8ee'), ('#eef2ff', '#ecfdf3'),
    ('#eff6ff', '#f0fdf4'), ('#f5f9ff', '#f6fef9'), ('#fafcff', '#f7fef9'), ('#e0e8ff', '#e7f8ee'),
]
for a, b in BRAND:
    reps.append((a, b, 0))

# —— 执行 + 断言 ——
for i, (old, new, n) in enumerate(reps):
    cnt = s.count(old)
    if n != 0:
        assert cnt == n, "替换未命中或多次命中(#%d): 期望%d次, 实际%d次\nOLD=%r" % (i, n, cnt, old[:60])
    s = s.replace(old, new)

# —— 收尾校验 ——
assert '/api/physics' not in s, '仍残留 /api/physics'
assert 'physics_progress' not in s, '仍残留 physics_progress'
assert '初高中物理' not in s, '仍残留 初高中物理'
assert '/api/biology' in s, 'API 未替换'
assert "PROG_KEY = 'biology_progress'" in s, 'PROG_KEY 未替换'

io.open(DST, 'w', encoding='utf-8').write(s)
print("wrote", DST, len(s), "bytes")

# —— 产物语法校验（抽取最长内联 script 跑 node --check）——
scripts = re.findall(r'<script>(.*?)</script>', s, re.S)
tmp = os.path.join(ROOT, 'tools', '_check_biology.js')
io.open(tmp, 'w', encoding='utf-8').write(max(scripts, key=len))
print("extracted script ->", os.path.getsize(tmp), "bytes")
print("DONE")
