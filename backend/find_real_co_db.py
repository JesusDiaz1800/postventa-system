import os
import django
import sys

# Setup Django
sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from django.db import connections

def list_dbs_and_check():
    db_alias = 'sap_db_co'
    print(f"Connecting via {db_alias}...")
    
    try:
        connection = connections[db_alias]
        with connection.cursor() as cursor:
            # 1. List all POL databases
            print("\nSearching for POL databases:")
            cursor.execute("SELECT name FROM sys.databases WHERE name LIKE '%POL%'")
            dbs = [row[0] for row in cursor.fetchall()]
            for db in dbs:
                print(f" - {db}")
            
            # 2. For each relevant DB, check OHEM and OSCL count
            for db in dbs:
                print(f"\n--- Checking DB: {db} ---")
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM [{db}].dbo.OHEM")
                    ohem = cursor.fetchone()[0]
                    cursor.execute(f"SELECT COUNT(*) FROM [{db}].dbo.OSCL")
                    oscl = cursor.fetchone()[0]
                    cursor.execute(f"SELECT COUNT(*) FROM [{db}].dbo.OCRD")
                    ocrd = cursor.fetchone()[0]
                    print(f"Employees (OHEM): {ohem}")
                    print(f"Service Calls (OSCL): {oscl}")
                    print(f"Customers (OCRD): {ocrd}")
                except Exception as e:
                    print(f"Error querying {db}: {e}")

    except Exception as e:
        print(f"Root ERROR: {e}")

if __name__ == "__main__":
    list_dbs_and_check()
