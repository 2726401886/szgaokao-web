# -*- coding: utf-8 -*-
"""首页接入 physics 模块（4 处 + 底部体验说明，缺一处卡片会一直显示"加载中"）：
  1) mod-card 卡片
  2) MODINFO 映射
  3) renderHome 渲染数组
  4) activate() 兜底 MODS
用法：python tools/patch_home_physics.py
"""
import io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, 'public', 'index.html')

s = io.open(HTML, encoding='utf-8').read()
reps = []


def add(old, new, n=1):
    reps.append((old, new, n))


# —— 1) mod-card：插在 history 卡片之后 ——
add("""      <button class="go" id="go-history" onclick="enterMod('history')">进入模块</button>
    </div>""",
    """      <button class="go" id="go-history" onclick="enterMod('history')">进入模块</button>
    </div>
    <div class="mod-card" id="mod-physics">
      <div class="icon">⚛️</div>
      <div class="name">初高中物理 · 知识点梳理·题库组卷·专题突破</div>
      <div class="desc">八年级至高三 · 25 个核心知识点（带自测）+ 题库 50 题（选择/填空/阅读/写作）+ 5 大专题包；受力分析·牛顿定律·曲线运动·功与能量·电磁学</div>
      <div><span class="state" id="st-physics">加载中</span></div>
      <button class="go" id="go-physics" onclick="enterMod('physics')">进入模块</button>
    </div>""")

# —— 2) MODINFO 映射 ——
add("  history:         { url: './history.html', name: '初高中历史 · 知识点梳理·题库组卷·专题突破' },",
    "  history:         { url: './history.html', name: '初高中历史 · 知识点梳理·题库组卷·专题突破' },\n"
    "  physics:         { url: './physics.html', name: '初高中物理 · 知识点梳理·题库组卷·专题突破' },")

# —— 3) renderHome 渲染数组 ——
add("'politics', 'geography', 'chemistry', 'history'].forEach(m => renderMod(m));",
    "'politics', 'geography', 'chemistry', 'history', 'physics'].forEach(m => renderMod(m));")

# —— 4) activate() 兜底 MODS ——
add("chemistry: 1, history: 1 }; renderHome(); }",
    "chemistry: 1, history: 1, physics: 1 }; renderHome(); }")

# —— 5) 底部体验说明 ——
add("初高中历史每个板块第 1 组</div>",
    "初高中历史每个板块第 1 组 / 初高中物理每个板块第 1 组</div>")

# —— 执行 + 断言 ——
for i, (old, new, n) in enumerate(reps):
    cnt = s.count(old)
    assert cnt == n, "替换未命中或多次命中(#%d): 期望%d次, 实际%d次\nOLD=%r" % (i, n, cnt, old[:70])
    s = s.replace(old, new)

# —— 收尾校验：4 处接入点齐全 ——
assert 'id="mod-physics"' in s, 'mod-card 缺失'
assert "enterMod('physics')" in s, 'go 按钮缺失'
assert "physics:         { url: './physics.html'" in s, 'MODINFO 缺失'
assert "'chemistry', 'history', 'physics'" in s, 'renderHome 数组缺失'
assert 'chemistry: 1, history: 1, physics: 1 }' in s, 'activate 兜底缺失'
assert "url: './physics.html'" in s, 'physics.html 未被引用'

io.open(HTML, 'w', encoding='utf-8').write(s)
print("patched", HTML, len(s), "bytes")
print("DONE")
