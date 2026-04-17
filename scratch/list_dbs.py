import os
import sys
import django

sys.path.append('backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from django.db import connections

def list_databases():
    try:
        # Use the Chile connection (sap_db) since we know ccalidad works there
        conn = connections['sap_db']
        with conn.cursor() as cursor:
            cursor.execute("SELECT name FROM sys.databases WHERE state = 0")
            rows = cursor.fetchall()
            print("--- BASES DE DATOS DISPONIBLES EN EL SERVIDOR ---")
            for row in rows:
                print(f"- {row[0]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_databases()
