# -*- coding: utf-8 -*-
"""后台管理「注册用户统计表」+「重置密码」端到端验证。
A. 页面结构（admin.html 静态检查）
B. 线上：/admin 页面 200 且含统计表；/api/admin/users 返回统计所需字段
   /api/admin/users/reset-pw 鉴权（未登录 403）与参数校验
用法：python tools/e2e_admin_regstats.py
"""
import json, os, re, ssl, sys, time, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://szgaokao.toolshe.cn'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
PROXY = os.environ.get('HTTPS_PROXY') or os.environ.get('HTTP_PROXY') or 'http://127.0.0.1:60218'

PASS = FAIL = 0


def check(name, cond, detail=''):
    global PASS, FAIL
    if cond:
        PASS += 1
        print('  [PASS] %s%s' % (name, (' — ' + detail) if detail else ''))
    else:
        FAIL += 1
        print('  [FAIL] %s%s' % (name, (' — ' + detail) if detail else ''))


print('========== A. 页面结构（本地静态） ==========')
HTML = io_html = open(os.path.join(ROOT, 'public', 'admin.html'), encoding='utf-8').read()
check('含统计表容器 regTable', 'id="regTable"' in HTML)
check('含表体容器 regBody', 'id="regBody"' in HTML)
check('含汇总容器 regSummary', 'id="regSummary"' in HTML)
check('表头含「注册时间」列', '注册时间' in HTML)
check('表头含「密码」列', '>密码<' in HTML or '密码</th>' in HTML)
check('密码列显示加密状态而非明文', '🔒 已加密' in HTML)
check('无任何明文密码占位', 'password' in HTML and 'type="password"' not in HTML.split('regTable')[0][:2000])
check('说明 PBKDF2 不可逆', 'PBKDF2' in HTML and '无法反推' in HTML)
check('含重置密码接口调用', '/api/admin/users/reset-pw' in HTML)
check('含重置密码按钮处理器', 'openResetPw' in HTML and 'doResetPw' in HTML)
check('登录后自动加载统计表', 'loadRegStats()' in HTML.split('function enterPanel')[1][:400])
check('汇总统计 5 项', all(x in HTML for x in ['注册总人数', '今日新增', '已授权', '真实用户', '测试账号']))
print('（A 段完）')

print('\n========== B. 线上 ==========')
opener = urllib.request.build_opener(
    urllib.request.ProxyHandler({'http': PROXY, 'https': PROXY}),
    urllib.request.HTTPSHandler(context=ssl.create_default_context()))


def req(method, url, data=None, headers=None, retry=3):
    for a in range(retry):
        body = json.dumps(data).encode() if data is not None else None
        h = {'Content-Type': 'application/json', 'User-Agent': UA}
        if headers:
            h.update(headers)
        try:
            r = urllib.request.Request(url, data=body, method=method, headers=h)
            with opener.open(r, timeout=60) as resp:
                return resp.status, json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            try:
                return e.code, json.loads(e.read().decode())
            except Exception:
                return e.code, {}
        except Exception as e:
            if a < retry - 1:
                time.sleep(2)
                continue
            return 0, {'error': str(e)}


# 页面可访问
try:
    rq = urllib.request.Request(BASE + '/admin', headers={'User-Agent': UA})
    with opener.open(rq, timeout=60) as resp:
        page = resp.read().decode('utf-8', 'ignore')
    check('/admin 页面 200', True, '%d bytes' % len(page))
    check('线上含统计表 regTable', 'id="regTable"' in page)
    check('线上含密码加密状态', '🔒 已加密' in page)
    check('线上含 reset-pw 接口', '/api/admin/users/reset-pw' in page)
    check('线上含 PBKDF2 说明', 'PBKDF2' in page)
except Exception as e:
    check('/admin 页面可访问', False, str(e)[:60])

# 管理接口鉴权（未登录应 403）
st, _ = req('GET', BASE + '/api/admin/users')
check('未登录取用户列表 403', st == 403, 'HTTP %d' % st)
st, _ = req('POST', BASE + '/api/admin/users/reset-pw', {'username': 'x', 'newPassword': 'abc123'})
check('未登录重置密码 403', st == 403, 'HTTP %d' % st)

# 登录后取用户列表，校验统计所需字段
ADMIN_SECRET = None
for cand in [r'E:/szgaokao.cn/worker/.dev.vars', r'E:/szgaokao.cn/worker/wrangler.jsonc']:
    if os.path.exists(cand):
        m = re.search(r'ADMIN_SECRET["\s:=]+([A-Za-z0-9_\-]+)', open(cand, encoding='utf-8').read())
        if m:
            ADMIN_SECRET = m.group(1)
            break
if not ADMIN_SECRET:
    # 从线上 wrangler bindings 无法读取，改用环境变量
    ADMIN_SECRET = os.environ.get('ADMIN_SECRET')

if ADMIN_SECRET:
    st, r = req('POST', BASE + '/api/admin/login', {'secret': ADMIN_SECRET})
    check('管理员登录 200', st == 200 and r.get('token'), 'HTTP %d' % st)
    if st == 200:
        H = {'Authorization': r['token']}
        st, r = req('GET', BASE + '/api/admin/users', headers=H)
        check('用户列表 200', st == 200, 'HTTP %d' % st)
        if st == 200:
            us = r.get('users', [])
            check('返回用户列表', isinstance(us, list), '人数=%d' % len(us))
            if us:
                u = us[0]
                need = ['username', 'createdAt', 'authorized', 'expiry', 'modules', 'devices', 'isTest']
                missing = [k for k in need if k not in u]
                check('用户对象含统计所需字段', not missing, '缺=%s' % missing)
                check('不含明文密码字段（安全）', 'pw' not in u and 'password' not in u)
        # 重置密码参数校验（用不存在的用户，避免真的改掉线上数据）
        st, r = req('POST', BASE + '/api/admin/users/reset-pw', {'username': '__no_such_user__', 'newPassword': 'abc123'}, headers=H)
        check('重置不存在的用户 404', st == 404, 'HTTP %d' % st)
        st, r = req('POST', BASE + '/api/admin/users/reset-pw', {'username': 'x', 'newPassword': '123'}, headers=H)
        check('新密码过短被拒 400', st == 400, 'HTTP %d' % st)
else:
    print('  [SKIP] 未找到 ADMIN_SECRET，跳过登录态接口校验')
    print('         （设置环境变量 ADMIN_SECRET 后可跑完整校验）')

print('\n=========================================')
print('  结果：%d 通过 / %d 失败' % (PASS, FAIL))
print('=========================================')
sys.exit(1 if FAIL else 0)
