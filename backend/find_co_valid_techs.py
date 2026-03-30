import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
import sys
sys.path.append(os.path.join(os.getcwd(), 'backend'))

django.setup()

from django.db import connections

def find_valid_technicians():
    try:
        with connections['sap_db_co'].cursor() as cursor:
            # Check HEM6 for technician role (roleID 1 is usually technician)
            print("Checking HEM6 for roleID 1 (Technician):")
            cursor.execute("""
                SELECT h.empID, e.firstName, e.lastName 
                FROM HEM6 h 
                JOIN OHEM e ON h.empID = e.empID 
                WHERE h.roleID = 1 AND e.Active = 'Y'
            """)
            rows = cursor.fetchall()
            for r in rows:
                print(f"Tech found in HEM6: ID {r[0]} ({r[1]} {r[2]})")
            
            if not rows:
                print("No employees found with roleID 1 in HEM6.")
            
            # Check OHEM field 'technician' if it exists
            print("\nChecking OHEM for technician='Y':")
            try:
                cursor.execute("SELECT empID, firstName, lastName FROM OHEM WHERE technician = 'Y' AND Active = 'Y'")
                rows = cursor.fetchall()
                for r in rows:
                    print(f"Tech found in OHEM field: ID {r[0]} ({r[1]} {r[2]})")
                if not rows:
                    print("No employees found with technician='Y' in OHEM.")
            except Exception as e:
                print(f"OHEM 'technician' field check failed (might not exist): {e}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_valid_technicians()
