
import os
import django
from django.conf import settings
from django.db import connection

# Setup Django environment manually
import sys
sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

def audit_db():
    with connection.cursor() as cursor:
        print("--- Tables in Database ---")
        cursor.execute("SELECT name FROM sys.tables ORDER BY name")
        tables = cursor.fetchall()
        for t in tables:
            print(t[0])
            
        print("\n--- Constraints (Potential Blockers) ---")
        cursor.execute("""
            SELECT 
                t.name AS TableName,
                c.name AS ColumnName,
                o.name AS ConstraintName
            FROM sys.objects o
            JOIN sys.parent_objects p ON o.parent_object_id = p.parent_object_id
            JOIN sys.tables t ON p.object_id = t.object_id
            JOIN sys.all_columns c ON c.column_id = o.parent_column_id AND c.object_id = t.object_id
            WHERE o.type_desc LIKE '%CONSTRAINT'
            ORDER BY t.name
        """)
        # This query might be simplistic, standard django inspectdb is also good.
        # Let's just rely on tables first.

if __name__ == '__main__':
    audit_db()
