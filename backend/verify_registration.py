import json
import urllib.request

req = urllib.request.Request(
    'http://127.0.0.1:8000/users/register',
    data=json.dumps({'username': 'testuser2', 'email': 'test2@example.com', 'password': 'secret123'}).encode(),
    headers={'Content-Type': 'application/json'},
    method='POST',
)

try:
    with urllib.request.urlopen(req) as resp:
        print(resp.status)
        print(resp.read().decode())
except Exception as e:
    print(type(e).__name__, e)
    if hasattr(e, 'read'):
        print(e.read().decode())
