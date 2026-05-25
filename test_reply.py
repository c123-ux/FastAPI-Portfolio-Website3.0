import urllib.request, json

# 1. 登录获取 token
data = json.dumps({'username': 'admin', 'password': 'admin123'}).encode()
req = urllib.request.Request(
    'http://127.0.0.1:8000/api/login',
    data=data,
    headers={'Content-Type': 'application/json'}
)
r = urllib.request.urlopen(req)
token = json.loads(r.read().decode())['access_token']
print('✅ 登录成功, Token:', token[:30] + '...')

# 2. 回复留言
reply_data = json.dumps({'reply': '感谢您的留言！我们会尽快与您联系。'}).encode()
req2 = urllib.request.Request(
    'http://127.0.0.1:8000/api/contacts/1/reply',
    data=reply_data,
    headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
)
r2 = urllib.request.urlopen(req2)
print('✅ 回复结果:', json.loads(r2.read().decode()))

# 3. 获取统计
r3 = urllib.request.urlopen('http://127.0.0.1:8000/api/stats')
print('✅ 统计:', json.dumps(json.loads(r3.read().decode()), ensure_ascii=False, indent=2))

print('\n🎉 所有功能测试通过！')
