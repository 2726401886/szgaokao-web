// szgaokao-web 后端：零依赖 Node.js
// 功能：用户注册 / 登录 / 授权码激活 / 授权校验 / 题库数据接口
// 防共享三层：① 授权码限次  ② 设备绑定（每账号限定设备数）  ③ 单会话踢人（登录即失效旧令牌）
// 运行：node server.js   （生产改 APP_SECRET / ADMIN_SECRET / PORT / MAX_DEVICES 环境变量）
const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const ROOT = __dirname;
const DATA = path.join(ROOT, 'data');
const PUBLIC = path.join(ROOT, 'public');
const SECRET = process.env.APP_SECRET || 'CHANGE_ME_IN_PROD_szgaokao';
const ADMIN_SECRET = process.env.ADMIN_SECRET || 'admin123';
const PORT = process.env.PORT || 3000;
const MAX_DEVICES = Math.max(1, Number(process.env.MAX_DEVICES || 2)); // 每账号允许绑定的设备数

fs.mkdirSync(DATA, { recursive: true });
let users = load('users.json', []);
let codes = load('codes.json', []);
let study = load('study.json', {}); // 学情云端数据：{ username: { log:{}, progress:{}, updated } }
let settings = load('settings.json', { trialOpen: false }); // 体验授权开关：新用户 7 天免费体验全部模块
const quiz = load('quiz.json', { volumes: [] });
const words = load('words.json', { groups: [] }); // 小学英语单词听读背记
const TRIAL_GROUP = 'g3a'; // 单词体验模式：未授权仅可学习第一个主题
const phonics = load('phonics.json', { levels: [] }); // 小学英语自然拼读专项
const TRIAL_RULE = 'p101'; // 拼读体验模式：未授权仅可学习第一条规则
const scenes = load('primary_scenes.json', { scenes: [] }); // 小学单词场景化（词→句→对话）
const TRIAL_SCENE = 's3a'; // 场景体验模式：未授权仅可学习第一个场景
const plist = load('primary_listening.json', { volumes: [] }); // 小学听说题型库
const TRIAL_LT = 'lt3'; // 听说题库体验模式：未授权仅可练习第 1 卷
const longman = load('longman.json', { books: [] }); // 深圳朗文 1A-6B 同步词
const TRIAL_LW = '1a'; // 朗文体验模式：未授权仅可学习 1A
const pexam = load('primary_exam.json', { volumes: [] }); // 校内期末同步包
const TRIAL_EX = 'ex3a'; // 期末包体验模式：未授权仅可练习第 1 套
const jlink = load('junior_link.json', { units: [] }); // 小升初衔接包
const TRIAL_JL = 'jl1'; // 衔接包体验模式：未授权仅可学习第 1 单元
const gread = load('graded_reading.json', { levels: [] }); // 分级阅读
const TRIAL_RD = 'r1a1'; // 分级阅读体验模式：未授权仅可阅读第 1 篇
const kw = load('ket_words.json', { groups: [] }); // KET 核心词
const TRIAL_KW = 'kw1'; // KET 词体验：仅放行第 1 组
const kx = load('ket_exam.json', { volumes: [] }); // KET 听说模拟
const TRIAL_KX = 'kx1a'; // KET 模拟体验：仅放行第 1 卷
const pw = load('pet_words.json', { groups: [] }); // PET 核心词
const TRIAL_PW = 'pw1'; // PET 词体验：仅放行第 1 组
const px = load('pet_exam.json', { volumes: [] }); // PET 听说模拟
const TRIAL_PX = 'px1a'; // PET 模拟体验：仅放行第 1 卷
const gk = load('gaokao_partb.json', { sets: [] }); // 高考听说 Part B 三问五答
const TRIAL_GK = 'gkb01'; // 高考专区体验模式：未授权仅可练习第 1 套
const TRIAL_VOL = 'v01'; // 中考题库体验模式：未授权仅可练习的试卷
const kidsWords = load('kids_words.json', { groups: [] }); // 幼儿启蒙词汇
const TRIAL_KIDS_W = 'k1'; // 幼儿词体验：仅放行第 1 组
const kidsLt = load('kids_listening.json', { volumes: [] }); // 幼儿听说题库
const TRIAL_KIDS_L = 'kl1'; // 幼儿听说体验：仅放行第 1 卷
const kidsSongs = load('kids_songs.json', { songs: [] }); // 幼儿儿歌磨耳朵
const TRIAL_KIDS_S = 'ks1'; // 儿歌体验：仅放行第 1 首
const kidsTpr = load('kids_tpr.json', { groups: [] }); // 幼儿 TPR 日常指令
const TRIAL_KIDS_T = 'kt1'; // TPR 体验：仅放行第 1 组
const kidsPhonics = load('kids_phonics.json', { letters: [], cvc: [], song: {} }); // 幼儿自然拼读
const TRIAL_KIDS_P = 'kp01'; // 拼读体验：仅放行前 3 个字母（A-C）
const kidsReading = load('kids_reading.json', { books: [] }); // 幼儿迷你绘本
const TRIAL_KIDS_R = 'kr1'; // 绘本体验：仅放行第 1 本
const MODULES = { primary: '小学英语', middle: '中考英语', gk: '高考英语', kids: '幼儿英语', math: '数学' }; // 模块授权白名单
const mathPrimary = load('math_primary.json', { product: '数学', volumes: [] }); // 小学数学（三年级上册）
const TRIAL_MP = 'mp301'; // 数学小学体验：仅放行第 1 单元
const mathMiddle = load('math_middle.json', { product: '数学', volumes: [] }); // 初中数学（七年级上册）
const TRIAL_MM = 'mj101'; // 数学初中体验：仅放行第 1 单元
const mathHigh = load('math_high.json', { product: '数学', volumes: [] }); // 高中数学（必修第一册）
const TRIAL_MH = 'mh101'; // 数学高中体验：仅放行第 1 单元

// —— 启动期数据迁移：兼容旧字段 ——
// 旧授权码只有 usedBy、没有 acts/maxActs → 视为已用（acts=1），避免被误判可复用
codes = codes.map(c => {
  if (c.maxActs == null) c.maxActs = 1;
  if (c.acts == null) c.acts = Array.isArray(c.usedBy) ? c.usedBy.length : (c.usedBy ? 1 : 0);
  if (c.days == null) c.days = c.plan === 'annual' ? 365 : (c.plan === 'semester' ? 180 : null); // 旧年度码迁移为 365 天
  return c;
});
// 旧用户没有 devices / sessionSeq → 补默认值
users = users.map(u => {
  if (!Array.isArray(u.devices)) u.devices = [];
  if (u.sessionSeq == null) u.sessionSeq = 0;
  if (u.modules == null) u.modules = u.authorized ? { primary: 1, middle: 1, gk: 1 } : {}; // 旧授权用户默认全模块
  return u;
});

function load(f, def) { try { return JSON.parse(fs.readFileSync(path.join(DATA, f), 'utf8')); } catch (e) { return def; } }
function save(f, o) { fs.writeFileSync(path.join(DATA, f), JSON.stringify(o, null, 2)); }

function hashPw(pw, salt) {
  const s = salt || crypto.randomBytes(16).toString('hex');
  const h = crypto.scryptSync(pw, s, 64).toString('hex');
  return { salt: s, hash: h };
}
function verifyPw(pw, salt, hash) { return crypto.scryptSync(pw, salt, 64).toString('hex') === hash; }

// 令牌 = HMAC(uid|ts|seq) + base64(uid|ts|seq)   seq 用于单会话踢人
function makeToken(uid, seq) {
  const p = uid + '|' + Date.now() + '|' + seq;
  return crypto.createHmac('sha256', SECRET).update(p).digest('hex') + '.' + Buffer.from(p).toString('base64');
}
function parseToken(t) {
  try {
    const [sig, b64] = t.split('.');
    const p = Buffer.from(b64, 'base64').toString('utf8');
    if (crypto.createHmac('sha256', SECRET).update(p).digest('hex') !== sig) return null;
    const parts = p.split('|');
    return { uid: parts[0], seq: Number(parts[2]) };
  } catch (e) { return null; }
}
// 校验令牌：签名有效 + 单会话（seq 必须等于用户当前 sessionSeq，否则被新登录踢出）
function uidOf(t) {
  const pt = parseToken(t);
  if (!pt) return null;
  const u = users.find(x => x.id === pt.uid);
  if (!u) return null;
  if (Number(u.sessionSeq || 0) !== pt.seq) return null;
  return u;
}
// 模块授权判定：授权有效（未过期）且该模块已解锁
function modAuthed(user, m) {
  return !!user.authorized && (!user.expiry || Number(user.expiry) > Date.now()) && !!((user.modules || {})[m]);
}
// 签发令牌并自增会话序号（单会话：旧令牌立即失效）
function issueToken(user) {
  user.sessionSeq = (Number(user.sessionSeq || 0)) + 1;
  save('users.json', users);
  return makeToken(user.id, user.sessionSeq);
}

// 取设备标识：优先前端指纹(device)，否则用 IP+UA 兜底（保证不崩，但绑定较弱）
function getDev(b, req) {
  const d = (b && typeof b.device === 'string' && b.device) || (req.headers['x-device'] || '');
  if (d) return d;
  const ip = (req.headers['x-forwarded-for'] || req.socket.remoteAddress || '').split(',')[0].trim();
  const ua = req.headers['user-agent'] || '';
  return 'fb-' + crypto.createHash('sha256').update(ip + '|' + ua).digest('hex').slice(0, 16);
}
// 绑定设备：已在列表→通过；未满→新增；已满→拒绝
function bindDevice(user, dev) {
  if (!dev) return true;
  if ((user.devices || []).includes(dev)) return true;
  if ((user.devices || []).length >= MAX_DEVICES) return false;
  user.devices = user.devices || [];
  user.devices.push(dev);
  return true;
}
// 受保护接口：请求设备是否在已绑定列表
function deviceAllowed(user, dev) {
  if (!dev) return false;
  return (user.devices || []).includes(dev);
}

// —— 管理员令牌（与用户令牌前缀隔离：payload 以 admin| 开头）——
function makeAdminToken() {
  const p = 'admin|' + Date.now();
  return crypto.createHmac('sha256', SECRET).update(p).digest('hex') + '.' + Buffer.from(p).toString('base64');
}
function parseAdminToken(t) {
  try {
    const [sig, b64] = t.split('.');
    const p = Buffer.from(b64, 'base64').toString('utf8');
    if (!p.startsWith('admin|')) return false;
    return crypto.createHmac('sha256', SECRET).update(p).digest('hex') === sig;
  } catch (e) { return false; }
}
const isAdmin = (req) => parseAdminToken((req.headers['authorization'] || '').replace(/^Bearer\s+/i, ''));

function send(res, code, obj) { res.writeHead(code, { 'Content-Type': 'application/json; charset=utf-8' }); res.end(JSON.stringify(obj)); }
function body(req) { return new Promise(r => { let d = ''; req.on('data', c => d += c); req.on('end', () => { try { r(JSON.parse(d || '{}')); } catch (e) { r({}); } }); }); }
const ok = (res, o) => send(res, 200, o);
const err = (res, c, m) => send(res, c, { error: m });

const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'application/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8', '.png': 'image/png', '.json': 'application/json; charset=utf-8', '.mp3': 'audio/mpeg' };
function staticFile(res, url) {
  let f = url === '/' ? '/index.html' : url.split('?')[0];
  if (f === '/admin') f = '/admin.html';
  const fp = path.join(PUBLIC, path.normalize(f).replace(/^(\.\.[/\\])+/, ''));
  if (!fp.startsWith(PUBLIC) || !fs.existsSync(fp)) { res.writeHead(404); return res.end('404'); }
  res.writeHead(200, { 'Content-Type': MIME[path.extname(fp)] || 'application/octet-stream' });
  fs.createReadStream(fp).pipe(res);
}

// —— 英语学情适配（与线上 worker.js 等价）：KET 听说模拟 + 中考英语听说道具化 ——
function englishTags(typeStr, bank) {
  const t = (typeStr || '').toLowerCase();
  if (bank === 'quiz') {
    if (t.indexOf('listen') >= 0) return ['英语·听力'];
    if (t === 'speaking') return ['英语·口语'];
    return ['英语·综合'];
  }
  // ket / plist / kids 均为听说类
  if (t.indexOf('speak') >= 0) return ['英语·口语'];
  if (bank === 'ket' && t === 'word') return ['英语·词汇']; // 保留 KET 原行为
  return ['英语·听力'];
}
// 知识点级标签：取题卷的 topic/title（按 · 拆分）前缀「英语·」（与线上 worker 等价）
function englishTopicTags(vol, bank) {
  if (!vol || bank === 'ket') return [];
  const raw = vol.topic || vol.title || '';
  return raw.split('·').map(s => s.trim()).filter(Boolean).map(s => '英语·' + s);
}
function buildEnglishPool(bank, authed) {
  const pool = [];
  if (bank === 'quiz') {
    const vols = authed ? quiz.volumes : quiz.volumes.filter(v => v.id === TRIAL_VOL);
    for (const v of vols) {
      for (const p of (v.parts || [])) {
        const qs = p.type === 'speaking' ? (p.tasks || []) : (p.questions || []);
        qs.forEach((qn, idx) => {
          if (!Array.isArray(qn.options)) return;
          const t = qn.type || p.type || '';
          pool.push({ id: qn.id, vol: v.id, idx, q: qn.question || qn.q || '', options: qn.options, answer: qn.answer, scene: qn.audio || null, tip: qn.analysis || qn.tip || qn.audioText || null, type: 'choice', tags: englishTags(t, 'quiz').concat(englishTopicTags(v, 'quiz')) });
        });
      }
    }
  } else if (bank === 'plist') {
    const vols = authed ? plist.volumes : plist.volumes.filter(v => v.id === TRIAL_LT);
    for (const v of vols) {
      (v.questions || []).forEach((qn, idx) => {
        if (!Array.isArray(qn.options)) return;
        pool.push({ id: qn.id, vol: v.id, idx, q: qn.q || qn.question || '', options: qn.options, answer: qn.answer, scene: qn.audio || null, tip: qn.tip || qn.analysis || qn.audioText || null, type: 'choice', tags: englishTags(qn.type, 'plist').concat(englishTopicTags(v, 'plist')) });
      });
    }
  } else if (bank === 'kids') {
    const vols = authed ? kidsLt.volumes : kidsLt.volumes.filter(v => v.id === TRIAL_KIDS_L);
    for (const v of vols) {
      (v.questions || []).forEach((qn, idx) => {
        if (!Array.isArray(qn.options)) return;
        pool.push({ id: qn.id, vol: v.id, idx, q: qn.q || qn.question || '', options: qn.options, answer: qn.answer, scene: qn.audio || null, tip: qn.tip || qn.analysis || qn.audioText || null, type: 'choice', tags: englishTags(qn.type, 'kids').concat(englishTopicTags(v, 'kids')) });
      });
    }
  } else if (bank === 'gk') {
    const sets = authed ? gk.sets : gk.sets.filter(s => s.id === TRIAL_GK);
    sets.forEach((s, idx) => {
      pool.push({
        id: s.id, vol: s.id, idx, q: s.title || s.id, options: null, answer: null,
        scene: (s.audio && s.audio.dialogue) || null, type: 'gkset', tags: ['英语·高考听说'],
        gk: { id: s.id, title: s.title, topic: s.topic, scene: s.scene, dialogue: s.dialogue, q3: s.q3, a5: s.a5, analysis: s.analysis, trap: s.trap, audio: s.audio },
      });
    });
  } else {
    const vols = authed ? kx.volumes : kx.volumes.filter(v => v.id === TRIAL_KX);
    for (const v of vols) {
      (v.questions || []).forEach((qn, idx) => {
        if (!Array.isArray(qn.options)) return;
        pool.push({ id: qn.id, vol: v.id, idx, q: qn.q || qn.question || '', options: qn.options, answer: qn.answer, scene: qn.audio || null, tip: qn.tip || qn.analysis || qn.audio_text || null, type: 'choice', tags: englishTags(qn.type, 'ket') });
      });
    }
  }
  return pool;
}
function findEnglishQuestion(qid) {
  for (const v of (quiz.volumes || [])) {
    for (const p of (v.parts || [])) {
      const qs = p.type === 'speaking' ? (p.tasks || []) : (p.questions || []);
      for (const qn of qs) if (qn.id === qid) return Object.assign({}, qn, { _bank: 'quiz', tags: englishTags(qn.type || p.type, 'quiz').concat(englishTopicTags(v, 'quiz')) });
    }
  }
  for (const v of (kx.volumes || [])) {
    for (const qn of (v.questions || [])) if (qn.id === qid) return Object.assign({}, qn, { _bank: 'ket', tags: englishTags(qn.type, 'ket') });
  }
  for (const v of (plist.volumes || [])) {
    for (const qn of (v.questions || [])) if (qn.id === qid) return Object.assign({}, qn, { _bank: 'plist', tags: englishTags(qn.type, 'plist').concat(englishTopicTags(v, 'plist')) });
  }
  for (const v of (kidsLt.volumes || [])) {
    for (const qn of (v.questions || [])) if (qn.id === qid) return Object.assign({}, qn, { _bank: 'kids', tags: englishTags(qn.type, 'kids').concat(englishTopicTags(v, 'kids')) });
  }
  for (const s of (gk.sets || [])) {
    if (s.id === qid) return Object.assign({}, s, { _bank: 'gk', tags: ['英语·高考听说'], gk: s });
  }
  return null;
}

const srv = http.createServer(async (req, res) => {
  const u = req.url.split('?')[0];
  const q = Object.fromEntries(new URL(req.url, 'http://x').searchParams);

  if (u.startsWith('/api/')) {
    const b = (req.method === 'POST') ? await body(req) : {};
    const dev = getDev(b, req); // 本次请求的设备标识

    // —— 注册（顺带绑定首台设备）——
    if (u === '/api/register' && req.method === 'POST') {
      const { username, password } = b;
      if (!username || !password) return err(res, 400, '用户名和密码必填');
      if (String(password).length < 6) return err(res, 400, '密码至少 6 位');
      if (users.find(x => x.username === username)) return err(res, 409, '用户名已存在');
      const { salt, hash } = hashPw(password);
      const user = { id: 'u' + Date.now(), username, salt, hash, authorized: false, code: null, expiry: null, modules: {}, createdAt: Date.now(), sessionSeq: 0, devices: [] };
      users.push(user);
      bindDevice(user, dev);            // 首台设备直接绑定
      if (settings.trialOpen) {         // 体验开关开启：新用户自动获 N 天全模块全功能（N 可配置，默认 7）
        const days = Math.min(3650, Math.max(1, Number(settings.trialDays) || 7));
        user.authorized = true;
        user.expiry = Date.now() + days * 864e5;
        user.modules = { kids: 1, primary: 1, middle: 1, gk: 1, math: 1 };
      }
      save('users.json', users);
      const token = issueToken(user);
      return ok(res, { token, username, devices: user.devices.length, maxDevices: MAX_DEVICES });
    }
    // —— 登录（绑定设备 + 单会话踢人）——
    if (u === '/api/login' && req.method === 'POST') {
      const { username, password } = b;
      const user = users.find(x => x.username === username);
      if (!user || !verifyPw(password, user.salt, user.hash)) return err(res, 401, '用户名或密码错误');
      if (!bindDevice(user, dev)) {
        return err(res, 403, `该账号最多绑定 ${MAX_DEVICES} 台设备且已达上限。请使用已绑定的常用设备登录，或联系管理员解绑一台后再试。`);
      }
      save('users.json', users);
      const token = issueToken(user);   // 自增 sessionSeq，旧令牌失效
      return ok(res, { token, username, devices: user.devices.length, maxDevices: MAX_DEVICES });
    }
    // —— 当前用户 ——
    if (u === '/api/me' && req.method === 'GET') {
      const user = uidOf(req.headers['authorization'] || '');
      if (!user) return err(res, 401, '未登录或登录已失效，请重新登录');
      if (!deviceAllowed(user, dev)) return err(res, 403, '当前设备未授权，请重新登录');
      const authOk = !!user.authorized && (!user.expiry || Number(user.expiry) > Date.now());
      return ok(res, { username: user.username, authorized: authOk, expiry: user.expiry, modules: user.modules || {}, devices: (user.devices || []).length, maxDevices: MAX_DEVICES });
    }
    // —— 激活授权码（限次）——
    if (u === '/api/activate' && req.method === 'POST') {
      const user = uidOf(req.headers['authorization'] || '');
      if (!user) return err(res, 401, '未登录或登录已失效，请重新登录');
      if (!deviceAllowed(user, dev)) return err(res, 403, '当前设备未授权，请重新登录');
      const { code } = b;
      const c = codes.find(x => x.code === code && (x.acts || 0) < (x.maxActs || 1));
      if (!c) return err(res, 400, '授权码无效、已使用或已达激活次数');
      c.acts = (c.acts || 0) + 1;
      c.usedBy = Array.isArray(c.usedBy) ? c.usedBy : (c.usedBy ? [c.usedBy] : []);
      c.usedBy.push(user.id); c.usedAt = Date.now();
      user.authorized = true; user.code = code; user.expiry = c.days ? Date.now() + c.days * 864e5 : null; // 时长从激活日起算
      user.modules = { primary: 1, middle: 1, gk: 1 }; // 激活码解锁全部模块
      save('codes.json', codes); save('users.json', users);
      return ok(res, { authorized: true, expiry: user.expiry });
    }
    // —— 解绑当前设备（释放设备名额）——
    if (u === '/api/device/unbind' && req.method === 'POST') {
      const user = uidOf(req.headers['authorization'] || '');
      if (!user) return err(res, 401, '未登录或登录已失效，请重新登录');
      if (!deviceAllowed(user, dev)) return err(res, 403, '当前设备未授权');
      user.devices = (user.devices || []).filter(d => d !== dev);
      save('users.json', users);
      return ok(res, { ok: true, devices: user.devices.length, maxDevices: MAX_DEVICES });
    }
    // —— 学情数据：拉取（合并云端与本地由前端负责）——
    if (u === '/api/study' && req.method === 'GET') {
      const user = uidOf(req.headers['authorization'] || '');
      if (!user) return err(res, 401, '未登录或登录已失效，请重新登录');
      if (!deviceAllowed(user, dev)) return err(res, 403, '当前设备未授权，请重新登录');
      const s = study[user.username] || {};
      return ok(res, { log: s.log || {}, progress: s.progress || {}, ans: s.ans || {}, tags: s.tags || {}, updated: s.updated || 0 });
    }
    // —— 学情数据：上传合并（log 按 last、progress 按 t 取新者胜）——
    if (u === '/api/study/sync' && req.method === 'POST') {
      const user = uidOf(req.headers['authorization'] || '');
      if (!user) return err(res, 401, '未登录或登录已失效，请重新登录');
      if (!deviceAllowed(user, dev)) return err(res, 403, '当前设备未授权，请重新登录');
      const cur = study[user.username] || { log: {}, progress: {}, ans: {}, tags: {} };
      const log = cur.log || {};
      const progress = cur.progress || {};
      const ans = cur.ans || {};
      const tags = cur.tags || {};
      const il = (b && typeof b.log === 'object' && b.log) || {};
      const ip = (b && typeof b.progress === 'object' && b.progress) || {};
      for (const k in il) {
        if (!il[k] || typeof il[k] !== 'object') continue;
        if (!log[k] || (Number(il[k].last) || 0) >= (Number(log[k].last) || 0)) log[k] = il[k];
      }
      for (const k in ip) {
        if (!ip[k] || typeof ip[k] !== 'object') continue;
        if (!progress[k] || (Number(ip[k].t) || 0) >= (Number(progress[k].t) || 0)) progress[k] = ip[k];
      }
      // 逐题作答累加（ans）+ 派生 tags 统计（P0 学情地基，镜像移植）
      // 记录格式：{ qid:string, correct:bool, choice?:number, time?:number(毫秒), tags?:string[] }
      const ia = (b && Array.isArray(b.ans)) ? b.ans : null;
      if (ia && ia.length) {
        for (const rec of ia) {
          if (!rec || !rec.qid || typeof rec.correct !== 'boolean') continue;
          const q = ans[rec.qid] || { r: 0, w: 0, lw: null, lt: 0, ts: 0, tags: [] };
          if (rec.correct) q.r += 1; else { q.w += 1; if (rec.choice != null) q.lw = rec.choice; }
          if (rec.time != null && rec.time > 0) q.lt = rec.time;
          q.ts = Date.now();
          const recTags = Array.isArray(rec.tags) ? rec.tags.filter(Boolean) : [];
          for (const t of recTags) if (!q.tags.includes(t)) q.tags.push(t);
          ans[rec.qid] = q;
          // 派生 tags 统计（供薄弱点/错题本/学习报告读取）
          const tagSet = recTags.length ? recTags : ['__untagged__'];
          for (const t of tagSet) {
            const tg = tags[t] || { wrong: 0, total: 0, last: 0 };
            tg.total += 1;
            if (!rec.correct) tg.wrong += 1;
            tg.last = Date.now();
            tags[t] = tg;
          }
        }
      }
      study[user.username] = { log, progress, ans, tags, updated: Date.now() };
      save('study.json', study);
      return ok(res, { ok: true, updated: study[user.username].updated });
    }
    // —— 管理员登录（密钥换令牌）——
    if (u === '/api/admin/login' && req.method === 'POST') {
      const { secret } = b;
      if (!secret || secret !== ADMIN_SECRET) return err(res, 403, '管理员密钥错误');
      return ok(res, { token: makeAdminToken() });
    }
    // —— 生成授权码（网页后台用；时长类型：permanent 永久 / annual 学年 / semester 学期 / custom 自定义天数）——
    if (u === '/api/admin/gen-codes' && req.method === 'POST') {
      if (!isAdmin(req)) return err(res, 403, '无权限');
      const PLAN_DAYS = { permanent: null, annual: 365, semester: 180 };
      const n = Math.min(50, Math.max(1, parseInt(b.count, 10) || 10));
      const maxActs = Math.min(99, Math.max(1, parseInt(b.maxActs, 10) || 1));
      let plan, days;
      if (b.plan === 'custom') {
        plan = 'custom';
        days = Math.min(3650, Math.max(1, parseInt(b.days, 10) || 30));
      } else if (PLAN_DAYS.hasOwnProperty(b.plan)) {
        plan = b.plan; days = PLAN_DAYS[b.plan];
      } else {
        plan = 'custom'; days = Math.min(3650, Math.max(1, parseInt(b.days, 10) || 30));
      }
      const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
      const made = [];
      for (let i = 0; i < n; i++) {
        let c;
        do { c = ''; for (let j = 0; j < 8; j++) c += chars[crypto.randomBytes(1)[0] % chars.length]; } while (codes.find(x => x.code === c));
        codes.push({ code: c, plan, days, maxActs, acts: 0, usedBy: [], usedAt: null, createdAt: Date.now() });
        made.push(c);
      }
      save('codes.json', codes);
      return ok(res, { codes: made, plan, days, maxActs });
    }
    // —— 授权码列表（管理员）——
    if (u === '/api/admin/codes' && req.method === 'GET') {
      if (!(isAdmin(req) || q.secret === ADMIN_SECRET)) return err(res, 403, '无权限');
      return ok(res, { codes: codes.map(c => ({ code: c.code, used: (c.acts || 0), maxActs: (c.maxActs || 1), plan: c.plan, days: c.days })) });
    }
    // —— 用户列表（管理员）——
    if (u === '/api/admin/users' && req.method === 'GET') {
      if (!isAdmin(req)) return err(res, 403, '无权限');
      return ok(res, { users: users.map(x => ({ id: x.id, username: x.username, authorized: !!x.authorized, code: x.code, expiry: x.expiry, modules: x.modules || {}, devices: x.devices || [], createdAt: x.createdAt })) });
    }
    // —— 解绑用户设备（管理员，释放设备名额）——
    if (u === '/api/admin/users/unbind' && req.method === 'POST') {
      if (!isAdmin(req)) return err(res, 403, '无权限');
      const { username, device } = b;
      const user = users.find(x => x.username === username);
      if (!user) return err(res, 404, '用户不存在');
      const before = (user.devices || []).length;
      user.devices = (user.devices || []).filter(d => d !== device);
      if (user.devices.length === before) return err(res, 400, '该设备不在绑定列表');
      save('users.json', users);
      return ok(res, { ok: true, devices: user.devices });
    }
    // —— 直接授权/调整授权（管理员，免授权码）——
    if (u === '/api/admin/users/grant' && req.method === 'POST') {
      if (!isAdmin(req)) return err(res, 403, '无权限');
      const PLAN_DAYS = { permanent: null, annual: 365, semester: 180 };
      let days;
      if (b.plan === 'custom') days = Math.min(3650, Math.max(1, parseInt(b.days, 10) || 30));
      else if (PLAN_DAYS.hasOwnProperty(b.plan)) days = PLAN_DAYS[b.plan];
      else return err(res, 400, '无效的授权类型');
      const user = users.find(x => x.username === b.username);
      if (!user) return err(res, 404, '用户不存在');
      const ALL = ['kids', 'primary', 'middle', 'gk', 'math'];
      let mods = ALL;
      if (Array.isArray(b.modules) && b.modules.length) {
        mods = b.modules.filter(m => ALL.includes(m));
        if (!mods.length) return err(res, 400, '无效的授权模块（可选：kids/primary/middle/gk/math）');
      }
      user.authorized = true;
      user.expiry = days ? Date.now() + days * 864e5 : null;
      user.modules = {}; mods.forEach(m => { user.modules[m] = 1; });
      save('users.json', users);
      return ok(res, { ok: true, expiry: user.expiry, modules: user.modules });
    }
    // —— 体验授权开关：读取 / 设置（管理员）——
    if (u === '/api/admin/settings' && req.method === 'GET') {
      if (!isAdmin(req)) return err(res, 403, '无权限');
      return ok(res, { trialOpen: !!settings.trialOpen, trialDays: Math.min(3650, Math.max(1, Number(settings.trialDays) || 7)) });
    }
    if (u === '/api/admin/settings' && req.method === 'POST') {
      if (!isAdmin(req)) return err(res, 403, '无权限');
      const on = b.trialOpen === true || b.trialOpen === '1' || b.trialOpen === 1;
      settings.trialOpen = on;
      settings.trialDays = Math.min(3650, Math.max(1, parseInt(b.trialDays, 10) || 7));
      save('settings.json', settings);
      return ok(res, { trialOpen: on, trialDays: settings.trialDays });
    }
    // —— 撤销用户授权（管理员）——
    if (u === '/api/admin/users/revoke' && req.method === 'POST') {
      if (!isAdmin(req)) return err(res, 403, '无权限');
      const user = users.find(x => x.username === b.username);
      if (!user) return err(res, 404, '用户不存在');
      user.authorized = false; user.code = null; user.expiry = null; user.modules = {};
      user.sessionSeq = (Number(user.sessionSeq || 0)) + 1; // 踢下线，需重新登录激活
      save('users.json', users);
      return ok(res, { ok: true });
    }
    // —— 卷列表 ——
    if (u === '/api/volumes' && req.method === 'GET') {
      const user = uidOf(req.headers['authorization'] || '');
      if (!user) return err(res, 401, '未登录或登录已失效，请重新登录');
      if (!deviceAllowed(user, dev)) return err(res, 403, '当前设备未授权，请重新登录');
      if (user.expiry && Number(user.expiry) <= Date.now()) return err(res, 403, '授权已过期，请联系管理员续费或重新激活');
      const authed = modAuthed(user, 'middle');
      const vols = quiz.volumes.map(v => ({ id: v.id, title: v.title, topic: v.topic, mainTrap: v.mainTrap, totalScore: v.totalScore, parts: (v.parts || []).map(p => ({ part: p.part, name: p.name, type: p.type, count: p.type === 'speaking' ? (p.tasks || []).length : (p.questions || []).length })) }));
      return ok(res, { volumes: authed ? vols : vols.filter(v => v.id === TRIAL_VOL), trial: !authed });
    }
    // —— 单卷题目 ——
    if (u.startsWith('/api/quiz') && req.method === 'GET') {
      const user = uidOf(req.headers['authorization'] || '');
      if (!user) return err(res, 401, '未登录或登录已失效，请重新登录');
      if (!deviceAllowed(user, dev)) return err(res, 403, '当前设备未授权，请重新登录');
      if (user.expiry && Number(user.expiry) <= Date.now()) return err(res, 403, '授权已过期，请联系管理员续费或重新激活');
      const authed = modAuthed(user, 'middle');
      const vol = quiz.volumes.find(v => v.id === q.vol);
      if (!vol) return err(res, 404, '卷不存在');
      if (!authed && vol.id !== TRIAL_VOL) return err(res, 403, '体验模式仅可练习 ' + TRIAL_VOL + '，输入授权码或联系管理员解锁全部试卷');
      return ok(res, vol);
    }
    // —— 幼儿启蒙词汇：组列表 / 单组单词（未授权 = 体验模式，仅放行第 1 组）——
    if (u === '/api/kids-words' && req.method === 'GET') {
      const user = uidOf(req.headers['authorization'] || '');
      if (!user) return err(res, 401, '未登录或登录已失效，请重新登录');
      if (!deviceAllowed(user, dev)) return err(res, 403, '当前设备未授权，请重新登录');
      if (user.expiry && Number(user.expiry) <= Date.now()) return err(res, 403, '授权已过期，请联系管理员续费或重新激活');
      const authed = modAuthed(user, 'kids');
      const gid = q.words || q.group;
      if (gid) {
        const g = kidsWords.groups.find(x => x.id === gid);
        if (!g) return err(res, 404, '主题不存在');
        if (!authed && gid !== TRIAL_KIDS_W) return err(res, 403, '体验模式仅可学习 ' + TRIAL_KIDS_W + '，输入授权码或联系管理员解锁全部主题');
        return ok(res, g);
      }
      const groups = kidsWords.groups.map(g => ({ id: g.id, grade: g.grade, title: g.title, count: g.words.length }));
      return ok(res, { groups: authed ? groups : groups.filter(g => g.id === TRIAL_KIDS_W), trial: !authed });
    }
    // —— 小学单词：组列表 / 单组单词 ——
    if (u === '/api/words' && req.method === 'GET') {
      const user = uidOf(req.headers['authorization'] || '');
      if (!user) return err(res, 401, '未登录或登录已失效，请重新登录');
      if (!deviceAllowed(user, dev)) return err(res, 403, '当前设备未授权，请重新登录');
      if (user.expiry && Number(user.expiry) <= Date.now()) return err(res, 403, '授权已过期，请联系管理员续费或重新激活');
      const authed = modAuthed(user, 'primary');
      const gid = q.words || q.group;
      if (gid) {
        const g = words.groups.find(x => x.id === gid);
        if (!g) return err(res, 404, '主题不存在');
        if (!authed && gid !== TRIAL_GROUP) return err(res, 403, '体验模式仅可学习 ' + TRIAL_GROUP + '，输入授权码或联系管理员解锁全部主题');
        return ok(res, g);
      }
      const groups = words.groups.map(g => ({ id: g.id, grade: g.grade, title: g.title, count: g.words.length }));
      return ok(res, { groups: authed ? groups : groups.filter(g => g.id === TRIAL_GROUP), trial: !authed });
    }
    // —— 小学自然拼读：级别列表（未授权 = 体验模式，仅放行第一条规则）——
    if (u === '/api/phonics' && req.method === 'GET') {
      const user = uidOf(req.headers['authorization'] || '');
      if (!user) return err(res, 401, '未登录或登录已失效，请重新登录');
      if (!deviceAllowed(user, dev)) return err(res, 403, '当前设备未授权，请重新登录');
      if (user.expiry && Number(user.expiry) <= Date.now()) return err(res, 403, '授权已过期，请联系管理员续费或重新激活');
      const authed = modAuthed(user, 'primary');
      if (!authed) {
        // 体验模式：仅保留第一条规则（p101），级别精简
        const lv0 = phonics.levels[0];
        if (!lv0) return ok(res, { levels: [], trial: true });
        const r0 = lv0.rules.find(x => x.id === TRIAL_RULE);
        const slim = { id: lv0.id, name: lv0.name, desc: lv0.desc, rules: r0 ? [r0] : [] };
        return ok(res, { levels: [slim], trial: true });
      }
      return ok(res, { levels: phonics.levels, trial: false });
    }
    // —— 小学单词场景化：场景列表 / 单场景（未授权 = 体验模式，仅放行第一个场景）——
    if (u === '/api/scenes' && req.method === 'GET') {
      const user = uidOf(req.headers['authorization'] || '');
      if (!user) return err(res, 401, '未登录或登录已失效，请重新登录');
      if (!deviceAllowed(user, dev)) return err(res, 403, '当前设备未授权，请重新登录');
      if (user.expiry && Number(user.expiry) <= Date.now()) return err(res, 403, '授权已过期，请联系管理员续费或重新激活');
      const authed = modAuthed(user, 'primary');
      const sid = q.scene;
      if (sid) {
        const sc = scenes.scenes.find(x => x.id === sid);
        if (!sc) return err(res, 404, '场景不存在');
        if (!authed && sid !== TRIAL_SCENE) return err(res, 403, '体验模式仅可学习 ' + TRIAL_SCENE + '，输入授权码或联系管理员解锁全部场景');
        return ok(res, sc);
      }
      const list = scenes.scenes.map(s => ({ id: s.id, grade: s.grade, title: s.title, count: s.sentences.length }));
      return ok(res, { scenes: authed ? list : list.filter(s => s.id === TRIAL_SCENE), trial: !authed });
    }
    // —— 小学听说题型库：卷列表 / 单卷（未授权 = 体验模式，仅放行第 1 卷）——
    if (u === '/api/primary-listening' && req.method === 'GET') {
      const user = uidOf(req.headers['authorization'] || '');
      if (!user) return err(res, 401, '未登录或登录已失效，请重新登录');
      if (!deviceAllowed(user, dev)) return err(res, 403, '当前设备未授权，请重新登录');
      if (user.expiry && Number(user.expiry) <= Date.now()) return err(res, 403, '授权已过期，请联系管理员续费或重新激活');
      const authed = modAuthed(user, 'primary');
      const vid = q.vol;
      if (vid) {
        const v = plist.volumes.find(x => x.id === vid);
        if (!v) return err(res, 404, '试卷不存在');
        if (!authed && vid !== TRIAL_LT) return err(res, 403, '体验模式仅可练习 ' + TRIAL_LT + '，输入授权码或联系管理员解锁全部试卷');
        return ok(res, v);
      }
      const list = plist.volumes.map(v => ({ id: v.id, grade: v.grade, title: v.title, topic: v.topic, count: v.questions.length }));
      return ok(res, { volumes: authed ? list : list.filter(v => v.id === TRIAL_LT), trial: !authed });
    }
    // —— 数学思维训练：卷列表 / 单卷（未授权 = 体验模式，仅放行第 1 单元）——
    if (u === '/api/math' && req.method === 'GET') {
      const user = uidOf(req.headers['authorization'] || '');
      if (!user) return err(res, 401, '未登录或登录已失效，请重新登录');
      if (!deviceAllowed(user, dev)) return err(res, 403, '当前设备未授权，请重新登录');
      if (user.expiry && Number(user.expiry) <= Date.now()) return err(res, 403, '授权已过期，请联系管理员续费或重新激活');
      const lvl = (q.level || 'p');
      let dataset, TRIAL;
      if (lvl === 'm') { dataset = mathMiddle; TRIAL = TRIAL_MM; }
      else if (lvl === 'h') { dataset = mathHigh; TRIAL = TRIAL_MH; }
      else { dataset = mathPrimary; TRIAL = TRIAL_MP; }
      const authed = modAuthed(user, 'math');
      const vid = q.vol;
      if (vid) {
        const v = dataset.volumes.find(x => x.id === vid);
        if (!v) return err(res, 404, '试卷不存在');
        if (!authed && vid !== TRIAL) return err(res, 403, '体验模式仅可练习 ' + TRIAL + '，输入授权码或联系管理员解锁全部单元');
        return ok(res, v);
      }
      const list = dataset.volumes.map(v => ({ id: v.id, grade: v.grade, title: v.title, topic: v.topic, count: v.questions.length }));
      return ok(res, { volumes: authed ? list : list.filter(v => v.id === TRIAL), trial: !authed });
    }
    // —— 基础自检中心：跨卷随机抽题（P1 能力补齐层，镜像移植）——
    if (u === '/api/selfcheck' && req.method === 'POST') {
      const user = uidOf(req.headers['authorization'] || '');
      if (!user) return err(res, 401, '未登录或登录已失效，请重新登录');
      if (!deviceAllowed(user, dev)) return err(res, 403, '当前设备未授权，请重新登录');
      const module = (b && b.module) || 'math';
      const lvl = (b && b.level) || 'p';
      const count = Math.min(20, Math.max(1, parseInt((b && b.count) || '10', 10) || 10));
      const wantTags = Array.isArray(b && b.tags) ? b.tags : [];
      if (module !== 'math' && module !== 'english') return err(res, 400, '暂仅支持数学/英语自检');
      if (module === 'english') {
        const bank = (b && b.bank) || 'ket';
        const authedE = modAuthed(user, bank === 'quiz' ? 'middle' : (bank === 'kids' ? 'kids' : (bank === 'gk' ? 'gk' : 'primary')));
        const epool = buildEnglishPool(bank, authedE);
        if (!epool.length) return err(res, 404, '该题型库暂无可练习题目');
        const needE = Math.min(count, epool.length);
        for (let i = epool.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); const t = epool[i]; epool[i] = epool[j]; epool[j] = t; }
        const questions = epool.slice(0, needE).map(it => ({
          qid: 'eng:' + it.id, id: it.id, vol: it.vol, idx: it.idx, type: it.type,
          q: it.q, options: it.options, answer: it.answer, scene: it.scene || null,
          optionImgs: null, tip: it.tip || null, tags: it.tags || null, steps: null, gk: it.gk || null,
        }));
        return ok(res, { questions, level: bank, count: questions.length, trial: !authedE, module: 'english' });
      }
      let dataset, TRIAL;
      if (lvl === 'm') { dataset = mathMiddle; TRIAL = TRIAL_MM; }
      else if (lvl === 'h') { dataset = mathHigh; TRIAL = TRIAL_MH; }
      else { dataset = mathPrimary; TRIAL = TRIAL_MP; }
      const authed = modAuthed(user, 'math');
      const vols = authed ? dataset.volumes : dataset.volumes.filter(v => v.id === TRIAL);
      const pool = [];
      for (const v of vols) {
        (v.questions || []).forEach((qn, idx) => { pool.push({ vol: v.id, idx, qn }); });
      }
      if (!pool.length) return err(res, 404, '该学段暂无可练习题目');
      let drawPool = pool;
      if (wantTags.length) {
        const fp = pool.filter(it => Array.isArray(it.qn.tags) && it.qn.tags.some(t => wantTags.indexOf(t) >= 0));
        if (fp.length) drawPool = fp; // 命中为空时回退全量，保证有题可做
      }
      const need = Math.min(count, drawPool.length);
      for (let i = drawPool.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        const t = drawPool[i]; drawPool[i] = drawPool[j]; drawPool[j] = t;
      }
      const questions = drawPool.slice(0, need).map(it => {
        const qn = it.qn;
        return {
          qid: 'math:' + it.vol + '#' + it.idx,
          id: qn.id != null ? qn.id : it.idx,
          vol: it.vol, idx: it.idx,
          type: qn.type || (Array.isArray(qn.options) && qn.options.length ? 'choice' : 'fill'),
          q: qn.q || qn.question || '',
          options: qn.options || null,
          answer: qn.answer,
          scene: qn.scene || null,
          optionImgs: qn.optionImgs || null,
          tip: qn.tip || qn.analysis || null,
          tags: qn.tags || null,
          steps: qn.steps || null,
        };
      });
      return ok(res, { questions, level: lvl, count: questions.length, trial: !authed });
    }
    // —— 按 qid 批量取题面（P2 错题本 / 重做用，镜像移植）——
    if (u === '/api/qbyid' && req.method === 'GET') {
      const user = uidOf(req.headers['authorization'] || '');
      if (!user) return err(res, 401, '未登录或登录已失效，请重新登录');
      if (!deviceAllowed(user, dev)) return err(res, 403, '当前设备未授权，请重新登录');
      const raw = (q.qids || '').split(',').map(s => s.trim()).filter(Boolean);
      const out = {};
      for (const id of raw) {
        if (id.indexOf('eng:') === 0) {
          const fq = findEnglishQuestion(id.slice(4));
          if (!fq) { out[id] = null; continue; }
          if (fq._bank === 'gk') {
            out[id] = {
              qid: id, vol: fq.vol || '', idx: fq.idx || 0, type: 'gkset',
              q: fq.title || fq.q || '', options: null, answer: null, scene: (fq.audio && fq.audio.dialogue) || null,
              optionImgs: null, tip: null, tags: fq.tags || null, steps: null, gk: fq.gk || null,
            };
            continue;
          }
          out[id] = {
            qid: id, vol: fq.vol || '', idx: fq.idx || 0, type: 'choice',
            q: fq.q || fq.question || '', options: fq.options || null, answer: fq.answer,
            scene: fq.audio || null, optionImgs: null, tip: fq.tip || fq.analysis || null,
            tags: fq.tags || null, steps: null,
          };
          continue;
        }
        const m = /^math:(mp|mj|mh)([0-9]+)#([0-9]+)$/.exec(id);
        if (!m) { out[id] = null; continue; }
        const pre = m[1], vol = m[1] + m[2], idx = parseInt(m[3], 10);
        const lvl = pre === 'mp' ? 'p' : (pre === 'mj' ? 'm' : 'h');
        const dataset = lvl === 'p' ? mathPrimary : (lvl === 'm' ? mathMiddle : mathHigh);
        const v = dataset.volumes.find(x => x.id === vol);
        const qn = v && v.questions ? v.questions[idx] : null;
        if (!qn) { out[id] = null; continue; }
        out[id] = {
          qid: id, vol, idx,
          type: qn.type || (Array.isArray(qn.options) && qn.options.length ? 'choice' : 'fill'),
          q: qn.q || qn.question || '',
          options: qn.options || null,
          answer: qn.answer,
          scene: qn.scene || null,
          optionImgs: qn.optionImgs || null,
          tip: qn.tip || qn.analysis || null,
          tags: qn.tags || null,
          steps: qn.steps || null,
        };
      }
      return ok(res, { questions: out });
    }
    // —— 幼儿听说题库：卷列表 / 单卷（未授权 = 体验模式，仅放行第 1 卷）——
    if (u === '/api/kids-listening' && req.method === 'GET') {
      const user = uidOf(req.headers['authorization'] || '');
      if (!user) return err(res, 401, '未登录或登录已失效，请重新登录');
      if (!deviceAllowed(user, dev)) return err(res, 403, '当前设备未授权，请重新登录');
      if (user.expiry && Number(user.expiry) <= Date.now()) return err(res, 403, '授权已过期，请联系管理员续费或重新激活');
      const authed = modAuthed(user, 'kids');
      const vid = q.vol;
      if (vid) {
        const v = kidsLt.volumes.find(x => x.id === vid);
        if (!v) return err(res, 404, '试卷不存在');
        if (!authed && vid !== TRIAL_KIDS_L) return err(res, 403, '体验模式仅可练习 ' + TRIAL_KIDS_L + '，输入授权码或联系管理员解锁全部试卷');
        return ok(res, v);
      }
      const list = kidsLt.volumes.map(v => ({ id: v.id, title: v.title, desc: v.desc, count: v.questions.length }));
      return ok(res, { volumes: authed ? list : list.filter(v => v.id === TRIAL_KIDS_L), trial: !authed });
    }
    // —— 幼儿儿歌磨耳朵：列表 / 单首（未授权 = 体验模式，仅放行第 1 首）——
    if (u === '/api/kids-songs' && req.method === 'GET') {
      const user = uidOf(req.headers['authorization'] || '');
      if (!user) return err(res, 401, '未登录或登录已失效，请重新登录');
      if (!deviceAllowed(user, dev)) return err(res, 403, '当前设备未授权，请重新登录');
      if (user.expiry && Number(user.expiry) <= Date.now()) return err(res, 403, '授权已过期，请联系管理员续费或重新激活');
      const authed = modAuthed(user, 'kids');
      const sid = q.id;
      if (sid) {
        const s = kidsSongs.songs.find(x => x.id === sid);
        if (!s) return err(res, 404, '儿歌不存在');
        if (!authed && sid !== TRIAL_KIDS_S) return err(res, 403, '体验模式仅可学 ' + TRIAL_KIDS_S + '，输入授权码或联系管理员解锁全部儿歌');
        return ok(res, s);
      }
      const list = kidsSongs.songs.map(s => ({ id: s.id, title: s.title, zhTitle: s.zhTitle, emoji: s.emoji, theme: s.theme, lines: s.lines.length }));
      return ok(res, { songs: authed ? list : list.filter(s => s.id === TRIAL_KIDS_S), trial: !authed });
    }
    // —— 幼儿 TPR 日常指令：组列表 / 单组（未授权 = 体验模式，仅放行第 1 组）——
    if (u === '/api/kids-tpr' && req.method === 'GET') {
      const user = uidOf(req.headers['authorization'] || '');
      if (!user) return err(res, 401, '未登录或登录已失效，请重新登录');
      if (!deviceAllowed(user, dev)) return err(res, 403, '当前设备未授权，请重新登录');
      if (user.expiry && Number(user.expiry) <= Date.now()) return err(res, 403, '授权已过期，请联系管理员续费或重新激活');
      const authed = modAuthed(user, 'kids');
      const gid = q.group;
      if (gid) {
        const g = kidsTpr.groups.find(x => x.id === gid);
        if (!g) return err(res, 404, '指令组不存在');
        if (!authed && gid !== TRIAL_KIDS_T) return err(res, 403, '体验模式仅可学 ' + TRIAL_KIDS_T + '，输入授权码或联系管理员解锁全部指令');
        return ok(res, g);
      }
      const list = kidsTpr.groups.map(g => ({ id: g.id, title: g.title, emoji: g.emoji, count: g.items.length }));
      return ok(res, { groups: authed ? list : list.filter(g => g.id === TRIAL_KIDS_T), trial: !authed });
    }
    // —— 幼儿自然拼读：字母/CVC/字母歌（未授权 = 体验模式，仅放行前 3 个字母）——
    if (u === '/api/kids-phonics' && req.method === 'GET') {
      const user = uidOf(req.headers['authorization'] || '');
      if (!user) return err(res, 401, '未登录或登录已失效，请重新登录');
      if (!deviceAllowed(user, dev)) return err(res, 403, '当前设备未授权，请重新登录');
      if (user.expiry && Number(user.expiry) <= Date.now()) return err(res, 403, '授权已过期，请联系管理员续费或重新激活');
      const authed = modAuthed(user, 'kids');
      const trialIdx = 3; // 体验放行前 3 个字母 A-C
      const letters = authed ? kidsPhonics.letters : kidsPhonics.letters.slice(0, trialIdx);
      const cvc = authed ? kidsPhonics.cvc : [];
      return ok(res, { letters, cvc, song: kidsPhonics.song, trial: !authed, trialHint: '体验模式可学 A-C 字母音，输入授权码或联系管理员解锁全部' });
    }
    // —— 幼儿迷你绘本：书目列表 / 单本（未授权 = 体验模式，仅放行第 1 本）——
    if (u === '/api/kids-reading' && req.method === 'GET') {
      const user = uidOf(req.headers['authorization'] || '');
      if (!user) return err(res, 401, '未登录或登录已失效，请重新登录');
      if (!deviceAllowed(user, dev)) return err(res, 403, '当前设备未授权，请重新登录');
      if (user.expiry && Number(user.expiry) <= Date.now()) return err(res, 403, '授权已过期，请联系管理员续费或重新激活');
      const authed = modAuthed(user, 'kids');
      const bid = q.id;
      if (bid) {
        const b = kidsReading.books.find(x => x.id === bid);
        if (!b) return err(res, 404, '绘本不存在');
        if (!authed && bid !== TRIAL_KIDS_R) return err(res, 403, '体验模式仅可读 ' + TRIAL_KIDS_R + '，输入授权码或联系管理员解锁全部绘本');
        return ok(res, b);
      }
      const list = kidsReading.books.map(b => ({ id: b.id, title: b.title, zhTitle: b.zhTitle, emoji: b.emoji, pages: b.pages.length }));
      return ok(res, { books: authed ? list : list.filter(b => b.id === TRIAL_KIDS_R), trial: !authed });
    }
    // —— 深圳朗文 1A-6B：册列表 / 单册（未授权 = 体验模式，仅放行 1A）——
    if (u === '/api/longman' && req.method === 'GET') {
      const user = uidOf(req.headers['authorization'] || '');
      if (!user) return err(res, 401, '未登录或登录已失效，请重新登录');
      if (!deviceAllowed(user, dev)) return err(res, 403, '当前设备未授权，请重新登录');
      if (user.expiry && Number(user.expiry) <= Date.now()) return err(res, 403, '授权已过期，请联系管理员续费或重新激活');
      const authed = modAuthed(user, 'primary');
      const bid = q.book;
      if (bid) {
        const bk = longman.books.find(x => x.level.toLowerCase() === String(bid).toLowerCase());
        if (!bk) return err(res, 404, '教材册次不存在');
        if (!authed && String(bid).toLowerCase() !== TRIAL_LW) return err(res, 403, '体验模式仅可学习 1A，输入授权码或联系管理员解锁全部 12 册');
        return ok(res, bk);
      }
      const list = longman.books.map(b => ({ level: b.level, title: b.title, units: b.units.length, words: b.units.reduce((n, u) => n + u.words.length, 0) }));
      return ok(res, { books: authed ? list : list.filter(b => b.level.toLowerCase() === TRIAL_LW), trial: !authed });
    }
    // —— 校内期末同步包：卷列表 / 单卷（未授权 = 体验模式，仅放行第 1 套）——
    if (u === '/api/primary-exam' && req.method === 'GET') {
      const user = uidOf(req.headers['authorization'] || '');
      if (!user) return err(res, 401, '未登录或登录已失效，请重新登录');
      if (!deviceAllowed(user, dev)) return err(res, 403, '当前设备未授权，请重新登录');
      if (user.expiry && Number(user.expiry) <= Date.now()) return err(res, 403, '授权已过期，请联系管理员续费或重新激活');
      const authed = modAuthed(user, 'primary');
      const vid = q.vol;
      if (vid) {
        const v = pexam.volumes.find(x => x.id === vid);
        if (!v) return err(res, 404, '试卷不存在');
        if (!authed && vid !== TRIAL_EX) return err(res, 403, '体验模式仅可练习 ' + TRIAL_EX + '，输入授权码或联系管理员解锁全部期末卷');
        return ok(res, v);
      }
      const list = pexam.volumes.map(v => ({ id: v.id, grade: v.grade, sem: v.sem, title: v.title, topic: v.topic, count: v.questions.length }));
      return ok(res, { volumes: authed ? list : list.filter(v => v.id === TRIAL_EX), trial: !authed });
    }
    // —— 小升初衔接包：单元列表 / 单单元（未授权 = 体验模式，仅放行第 1 单元）——
    if (u === '/api/junior-link' && req.method === 'GET') {
      const user = uidOf(req.headers['authorization'] || '');
      if (!user) return err(res, 401, '未登录或登录已失效，请重新登录');
      if (!deviceAllowed(user, dev)) return err(res, 403, '当前设备未授权，请重新登录');
      if (user.expiry && Number(user.expiry) <= Date.now()) return err(res, 403, '授权已过期，请联系管理员续费或重新激活');
      const authed = modAuthed(user, 'primary');
      const uid = q.unit;
      if (uid) {
        const un = jlink.units.find(x => x.id === uid);
        if (!un) return err(res, 404, '单元不存在');
        if (!authed && uid !== TRIAL_JL) return err(res, 403, '体验模式仅可学习 ' + TRIAL_JL + '，输入授权码或联系管理员解锁全部单元');
        return ok(res, un);
      }
      const list = jlink.units.map(un => ({ id: un.id, title: un.title, grammar: un.grammar.length, words: un.words.length, practice: un.practice.length }));
      return ok(res, { units: authed ? list : list.filter(un => un.id === TRIAL_JL), trial: !authed });
    }
    // —— 分级阅读：级别列表 / 单篇（未授权 = 体验模式，仅放行第 1 篇）——
    if (u === '/api/graded-reading' && req.method === 'GET') {
      const user = uidOf(req.headers['authorization'] || '');
      if (!user) return err(res, 401, '未登录或登录已失效，请重新登录');
      if (!deviceAllowed(user, dev)) return err(res, 403, '当前设备未授权，请重新登录');
      if (user.expiry && Number(user.expiry) <= Date.now()) return err(res, 403, '授权已过期，请联系管理员续费或重新激活');
      const authed = modAuthed(user, 'primary');
      const aid = q.article;
      if (aid) {
        let art = null;
        for (const lv of gread.levels) {
          const f = lv.articles.find(x => x.id === aid);
          if (f) { art = f; break; }
        }
        if (!art) return err(res, 404, '文章不存在');
        if (!authed && aid !== TRIAL_RD) return err(res, 403, '体验模式仅可阅读 ' + TRIAL_RD + '，输入授权码或联系管理员解锁全部文章');
        return ok(res, art);
      }
      const list = gread.levels.map(lv => ({ id: lv.id, name: lv.name, desc: lv.desc, articles: lv.articles.map(a => ({ id: a.id, title: a.title, words: (a.text || '').split(' ').length })) }));
      const slim = list.map(lv => ({ ...lv, articles: lv.articles.filter(a => a.id === TRIAL_RD) })).filter(lv => lv.articles.length > 0);
      return ok(res, { levels: authed ? list : slim, trial: !authed });
    }
    // —— KET / PET 备考包：词组分册 / 模拟卷（未授权 = 体验模式，仅放行第 1 组/第 1 卷）——
    if (u === '/api/ket-words' || u === '/api/pet-words' || u === '/api/ket-exam' || u === '/api/pet-exam') {
      const user = uidOf(req.headers['authorization'] || '');
      if (!user) return err(res, 401, '未登录或登录已失效，请重新登录');
      if (!deviceAllowed(user, dev)) return err(res, 403, '当前设备未授权，请重新登录');
      if (user.expiry && Number(user.expiry) <= Date.now()) return err(res, 403, '授权已过期，请联系管理员续费或重新激活');
      const authed = modAuthed(user, 'primary');
      const isWords = u.indexOf('words') > -1;
      const isKET = u.indexOf('ket') > -1;
      const data = isWords ? (isKET ? kw : pw) : (isKET ? kx : px);
      const trial = isWords ? (isKET ? TRIAL_KW : TRIAL_PW) : (isKET ? TRIAL_KX : TRIAL_PX);
      if (isWords) {
        const gid = q.group;
        if (gid) {
          const g = data.groups.find(x => x.id === gid);
          if (!g) return err(res, 404, '主题不存在');
          if (!authed && gid !== trial) return err(res, 403, '体验模式仅可学习第 1 组，输入授权码或联系管理员解锁全部主题');
          return ok(res, g);
        }
        const list = data.groups.map(g => ({ id: g.id, title: g.title, count: g.count }));
        return ok(res, { level: data.level, name: data.name, groups: authed ? list : list.filter(g => g.id === trial), trial: !authed });
      } else {
        const vid = q.vol;
        if (vid) {
          const v = data.volumes.find(x => x.id === vid);
          if (!v) return err(res, 404, '试卷不存在');
          if (!authed && vid !== trial) return err(res, 403, '体验模式仅可练习第 1 套，输入授权码或联系管理员解锁全部模拟卷');
          return ok(res, v);
        }
        const list = data.volumes.map(v => ({ id: v.id, title: v.title, topic: v.topic, count: v.questions.length }));
        return ok(res, { level: data.level, name: data.name, volumes: authed ? list : list.filter(v => v.id === trial), trial: !authed });
      }
    }
    // —— 高考听说 Part B：卷列表 / 单卷（未授权 = 体验模式，仅放行 gkb01）——
    if (u === '/api/gk/volumes' && req.method === 'GET') {
      const user = uidOf(req.headers['authorization'] || '');
      if (!user) return err(res, 401, '未登录或登录已失效，请重新登录');
      if (!deviceAllowed(user, dev)) return err(res, 403, '当前设备未授权，请重新登录');
      if (user.expiry && Number(user.expiry) <= Date.now()) return err(res, 403, '授权已过期，请联系管理员续费或重新激活');
      const authed = modAuthed(user, 'gk');
      const sets = gk.sets.map(s => ({ id: s.id, title: s.title, topic: s.topic }));
      return ok(res, { sets: authed ? sets : sets.filter(s => s.id === TRIAL_GK), trial: !authed });
    }
    if (u === '/api/gk/quiz' && req.method === 'GET') {
      const user = uidOf(req.headers['authorization'] || '');
      if (!user) return err(res, 401, '未登录或登录已失效，请重新登录');
      if (!deviceAllowed(user, dev)) return err(res, 403, '当前设备未授权，请重新登录');
      if (user.expiry && Number(user.expiry) <= Date.now()) return err(res, 403, '授权已过期，请联系管理员续费或重新激活');
      const authed = modAuthed(user, 'gk');
      const s = gk.sets.find(x => x.id === q.set);
      if (!s) return err(res, 404, '试卷不存在');
      if (!authed && s.id !== TRIAL_GK) return err(res, 403, '体验模式仅可练习 gkb01，输入授权码或联系管理员解锁全部试卷');
      return ok(res, s);
    }
    return err(res, 404, '接口不存在');
  }
  staticFile(res, u);
});

srv.listen(PORT, () => console.log('szgaokao-web 已启动: http://localhost:' + PORT + '  (每账号设备上限=' + MAX_DEVICES + ')'));
