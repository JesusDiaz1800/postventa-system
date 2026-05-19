
import os
import django
from django.db import connection

import sys
sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from django.apps import apps

def check_obsolete():
    # 1. Get Real DB Tables
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sys.tables WHERE type='U'")
        db_tables = {row[0] for row in cursor.fetchall()}

    # 2. Get Django Tables
    django_tables = set()
    for model in apps.get_models():
        django_tables.add(model._meta.db_table)
    
    # Add system tables that might not be in get_models() explicitly sometimes? 
    # Usually standard django contrib models cover these (auth_user, django_session, etc)
    # But django_migrations is special.
    django_tables.add('django_migrations')
    
    # 3. Find Difference
    orphans = db_tables - django_tables
    
    print(f"Total DB Tables: {len(db_tables)}")
    print(f"Total Django Models: {len(django_tables)}")
    print(f"Orphan Tables (Candidates for deletion): {len(orphans)}")
    print("-" * 30)
    for t in sorted(orphans):
        print(t)

if __name__ == '__main__':
    check_obsolete()
