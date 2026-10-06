# -*- coding: utf-8 -*-
"""把 history_gd.json 注入 worker.js（常量块 + trial 常量 + /api/history-gd 路由）。幂等。

⚠️ 关键（已踩过的坑，见 skill szg-new-module-mirror 2.8 节）：
  路由必须插在锚点「整块结束之后」。若只匹配到锚点行的 `{` 之后，新路由会落进
  锚点 if 的作用域内部 —— 语法合法、node --check 通过，但运行时永不可达（线上全 404）。
  故此处用花括号配平定位整块末尾。
⚠️ 校验常量唯一性必须用行首正则（形如 ^var X\\s*=），不能用子串计数（前缀会被算进去）。
用法：python tools/inject_history_gd.py
"""
import io, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKER = r'E:/szgaokao.cn/worker/src/worker.js'
GD_JSON = os.path.join(ROOT, 'data', 'history_gd.json')

GD = json.load(io.open(GD_JSON, encoding='utf-8'))

TAG = 'HISTORY_GD_DEFAULT'
ROUTE_PATH = '/api/history-gd'
TRIAL = 'TRIAL_HISTORY_GD'

ROUTES = r'''
    if (path === "/api/history-gd" && method === "GET") {
      const user = await uidOf(request, env);
      if (!user) return err(401, "未登录或登录已失效，请重新登录");
      const dev = getDev({}, request);
      if (!parseDevices(user).includes(dev)) return err(403, "当前设备未授权，请重新登录");
      const authed = modAuthed(user, "history") || modAuthed(user, "primary");
      const pid = q.get("paper");
      const all = history_gd_default.papers;
      if (pid) {
        const p = all.find((x) => x.id === pid);
        if (!p) return err(404, "卷不存在");
        if (!authed && all.findIndex((x) => x.id === pid) >= TRIAL_HISTORY_GD)
          return err(403, "体验模式仅可使用第 1 套卷，输入授权码或联系管理员解锁全部卷组");
        return ok(p);
      }
      const list = all.map((p) => ({
        id: p.id, year: p.year, title: p.title, kind: p.kind, notice: p.notice,
        examType: p.examType, totalScore: p.totalScore, durationMin: p.durationMin, theme: p.theme,
        questionCount: p.modules.reduce((n, m) => n + m.parts.reduce((k, x) => k + x.questions.length, 0), 0),
      }));
      return ok({
        region: history_gd_default.region, examType: history_gd_default.examType,
        kind: history_gd_default.kind, notice: history_gd_default.notice,
        structure: history_gd_default.structure,
        papers: authed ? list : list.slice(0, TRIAL_HISTORY_GD), trial: !authed,
      });
    }
'''


def block_end(text, start_idx):
    """从 start_idx 处的 '{' 开始做花括号配平，返回该块结束后的位置。"""
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
    start = '// === %s_START ===' % TAG
    end = '// === %s_END ===' % TAG
    raw = json.dumps(GD, ensure_ascii=False, separators=(',', ':'))
    assert raw.count('\n') == 0, 'compact 不应含换行'
    blk = start + '\nvar history_gd_default = ' + raw + ';\n' + end + '\n'
    if start in wk:
        wk = re.sub(re.escape(start) + r'.*?' + re.escape(end) + r'\n',
                    lambda m: blk, wk, count=1, flags=re.S)
        print('替换已有 %s 块' % TAG)
    else:
        anchor = '// === HISTORY_LINK_DEFAULT_END ==='
        i = wk.find(anchor)
        assert i > 0, '找不到锚点 ' + anchor
        pos = wk.index('\n', i) + 1
        wk = wk[:pos] + blk + wk[pos:]
        print('插入 %s 块' % TAG)

    # ---- 2) trial 常量（行首正则，避开尾注释坑）----
    if not re.search(r'^var ' + TRIAL + r'\s*=', wk, flags=re.M):
        anchor = 'var TRIAL_HISTORY_LINK = "hl1";'
        i = wk.find(anchor)
        assert i > 0, '找不到 trial 锚点'
        pos = wk.index('\n', i) + 1
        wk = wk[:pos] + 'var %s = 1;   // 广东高考卷：trial 仅开放第 1 套\n' % TRIAL + wk[pos:]
        print('插入 %s' % TRIAL)
    else:
        print('%s 已存在' % TRIAL)

    # ---- 3) 路由（花括号配平，插在 history-link 整块之后）----
    if ('path === "%s"' % ROUTE_PATH) not in wk:
        anchor = 'if (path === "/api/history-link" && method === "GET") {'
        i = wk.find(anchor)
        assert i > 0, '找不到路由锚点'
        pos = block_end(wk, wk.index('{', i))
        while pos < len(wk) and wk[pos] == '\n':
            pos += 1
        wk = wk[:pos] + ROUTES + '\n' + wk[pos:]
        print('插入 %s 路由' % ROUTE_PATH)
    else:
        print('路由已存在')

    io.open(WORKER, 'w', encoding='utf-8').write(wk)

    # ---- 4) 产物校验 ----
    chk = io.open(WORKER, encoding='utf-8').read()
    assert chk.count('// === %s_START ===' % TAG) == 1, TAG + ' 块数量异常'
    assert ('var history_gd_default =') in chk, TAG + ' 变量未定义'
    n = len(re.findall(r'^var ' + TRIAL + r'\s*=', chk, flags=re.M))
    assert n == 1, '%s 未定义或重复（n=%d）' % (TRIAL, n)
    assert chk.count('path === "%s"' % ROUTE_PATH) == 1, ROUTE_PATH + ' 路由数量异常'
    # 路由必须在 history-link 之后
    assert chk.index('path === "%s"' % ROUTE_PATH) > chk.index('path === "/api/history-link"'), \
        '路由位置错误：必须在 /api/history-link 之后'
    # 无悬空 TRIAL_ 引用
    defined = set(re.findall(r'var (TRIAL_[A-Z_]+)', chk))
    used = set(re.findall(r'(?<![\w.])TRIAL_[A-Z_]+', chk))
    miss = sorted(u for u in used if u not in defined)
    assert not miss, '未定义却被引用的 TRIAL_ 常量: %r' % miss
    print('产物校验通过（位置正确 · 无悬空引用）')
    print('worker.js 新大小', os.path.getsize(WORKER))


if __name__ == '__main__':
    main()
    print('DONE')
