# -*- coding: utf-8 -*-
"""把 biology 四份数据注入 worker.js（常量块 + trial 常量 + 4 条路由）。幂等。

⚠️ 与 inject_physics.py 同款规则（见 skill szg-new-module-mirror 2.8 节）：
  1) 路由插在「专业英语单词记忆」整块注释之前（顶层，不落进任何 if 作用域）。
  2) 校验常量唯一性用行首正则（^var X\\s*=），避免 TRIAL_BIOLOGY 被 TRIAL_BIOLOGY_EXAM 干扰。
  3) re.sub 替换串走「函数返回」，避免 JSON 的 \\n 被当换行。
用法：python tools/inject_biology.py
"""
import io, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKER = r'E:/szgaokao.cn/worker/src/worker.js'
DATA = os.path.join(ROOT, 'data')

BOOK = json.load(io.open(os.path.join(DATA, 'biology_book.json'), encoding='utf-8'))
EXAM = json.load(io.open(os.path.join(DATA, 'biology_exam.json'), encoding='utf-8'))
KNOWLEDGE = json.load(io.open(os.path.join(DATA, 'biology_knowledge.json'), encoding='utf-8'))
LINK = json.load(io.open(os.path.join(DATA, 'biology_link.json'), encoding='utf-8'))

BLOCKS = [
    ('BIOLOGY_BOOK_DEFAULT', 'biology_book_default', BOOK),
    ('BIOLOGY_EXAM_DEFAULT', 'biology_exam_default', EXAM),
    ('BIOLOGY_KNOWLEDGE_DEFAULT', 'biology_knowledge_default', KNOWLEDGE),
    ('BIOLOGY_LINK_DEFAULT', 'biology_link_default', LINK),
]

TRIAL_LINES = (
    'var TRIAL_BIOLOGY = 1;          // 生物：trial 仅开放每板块首个分组\n'
    'var TRIAL_BIOLOGY_EXAM = 5;     // 生物题库：trial 仅返回前 5 题\n'
    'var TRIAL_BIOLOGY_LINK = "bl1"; // 生物衔接包：trial 仅开放第 1 单元\n'
)

ROUTES = r'''
    // —— 初高中生物：课本同步 / 知识点梳理 / 题库 / 专题突破 ——
    if (path === "/api/biology-book" && method === "GET") {
      const user = await uidOf(request, env);
      if (!user) return err(401, "未登录或登录已失效，请重新登录");
      const dev = getDev({}, request);
      if (!parseDevices(user).includes(dev)) return err(403, "当前设备未授权，请重新登录");
      const authed = modAuthed(user, "biology") || modAuthed(user, "primary");
      const bookId = q.get("book"), chapterId = q.get("chapter"), sectionId = q.get("section");
      const books = JSON.parse(JSON.stringify(biology_book_default.books));
      if (sectionId) {
        for (const b of books) for (const c of b.chapters) { const s = c.sections.find((x) => x.id === sectionId); if (s) return ok({ section: s, trial: !authed }); }
        return err(404, "节不存在");
      }
      if (chapterId) {
        for (const b of books) { const c = b.chapters.find((x) => x.id === chapterId); if (c) return ok({ chapter: c, trial: !authed }); }
        return err(404, "章不存在");
      }
      if (bookId) {
        const b = books.find((x) => x.id === bookId);
        if (!b) return err(404, "册不存在");
        if (!authed && b.chapters.length) b.chapters = b.chapters.slice(0, 1);
        return ok({ book: b, trial: !authed });
      }
      if (!authed) books.forEach((b) => { if (b.chapters.length) b.chapters = b.chapters.slice(0, 1); });
      const list = books.map((b) => ({ id: b.id, name: b.name, term: b.term, chapterCount: b.chapters.length, sectionCount: b.chapters.reduce((n, c) => n + c.sections.length, 0) }));
      return ok({ books: list, edition: biology_book_default.edition, trial: !authed });
    }
    if (path === "/api/biology-exam" && method === "GET") {
      const user = await uidOf(request, env);
      if (!user) return err(401, "未登录或登录已失效，请重新登录");
      const dev = getDev({}, request);
      if (!parseDevices(user).includes(dev)) return err(403, "当前设备未授权，请重新登录");
      const authed = modAuthed(user, "biology") || modAuthed(user, "primary");
      const list = biology_exam_default.questions;
      const qids = q.get("ids");
      if (qids) { const map = {}; list.forEach((x) => { map[x.id] = x; }); const picked = qids.split(",").filter((id) => map[id]).map((id) => map[id]); return ok({ questions: picked }); }
      const g = q.get("grade"), t = q.get("topic"), ty = q.get("type"), d = q.get("difficulty");
      let flt = list;
      if (g) flt = flt.filter((x) => String(x.grade) === g);
      if (t) flt = flt.filter((x) => String(x.topic) === t);
      if (ty) flt = flt.filter((x) => String(x.type) === ty);
      if (d) flt = flt.filter((x) => String(x.difficulty) === d);
      if (!authed) flt = flt.slice(0, TRIAL_BIOLOGY_EXAM);
      return ok({ questions: flt, topics: biology_exam_default.topics, trial: !authed, total: list.length });
    }
    if (path === "/api/biology-knowledge" && method === "GET") {
      const user = await uidOf(request, env);
      if (!user) return err(401, "未登录或登录已失效，请重新登录");
      const dev = getDev({}, request);
      if (!parseDevices(user).includes(dev)) return err(403, "当前设备未授权，请重新登录");
      const authed = modAuthed(user, "biology") || modAuthed(user, "primary");
      const bookId = q.get("book"), chapterId = q.get("chapter"), sectionId = q.get("section");
      const books = JSON.parse(JSON.stringify(biology_knowledge_default.books));
      if (sectionId) {
        for (const b of books) for (const c of b.chapters) { const s = c.sections.find((x) => x.id === sectionId); if (s) return ok({ section: s, trial: !authed }); }
        return err(404, "节不存在");
      }
      if (chapterId) {
        for (const b of books) { const c = b.chapters.find((x) => x.id === chapterId); if (c) return ok({ chapter: c, trial: !authed }); }
        return err(404, "章不存在");
      }
      if (bookId) {
        const b = books.find((x) => x.id === bookId);
        if (!b) return err(404, "册不存在");
        if (!authed && b.chapters.length) b.chapters = b.chapters.slice(0, 1);
        return ok({ book: b, trial: !authed });
      }
      if (!authed) books.forEach((b) => { if (b.chapters.length) b.chapters = b.chapters.slice(0, 1); });
      const list = books.map((b) => ({ id: b.id, name: b.name, term: b.term, chapterCount: b.chapters.length, sectionCount: b.chapters.reduce((n, c) => n + c.sections.length, 0) }));
      return ok({ books: list, edition: biology_knowledge_default.edition, trial: !authed });
    }
    if (path === "/api/biology-link" && method === "GET") {
      const user = await uidOf(request, env);
      if (!user) return err(401, "未登录或登录已失效，请重新登录");
      const dev = getDev({}, request);
      if (!parseDevices(user).includes(dev)) return err(403, "当前设备未授权，请重新登录");
      const authed = modAuthed(user, "biology") || modAuthed(user, "primary");
      const list = biology_link_default.units;
      const uid2 = q.get("unit");
      if (uid2) { const un = list.find((x) => x.id === uid2); if (!un) return err(404, "单元不存在"); if (!authed && uid2 !== TRIAL_BIOLOGY_LINK) return err(403, "体验模式仅可学习第 1 单元，输入授权码或联系管理员解锁全部单元"); return ok(un); }
      return ok({ units: authed ? list : list.filter((x) => x.id === TRIAL_BIOLOGY_LINK), trial: !authed });
    }
'''


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
    if 'TRIAL_BIOLOGY_EXAM' not in wk:
        anchor = 'var TRIAL_HISTORY_GD = 1;'
        i = wk.find(anchor)
        assert i > 0, '找不到 trial 锚点'
        pos = wk.index('\n', i) + 1
        wk = wk[:pos] + TRIAL_LINES + wk[pos:]
        print('插入 trial 常量')
    else:
        print('trial 常量已存在')

    # ---- 3) 路由（插在「专业英语单词记忆」整块注释之前，顶层）----
    if 'path === "/api/biology-book"' not in wk:
        anchor = '// —— 专业英语单词记忆：词书列表 / 取词 / 评分 / 队列 / 统计 ——'
        i = wk.find(anchor)
        assert i > 0, '找不到路由锚点'
        wk = wk[:i] + ROUTES + '\n' + wk[i:]
        print('插入 4 条路由')
    else:
        print('路由已存在')

    io.open(WORKER, 'w', encoding='utf-8').write(wk)

    # ---- 4) 产物校验 ----
    chk = io.open(WORKER, encoding='utf-8').read()
    for tag, var, _ in BLOCKS:
        assert chk.count('// === %s_START ===' % tag) == 1, tag + ' 块数量异常'
        assert ('var ' + var + ' =') in chk, tag + ' 变量未定义'
    for t in ('TRIAL_BIOLOGY', 'TRIAL_BIOLOGY_EXAM', 'TRIAL_BIOLOGY_LINK'):
        n = len(re.findall(r'^var ' + t + r'\s*=', chk, flags=re.M))
        assert n == 1, '%s 未定义或重复（n=%d）' % (t, n)
    for r in ('/api/biology-book"', '/api/biology-exam"', '/api/biology-knowledge"', '/api/biology-link"'):
        assert chk.count('path === "%s' % r) == 1, r + ' 路由数量异常'
    defined = set(re.findall(r'var (TRIAL_[A-Z_]+)', chk))
    used = set(re.findall(r'(?<![\w.])TRIAL_[A-Z_]+', chk))
    miss = sorted(u for u in used if u not in defined)
    assert not miss, '未定义却被引用的 TRIAL_ 常量: %r' % miss
    print('产物校验通过（常量/路由唯一 · 无悬空引用）')
    print('worker.js 新大小', os.path.getsize(WORKER))


if __name__ == '__main__':
    main()
    print('DONE')
