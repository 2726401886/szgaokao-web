# -*- coding: utf-8 -*-
"""将 chemistry 模块接入首页（index.html）：mod-card / MODINFO / forEach / hint / 激活 MODS / anyLocked
同时修改 web 与 worker 两份 index.html（两者模块列表略有差异，本脚本用通用锚点兼容）。
每个替换均断言命中一次。
用法：python tools/patch_home_chemistry.py
"""
import io, os

WEB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'public', 'index.html')
WORKER = r'E:/szgaokao.cn/worker/public/index.html'

REPS = []


def add(old, new):
    REPS.append((old, new))


# 1) mod-card：插在 geography 卡片之后、mindmap 工具卡之前
OLD_CARD = """      <button class="go" id="go-geography" onclick="enterMod('geography')">进入模块</button>
    </div>
    <div class="mod-card tool-card" id="mod-mindmap" style="border-color:var(--brand,#6a5cff);">"""
NEW_CARD = """      <button class="go" id="go-geography" onclick="enterMod('geography')">进入模块</button>
    </div>
    <div class="mod-card" id="mod-chemistry">
      <div class="icon">⚗️</div>
      <div class="name">初高中化学 · 知识点梳理·题库组卷·专题突破</div>
      <div class="desc">九年级至高三 · 44 个核心知识点（带自测）+ 题库 46 题（选择/填空/实验探究/论述）+ 5 大专题包；物质变化·离子反应·物质的量·元素周期律·有机化学</div>
      <div><span class="state" id="st-chemistry">加载中</span></div>
      <button class="go" id="go-chemistry" onclick="enterMod('chemistry')">进入模块</button>
    </div>
    <div class="mod-card tool-card" id="mod-mindmap" style="border-color:var(--brand,#6a5cff);">"""
add(OLD_CARD, NEW_CARD)

# 2) MODINFO
OLD_MODINFO = """  geography:       { url: './geography.html', name: '初高中地理 · 知识点梳理·题库组卷·专题突破' },
};"""
NEW_MODINFO = """  geography:       { url: './geography.html', name: '初高中地理 · 知识点梳理·题库组卷·专题突破' },
  chemistry:       { url: './chemistry.html', name: '初高中化学 · 知识点梳理·题库组卷·专题突破' },
};"""
add(OLD_MODINFO, NEW_MODINFO)

# 3) forEach：在 geography 之后追加 chemistry
add("', 'geography'].forEach(m => renderMod(m));", "', 'geography', 'chemistry'].forEach(m => renderMod(m));")

# 4) hint：追加 chemistry 体验说明
add("初高中地理每个板块第 1 组</div>", "初高中地理每个板块第 1 组 / 初高中化学每个板块第 1 组</div>")

# 5) 激活成功 MODS：追加 chemistry:1
OLD_ACT = "politics: 1, geography: 1 }; renderHome(); }"
NEW_ACT = "politics: 1, geography: 1, chemistry: 1 }; renderHome(); }"
add(OLD_ACT, NEW_ACT)

# 6) anyLocked：追加 !MODS.chemistry
OLD_ANY = "const anyLocked = !MODS.kids || !MODS.primary || !MODS.middle || !MODS.gk || !MODS.math || !MODS.politics || !MODS.geography;"
NEW_ANY = "const anyLocked = !MODS.kids || !MODS.primary || !MODS.middle || !MODS.gk || !MODS.math || !MODS.politics || !MODS.geography || !MODS.chemistry;"
add(OLD_ANY, NEW_ANY)


def patch(path):
    s = io.open(path, encoding='utf-8').read()
    for i, (old, new) in enumerate(REPS):
        cnt = s.count(old)
        assert cnt == 1, "文件 %s 替换 #%d 期望1次实际%d次\nOLD=%r" % (path, i, cnt, old[:50])
        s = s.replace(old, new)
    io.open(path, 'w', encoding='utf-8').write(s)
    print("patched", path, len(s), "bytes")


for f in (WEB, WORKER):
    assert os.path.exists(f), "文件不存在: " + f
    patch(f)
print("DONE")
