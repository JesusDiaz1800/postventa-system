import os
import django
from django.db import connections

os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.core.settings'
django.setup()

def find_regional():
    # Buscamos en Chile y Perú
    for country, alias in [('CL', 'sap_db'), ('PE', 'sap_db_pe')]:
        try:
            print(f"Searching in {country} ({alias})...")
            with connections[alias].cursor() as cursor:
                cursor.execute("SELECT EmpID, firstName, lastName FROM OHEM WHERE firstName LIKE %s OR lastName LIKE %s", ['%Cristian%', '%Peña%'])
                rows = cursor.fetchall()
                if rows:
                    for r in rows: print(f"Found in {country}: ID={r[0]}, Name={r[1]} {r[2]}")
                else:
                    print(f"Not found in {country}")
        except Exception as e:
            print(f"Error in {country}: {e}")

if __name__ == "__main__":
    find_regional()
