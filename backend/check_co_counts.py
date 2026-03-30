import os
import django
import sys

# Setup Django
sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from django.db import connections

def check_counts():
    db_alias = 'sap_db_co'
    print(f"Checking counts in {db_alias}...")
    
    try:
        connection = connections[db_alias]
        with connection.cursor() as cursor:
            # Check OHEM (Employees)
            cursor.execute("SELECT COUNT(*) FROM OHEM")
            ohem_count = cursor.fetchone()[0]
            print(f"Total rows in OHEM: {ohem_count}")
            
            # Check OSCL (Service Calls)
            cursor.execute("SELECT COUNT(*) FROM OSCL")
            oscl_count = cursor.fetchone()[0]
            print(f"Total rows in OSCL: {oscl_count}")
            
            if oscl_count > 0:
                print("\nLast 5 Service Calls (DocNum, Customer, Technician ID):")
                cursor.execute("SELECT TOP 5 DocNum, customer, technician FROM OSCL ORDER BY DocNum DESC")
                for row in cursor.fetchall():
                    print(row)
            
            # Check OCRD (Customers) just to be sure we have data at all
            cursor.execute("SELECT COUNT(*) FROM OCRD")
            ocrd_count = cursor.fetchone()[0]
            print(f"\nTotal rows in OCRD: {ocrd_count}")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    check_counts()
