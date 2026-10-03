# -*- coding: utf-8 -*-
"""在 public/hchinese.html 新增「📄 广东高考卷」Tab（5 套结构仿真卷）。
改动：
  - SECTIONS 插入 gdpaper 板块
  - selectSection 支持 'gdpaper'（独立整幅渲染）
  - renderGdPaperPage（卷列表）/ renderGdPaper（整卷渲染，含分节分值与试卷头）
  - 键盘翻页排除 gdpaper
所有替换均断言命中次数。
"""
import io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'public', 'hchinese.html')
DST = os.path.join(ROOT, 'public', 'hchinese.html')

s = io.open(SRC, encoding='utf-8').read()
reps = []
def add(old, new, n=1):
    reps.append((old, new, n))

# 1) SECTIONS 插入
add("    { k: 'textbook', t: '📖 课本同步', modes: [] },",
    "    { k: 'textbook', t: '📖 课本同步', modes: [] },\n    { k: 'gdpaper', t: '📄 广东高考卷', modes: [] },")

# 2) selectSection 分发
add("""    if (k === 'exam' || k === 'link' || k === 'textbook') {
      // 独立板块：隐藏左侧分组栏，整幅渲染
      $('#sidePane').style.display = 'none';
      $('#mainArea').style.flex = '1 1 100%';
      if (k === 'exam') renderExamPage();
      else if (k === 'textbook') renderTextbookPage();
      else renderLinkPage();
      return;
    }""",
    """    if (k === 'exam' || k === 'link' || k === 'textbook' || k === 'gdpaper') {
      // 独立板块：隐藏左侧分组栏，整幅渲染
      $('#sidePane').style.display = 'none';
      $('#mainArea').style.flex = '1 1 100%';
      if (k === 'exam') renderExamPage();
      else if (k === 'textbook') renderTextbookPage();
      else if (k === 'gdpaper') renderGdPaperPage();
      else renderLinkPage();
      return;
    }""")

# 3) renderSide / navMode 排除
add("    if (section === 'exam' || section === 'link' || section === 'textbook') return;\n    const groups = curGroups();",
    "    if (section === 'exam' || section === 'link' || section === 'textbook' || section === 'gdpaper') return;\n    const groups = curGroups();")
add("    const navMode = (section !== 'exam' && section !== 'link' && section !== 'textbook' && mode === 'read');",
    "    const navMode = (section !== 'exam' && section !== 'link' && section !== 'textbook' && section !== 'gdpaper' && mode === 'read');")

# 4) 渲染器 + CSS
ANCHOR = "  // ================== 板块：课本同步（人教版五册） =================="
GD = r'''  // ================== 板块：广东高考卷（结构仿真卷） ==================
  function renderGdPaperPage() {
    $('#mainArea').innerHTML = '<div class="empty">加载中…</div>';
    api('/api/hchinese-paper').then(function (r) {
      if (r.s !== 200) { $('#mainArea').innerHTML = '<div class="err-msg">' + (r.j.error || '加载失败，请登录后重试') + '</div>'; return; }
      const d = r.j;
      const st = (d.structure || []).map(m =>
        '<div class="gd-st"><b>' + esc(m.name) + '</b><span class="gd-st-sc">' + m.score + '分</span><div class="gd-st-d">' + esc(m.detail || '') + '</div></div>').join('');
      const cards = (d.papers || []).map(p =>
        '<div class="gd-card" data-p="' + esc(p.id) + '">' +
          '<div class="gd-card-y">' + p.year + '</div>' +
          '<div class="gd-card-b">' +
            '<div class="gd-card-t">' + esc(p.title) + '</div>' +
            '<div class="gd-card-m">' + p.totalScore + '分 · ' + p.durationMin + '分钟 · ' + p.questionCount + '题</div>' +
          '</div>' +
          '<div class="gd-card-go">查看整卷 →</div>' +
        '</div>').join('');
      $('#mainArea').innerHTML =
        '<div class="gd-wrap">' +
          '<div class="gd-hd">📄 ' + esc(d.region) + '高考语文 · 结构仿真卷<span class="gd-ed">' + esc(d.examType || '') + '</span></div>' +
          '<div class="gd-warn">⚠️ <b>重要说明</b>：' + esc(d.notice) + '</div>' +
          (d.trial ? '<div class="gd-tip">🎁 体验模式：仅开放第 1 套卷。输入授权码或联系管理员（微信 13538237315）解锁全部 5 套。</div>' : '') +
          '<div class="gd-st-h">试卷结构（满分150分）</div>' +
          '<div class="gd-sts">' + st + '</div>' +
          '<div class="gd-st-h">卷列表</div>' +
          '<div class="gd-cards">' + (cards || '<div class="empty">暂无试卷</div>') + '</div>' +
        '</div>';
      document.querySelectorAll('.gd-card').forEach(el => el.addEventListener('click', () => renderGdPaper(el.dataset.p)));
    });
  }

  function renderGdPaper(paperId) {
    $('#mainArea').innerHTML = '<div class="empty">加载中…</div>';
    api('/api/hchinese-paper?paper=' + encodeURIComponent(paperId)).then(function (r) {
      if (r.s !== 200) { $('#mainArea').innerHTML = '<div class="err-msg">' + (r.j.error || '加载失败') + '</div>'; return; }
      const p = r.j;
      const CNM = ['一', '二', '三', '四'];
      const mods = p.modules.map(function (m, mi) {
        const parts = m.parts.map(function (part) {
          let body = '';
          if (part.text) {
            const t = part.text;
            let txt = '';
            if (t.title) txt += '<div class="gd-t-title">' + esc(t.title) + '</div>';
            if (t.source) txt += '<div class="gd-t-src">出处：' + esc(t.source) + (t.author ? '／' + esc(t.author) : '') + '</div>';
            if (t.lines) txt += '<div class="gd-t-body">' + t.lines.map(esc).join('<br>') + '</div>';
            if (part.text2) {
              const t2 = part.text2;
              txt += '<div class="gd-t-title" style="margin-top:12px;">' + esc(t2.title) + '</div>';
              if (t2.source) txt += '<div class="gd-t-src">出处：' + esc(t2.source) + '</div>';
              if (t2.lines) txt += '<div class="gd-t-body">' + t2.lines.map(esc).join('<br>') + '</div>';
            }
            body += '<div class="gd-passage">' + txt + '</div>';
          }
          // 信息类/文学类的材料放在 questions 之外，用 part.textObj 传入时此处不用
          if (part.ctxText) body += '<div class="gd-passage"><div class="gd-t-title">' + esc(part.ctxText.title) + '</div><div class="gd-t-body">' + esc(part.ctxText.text) + '</div></div>';
          const qs = part.questions.map(function (q) {
            if (q.type === 'choice') {
              return '<div class="gd-q"><div class="gd-q-stem">' + q.no + '．' + esc(q.stem) + '（' + q.score + '分）</div>' +
                '<div class="gd-q-opts" data-p="' + esc(p.id) + '" data-no="' + q.no + '">' +
                q.options.map(function (o, oi) { return '<div class="gd-q-o" data-oi="' + oi + '">' + String.fromCharCode(65 + oi) + '．' + esc(o) + '</div>'; }).join('') +
                '</div><div class="gd-q-res" data-no="' + q.no + '"></div><div class="gd-q-ana" data-no="' + q.no + '">' + esc(q.analysis) + '</div></div>';
            }
            if (q.type === 'write') {
              return '<div class="gd-q"><div class="gd-q-stem">' + q.no + '．' + esc(q.stem).replace(/\n/g, '<br>') + '（' + q.score + '分）</div>' +
                '<div class="gd-write-line"></div></div>';
            }
            return '<div class="gd-q"><div class="gd-q-stem">' + q.no + '．' + esc(q.stem) + '（' + q.score + '分）</div>' +
              '<div class="gd-q-sub">参考答案：' + esc(q.answer) + '</div>' +
              '<div class="gd-q-ana" data-no="' + q.no + '">' + esc(q.analysis) + '</div></div>';
          }).join('');
          return '<div class="gd-part"><div class="gd-part-h">' + esc(part.name) + '<span class="gd-part-sc">' + part.score + '分</span>' +
            (part.source ? '<span class="gd-part-src">' + esc(part.source) + '</span>' : '') + '</div>' + body + qs + '</div>';
        }).join('');
        return '<div class="gd-mod"><div class="gd-mod-h">' + CNM[mi] + '、' + esc(m.name) + '<span class="gd-mod-sc">共' + m.score + '分</span></div>' +
          (m.note ? '<div class="gd-mod-note">' + esc(m.note) + '</div>' : '') + parts + '</div>';
      }).join('');

      $('#mainArea').innerHTML =
        '<div class="gd-wrap">' +
          '<div class="gd-hd"><button class="gd-back" id="gdBack">← 返回卷列表</button> ' + esc(p.title) + '<span class="gd-ed">' + esc(p.examType) + '</span></div>' +
          '<div class="gd-warn">⚠️ <b>结构仿真卷</b>：' + esc(p.notice) + '</div>' +
          '<div class="gd-paper">' +
            '<div class="gd-p-hd"><div class="gd-p-name">' + esc(p.title) + '</div>' +
            '<div class="gd-p-meta">考试时间：' + p.durationMin + '分钟　满分：' + p.totalScore + '分</div>' +
            '<div class="gd-p-meta">学校：____________　班级：____________　姓名：____________　学号：____________</div></div>' +
            mods +
          '</div>' +
        '</div>';
      $('#gdBack').addEventListener('click', renderGdPaperPage);
      // 选择题判分
      document.querySelectorAll('.gd-q-opts').forEach(function (box) {
        var pid = box.dataset.p, no = box.dataset.no;
        box.querySelectorAll('.gd-q-o').forEach(function (o) {
          o.addEventListener('click', function () {
            if (box.dataset.locked) return;
            box.dataset.locked = '1';
            // 从 paper 数据找答案
            var ans = null;
            var pap = window.__GD_CACHE && window.__GD_CACHE[pid];
            if (pap) {
              pap.modules.forEach(function (m) {
                m.parts.forEach(function (pt) {
                  pt.questions.forEach(function (q) { if (String(q.no) === String(no) && q.type === 'choice') ans = q.answer; });
                });
              });
            }
            var oi = Number(o.dataset.oi);
            box.querySelectorAll('.gd-q-o').forEach(function (x) {
              if (ans !== null && Number(x.dataset.oi) === ans) x.classList.add('right');
              else if (x === o) x.classList.add('wrong');
            });
            var res = document.querySelector('.gd-q-res[data-no="' + no + '"]');
            if (res) {
              res.textContent = (ans !== null && oi === ans) ? '✅ 正确！' : (ans !== null ? '❌ 正确答案：' + String.fromCharCode(65 + ans) : '');
              res.className = 'gd-q-res ' + (ans !== null && oi === ans ? 'ok' : 'bad');
            }
            var ana = document.querySelector('.gd-q-ana[data-no="' + no + '"]');
            if (ana) ana.style.display = 'block';
          });
        });
      });
      // 主观题答案默认展开
      document.querySelectorAll('.gd-q-ana').forEach(function (a) { a.style.display = 'block'; });
    });
  }
'''
add(ANCHOR, GD + ANCHOR)

# CSS
CSS_ANCHOR = "  /* —— 课本同步 —— */"
GD_CSS = """  /* —— 广东高考卷 —— */
  .gd-wrap { max-width:1000px; }
  .gd-hd { font-size:18px; font-weight:800; margin-bottom:10px; display:flex; align-items:center; gap:10px; flex-wrap:wrap; }
  .gd-ed { font-size:12px; font-weight:500; color:#8e44ad; background:#f5eefa; padding:3px 10px; border-radius:12px; }
  .gd-back { border:none; background:#f5eefa; color:#8e44ad; font-size:13px; font-weight:700; padding:6px 12px; border-radius:14px; cursor:pointer; }
  .gd-warn { font-size:12.5px; color:#7a5c00; background:#fffbe8; border:1px solid #f3e6b8; border-radius:12px; padding:10px 14px; margin-bottom:12px; line-height:1.8; }
  .gd-tip { font-size:12.5px; color:#1a56db; background:#eef2ff; border:1px solid #c9d6ff; border-radius:12px; padding:10px 14px; margin-bottom:12px; }
  .gd-st-h { font-size:14px; font-weight:800; margin:14px 0 8px; }
  .gd-sts { display:flex; gap:10px; flex-wrap:wrap; }
  .gd-st { background:#fff; border:1.5px solid #f0e6f9; border-radius:12px; padding:11px 14px; flex:1 1 210px; }
  .gd-st b { font-size:14px; }
  .gd-st-sc { font-size:12px; font-weight:700; color:#8e44ad; margin-left:8px; }
  .gd-st-d { font-size:11.5px; color:#999; margin-top:5px; line-height:1.6; }
  .gd-cards { display:flex; gap:12px; flex-wrap:wrap; }
  .gd-card { flex:1 1 290px; background:#fff; border:1.5px solid #f0e6f9; border-radius:14px; padding:14px; cursor:pointer; display:flex; gap:12px; align-items:center; }
  .gd-card:hover { border-color:#8e44ad; box-shadow:0 6px 20px rgba(142,68,173,.12); }
  .gd-card-y { font-size:20px; font-weight:800; color:#8e44ad; background:#f5eefa; border-radius:12px; padding:10px 12px; }
  .gd-card-b { flex:1; }
  .gd-card-t { font-size:14.5px; font-weight:700; }
  .gd-card-m { font-size:12px; color:#999; margin-top:4px; }
  .gd-card-go { font-size:12px; color:#8e44ad; font-weight:700; white-space:nowrap; }
  .gd-paper { background:#fff; border-radius:16px; padding:20px 18px; box-shadow:0 4px 16px rgba(0,0,0,.05); }
  .gd-p-hd { text-align:center; border-bottom:2px solid #8e44ad; padding-bottom:12px; margin-bottom:16px; }
  .gd-p-name { font-size:19px; font-weight:800; }
  .gd-p-meta { font-size:12.5px; color:#666; margin-top:6px; }
  .gd-mod { margin-bottom:20px; }
  .gd-mod-h { font-size:15.5px; font-weight:800; margin-bottom:6px; }
  .gd-mod-sc { font-size:12px; font-weight:600; color:#8e44ad; background:#f5eefa; padding:2px 9px; border-radius:10px; margin-left:8px; }
  .gd-mod-note { font-size:11.5px; color:#999; margin-bottom:8px; }
  .gd-part { margin:12px 0 12px 12px; }
  .gd-part-h { font-size:13.5px; font-weight:700; color:#444; margin-bottom:6px; }
  .gd-part-sc { font-size:11.5px; color:#8e44ad; margin-left:8px; }
  .gd-part-src { font-size:11px; color:#aaa; margin-left:8px; }
  .gd-passage { background:#faf8fc; border-left:3px solid #c9a8dc; border-radius:0 10px 10px 0; padding:11px 14px; margin-bottom:9px; }
  .gd-t-title { font-size:14px; font-weight:700; }
  .gd-t-src { font-size:11.5px; color:#999; margin-top:3px; }
  .gd-t-body { font-size:13.5px; line-height:2; margin-top:6px; color:#333; }
  .gd-q { margin:10px 0; }
  .gd-q-stem { font-size:13.5px; font-weight:700; line-height:1.9; }
  .gd-q-o { font-size:13px; margin:5px 0 5px 14px; padding:6px 10px; border-radius:8px; cursor:pointer; }
  .gd-q-o:hover { background:#f5eefa; }
  .gd-q-o.right { background:#e8f8ee; color:#1a6b37; font-weight:700; }
  .gd-q-o.wrong { background:#fdecec; color:#a12626; }
  .gd-q-res { font-size:12.5px; font-weight:700; margin-left:14px; }
  .gd-q-res.ok { color:#2a8; }
  .gd-q-res.bad { color:#e23; }
  .gd-q-sub { font-size:12.5px; color:#666; margin:5px 0 5px 14px; background:#faf8fc; border-radius:8px; padding:6px 10px; }
  .gd-q-ana { display:none; font-size:12px; color:#888; margin:5px 0 5px 14px; background:#faf8fc; border-radius:8px; padding:6px 10px; line-height:1.7; }
  .gd-write-line { border-bottom:1px solid #ddd; min-height:120px; margin-top:8px; }

"""
add(CSS_ANCHOR, GD_CSS + CSS_ANCHOR)

# 缓存整卷数据供判分使用
add("  // ================== 板块：广东高考卷（结构仿真卷） ==================",
    "  // ================== 板块：广东高考卷（结构仿真卷） ==================\n  window.__GD_CACHE = window.__GD_CACHE || {};")

# 载入整卷时缓存
add("      const p = r.j;\n      const CNM = ['一', '二', '三', '四'];",
    "      const p = r.j;\n      window.__GD_CACHE = window.__GD_CACHE || {};\n      window.__GD_CACHE[p.id] = p;\n      const CNM = ['一', '二', '三', '四'];")

for i, (old, new, n) in enumerate(reps):
    cnt = s.count(old)
    if n != 0:
        assert cnt == n, "替换未命中或多次命中(#%d): 期望%d 实际%d\nOLD=%r" % (i, n, cnt, old[:70])
    s = s.replace(old, new, n)

io.open(DST, 'w', encoding='utf-8').write(s)
print("updated", DST, len(s), "bytes")
print("DONE")
