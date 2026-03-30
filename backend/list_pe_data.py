import os
import sys
import django

# Add the backend directory to sys.path
backend_dir = r"c:\Users\jdiaz\Desktop\postventa-system\backend"
sys.path.append(backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.sap_integration.models import ServiceCall
from django.db import connections
from apps.core.thread_local import set_current_country

def list_techs():
    set_current_country('PE')
    print("Listando Empleados (OHEM) en PE...")
    try:
        with connections['sap_db_pe'].cursor() as cursor:
            cursor.execute("SELECT TOP 50 empID, firstName, lastName, Active, jobTitle FROM OHEM ORDER BY empID")
            columns = [col[0] for col in cursor.description]
            for row in cursor.fetchall():
                print(dict(zip(columns, row)))
                
        print("\nListando Series válidas para OSCL (PE)...")
        with connections['sap_db_pe'].cursor() as cursor:
            cursor.execute("SELECT Series, SeriesName, IsDefault FROM NNM1 WHERE ObjectCode = '191'")
            for row in cursor.fetchall():
                print(f"Series: {row}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_techs()
