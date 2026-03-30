import os
import django
from django.db import connections

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def check_sap_technicians_flag():
    print("--- Empleados con flag 'technician' en SAP Perú ---")
    try:
        with connections['sap_db_pe'].cursor() as cursor:
            # Contar por el flag oficial de SAP
            cursor.execute("SELECT empID, firstName, lastName, technician FROM OHEM WHERE Active = 'Y' AND technician = 'Y'")
            rows = cursor.fetchall()
            print(f"Total con flag 'Y': {len(rows)}")
            for row in rows:
                firstName = row[1] or ""
                lastName = row[2] or ""
                print(f"ID: {row[0]}, Name: {firstName} {lastName}, Flag: {row[3]}")
    except Exception as e:
        print(f"Error consultando SAP PE: {e}")

if __name__ == "__main__":
    check_sap_technicians_flag()
