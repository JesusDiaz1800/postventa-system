import os
import sys
import django

# Add the backend directory to sys.path
backend_dir = r"c:\Users\jdiaz\Desktop\postventa-system\backend"
sys.path.append(backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from django.db import connections
from apps.core.thread_local import set_current_country

def list_tables():
    set_current_country('PE')
    print("Buscando nombres de tablas en PE...")
    try:
        with connections['sap_db_pe'].cursor() as cursor:
            cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME LIKE 'OSC%' OR TABLE_NAME LIKE '%PRBL%'")
            for row in cursor.fetchall():
                print(f"Table: {row[0]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_tables()
