import urllib.request, json

# 1. 获取验证码
r = urllib.request.urlopen('http://127.0.0.1:8000/api/captcha')
captcha = json.loads(r.read().decode())
print('验证码:', captcha)

# 2. 计算正确答案
parts = captcha['question'].split('=')
question = parts[0].strip()  # e.g. "8 - 3"
a, op, b = question.split()
a, b = int(a), int(b)
if op == '+':
    answer = str(a + b)
else:
    answer = str(a - b)
print('答案:', answer)

# 3. 提交表单
submit_data = json.dumps({
    'name': '测试用户',
    'email': 'test@test.com',
    'subject': '合作咨询',
    'message': '这是一条来自 API 测试的留言',
    'captcha_id': captcha['captcha_id'],
    'captcha_answer': answer
}).encode()

req2 = urllib.request.Request(
    'http://127.0.0.1:8000/api/contact',
    data=submit_data,
    headers={'Content-Type': 'application/json'}
)
r2 = urllib.request.urlopen(req2)
print('提交结果:', r2.status, r2.read().decode())

# 4. 获取所有留言
r3 = urllib.request.urlopen('http://127.0.0.1:8000/api/contacts')
result = json.loads(r3.read().decode())
print('留言总数:', result['count'])
for c in result['contacts'][:2]:
    print(f"  [{c['id']}] {c['name']}: {c['message'][:30]}...")

# 5. 获取统计
r4 = urllib.request.urlopen('http://127.0.0.1:8000/api/stats')
stats = json.loads(r4.read().decode())
print('统计数据:', json.dumps(stats, ensure_ascii=False, indent=2))
