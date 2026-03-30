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
    print(f"Checking for technicians in {db_alias} with ROLES in HEM6...")
    
    try:
        connection = connections[db_alias]
        with connection.cursor() as cursor:
            # Query employees and their roles
            query = """
                SELECT T0.empID, T0.firstName, T0.lastName, T1.roleID, T2.name
                FROM OHEM T0
                INNER JOIN HEM6 T1 ON T0.empID = T1.empID
                INNER JOIN OROL T2 ON T1.roleID = T2.roleID
                WHERE T0.Active = 'Y'
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            print(f"Technicians with Roles found: {len(rows)}")
            for row in rows:
                print(f" - ID: {row[0]}, Name: {row[1]} {row[2]}, RoleID: {row[3]}, RoleName: {row[4]}")
            
            if len(rows) > 0:
                print(f"\nRECOMMENDED: Use Technician ID {rows[0][0]} for PE fallback.")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    check_pe_techs()
