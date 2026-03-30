import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
import sys
sys.path.append(os.path.join(os.getcwd(), 'backend'))

django.setup()

from django.db import connections

def debug_oscl_masters():
    try:
        with connections['sap_db_co'].cursor() as cursor:
            print("Checking Origins (OORN):")
            cursor.execute("SELECT OriginID, Name FROM OORN")
            rows = cursor.fetchall()
            for r in rows:
                print(f"OriginID: {r[0]}, Name: {r[1]}")
                
            print("\nChecking Problem Types (OTYP):")
            cursor.execute("SELECT PrblmID, Name FROM OTYP")
            rows = cursor.fetchall()
            for r in rows:
                print(f"PrblmID: {r[0]}, Name: {r[1]}")
                
            print("\nChecking Call Types (OCTP):")
            cursor.execute("SELECT CallTypeID, Name FROM OCTP")
            rows = cursor.fetchall()
            for r in rows:
                print(f"CallTypeID: {r[0]}, Name: {r[1]}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_oscl_masters()
