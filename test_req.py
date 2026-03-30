import urllib.request
import json
req = urllib.request.Request(
    'http://127.0.0.1:8000/api/auth/login/',
    data=b'{"username":"jdiaz","password":"adminJDR"}',
    headers={'Content-Type':'application/json'}
)
try:
    print(urllib.request.urlopen(req).read().decode())
except Exception as e:
    print(e.read().decode())
