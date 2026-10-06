# -*- coding: utf-8 -*-
"""刷新 worker.js 中的 HCHINESE_KWD 常量块（幂等：已注入则替换，未注入则插入），
并确保存在 /api/hchinese-kwd 路由与 TRIAL_HCHINESE_KWD 常量。

⚠️ 关键：re.sub 的替换串必须走「函数返回」，否则 JSON 里的 \\n 会被当作换行注入。
用法：python tools/refresh_hchinese_kwd.py
"""
import io, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKER = r'E:/szgaokao.cn/worker/src/worker.js'
KWD_JSON = os.path.join(ROOT, 'data', 'hchinese_kwd.json')

KWD = json.load(io.open(KWD_JSON, encoding='utf-8'))


def compact(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':'))


def main():
    wk = io.open(WORKER, encoding='utf-8').read()

    raw = compact(KWD)
    assert raw.count('\n') == 0, "compact 不应含换行，实际 %d" % raw.count('\n')

    block = ("// === HCHINESE_KWD_DEFAULT_START ===\n"
             "var hchinese_kwd_default = " + raw + ";\n"
             "// === HCHINESE_KWD_DEFAULT_END ===\n")

    # 1) 常量块
    if "HCHINESE_KWD_DEFAULT_START" in wk:
        wk = re.sub(r"// === HCHINESE_KWD_DEFAULT_START ===.*?// === HCHINESE_KWD_DEFAULT_END ===\n",
                    lambda m: block, wk, count=1, flags=re.S)
        print("替换已有 HCHINESE_KWD 块")
    else:
        marker = "// === HCHINESE_GD_DEFAULT_END ==="
        assert re.search(re.escape(marker), wk), "找不到 HCHINESE_GD_DEFAULT_END 标记"
        wk = re.sub(re.escape(marker) + r'.*\n', lambda m: m.group(0) + block, wk, count=1)
        print("插入 HCHINESE_KWD 块")

    # 2) trial 常量
    if "TRIAL_HCHINESE_KWD" not in wk:
        anchor = "var TRIAL_HCHINESE_GD = 1;"
        assert anchor in wk, "找不到 TRIAL_HCHINESE_GD"
        wk = wk.replace(anchor, anchor + "\nvar TRIAL_HCHINESE_KWD = 1;   // 课外阅读拓展：trial 仅开放第 1 专题", 1)
        print("插入 TRIAL_HCHINESE_KWD 常量")

    # 3) 路由（插到 hchinese-paper 路由之后）
    if '"/api/hchinese-kwd"' not in wk:
        anchor = 'if (path === "/api/hchinese-paper" && method === "GET") {'
        i = wk.find(anchor)
        assert i > 0, "找不到 hchinese-paper 路由"
        # 找到该路由块的结束（下一个 "\n    }\n" 之后的空行）——用其后第一个独立缩进路由做锚点更稳
        # 简化：在 hchinese-paper 路由结束的 "return ok({ ... papers: ... });\n    }" 后插入
        m = re.search(r'(if \(path === "/api/hchinese-paper".*?\n    \}\n)', wk, re.S)
        assert m, "无法定位 hchinese-paper 路由结束"
        route = m.group(1)
        new_route = route + """
    if (path === "/api/hchinese-kwd" && method === "GET") {
      const user = await uidOf(request, env);
      if (!user) return err(401, "未登录或登录已失效，请重新登录");
      const dev = getDev({}, request);
      if (!parseDevices(user).includes(dev)) return err(403, "当前设备未授权，请重新登录");
      const authed = modAuthed(user, "hchinese") || modAuthed(user, "primary");
      const uid2 = q.get("unit");
      const all = hchinese_kwd_default.units;
      if (uid2) { const u = all.find((x) => x.id === uid2); if (!u) return err(404, "专题不存在"); if (!authed && all.findIndex((x) => x.id === uid2) >= TRIAL_HCHINESE_KWD) return err(403, "体验模式仅可使用第 1 专题，输入授权码或联系管理员解锁全部专题"); return ok(u); }
      const list = all.map((u) => ({ id: u.id, no: u.no, title: u.title, desc: u.desc, questionCount: u.questionCount }));
      return ok({ examType: hchinese_kwd_default.examType, notice: hchinese_kwd_default.notice, structure: hchinese_kwd_default.structure, units: authed ? list : list.slice(0, TRIAL_HCHINESE_KWD), trial: !authed });
    }
"""
        wk = wk[:m.start(1)] + new_route + wk[m.end(1):]
        print("插入 /api/hchinese-kwd 路由")

    io.open(WORKER, 'w', encoding='utf-8').write(wk)
    print("worker.js 新大小", os.path.getsize(WORKER))


if __name__ == "__main__":
    main()
    print("DONE")
