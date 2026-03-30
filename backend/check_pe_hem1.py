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

def check_hem1():
    set_current_country('PE')
    print("Verificando roles en HEM1 y OHTL/OHRL (PE)...")
    try:
        with connections['sap_db_pe'].cursor() as cursor:
            # En B1, el rol de técnico se define con un ID específico. 
            # El ID suele ser 1 (Technician), 2 (Manager), 3 (Sales).
            cursor.execute("SELECT empID, roleID FROM HEM1 WHERE empID IN (1, 13)")
            for row in cursor.fetchall():
                print(f"HEM1 Role: {row}")
                
            cursor.execute("SELECT TOP 10 ID, Name FROM OHRL") # Roles
            for row in cursor.fetchall():
                print(f"OHRL role: {row}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_hem1()
