# -*- coding: utf-8 -*-
"""把 politics_gd（广东高考政治结构仿真卷）幂等注入 worker.js。
常量块 + /api/politics-gd 路由 + trial 常量。
⚠️ 幂等：先断言标记为 0 再跑；重复运行会重复块。
用法：python tools/inject_politics_gd.py
"""
import io, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKER = r'E:/szgaokao.cn/worker/src/worker.js'
GD_JSON = os.path.join(ROOT, 'data', 'politics_gd.json')

GD = json.load(io.open(GD_JSON, encoding='utf-8'))


def compact(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':'))


def main():
    wk = io.open(WORKER, encoding='utf-8').read()
    assert wk.count("POLITICS_GD_DEFAULT_START") == 0, "POLITICS_GD 已注入，请先 git checkout -- src/worker.js 还原"

    # 1) 常量块：插在 POLITICS_LINK_DEFAULT_END 行之后
    marker = "// === POLITICS_LINK_DEFAULT_END ==="
    assert re.search(re.escape(marker), wk), "找不到 POLITICS_LINK_DEFAULT_END 标记"
    const_block = (
        "// === POLITICS_GD_DEFAULT_START ===\n"
        "var politics_gd_default = " + compact(GD) + ";\n"
        "// === POLITICS_GD_DEFAULT_END ===\n"
    )
    wk = re.sub(re.escape(marker) + r'.*\n', lambda m: m.group(0) + const_block, wk, count=1)

    # 2) trial 常量：插在 TRIAL_POLITICS_EXAM 行之后
    trial_marker = "var TRIAL_POLITICS_EXAM = 5;"
    assert re.search(re.escape(trial_marker), wk), "找不到 TRIAL_POLITICS_EXAM"
    trial_block = (
        "var TRIAL_POLITICS_GD = 1;   // 广东政治仿真卷：trial 仅开放第 1 套\n"
    )
    wk = re.sub(re.escape(trial_marker) + r'.*\n', lambda m: m.group(0) + trial_block, wk, count=1)

    # 3) 路由：插在 /api/politics-link 路由块之后（用 404 兜底行做锚更稳）
    route_anchor = 'return err(404, "\\u63A5\\u53E3\\u4E0D\\u5B58\\u5728");'
    assert re.search(re.escape(route_anchor), wk), "找不到 404 兜底路由"
    route_block = (
        "    if (path === \"/api/politics-gd\" && method === \"GET\") {\n"
        "      const user = await uidOf(request, env);\n"
        "      if (!user) return err(401, \"\\u672A\\u767B\\u5F55\\u6216\\u767B\\u5F55\\u5DF2\\u5931\\u6548\\uFF0C\\u8BF7\\u91CD\\u65B0\\u767B\\u5F55\");\n"
        "      const dev = getDev({}, request);\n"
        "      if (!parseDevices(user).includes(dev)) return err(403, \"\\u5F53\\u524D\\u8BBE\\u5907\\u672A\\u6388\\u6743\\uFF0C\\u8BF7\\u91CD\\u65B0\\u767B\\u5F55\");\n"
        "      const authed = modAuthed(user, \"politics\") || modAuthed(user, \"primary\");\n"
        "      const pid = q.get(\"paper\");\n"
        "      const all = politics_gd_default.papers;\n"
        "      if (pid) { const p = all.find((x) => x.id === pid); if (!p) return err(404, \"\\u5377\\u4E0D\\u5B58\\u5728\"); if (!authed && Number(pid.slice(-4)) !== TRIAL_POLITICS_GD) return err(403, \"\\u4F53\\u9A8C\\u6A21\\u5F0F\\u4EC5\\u53EF\\u4F7F\\u7528\\u7B2C 1 \\u5957\\u5377\\uFF0C\\u8F93\\u5165\\u6388\\u6743\\u7801\\u6216\\u8054\\u7CFB\\u7BA1\\u7406\\u5458\\u89E3\\u9501\\u5168\\u90E8\\u5377\\u7EC4\"); return ok(p); }\n"
        "      const list = all.map((p) => ({ id: p.id, year: p.year, title: p.title, theme: p.theme, totalScore: p.totalScore, durationMin: p.durationMin, questionCount: p.modules.reduce((n, m) => n + m.parts.reduce((k, x) => k + x.questions.length, 0), 0) }));\n"
        "      return ok({ region: politics_gd_default.region, examType: politics_gd_default.examType, kind: politics_gd_default.kind, notice: politics_gd_default.notice, structure: politics_gd_default.structure, papers: authed ? list : list.slice(0, TRIAL_POLITICS_GD), trial: !authed });\n"
        "    }\n"
        "    " + route_anchor + "\n"
    )
    wk = re.sub(re.escape(route_anchor) + r'.*\n', lambda m: route_block, wk, count=1)

    io.open(WORKER, 'w', encoding='utf-8').write(wk)
    print("injected into worker.js, new size", os.path.getsize(WORKER))


if __name__ == "__main__":
    main()
    print("DONE")
