import os
import django
import sys

# Setup Django
sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from django.db import connections

def verify_new_tech():
    db_alias = 'sap_db_co'
    print(f"Checking for technicians in {db_alias}...")
    
    try:
        connection = connections[db_alias]
        with connection.cursor() as cursor:
            # Query standard columns we know exist
            cursor.execute("SELECT empID, firstName, lastName, Active FROM OHEM")
            rows = cursor.fetchall()
            print(f"Total employees found: {len(rows)}")
            for row in rows:
                print(f" - ID: {row[0]}, Name: {row[1]} {row[2]}, Active: {row[3]}")
            
            if len(rows) > 0:
                print(f"\nSUCCESS: Found technician with ID {rows[0][0]}")
                return rows[0][0]
    except Exception as e:
        print(f"ERROR: {e}")
    return None

if __name__ == "__main__":
    verify_new_tech()
