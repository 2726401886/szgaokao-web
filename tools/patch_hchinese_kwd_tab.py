# -*- coding: utf-8 -*-
"""hchinese.html 增加「📖 课外阅读拓展」板块（4 专题 × 20 题，含答案）。
复用既有 gd-* 紫色样式与渲染范式；数据来自 /api/hchinese-kwd。
改动点（全部断言命中）：
  1) CSS 追加 .gd-box（结构字符串盒）
  2) SECTIONS 新增 { k:'kwd' }
  3) selectSection 走整幅渲染分支 → renderKwdPage()
  4) renderSide 跳过 kwd
  5) 插入 KWD 渲染器（单选判分 + 主观参考答案）
用法：python tools/patch_hchinese_kwd_tab.py
"""
import io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, 'public', 'hchinese.html')

s = io.open(HTML, encoding='utf-8').read()
reps = []


def add(old, new, n=1):
    reps.append((old, new, n))


# ---------- 1) CSS：.gd-box ----------
add("  .gd-st-d { font-size:11.5px; color:#999; margin-top:5px; line-height:1.6; }",
    "  .gd-st-d { font-size:11.5px; color:#999; margin-top:5px; line-height:1.6; }\n"
    "  .gd-box { background:#fff; border:1.5px solid #f0e6f9; border-radius:12px; padding:11px 14px; font-size:13px; line-height:1.8; color:#444; }")

# ---------- 2) SECTIONS ----------
add("    { k: 'gdpaper', t: '📄 广东高考卷', modes: [] },",
    "    { k: 'gdpaper', t: '📄 广东高考卷', modes: [] },\n"
    "    { k: 'kwd', t: '📖 课外阅读拓展', modes: [] },")

# ---------- 3) selectSection 分支 ----------
add("    if (k === 'exam' || k === 'link' || k === 'textbook' || k === 'gdpaper') {",
    "    if (k === 'exam' || k === 'link' || k === 'textbook' || k === 'gdpaper' || k === 'kwd') {")
add("      else if (k === 'gdpaper') renderGdPaperPage();\n      else renderLinkPage();",
    "      else if (k === 'gdpaper') renderGdPaperPage();\n      else if (k === 'kwd') renderKwdPage();\n      else renderLinkPage();")

# ---------- 4) renderSide 跳过 ----------
add("    if (section === 'exam' || section === 'link' || section === 'textbook' || section === 'gdpaper') return;",
    "    if (section === 'exam' || section === 'link' || section === 'textbook' || section === 'gdpaper' || section === 'kwd') return;")

# ---------- 5) 渲染器 ----------
ANCHOR = "  // ================== 板块：题库组卷 =================="
KWD_JS = r'''  // ================== 板块：课外阅读拓展（4 专题） ==================
  window.__KWD_CACHE = window.__KWD_CACHE || {};
  function renderKwdPage() {
    $('#mainArea').innerHTML = '<div class="empty">加载中…</div>';
    api('/api/hchinese-kwd').then(function (r) {
      if (r.s !== 200) { $('#mainArea').innerHTML = '<div class="err-msg">' + (r.j.error || '加载失败，请登录后重试') + '</div>'; return; }
      const d = r.j;
      const cards = (d.units || []).map(function (u) {
        return '<div class="gd-card" data-u="' + esc(u.id) + '">' +
          '<div class="gd-card-y" style="font-size:15px;">' + esc(u.no) + '</div>' +
          '<div class="gd-card-b"><div class="gd-card-t">' + esc(u.title) + '</div>' +
          '<div class="gd-card-m">' + esc(u.desc || '') + ' · 共 ' + u.questionCount + ' 题</div></div>' +
          '<div class="gd-card-go">进入专题 →</div></div>';
      }).join('');
      $('#mainArea').innerHTML =
        '<div class="gd-wrap">' +
          '<div class="gd-hd">📖 高中语文 · 课外阅读拓展<span class="gd-ed">' + esc(d.examType || '') + '</span></div>' +
          '<div class="gd-warn">⚠️ <b>说明</b>：' + esc(d.notice) + '</div>' +
          (d.trial ? '<div class="gd-tip">🎁 体验模式：仅开放第 1 专题。输入授权码或联系管理员（微信 13538237315）解锁全部 4 专题。</div>' : '') +
          '<div class="gd-st-h">专题结构</div><div class="gd-box">' + esc(d.structure || '') + '</div>' +
          '<div class="gd-st-h">专题列表</div>' +
          '<div class="gd-cards">' + (cards || '<div class="empty">暂无专题</div>') + '</div>' +
        '</div>';
      document.querySelectorAll('.gd-card[data-u]').forEach(el => el.addEventListener('click', () => openKwdUnit(el.dataset.u)));
    });
  }

  function openKwdUnit(unitId) {
    $('#mainArea').innerHTML = '<div class="empty">加载中…</div>';
    api('/api/hchinese-kwd?unit=' + encodeURIComponent(unitId)).then(function (r) {
      if (r.s !== 200) { $('#mainArea').innerHTML = '<div class="err-msg">专题加载失败</div>'; return; }
      const u = r.j;
      window.__KWD_CACHE[u.id] = u;
      const secs = u.sections.map(function (sec) {
        const qs = sec.questions.map(function (q) {
          if (q.type === 'choice') {
            return '<div class="gd-q"><div class="gd-q-stem">' + q.no + '．' + esc(q.stem) + '</div>' +
              '<div class="gd-q-opts" data-u="' + esc(u.id) + '" data-no="' + q.no + '">' +
              q.options.map(function (o, oi) { return '<div class="gd-q-o" data-oi="' + oi + '">' + String.fromCharCode(65 + oi) + '．' + esc(o) + '</div>'; }).join('') +
              '</div><div class="gd-q-res" data-no="' + q.no + '"></div><div class="gd-q-ana" data-no="' + q.no + '">' + esc(q.analysis || '') + '</div></div>';
          }
          return '<div class="gd-q"><div class="gd-q-stem">' + q.no + '．' + esc(q.stem) + '</div>' +
            '<div class="gd-q-sub">参考答案：' + esc(q.answer) + '</div>' +
            (q.analysis ? '<div class="gd-q-ana" data-no="' + q.no + '">' + esc(q.analysis) + '</div>' : '') + '</div>';
        }).join('');
        return '<div class="gd-part"><div class="gd-part-h">' + esc(sec.name) + (sec.score ? '<span class="gd-part-sc">' + sec.score + '分</span>' : '') + '</div>' + qs + '</div>';
      }).join('');
      $('#mainArea').innerHTML =
        '<div class="gd-wrap">' +
          '<div class="gd-hd"><button class="gd-back" id="kwdBack">← 返回专题列表</button> ' + esc(u.no) + ' ' + esc(u.title) + '</div>' +
          '<div class="gd-warn">⚠️ ' + esc(u.desc || '') + '</div>' +
          '<div class="gd-paper">' + secs + '</div>' +
        '</div>';
      $('#kwdBack').addEventListener('click', renderKwdPage);
      document.querySelectorAll('.gd-q-opts').forEach(function (box) {
        var uId = box.dataset.u, no = box.dataset.no;
        box.querySelectorAll('.gd-q-o').forEach(function (o) {
          o.addEventListener('click', function () {
            if (box.dataset.locked) return;
            box.dataset.locked = '1';
            var ans = null;
            var un = window.__KWD_CACHE && window.__KWD_CACHE[uId];
            if (un) un.sections.forEach(function (sec) { sec.questions.forEach(function (q) { if (String(q.no) === String(no) && q.type === 'choice') ans = q.answer; }); });
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
      document.querySelectorAll('.gd-q-ana').forEach(function (a) { a.style.display = 'block'; });
    });
  }

'''
add(ANCHOR, KWD_JS + ANCHOR)

# ---------- 执行 + 断言 ----------
for i, (old, new, n) in enumerate(reps):
    cnt = s.count(old)
    assert cnt == n, "替换未命中或多次命中(#%d): 期望%d次, 实际%d次\nOLD=%r" % (i, n, cnt, old[:70])
    s = s.replace(old, new)

# ---------- 收尾校验 ----------
assert 'renderKwdPage' in s, 'KWD 渲染器未插入'
assert "/api/hchinese-kwd" in s, 'KWD API 未调用'
assert ".gd-box" in s, '.gd-box CSS 未插入'
assert "k: 'kwd'" in s, 'SECTIONS 未加入 kwd'

io.open(HTML, 'w', encoding='utf-8').write(s)
print("patched", HTML, len(s), "bytes")
print("DONE")
