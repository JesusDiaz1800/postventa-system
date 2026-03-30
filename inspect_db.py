
import os
import sys
import django

# Add backend to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from django.db import connection

def inspect_columns():
    with connection.cursor() as cursor:
        # Get column info for incidents table in SQL Server with schema
        cursor.execute("""
            SELECT 
                table_schema,
                column_name, 
                is_nullable, 
                data_type
            FROM information_schema.columns
            WHERE table_name = 'incidents'
            ORDER BY table_schema, column_name
        """)
        columns = cursor.fetchall()
        
        print(f"{'Schema':<10} {'Column Name':<30} {'Is Nullable':<15} {'Data Type':<15}")
        print("-" * 80)
        for col in columns:
            print(f"{col[0]:<10} {col[1]:<30} {col[2]:<15} {col[3]}")

if __name__ == "__main__":
    inspect_columns()
