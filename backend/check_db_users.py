
import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    # try another common path if it fails
    os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.core.settings'

try:
    django.setup()
except Exception as e:
    print(f"Error setting up django with postventa_system.settings: {e}")
    os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.core.settings'
    django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()
from django.db import connections

def check_users():
    print("--- Database User Check ---")
    databases = settings.DATABASES.keys()
    print(f"Configured databases: {list(databases)}")
    
    for db in databases:
        try:
            count = User.objects.using(db).filter(username='jdiaz').count()
            users = User.objects.using(db).filter(username='jdiaz').values('username', 'is_active', 'role')
            print(f"DB '{db}': found {count} user(s) named 'jdiaz'")
            for u in users:
                print(f"  - {u}")
        except Exception as e:
            print(f"DB '{db}': error checking users: {e}")

if __name__ == "__main__":
    check_users()
