import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
import sys
sys.path.append(os.path.join(os.getcwd(), 'backend'))

django.setup()

from django.db import connections

def debug_hem6_roles():
    try:
        with connections['sap_db_co'].cursor() as cursor:
            print("Checking all role IDs in HEM6:")
            cursor.execute("SELECT DISTINCT roleID FROM HEM6")
            rows = cursor.fetchall()
            for r in rows:
                print(f"RoleID: {r[0]}")
                
            print("\nChecking all employees in HEM6:")
            cursor.execute("SELECT TOP 10 h.empID, h.roleID, e.firstName, e.lastName FROM HEM6 h JOIN OHEM e ON h.empID = e.empID")
            rows = cursor.fetchall()
            for r in rows:
                print(f"EmpID: {r[0]}, RoleID: {r[1]}, Name: {r[2]} {r[3]}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_hem6_roles()
