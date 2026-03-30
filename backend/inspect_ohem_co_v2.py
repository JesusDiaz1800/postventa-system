import os
import django
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
import sys
sys.path.append(os.path.join(os.getcwd(), 'backend'))
django.setup()

from django.db import connections

def inspect_ohem_co():
    try:
        with connections['sap_db_co'].cursor() as cursor:
            print("--- ANALIZANDO TODOS LOS EMPLEADOS ACTIVOS (CO) ---")
            cursor.execute("SELECT empID, firstName, lastName, position FROM OHEM WHERE Active = 'Y'")
            rows = cursor.fetchall()
            if not rows:
                print("No se encontraron empleados activos.")
            for r in rows:
                print(f"ID: {r[0]}, Name: {r[1]} {r[2]}, Pos: {r[3]}")
                
            # Buscar que hay en OHEM en general
            cursor.execute("SELECT COUNT(*) FROM OHEM")
            count = cursor.fetchone()[0]
            print(f"\nTotal empleados en OHEM: {count}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_ohem_co()
