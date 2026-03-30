import os
import sys
import django

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from apps.users.models import User
from apps.notifications.models import NotificationPreferences
from apps.core.thread_local import set_current_country

def verify_admins():
    checks = [
        {'username': 'jdiaz.pe', 'db': 'default_pe', 'country': 'PE'},
        {'username': 'jdiaz.co', 'db': 'default_co', 'country': 'CO'}
    ]
    
    print("=" * 60)
    print("   VERIFYING TENANT ADMINISTRATORS")
    print("=" * 60)
    
    for check in checks:
        username = check['username']
        db_alias = check['db']
        country = check['country']
        
        print(f"\n[VERIFYING] {db_alias} ({country})")
        set_current_country(country)
        
        try:
            # Check User
            user = User.objects.using(db_alias).filter(username=username).first()
            if user:
                print(f"   [OK] User '{username}' found. ID: {user.id}, Role: {user.role}, Staff: {user.is_staff}")
                
                # Check Preferences
                pref = NotificationPreferences.objects.using(db_alias).filter(user=user).first()
                if pref:
                    print(f"   [OK] NotificationPreferences found for '{username}'")
                else:
                    print(f"   [MISSING] NotificationPreferences NOT found for '{username}'. Creating now...")
                    NotificationPreferences.objects.using(db_alias).create(user=user)
                    print(f"   [FIXED] NotificationPreferences created for '{username}'")
            else:
                print(f"   [MISSING] User '{username}' NOT found in {db_alias}")
        except Exception as e:
            print(f"   [ERROR] Verification failed for {db_alias}: {e}")

    print("\n" + "=" * 60)
    print("   VERIFICATION COMPLETED!")
    print("=" * 60)

if __name__ == '__main__':
    verify_admins()
