# -*- coding: utf-8 -*-
"""刷新 worker.js 中的 ENGLISH_GD 常量块（幂等：已注入则替换，未注入则插入）。

⚠️ 关键：re.sub 的替换串必须走「函数返回」，否则 JSON 里的 \\n 会被当作换行注入。
用法：python tools/refresh_english_gd.py
"""
import io, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKER = r'E:/szgaokao.cn/worker/src/worker.js'
GD_JSON = os.path.join(ROOT, 'data', 'english_gd.json')

GD = json.load(io.open(GD_JSON, encoding='utf-8'))


def compact(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':'))


def main():
    wk = io.open(WORKER, encoding='utf-8').read()

    raw = compact(GD)
    assert raw.count('\n') == 0, "compact 不应含换行，实际 %d" % raw.count('\n')

    block = ("// === ENGLISH_GD_DEFAULT_START ===\n"
             "var english_gd_default = " + raw + ";\n"
             "// === ENGLISH_GD_DEFAULT_END ===\n")

    if "ENGLISH_GD_DEFAULT_START" in wk:
        wk = re.sub(r"// === ENGLISH_GD_DEFAULT_START ===.*?// === ENGLISH_GD_DEFAULT_END ===\n",
                    lambda m: block, wk, count=1, flags=re.S)
        print("替换已有 ENGLISH_GD 块")
    else:
        marker = "// === GEOGRAPHY_GD_DEFAULT_END ==="
        assert re.search(re.escape(marker), wk), "找不到 GEOGRAPHY_GD_DEFAULT_END 标记"
        wk = re.sub(re.escape(marker) + r'.*\n', lambda m: m.group(0) + block, wk, count=1)
        print("插入 ENGLISH_GD 块")

    io.open(WORKER, 'w', encoding='utf-8').write(wk)
    print("worker.js 新大小", os.path.getsize(WORKER))


if __name__ == "__main__":
    main()
    print("DONE")
