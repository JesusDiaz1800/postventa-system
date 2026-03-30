import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
import sys
sys.path.append(os.path.join(os.getcwd(), 'backend'))

django.setup()

from django.db import connections

def list_all_hem6_and_ohem():
    try:
        with connections['sap_db_co'].cursor() as cursor:
            print("Listing all HEM6 entries:")
            cursor.execute("SELECT h.empID, h.roleID, e.firstName, e.lastName FROM HEM6 h JOIN OHEM e ON h.empID = e.empID")
            rows = cursor.fetchall()
            for r in rows:
                print(f"EmpID: {r[0]}, RoleID: {r[1]}, Name: {r[2]} {r[3]}")
                
            print("\nListing all active OHEM employees:")
            cursor.execute("SELECT empID, firstName, lastName FROM OHEM WHERE Active = 'Y'")
            rows = cursor.fetchall()
            for r in rows:
                # Check if they are in HEM6
                cursor.execute("SELECT roleID FROM HEM6 WHERE empID = %s", [r[0]])
                role_row = cursor.fetchone()
                role_str = f"RoleID: {role_row[0]}" if role_row else "NOT IN HEM6"
                print(f"EmpID: {r[0]}, Name: {r[1]} {r[2]}, {role_str}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_all_hem6_and_ohem()
