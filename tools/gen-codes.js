// 管理员工具：生成授权码并写入 data/codes.json
// 用法：node tools/gen-codes.js 10 [annual|permanent]
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const DATA = path.join(__dirname, '..', 'data');
fs.mkdirSync(DATA, { recursive: true });
const n = parseInt(process.argv[2] || '10', 10);
const plan = process.argv[3] || 'permanent';
const codes = (() => { try { return JSON.parse(fs.readFileSync(path.join(DATA, 'codes.json'), 'utf8')); } catch (e) { return []; } })();
const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
for (let i = 0; i < n; i++) {
  let c = '';
  for (let j = 0; j < 8; j++) c += chars[crypto.randomBytes(1)[0] % chars.length];
  codes.push({ code: c, plan, maxActs: 1, acts: 0, usedBy: null, usedAt: null, createdAt: Date.now() });
}
fs.writeFileSync(path.join(DATA, 'codes.json'), JSON.stringify(codes, null, 2));
console.log('已生成 ' + n + ' 个授权码（plan=' + plan + '）：');
codes.slice(-n).forEach(c => console.log('  ' + c.code));
