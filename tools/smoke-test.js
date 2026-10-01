// 端到端冒烟测试：注册→登录→单会话踢人→设备绑定→激活(限次)→题库→管理员后台
// BASE 环境变量可指向公网（如 https://szgaokao.toolshe.cn）
const BASE = process.env.BASE || 'http://127.0.0.1:3000';
const RESOLVE_IP = process.env.RESOLVE_IP || '';  // 本地 DNS 滞后时可指定 CF 边缘 IP
const http = require(BASE.startsWith('https') ? 'https' : 'http');
const HOSTPORT = new URL(BASE);
function req(method, path, body, token, dev) {
  return new Promise((resolve, reject) => {
    const data = body ? JSON.stringify(body) : null;
    const headers = Object.assign({ 'Content-Type': 'application/json' },
      token ? { authorization: token } : {},
      dev ? { 'x-device': dev } : {},
      data ? { 'Content-Length': Buffer.byteLength(data) } : {});
    if (RESOLVE_IP) headers.Host = HOSTPORT.hostname;
    const r = http.request({
      host: RESOLVE_IP || HOSTPORT.hostname,
      port: HOSTPORT.port || (BASE.startsWith('https') ? 443 : 80),
      path, method, headers,
      ...(BASE.startsWith('https') ? { servername: HOSTPORT.hostname } : {})
    }, res => {
      let d = ''; res.on('data', c => d += c); res.on('end', () => { try { resolve({ code: res.statusCode, json: JSON.parse(d || '{}') }); } catch (e) { resolve({ code: res.statusCode, raw: d }); } });
    });
    r.on('error', reject); if (data) r.write(data); r.end();
  });
}
let PASS = 0, FAIL = 0;
function check(name, cond, detail) {
  if (cond) { PASS++; console.log('  ✓ ' + name + (detail ? '  ' + detail : '')); }
  else { FAIL++; console.log('  ✗ ' + name + (detail ? '  ' + detail : '')); }
}
(async () => {
  const uname = 'test' + Date.now();
  const pw = 'secret123';
  const D1 = 'dev-smoke-aaa1', D2 = 'dev-smoke-bbb2';
  let r;

  console.log('【1】注册 / 登录');
  r = await req('POST', '/api/register', { username: uname, password: pw }, null, D1);
  check('注册(设备D1)', r.code === 200 && r.json.token, 'devices=' + r.json.devices + '/' + r.json.maxDevices);
  const t1 = r.json.token;
  r = await req('POST', '/api/login', { username: uname, password: pw }, null, D1);
  check('登录(设备D1)', r.code === 200 && r.json.token);
  const t2 = r.json.token;

  console.log('【2】单会话踢人');
  r = await req('GET', '/api/me', null, t1, D1);
  check('旧令牌 t1 已被新登录踢掉', r.code === 401, '-> ' + r.code);

  console.log('【3】设备绑定');
  r = await req('GET', '/api/me', null, t2, D2);
  check('未绑定设备 D2 被拒', r.code === 403, '-> ' + r.code);
  r = await req('GET', '/api/me', null, t2, D1);
  check('已绑定设备 D1 通过', r.code === 200, 'devices=' + r.json.devices + '/' + r.json.maxDevices);
  r = await req('GET', '/api/volumes', null, t2, D1);
  check('未激活=体验模式(仅卷1)', r.code === 200 && r.json.trial === true && (r.json.volumes || []).length === 1 && r.json.volumes[0].id === 'v01');
  r = await req('GET', '/api/quiz?vol=v01', null, t2, D1);
  check('体验可练试卷01', r.code === 200);
  r = await req('GET', '/api/quiz?vol=v02', null, t2, D1);
  check('体验练卷2被拦', r.code === 403, r.json.error || '');

  console.log('【4】管理员后台');
  r = await req('POST', '/api/admin/login', { secret: 'wrong-secret' });
  check('错误密钥被拒', r.code === 403);
  r = await req('POST', '/api/admin/login', { secret: process.env.ADMIN_SECRET || 'admin123' });
  check('管理员登录', r.code === 200 && r.json.token);
  const AT = r.json.token;
  r = await req('GET', '/api/admin/users', null, AT);
  check('用户列表(带令牌)', r.code === 200 && r.json.users.some(u => u.username === uname));
  r = await req('GET', '/api/admin/users', null, t2);
  check('用户令牌不能访问管理接口', r.code === 403);

  console.log('【5】授权码限次 + 学期/自定义时长');
  r = await req('POST', '/api/admin/gen-codes', { count: 2, plan: 'semester', maxActs: 1 }, AT);
  check('网页生成 2 个学期码', r.code === 200 && r.json.codes.length === 2, 'days=' + r.json.days);
  check('学期时长 = 180 天', r.json.days === 180);
  r = await req('POST', '/api/admin/gen-codes', { count: 1, plan: 'custom', days: 90 }, AT);
  check('自定义 90 天码', r.code === 200 && r.json.days === 90, 'plan=' + r.json.plan);
  const c1 = r.json.codes[0] || 'NOCODE';
  const semCode = (await req('POST', '/api/admin/gen-codes', { count: 1, plan: 'semester' }, AT)).json.codes[0];
  r = await req('POST', '/api/activate', { code: semCode }, t2, D1);
  const durDays = r.json.expiry ? (r.json.expiry - Date.now()) / 864e5 : 0;
  check('激活成功且时长≈180天', r.code === 200 && r.json.authorized && Math.abs(durDays - 180) < 0.01, '实际时长=' + durDays.toFixed(1) + '天');
  r = await req('POST', '/api/activate', { code: semCode }, t2, D1);
  check('同一码再次激活被拒(限次)', r.code === 400);
  r = await req('GET', '/api/admin/codes', null, AT);
  const cc = r.json.codes.find(x => x.code === semCode);
  check('码状态 used/maxActs 正确', cc && cc.used === 1 && cc.maxActs === 1, `${semCode} ${cc.used}/${cc.maxActs}`);

  console.log('【6】授权后取题库');
  r = await req('GET', '/api/volumes', null, t2, D1);
  check('授权后全卷+非体验', r.code === 200 && r.json.trial === false && (r.json.volumes || []).length === 6, '卷数=' + (r.json.volumes || []).length);
  const vid = r.json.volumes[0].id;
  r = await req('GET', '/api/quiz?vol=' + vid, null, t2, D1);
  check('单卷题目', r.code === 200 && (r.json.parts || []).length > 0, 'parts=' + (r.json.parts || []).length);

  console.log('【7】管理员解绑/撤销');
  r = await req('POST', '/api/admin/users/unbind', { username: uname, device: D1 }, AT);
  check('管理员解绑 D1', r.code === 200);
  r = await req('GET', '/api/me', null, t2, D1);
  check('解绑后原设备被拒', r.code === 403);
  r = await req('POST', '/api/admin/users/revoke', { username: uname }, AT);
  check('撤销授权', r.code === 200);

  console.log('【8】后台直接授权（免授权码）');
  r = await req('POST', '/api/admin/users/grant', { username: uname, plan: 'semester' }, AT);
  check('后台授予学期授权', r.code === 200 && r.json.ok);
  r = await req('POST', '/api/login', { username: uname, password: pw }, null, D1);
  const t3 = r.json.token;
  check('解绑后重新登录(重绑设备)', r.code === 200 && r.json.token);
  r = await req('GET', '/api/me', null, t3, D1);
  const gd = r.json.expiry ? (r.json.expiry - Date.now()) / 864e5 : 0;
  check('授权生效且时长≈180天', r.code === 200 && r.json.authorized && Math.abs(gd - 180) < 0.01, '实际时长=' + gd.toFixed(1) + '天');
  r = await req('GET', '/api/volumes', null, t3, D1);
  check('授权后可拉题库', r.code === 200 && (r.json.volumes || []).length > 0);

  console.log('\n=== 结果: ' + PASS + ' 通过 / ' + FAIL + ' 失败 ' + (FAIL === 0 ? '，全部通过 ✓' : '，存在失败 ✗'));
  process.exit(FAIL === 0 ? 0 : 1);
})().catch(e => { console.error('TEST ERROR', e); process.exit(1); });
