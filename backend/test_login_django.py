import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
import django
try:
    django.setup()
    from django.test import Client
    c = Client()
    print("Testing login...")
    response = c.post('/api/auth/login/', {'username': 'jdiaz', 'password': 'adminJDR'}, content_type='application/json')
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.content.decode('utf-8')}")
except Exception as e:
    import traceback
    traceback.print_exc()
