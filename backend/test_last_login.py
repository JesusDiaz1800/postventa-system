
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from apps.users.models import User
from django.contrib.auth.models import update_last_login
from django.utils import timezone

def test_update():
    try:
        user = User.objects.get(username='jdiaz')
        print(f"Before update: {user.last_login}")
        
        # Manually update
        update_last_login(None, user=user)
        
        # Re-fetch
        user.refresh_from_db()
        print(f"After update: {user.last_login}")
        
    except User.DoesNotExist:
        print("User jdiaz not found")

if __name__ == '__main__':
    test_update()
