import os
import django
import sys
from django.db import connections

# Setup Django
sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

def check_pe_techs():
    db_alias = 'sap_db_pe'
    print(f"Checking for technicians in {db_alias} with ANY role in HEM6...")
    
    try:
        connection = connections[db_alias]
        with connection.cursor() as cursor:
            # Query employees in HEM6
            query = """
                SELECT DISTINCT T0.empID, T1.firstName, T1.lastName
                FROM HEM6 T0
                INNER JOIN OHEM T1 ON T0.empID = T1.empID
                WHERE T1.Active = 'Y'
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            print(f"Technicians with Roles found: {len(rows)}")
            for row in rows:
                print(f" - ID: {row[0]}, Name: {row[1]} {row[2]}")
            
            if len(rows) > 0:
                print(f"\nRECOMMENDED: Use Technician ID {rows[0][0]} for PE fallback.")
            else:
                print("\nWARNING: No employees found in HEM6 for PE.")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    check_pe_techs()
