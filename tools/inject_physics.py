# -*- coding: utf-8 -*-
"""把 physics 三份数据注入 worker.js（常量块 + trial 常量 + 3 条路由）。幂等。

⚠️ 两个已踩过的坑（见 skill szg-new-module-mirror 2.8 节）：
  1) 路由必须插在锚点「整块结束之后」，否则会落进锚点 if 的作用域内 ——
     语法合法、node --check 通过，但运行时永不可达（线上全 404）。故用花括号配平定位。
  2) 校验常量唯一性必须用行首正则（形如 ^var X\\s*=），子串计数会把前缀（TRIAL_PHYSICS 之于
     TRIAL_PHYSICS_EXAM）算进去而误报。
  3) re.sub 替换串必须走「函数返回」，否则 JSON 里的 \\n 会被当换行注入。
用法：python tools/inject_physics.py
"""
import io, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKER = r'E:/szgaokao.cn/worker/src/worker.js'
DATA = os.path.join(ROOT, 'data')

HISTORY = json.load(io.open(os.path.join(DATA, 'physics.json'), encoding='utf-8'))
EXAM = json.load(io.open(os.path.join(DATA, 'physics_exam.json'), encoding='utf-8'))
LINK = json.load(io.open(os.path.join(DATA, 'physics_link.json'), encoding='utf-8'))

BLOCKS = [
    ('PHYSICS_DEFAULT', 'physics_default', HISTORY),
    ('PHYSICS_EXAM_DEFAULT', 'physics_exam_default', EXAM),
    ('PHYSICS_LINK_DEFAULT', 'physics_link_default', LINK),
]

TRIAL_LINES = (
    'var TRIAL_PHYSICS = 1;          // 物理：trial 仅开放每板块首个分组\n'
    'var TRIAL_PHYSICS_EXAM = 5;     // 物理题库：trial 仅返回前 5 题\n'
    'var TRIAL_PHYSICS_LINK = "pl1"; // 物理衔接包：trial 仅开放第 1 单元\n'
)

ROUTES = r'''
    // —— 初高中物理：知识点 / 题库 / 专题衔接 ——
    if (path === "/api/physics" && method === "GET") {
      const user = await uidOf(request, env);
      if (!user) return err(401, "未登录或登录已失效，请重新登录");
      const dev = getDev({}, request);
      if (!parseDevices(user).includes(dev)) return err(403, "当前设备未授权，请重新登录");
      const authed = modAuthed(user, "physics") || modAuthed(user, "primary");
      const sec = JSON.parse(JSON.stringify(physics_default.sections));
      const trimSec = (s) => { if (!authed && s.groups && s.groups.length) s.groups = s.groups.slice(0, 1); return s; };
      Object.keys(sec).forEach((k) => { sec[k] = trimSec(sec[k]); });
      return ok({ sections: sec, trial: !authed });
    }
    if (path === "/api/physics-exam" && method === "GET") {
      const user = await uidOf(request, env);
      if (!user) return err(401, "未登录或登录已失效，请重新登录");
      const dev = getDev({}, request);
      if (!parseDevices(user).includes(dev)) return err(403, "当前设备未授权，请重新登录");
      const authed = modAuthed(user, "physics") || modAuthed(user, "primary");
      const list = physics_exam_default.questions;
      const qids = q.get("ids");
      if (qids) { const map = {}; list.forEach((x) => { map[x.id] = x; }); const picked = qids.split(",").filter((id) => map[id]).map((id) => map[id]); return ok({ questions: picked }); }
      const g = q.get("grade"), t = q.get("topic"), ty = q.get("type"), d = q.get("difficulty");
      let flt = list;
      if (g) flt = flt.filter((x) => String(x.grade) === g);
      if (t) flt = flt.filter((x) => String(x.topic) === t);
      if (ty) flt = flt.filter((x) => String(x.type) === ty);
      if (d) flt = flt.filter((x) => String(x.difficulty) === d);
      if (!authed) flt = flt.slice(0, TRIAL_PHYSICS_EXAM);
      return ok({ questions: flt, topics: physics_exam_default.topics, trial: !authed, total: list.length });
    }
    if (path === "/api/physics-link" && method === "GET") {
      const user = await uidOf(request, env);
      if (!user) return err(401, "未登录或登录已失效，请重新登录");
      const dev = getDev({}, request);
      if (!parseDevices(user).includes(dev)) return err(403, "当前设备未授权，请重新登录");
      const authed = modAuthed(user, "physics") || modAuthed(user, "primary");
      const list = physics_link_default.units;
      const uid2 = q.get("unit");
      if (uid2) { const un = list.find((x) => x.id === uid2); if (!un) return err(404, "单元不存在"); if (!authed && uid2 !== TRIAL_PHYSICS_LINK) return err(403, "体验模式仅可学习第 1 单元，输入授权码或联系管理员解锁全部单元"); return ok(un); }
      return ok({ units: authed ? list : list.filter((x) => x.id === TRIAL_PHYSICS_LINK), trial: !authed });
    }
'''


def block_end(text, start_idx):
    """从 start_idx 处 '{' 做花括号配平，返回该块结束后的位置。"""
    depth = 0
    j = start_idx
    started = False
    while j < len(text):
        if text[j] == '{':
            depth += 1
            started = True
        elif text[j] == '}':
            depth -= 1
            if started and depth == 0:
                return j + 1
        j += 1
    raise AssertionError('花括号未配平')


def main():
    wk = io.open(WORKER, encoding='utf-8').read()

    # ---- 1) 常量块 ----
    for tag, var, obj in BLOCKS:
        start = '// === %s_START ===' % tag
        end = '// === %s_END ===' % tag
        raw = json.dumps(obj, ensure_ascii=False, separators=(',', ':'))
        assert raw.count('\n') == 0, tag + ' compact 含换行'
        blk = start + '\nvar ' + var + ' = ' + raw + ';\n' + end + '\n'
        if start in wk:
            wk = re.sub(re.escape(start) + r'.*?' + re.escape(end) + r'\n',
                        lambda m: blk, wk, count=1, flags=re.S)
            print('替换已有 %s 块' % tag)
        else:
            anchor = '// === HISTORY_GD_DEFAULT_END ==='
            i = wk.find(anchor)
            assert i > 0, '找不到锚点 ' + anchor
            pos = wk.index('\n', i) + 1
            wk = wk[:pos] + blk + wk[pos:]
            print('插入 %s 块' % tag)

    # ---- 2) trial 常量 ----
    if 'TRIAL_PHYSICS_EXAM' not in wk:
        anchor = 'var TRIAL_HISTORY_GD = 1;'
        i = wk.find(anchor)
        assert i > 0, '找不到 trial 锚点'
        pos = wk.index('\n', i) + 1
        wk = wk[:pos] + TRIAL_LINES + wk[pos:]
        print('插入 trial 常量')
    else:
        print('trial 常量已存在')

    # ---- 3) 路由（花括号配平，插在 history-gd 整块之后）----
    if 'path === "/api/physics"' not in wk:
        anchor = 'if (path === "/api/history-gd" && method === "GET") {'
        i = wk.find(anchor)
        assert i > 0, '找不到路由锚点'
        pos = block_end(wk, wk.index('{', i))
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
    for t in ('TRIAL_PHYSICS', 'TRIAL_PHYSICS_EXAM', 'TRIAL_PHYSICS_LINK'):
        n = len(re.findall(r'^var ' + t + r'\s*=', chk, flags=re.M))
        assert n == 1, '%s 未定义或重复（n=%d）' % (t, n)
    for r in ('/api/physics"', '/api/physics-exam"', '/api/physics-link"'):
        assert chk.count('path === "%s' % r) == 1, r + ' 路由数量异常'
    # 路由位置：必须在 history-gd 之后
    assert chk.index('path === "/api/physics"') > chk.index('path === "/api/history-gd"'), '路由位置错误'
    defined = set(re.findall(r'var (TRIAL_[A-Z_]+)', chk))
    used = set(re.findall(r'(?<![\w.])TRIAL_[A-Z_]+', chk))
    miss = sorted(u for u in used if u not in defined)
    assert not miss, '未定义却被引用的 TRIAL_ 常量: %r' % miss
    print('产物校验通过（位置正确 · 无悬空引用）')
    print('worker.js 新大小', os.path.getsize(WORKER))


if __name__ == '__main__':
    main()
    print('DONE')
