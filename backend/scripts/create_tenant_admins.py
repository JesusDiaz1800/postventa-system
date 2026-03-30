import os
import sys
import django

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from apps.users.models import User
from apps.core.thread_local import set_current_country

def create_admins():
    admins = [
        {
            'username': 'jdiaz.pe',
            'email': 'jdiaz.pe@example.com',
            'db': 'default_pe',
            'country': 'PE'
        },
        {
            'username': 'jdiaz.co',
            'email': 'jdiaz.co@example.com',
            'db': 'default_co',
            'country': 'CO'
        }
    ]
    
    password = 'adminJDR'
    
    print("=" * 60)
    print("   CREATING TENANT ADMINISTRATORS")
    print("=" * 60)
    
    for admin in admins:
        username = admin['username']
        email = admin['email']
        db_alias = admin['db']
        country = admin['country']
        
        print(f"\n[TARGET] Database: {db_alias} ({country}) (User: {username})")
        
        try:
            # Set thread-local context for DynamicTenantRouter
            set_current_country(country)
            
            # Check if user already exists in this DB
            if User.objects.using(db_alias).filter(username=username).exists():
                print(f"   [SKIP] User '{username}' already exists in {db_alias}")
            else:
                # Create superuser
                user = User.objects.db_manager(db_alias).create_superuser(
                    username=username,
                    email=email,
                    password=password,
                    role='admin'
                )
                print(f"   [SUCCESS] Created superuser '{username}' in {db_alias}")
        except Exception as e:
            print(f"   [ERROR] Failed to create user in {db_alias}: {e}")

    print("\n" + "=" * 60)
    print("   PROCESS COMPLETED!")
    print("=" * 60)

if __name__ == '__main__':
    create_admins()
