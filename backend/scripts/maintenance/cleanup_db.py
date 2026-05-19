
import os
import django
from django.db import connection

import sys
sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from django.apps import apps

def cleanup_db():
    print("--- Starting DB Cleanup ---")
    
    # 1. Get Real DB Tables
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sys.tables WHERE type='U'")
        db_tables = {row[0] for row in cursor.fetchall()}

    # 2. Get Django Tables
    django_tables = set()
    for model in apps.get_models():
        django_tables.add(model._meta.db_table)
    
    # Add system/special tables
    django_tables.add('django_migrations')
    django_tables.add('django_content_type')
    django_tables.add('django_admin_log')
    django_tables.add('django_session')
    
    # 3. Find Difference
    orphans = db_tables - django_tables
    
    if not orphans:
        print("No orphan tables found. Database is clean.")
        return

    print(f"Found {len(orphans)} orphan tables:")
    for t in sorted(orphans):
        print(f" - {t}")
        
    # 4. Drop them
    with connection.cursor() as cursor:
        # Disable constraints? SQL Server way:
        # cursor.execute("EXEC sp_msforeachtable \"ALTER TABLE ? NOCHECK CONSTRAINT all\"")
        
        # We try to drop. If dependency exists, we might need topological sort or just force.
        # Simple loop for now.
        for t in sorted(orphans):
            try:
                print(f"Dropping {t}...", end='')
                cursor.execute(f"DROP TABLE [{t}]")
                print(" OK")
            except Exception as e:
                print(f" FAILED: {e}")

    print("--- Cleanup Complete ---")

if __name__ == '__main__':
    cleanup_db()
