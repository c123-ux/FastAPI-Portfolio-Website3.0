import urllib.request, json

data = json.dumps({'username': 'admin', 'password': 'admin123'}).encode()
req = urllib.request.Request(
    'http://127.0.0.1:8000/api/login',
    data=data,
    headers={'Content-Type': 'application/json'}
)

try:
    r = urllib.request.urlopen(req)
    print('Success:', r.status, r.read().decode())
except urllib.error.HTTPError as e:
    print('Error:', e.code, e.reason)
    print(e.read().decode())
except Exception as e:
    print('Exception:', str(e))
