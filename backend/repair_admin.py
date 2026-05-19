import os
import sys
import django

# Setup Django
sys.path.append(r'C:\Users\jdiaz\Desktop\sertec-system\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from apps.users.models import User

def repair():
    try:
        u = User.objects.filter(username='jdiaz').first()
        if u:
            u.role = 'admin'
            u.is_superuser = True
            u.is_staff = True
            u.permissions_override = {}
            u.pages_override = []
            u.save()
            print(f"User {u.username} (ID: {u.id}) REPAIRED SUCCESSFULLY")
        else:
            print("User jdiaz not found")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    repair()
