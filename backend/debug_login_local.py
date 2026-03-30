import os
import sys
import traceback

# MATCHING manage.py LOGIC
# manage.py is in backend/
# It likely doesn't mess with sys.path much, assume standard python behavior.
# But we are running a script from backend/ folder.

# Use absolute paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Add the backend directory itself to sys.path so 'postventa_system' (which is a folder inside backend)
# can be imported as a top-level package.
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

print(f"DEBUG: sys.path: {sys.path}")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')

try:
    from django.core.management import execute_from_command_line
    import django
    django.setup()
    print("DEBUG: Django setup successful.")
except Exception as e:
    print(f"CRITICAL: Django setup failed: {e}")
    traceback.print_exc()
    sys.exit(1)

from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import connection

User = get_user_model()

def test_login_logic():
    print("--- STARTING LOGIN DEBUG ---")
    
    # 0. Check DB connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("DB Connection: OK")
    except Exception as e:
        print(f"CRITICAL DB ERROR: {e}")
        traceback.print_exc()
        return

    # 1. User Check
    username = 'jdiaz'
    user = User.objects.filter(username=username).first()
    if not user:
        user = User.objects.filter(role='admin').first()
        if user:
            print(f"Using admin user: {user.username}")
        else:
            print("No suitable user found.")
            return
    else:
        print(f"User found: {username}")

    # 2. Simulate Login View Logic
    try:
        from django.utils import timezone
        print("Attempting last_login update...")
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        print("last_login update: OK")
    except Exception as e:
        print(f"last_login ERROR: {e}")
        traceback.print_exc()

    try:
        print("Attempting JWT generation...")
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)
        print("JWT generation: OK")
    except Exception as e:
        print(f"JWT ERROR: {e}")
        traceback.print_exc()

    try:
        from apps.audit.models import AuditLogManager
        print("Attempting Audit Log...")
        AuditLogManager.log_action(
            user=user, 
            action='user_login', 
            description='DEBUG', 
            ip_address='127.0.0.1'
        )
        print("Audit Log: OK")
    except Exception as e:
        print(f"AUDIT ERROR: {e}")
        traceback.print_exc()

    print("--- END DEBUG ---")

if __name__ == '__main__':
    test_login_logic()
