import os
import sys
import django

# Add the backend directory to sys.path
backend_dir = r"c:\Users\jdiaz\Desktop\postventa-system\backend"
sys.path.append(backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.sap_integration.sap_query_service import SAPQueryService
from apps.core.thread_local import set_current_country

def discover():
    set_current_country('PE')
    qs = SAPQueryService()
    print(f"Buscando UDFs para OSCL en PE...")
    udfs = qs.get_available_udfs('OSCL')
    for u in sorted(udfs):
        print(f"UDF: {u}")
    
    # También imprimir campos nativos si es posible vía SQL crudo
    from django.db import connections
    try:
        with connections[qs._get_db_alias()].cursor() as cursor:
            # SQL Server query for columns
            cursor.execute("SELECT TOP 0 * FROM OSCL")
            columns = [column[0] for column in cursor.description]
            print("\nTODOS LOS CAMPOS EN OSCL (PE):")
            for col in sorted(columns):
                print(f"COL: {col}")
    except Exception as e:
        print(f"Error consultando columnas: {e}")

if __name__ == "__main__":
    discover()
