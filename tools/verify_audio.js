// 验证：API 返回 audio 路径 + audioText，且静态 MP3 以 audio/mpeg 返回
const http = require('http');
const PORT = process.env.PORT || 3000;
function req(method, path, body, token) {
  return new Promise((resolve, reject) => {
    const data = body ? JSON.stringify(body) : null;
    const r = http.request({ host: '127.0.0.1', port: PORT, path, method, headers: Object.assign({ 'Content-Type': 'application/json' }, token ? { authorization: token } : {}, data ? { 'Content-Length': Buffer.byteLength(data) } : {}) }, res => {
      let d = ''; res.on('data', c => d += c); res.on('end', () => { try { resolve({ code: res.statusCode, ct: res.headers['content-type'], len: res.headers['content-length'], json: JSON.parse(d || '{}') }); } catch (e) { resolve({ code: res.statusCode, ct: res.headers['content-type'], len: res.headers['content-length'], raw: d }); } });
    });
    r.on('error', reject); if (data) r.write(data); r.end();
  });
}
(async () => {
  const uname = 'audiocheck' + Date.now();
  let r = await req('POST', '/api/register', { username: uname, password: 'secret123' });
  const token = r.json.token;
  r = await req('GET', '/api/admin/codes?secret=admin123');
  const code = r.json.codes.find(c => !c.used).code;
  await req('POST', '/api/activate', { code }, token);
  r = await req('GET', '/api/quiz?vol=v01', null, token);
  const A1 = r.json.parts.find(p => p.part === 'A').questions[0];
  const D1 = r.json.parts.find(p => p.part === 'D').questions[0];
  console.log('A1.audio =', A1.audio, '| audioText =', A1.audioText);
  console.log('D1.audio =', D1.audio, '| 是路径?', A1.audio.startsWith('/audio/'));
  // 静态拉取一个 mp3
  r = await req('GET', A1.audio);
  console.log('GET', A1.audio, '->', r.code, '| content-type:', r.ct, '| bytes:', r.len);
  r = await req('GET', D1.audio);
  console.log('GET', D1.audio, '->', r.code, '| content-type:', r.ct, '| bytes:', r.len);
  const okAll = A1.audio.startsWith('/audio/') && D1.audio.startsWith('/audio/') && r.ct === 'audio/mpeg';
  console.log('\n=== 音频验证', okAll ? '通过 ✅' : '失败 ❌', '===');
})().catch(e => { console.error('ERR', e); process.exit(1); });
