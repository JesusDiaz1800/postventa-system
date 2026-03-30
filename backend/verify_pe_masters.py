import os
import sys
import django

# Add the backend directory to sys.path
backend_dir = r"c:\Users\jdiaz\Desktop\postventa-system\backend"
sys.path.append(backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from django.db import connections
from apps.core.thread_local import set_current_country

def verify_problems():
    set_current_country('PE')
    print("Listando ProblemTypes (OSPT) en PE...")
    try:
        with connections['sap_db_pe'].cursor() as cursor:
            cursor.execute("SELECT PrblmTypID, Name FROM OSPT")
            for row in cursor.fetchall():
                print(f"Problem: {row}")
                
        print("\nListando CallTypes (OSCT) en PE...")
        with connections['sap_db_pe'].cursor() as cursor:
            cursor.execute("SELECT CallTypeID, Name FROM OSCT")
            for row in cursor.fetchall():
                print(f"CallType: {row}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_problems()
