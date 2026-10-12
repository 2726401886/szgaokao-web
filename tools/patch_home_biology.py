# -*- coding: utf-8 -*-
"""首页接入 biology 模块（4 处 + 底部体验说明，缺一处卡片会一直显示"加载中"）：
  1) mod-card 卡片（插在 physics 卡片之后）
  2) MODINFO 映射
  3) renderHome 渲染数组
  4) activate() 兜底 MODS
用法：python tools/patch_home_biology.py
"""
import io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, 'public', 'index.html')

s = io.open(HTML, encoding='utf-8').read()
reps = []


def add(old, new, n=1):
    reps.append((old, new, n))


# —— 1) mod-card：插在 physics 卡片之后 ——
add("""      <button class="go" id="go-physics" onclick="enterMod('physics')">进入模块</button>
    </div>""",
    """      <button class="go" id="go-physics" onclick="enterMod('physics')">进入模块</button>
    </div>
    <div class="mod-card" id="mod-biology">
      <div class="icon">🌿</div>
      <div class="name">初高中生物 · 知识点梳理·题库组卷·专题突破</div>
      <div class="desc">七年级至高三 · 4 册课本同步（49 核心知识点带自测 + 同步练习）+ 题库 56 题（选择/填空/阅读/写作）+ 5 大专题突破包；细胞结构·遗传定律·DNA与基因·动物与菌类·生物与环境稳态</div>
      <div><span class="state" id="st-biology">加载中</span></div>
      <button class="go" id="go-biology" onclick="enterMod('biology')">进入模块</button>
    </div>""")

# —— 2) MODINFO 映射 ——
add("  physics:         { url: './physics.html', name: '初高中物理 · 知识点梳理·题库组卷·专题突破' },",
    "  physics:         { url: './physics.html', name: '初高中物理 · 知识点梳理·题库组卷·专题突破' },\n"
    "  biology:         { url: './biology.html', name: '初高中生物 · 知识点梳理·题库组卷·专题突破' },")

# —— 3) renderHome 渲染数组 ——
add("'politics', 'geography', 'chemistry', 'history', 'physics'].forEach(m => renderMod(m));",
    "'politics', 'geography', 'chemistry', 'history', 'physics', 'biology'].forEach(m => renderMod(m));")

# —— 4) activate() 兜底 MODS ——
add("chemistry: 1, history: 1, physics: 1 }; renderHome(); }",
    "chemistry: 1, history: 1, physics: 1, biology: 1 }; renderHome(); }")

# —— 5) 底部体验说明 ——
add("初高中物理每个板块第 1 组</div>",
    "初高中物理每个板块第 1 组 / 初高中生物每个板块第 1 组</div>")

# —— 执行 + 断言 ——
for i, (old, new, n) in enumerate(reps):
    cnt = s.count(old)
    assert cnt == n, "替换未命中或多次命中(#%d): 期望%d次, 实际%d次\nOLD=%r" % (i, n, cnt, old[:70])
    s = s.replace(old, new)

# —— 收尾校验：4 处接入点齐全 ——
assert 'id="mod-biology"' in s, 'mod-card 缺失'
assert "enterMod('biology')" in s, 'go 按钮缺失'
assert "biology:         { url: './biology.html'" in s, 'MODINFO 缺失'
assert "'chemistry', 'history', 'physics', 'biology'" in s, 'renderHome 数组缺失'
assert 'chemistry: 1, history: 1, physics: 1, biology: 1 }' in s, 'activate 兜底缺失'
assert "url: './biology.html'" in s, 'biology.html 未被引用'

io.open(HTML, 'w', encoding='utf-8').write(s)
print("patched", HTML, len(s), "bytes")
print("DONE")
