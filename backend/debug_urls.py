import os
import sys
import django
from django.urls import resolve, reverse, Resolver404

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

test_urls = [
    '/api/documents/attachments/incident/20261/',
    '/api/documents/attachments/v2/incident/20261/',
    '/api/documents/incident-attachments/20261/',
    '/api/documents/incident/20261/documents/',
]

print("--- Testing URL Resolution ---")
for url in test_urls:
    try:
        match = resolve(url)
        print(f"OK: {url} -> {match.func.__name__}")
        print(f"   Name: {match.url_name}, Kwargs: {match.kwargs}")
    except Resolver404:
        print(f"FAIL: {url} -> NOT FOUND")
    except Exception as e:
        print(f"ERROR: {url} -> {str(e)}")

print("\n--- Testing URL Reversing ---")
names = [
    'list-attachments-by-incident',
    'list-attachments-by-incident-v2',
    'list_incident_attachments',
    'list_incident_documents',
]

for name in names:
    try:
        url = reverse(name, kwargs={'incident_id': 20261})
        print(f"OK: {name} -> {url}")
    except Exception as e:
        print(f"FAIL: {name} -> {str(e)}")
