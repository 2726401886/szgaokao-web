# -*- coding: utf-8 -*-
"""把 history 三份数据注入 worker.js（常量块 + trial 常量 + 3 条路由）。幂等。

⚠️ 关键（踩过的坑）：
  1) re.sub 替换串必须走「函数返回」，否则 JSON 里的 \\n 会被当换行注入。
  2) 锚点若带尾注释，`marker + "\\n"` 匹配 0 次 → replace 静默 no-op，
     常量没插进去而路由引用它 → 运行时 ReferenceError。
     故本脚本用「行首正则」定位，并断言产物存在。
  3) 重复运行会插入重复块 + 重复路由，故每次先判断标记是否存在。
用法：python tools/inject_history.py
"""
import io, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKER = r'E:/szgaokao.cn/worker/src/worker.js'
DATA = os.path.join(ROOT, 'data')


def compact(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':'))


HISTORY = json.load(io.open(os.path.join(DATA, 'history.json'), encoding='utf-8'))
EXAM = json.load(io.open(os.path.join(DATA, 'history_exam.json'), encoding='utf-8'))
LINK = json.load(io.open(os.path.join(DATA, 'history_link.json'), encoding='utf-8'))

BLOCKS = [
    ('HISTORY_DEFAULT', 'history_default', HISTORY),
    ('HISTORY_EXAM_DEFAULT', 'history_exam_default', EXAM),
    ('HISTORY_LINK_DEFAULT', 'history_link_default', LINK),
]

TRIAL_LINES = (
    'var TRIAL_HISTORY = 1;          // 高中历史：trial 仅开放每板块首个分组\n'
    'var TRIAL_HISTORY_EXAM = 5;     // 历史题库：trial 仅返回前 5 题\n'
    'var TRIAL_HISTORY_LINK = "hl1"; // 历史衔接包：trial 仅开放第 1 单元\n'
)

ROUTES = r'''
    // —— 高中历史：知识点 / 题库 / 专题衔接 ——
    if (path === "/api/history" && method === "GET") {
      const user = await uidOf(request, env);
      if (!user) return err(401, "未登录或登录已失效，请重新登录");
      const dev = getDev({}, request);
      if (!parseDevices(user).includes(dev)) return err(403, "当前设备未授权，请重新登录");
      const authed = modAuthed(user, "history") || modAuthed(user, "primary");
      const sec = JSON.parse(JSON.stringify(history_default.sections));
      const trimSec = (s) => { if (!authed && s.groups && s.groups.length) s.groups = s.groups.slice(0, 1); return s; };
      Object.keys(sec).forEach((k) => { sec[k] = trimSec(sec[k]); });
      return ok({ sections: sec, trial: !authed });
    }
    if (path === "/api/history-exam" && method === "GET") {
      const user = await uidOf(request, env);
      if (!user) return err(401, "未登录或登录已失效，请重新登录");
      const dev = getDev({}, request);
      if (!parseDevices(user).includes(dev)) return err(403, "当前设备未授权，请重新登录");
      const authed = modAuthed(user, "history") || modAuthed(user, "primary");
      const list = history_exam_default.questions;
      const qids = q.get("ids");
      if (qids) { const map = {}; list.forEach((x) => { map[x.id] = x; }); const picked = qids.split(",").filter((id) => map[id]).map((id) => map[id]); return ok({ questions: picked }); }
      const g = q.get("grade"), t = q.get("topic"), ty = q.get("type"), d = q.get("difficulty");
      let flt = list;
      if (g) flt = flt.filter((x) => String(x.grade) === g);
      if (t) flt = flt.filter((x) => String(x.topic) === t);
      if (ty) flt = flt.filter((x) => String(x.type) === ty);
      if (d) flt = flt.filter((x) => String(x.difficulty) === d);
      if (!authed) flt = flt.slice(0, TRIAL_HISTORY_EXAM);
      return ok({ questions: flt, topics: history_exam_default.topics, trial: !authed, total: list.length });
    }
    if (path === "/api/history-link" && method === "GET") {
      const user = await uidOf(request, env);
      if (!user) return err(401, "未登录或登录已失效，请重新登录");
      const dev = getDev({}, request);
      if (!parseDevices(user).includes(dev)) return err(403, "当前设备未授权，请重新登录");
      const authed = modAuthed(user, "history") || modAuthed(user, "primary");
      const list = history_link_default.units;
      const uid2 = q.get("unit");
      if (uid2) { const un = list.find((x) => x.id === uid2); if (!un) return err(404, "单元不存在"); if (!authed && uid2 !== TRIAL_HISTORY_LINK) return err(403, "体验模式仅可学习第 1 单元，输入授权码或联系管理员解锁全部单元"); return ok(un); }
      return ok({ units: authed ? list : list.filter((x) => x.id === TRIAL_HISTORY_LINK), trial: !authed });
    }
'''


def main():
    wk = io.open(WORKER, encoding='utf-8').read()
    added_blocks = 0

    # ---- 1) 常量块 ----
    for tag, var, obj in BLOCKS:
        start = '// === %s_START ===' % tag
        end = '// === %s_END ===' % tag
        raw = compact(obj)
        assert raw.count('\n') == 0, tag + ' compact 含换行'
        block = start + '\nvar ' + var + ' = ' + raw + ';\n' + end + '\n'
        if start in wk:
            wk = re.sub(re.escape(start) + r'.*?' + re.escape(end) + r'\n',
                        lambda m: block, wk, count=1, flags=re.S)
            print('替换已有 %s 块' % tag)
        else:
            anchor = '// === HCHINESE_KWD_DEFAULT_END ==='
            i = wk.find(anchor)
            assert i > 0, '找不到锚点 ' + anchor
            m = re.match(r'.*?\n', wk[i:], re.S)
            assert m, '锚点行结构异常'
            pos = i + m.end()
            wk = wk[:pos] + block + wk[pos:]
            print('插入 %s 块' % tag)
        added_blocks += 1

    # ---- 2) trial 常量（用行首正则，避免尾注释坑）----
    if 'TRIAL_HISTORY_EXAM' not in wk:
        anchor = 'var TRIAL_HCHINESE_GD = 1;'
        i = wk.find(anchor)
        assert i > 0, '找不到 trial 锚点'
        m = re.match(r'.*?\n', wk[i:], re.S)
        assert m, 'trial 锚点行结构异常'
        wk = wk[:i + m.end()] + TRIAL_LINES + wk[i + m.end():]
        print('插入 trial 常量')
    else:
        print('trial 常量已存在')

    # ---- 3) 路由 ----
    if 'path === "/api/history"' not in wk:
        # ⚠️ 必须插在锚点「整块结束之后」，不能紧跟锚点行 { 之后 —— 那会落进锚点 if 的作用域，
        #    路由永不可达（表现为线上 404）。故先定位锚点整块，再插到其后。
        anchor = 'if (path === "/api/hchinese-kwd" && method === "GET") {'
        i = wk.find(anchor)
        assert i > 0, '找不到路由锚点'
        # 从锚点起做花括号配平，找到该 if 块的结束位置
        depth = 0
        j = i
        started = False
        while j < len(wk):
            ch = wk[j]
            if ch == '{':
                depth += 1
                started = True
            elif ch == '}':
                depth -= 1
                if started and depth == 0:
                    break
            j += 1
        assert started and depth == 0, '锚点 if 块花括号未配平'
        pos = j + 1
        while pos < len(wk) and wk[pos] == '\n':
            pos += 1
        wk = wk[:pos] + ROUTES + '\n' + wk[pos:]
        print('插入 3 条路由')
    else:
        print('路由已存在')

    io.open(WORKER, 'w', encoding='utf-8').write(wk)

    # ---- 4) 产物校验 ----
    chk = io.open(WORKER, encoding='utf-8').read()
    for tag, var, _ in BLOCKS:
        assert chk.count('// === %s_START ===' % tag) == 1, tag + ' 块数量异常'
        assert ('var ' + var + ' =') in chk, tag + ' 变量未定义'
    for t in ('TRIAL_HISTORY', 'TRIAL_HISTORY_EXAM', 'TRIAL_HISTORY_LINK'):
        # 行首精确匹配：避免 TRIAL_HISTORY 是 TRIAL_HISTORY_EXAM 前缀导致子串误计
        n = len(re.findall(r'^var ' + t + r'\s*=', chk, flags=re.M))
        assert n == 1, '%s 未定义或重复（n=%d）' % (t, n)
    for r in ('/api/history"', '/api/history-exam"', '/api/history-link"'):
        assert chk.count('path === "%s' % r) == 1, r + ' 路由数量异常'
    # 所有被引用的 TRIAL_* 必须已定义
    defined = set(re.findall(r'var (TRIAL_[A-Z_]+)', chk))
    used = set(re.findall(r'(?<![\w.])TRIAL_[A-Z_]+', chk))
    miss = sorted(u for u in used if u not in defined)
    assert not miss, '未定义却被引用的 TRIAL_ 常量: %r' % miss
    print('产物校验通过（TRIAL_ 无悬空引用）')
    print('worker.js 新大小', os.path.getsize(WORKER))


if __name__ == '__main__':
    main()
    print('DONE')
