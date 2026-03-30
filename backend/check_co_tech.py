import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
import sys
sys.path.append(os.path.join(os.getcwd(), 'backend'))

django.setup()

from django.db import connections

def check_tech_1_and_get_fallback():
    try:
        with connections['sap_db_co'].cursor() as cursor:
            # Check if empID 1 exists and is active
            cursor.execute("SELECT empID, firstName, lastName FROM OHEM WHERE empID = 1 AND Active = 'Y'")
            row = cursor.fetchone()
            if row:
                print(f"Tech 1 found: {row[1]} {row[2]}")
                return 1
            
            # If not found, find a fallback
            print("Tech 1 not found or inactive. Finding fallback...")
            cursor.execute("SELECT TOP 1 empID, firstName, lastName FROM OHEM WHERE Active = 'Y' ORDER BY empID ASC")
            row = cursor.fetchone()
            if row:
                print(f"Fallback tech found: ID {row[0]} ({row[1]} {row[2]})")
                return row[0]
            
            print("No active technicians found in CO.")
            return None
    except Exception as e:
        print(f"Error connecting to sap_db_co: {e}")
        return None

if __name__ == "__main__":
    check_tech_1_and_get_fallback()
