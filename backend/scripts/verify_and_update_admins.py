import os
import sys
import django

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from apps.users.models import User
from apps.core.thread_local import set_current_country

def verify_and_update_admins():
    print("=" * 60)
    print("   VERIFYING AND UPDATING TENANT ADMINS")
    print("=" * 60)

    admins = [
        {
            'username': 'jdiaz.pe',
            'email': 'jdiaz.pe@example.com',
            'db': 'default_pe',
            'country': 'PE',
            'password': 'adminJDR'
        },
        {
            'username': 'jdiaz.co',
            'email': 'jdiaz.co@example.com',
            'db': 'default_co',
            'country': 'CO',
            'password': 'adminJDR'
        }
    ]

    for admin in admins:
        username = admin['username']
        country = admin['country']
        db_alias = admin['db']
        password = admin['password']

        print(f"\n[TARGET] User: {username} | Country: {country} | DB: {db_alias}")
        
        try:
            # Set thread-local context
            set_current_country(country)
            
            # Try to get user
            user = None
            if User.objects.using(db_alias).filter(username=username).exists():
                user = User.objects.using(db_alias).get(username=username)
                print(f"   [FOUND] User exists.")
            else:
                print(f"   [NOT FOUND] Creating user...")
                user = User.objects.db_manager(db_alias).create_superuser(
                    username=username,
                    email=admin['email'],
                    password=password,
                    role='admin'
                )
                print(f"   [CREATED] User created successfully.")

            # Force update password
            user.set_password(password)
            user.save(using=db_alias)
            print(f"   [SUCCESS] Password set to '{password}'")
            
        except Exception as e:
            print(f"   [ERROR] Failed to process {username}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print("   PROCESS COMPLETED")
    print("=" * 60)

if __name__ == '__main__':
    verify_and_update_admins()
