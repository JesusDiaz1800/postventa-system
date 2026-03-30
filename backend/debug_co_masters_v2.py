import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
import sys
sys.path.append(os.path.join(os.getcwd(), 'backend'))

django.setup()

from django.db import connections

def debug_oscl_masters_v2():
    try:
        with connections['sap_db_co'].cursor() as cursor:
            # Checking Problem Types (Usually OTYP)
            print("Checking OTYP (Problem Types):")
            try:
                cursor.execute("SELECT PrblmID, Name FROM OTYP")
                rows = cursor.fetchall()
                for r in rows:
                    print(f"PrblmID: {r[0]}, Name: {r[1]}")
            except Exception as e:
                print(f"OTYP Failed: {e}")
                
            # Checking Call Types (Usually OCTP)
            print("\nChecking OCTP (Call Types):")
            try:
                cursor.execute("SELECT CallTypeID, Name FROM OCTP")
                rows = cursor.fetchall()
                for r in rows:
                    print(f"CallTypeID: {r[0]}, Name: {r[1]}")
            except Exception as e:
                print(f"OCTP Failed: {e}")
                
            # Checking a real OSCL record to see values
            print("\nChecking a real OSCL record:")
            try:
                cursor.execute("SELECT TOP 1 origin, problemTyp, callType, assignee, technician FROM OSCL")
                row = cursor.fetchone()
                if row:
                    print(f"Sample OSCL -> Origin: {row[0]}, ProblemType: {row[1]}, CallType: {row[2]}, Assignee: {row[3]}, Technician: {row[4]}")
            except Exception as e:
                print(f"OSCL Check Failed: {e}")

    except Exception as e:
        print(f"Global Error: {e}")

if __name__ == "__main__":
    debug_oscl_masters_v2()
