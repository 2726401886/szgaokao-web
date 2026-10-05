# -*- coding: utf-8 -*-
"""刷新 worker.js 中的 GEOGRAPHY_GD 常量块（幂等：已注入则替换，未注入则插入），
并修复 trial 访问 bug：原 `Number(pid.slice(-4))` 会把首套卷也 403，
改为按试卷在列表中的位置判断（前 TRIAL_GEOGRAPHY_GD 套对 trial 开放）。

⚠️ 关键：re.sub 的替换串必须走「函数返回」，否则 JSON 里的 \\n 会被当作换行注入。
用法：python tools/refresh_geography_gd.py
"""
import io, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKER = r'E:/szgaokao.cn/worker/src/worker.js'
GD_JSON = os.path.join(ROOT, 'data', 'geography_gd.json')

GD = json.load(io.open(GD_JSON, encoding='utf-8'))


def compact(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':'))


def main():
    wk = io.open(WORKER, encoding='utf-8').read()

    raw = compact(GD)
    assert raw.count('\n') == 0, "compact 不应含换行，实际 %d" % raw.count('\n')

    block = ("// === GEOGRAPHY_GD_DEFAULT_START ===\n"
             "var geography_gd_default = " + raw + ";\n"
             "// === GEOGRAPHY_GD_DEFAULT_END ===\n")

    if "GEOGRAPHY_GD_DEFAULT_START" in wk:
        # 用函数返回替换串，避免 \\n 被 re.sub 当作换行
        wk = re.sub(r"// === GEOGRAPHY_GD_DEFAULT_START ===.*?// === GEOGRAPHY_GD_DEFAULT_END ===\n",
                    lambda m: block, wk, count=1, flags=re.S)
        print("替换已有 GEOGRAPHY_GD 块")
    else:
        marker = "// === GEOGRAPHY_LINK_DEFAULT_END ==="
        assert re.search(re.escape(marker), wk), "找不到 GEOGRAPHY_LINK_DEFAULT_END 标记"
        wk = re.sub(re.escape(marker) + r'.*\n', lambda m: m.group(0) + block, wk, count=1)
        print("插入 GEOGRAPHY_GD 块")

    # 修复 trial 校验：按位置而非 id 尾号
    old = 'if (!authed && Number(pid.slice(-4)) !== TRIAL_GEOGRAPHY_GD)'
    new = 'if (!authed && all.findIndex((x) => x.id === pid) >= TRIAL_GEOGRAPHY_GD)'
    if old in wk:
        wk = wk.replace(old, new)
        print("已修复 trial 校验为按位置判断")
    else:
        print("（trial 校验行未匹配，可能已修复或无此行）")

    io.open(WORKER, 'w', encoding='utf-8').write(wk)
    print("worker.js 新大小", os.path.getsize(WORKER))


if __name__ == "__main__":
    main()
    print("DONE")
