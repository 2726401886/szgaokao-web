# -*- coding: utf-8 -*-
"""将 politics 模块接入首页（index.html）：mod-card / MODINFO / forEach / hint / 激活 MODS / anyLocked
同时修改 web 与 worker 两份 index.html（两者仅 vocab 模块差异，本脚本用通用锚点兼容）。
每个替换均断言命中一次。
"""
import io, os

WEB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'public', 'index.html')
WORKER = r'E:/szgaokao.cn/worker/public/index.html'

REPS = []


def add(old, new):
    REPS.append((old, new))


# 1) mod-card：插在 hchinese 卡片之后、mindmap 工具卡之前
OLD_CARD = """      <button class="go" id="go-hchinese" onclick="enterMod('hchinese')">进入模块</button>
    </div>
    <div class="mod-card tool-card" id="mod-mindmap" style="border-color:var(--brand,#6a5cff);">"""
NEW_CARD = """      <button class="go" id="go-hchinese" onclick="enterMod('hchinese')">进入模块</button>
    </div>
    <div class="mod-card" id="mod-politics">
      <div class="icon">🏛️</div>
      <div class="name">初高中道法·政治 · 知识点梳理·题库组卷·专题突破</div>
      <div class="desc">七年级至高三 · 37 个核心知识点（带自测）+ 题库 57 题（选择/填空/阅读/写作）+ 5 大专题突破包；宪法/改革开放/制度自信/哲学/全球化</div>
      <div><span class="state" id="st-politics">加载中</span></div>
      <button class="go" id="go-politics" onclick="enterMod('politics')">进入模块</button>
    </div>
    <div class="mod-card tool-card" id="mod-mindmap" style="border-color:var(--brand,#6a5cff);">"""
add(OLD_CARD, NEW_CARD)

# 2) MODINFO
OLD_MODINFO = """  hchinese:        { url: './hchinese.html', name: '高中语文 · 字词古诗文文言文阅读名著写作' },
};"""
NEW_MODINFO = """  hchinese:        { url: './hchinese.html', name: '高中语文 · 字词古诗文文言文阅读名著写作' },
  politics:        { url: './politics.html', name: '初高中道法·政治 · 知识点梳理·题库组卷·专题突破' },
};"""
add(OLD_MODINFO, NEW_MODINFO)

# 3) forEach：在 hchinese 之后追加 politics（锚点通用，兼容 vocab 存在与否）
add("', 'hchinese'].forEach(m => renderMod(m));", "', 'hchinese', 'politics'].forEach(m => renderMod(m));")

# 4) hint：追加 politics 体验说明
add("高中语文每个板块第 1 组</div>", "高中语文每个板块第 1 组 / 初高中道法政治每个板块第 1 组</div>")

# 5) 激活成功 MODS：追加 politics:1
OLD_ACT = " MODS = { kids: 1, primary: 1, junior: 1, middle: 1, gk: 1, math: 1, senior: 1, 'senior-grammar': 1, 'senior-exam': 1, chinese: 1, jchinese: 1, hchinese: 1 }; renderHome(); }"
NEW_ACT = " MODS = { kids: 1, primary: 1, junior: 1, middle: 1, gk: 1, math: 1, senior: 1, 'senior-grammar': 1, 'senior-exam': 1, chinese: 1, jchinese: 1, hchinese: 1, politics: 1 }; renderHome(); }"
add(OLD_ACT, NEW_ACT)

# 6) anyLocked：追加 !MODS.politics
OLD_ANY = "    const anyLocked = !MODS.kids || !MODS.primary || !MODS.middle || !MODS.gk || !MODS.math;"
NEW_ANY = "    const anyLocked = !MODS.kids || !MODS.primary || !MODS.middle || !MODS.gk || !MODS.math || !MODS.politics;"
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
