import os
import django
import sys

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from django.db import connection
from apps.users.models import User

def audit_db():
    print("--- DB AUDIT START ---")
    with connection.cursor() as cursor:
        # 1. List all tables
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        tables = [t[0] for t in cursor.fetchall()]
        print(f"Total tables: {len(tables)}")
        print(f"All tables: {tables}")

        # 2. Check 'users' table columns
        if 'users' in tables:
            print("\nColumns in 'users' table:")
            cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'users'")
            cols = [c[0] for c in cursor.fetchall()]
            print(cols)
            for target in ['sap_user', 'sap_password']:
                if target in cols:
                    print(f"Found: {target}")
                else:
                    print(f"MISSING: {target}")
        
        # 3. Check 'users_user' if it exists
        if 'users_user' in tables:
            print("\nColumns in 'users_user' table:")
            cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'users_user'")
            print([c[0] for c in cursor.fetchall()])

    print("\n--- Model Check ---")
    print(f"User Model db_table: {User._meta.db_table}")
    
    try:
        u_count = User.objects.count()
        print(f"User count via ORM: {u_count}")
    except Exception as e:
        print(f"ORM User Query Failed: {e}")

if __name__ == "__main__":
    audit_db()
