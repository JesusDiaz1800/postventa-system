import os
import django
import sys

# Setup Django
sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from django.db import connections

def check_manual_call():
    db_alias = 'sap_db_co'
    print(f"Checking for manual service calls in {db_alias}...")
    
    try:
        connection = connections[db_alias]
        with connection.cursor() as cursor:
            # 1. Row count to see if anything was added
            cursor.execute("SELECT COUNT(*) FROM OSCL")
            count = cursor.fetchone()[0]
            print(f"Total service calls in OSCL: {count}")
            
            if count > 0:
                print("\nLast Service Calls (DocNum, Customer, Technician ID):")
                cursor.execute("SELECT TOP 5 DocNum, customer, technician FROM OSCL ORDER BY DocNum DESC")
                for row in cursor.fetchall():
                    print(f" - DocNum: {row[0]}, Customer: {row[1]}, Technician Code: {row[2]}")
            else:
                print("No service calls found. Did you create it in TSTPOLCOLOMBIA_2?")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    check_manual_call()
