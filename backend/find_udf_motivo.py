import os
import django
from django.db import connections

os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.core.settings'
django.setup()

def find_udf_motivo():
    alias = 'sap_db_pe'
    try:
        print(f"Searching CUFD in {alias}...")
        with connections[alias].cursor() as cursor:
            # Seleccionamos AliasID y Descr de CUFD para OSCL
            cursor.execute("SELECT AliasID, Descr FROM CUFD WHERE TableID = 'OSCL' AND (Descr LIKE '%MOTIVO%' OR Descr LIKE '%VISITA%')")
            rows = cursor.fetchall()
            
            if not rows:
                print("No UDF found with MOTIVO or VISITA in its description.")
            else:
                for row in rows:
                    print(f"UDF Alias: {row[0]}, Label: {row[1]}")
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_udf_motivo()
