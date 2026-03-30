import os
import django
import sys
from django.db import connections

# Setup Django
sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

def list_oscl_columns():
    db_alias = 'sap_db_pe'
    print(f"Listing columns for OSCL in {db_alias}...")
    
    try:
        connection = connections[db_alias]
        with connection.cursor() as cursor:
            # Query column names
            query = """
                SELECT COLUMN_NAME
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = 'OSCL'
                ORDER BY COLUMN_NAME
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            print(f"Columns found: {len(rows)}")
            for row in rows:
                print(f" - {row[0]}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    list_oscl_columns()
