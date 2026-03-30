import os
import django
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
import sys
sys.path.append(os.path.join(os.getcwd(), 'backend'))
django.setup()

from django.db import connections

def inspect_users_and_employees():
    try:
        with connections['sap_db_co'].cursor() as cursor:
            print("--- INSPECCIONANDO USUARIOS (OUSR) ---")
            # Listar los primeros 30 usuarios activos
            cursor.execute("SELECT USERID, USER_CODE, U_NAME FROM OUSR WHERE GROUPS = 'N' ORDER BY U_NAME")
            users = cursor.fetchall()
            print(f"Total Usuarios (OUSR): {len(users)}")
            for r in users[:20]:
                print(f"  ID: {r[0]}, Code: {r[1]}, Name: {r[2]}")

            print("\n--- INSPECCIONANDO EMPLEADOS (OHEM) SIN FILTRO ACTIVE ---")
            cursor.execute("SELECT empID, firstName, lastName, Active FROM OHEM ORDER BY firstName")
            employees = cursor.fetchall()
            print(f"Total Empleados (OHEM): {len(employees)}")
            for r in employees[:20]:
                print(f"  ID: {r[0]}, Name: {r[1]} {r[2]}, Active: {r[3]}")

            # Buscar si el ID 22 (del screenshot status bar) es un empleado o un usuario
            print("\n--- BUSCANDO ID 22 ---")
            cursor.execute("SELECT empID, firstName, lastName FROM OHEM WHERE empID = 22")
            row = cursor.fetchone()
            if row: print(f"  ID 22 is Employee: {row[1]} {row[2]}")
            else:
                cursor.execute("SELECT USERID, U_NAME FROM OUSR WHERE USERID = 22")
                row = cursor.fetchone()
                if row: print(f"  ID 22 is User: {row[1]}")
                else: print("  ID 22 not found in OHEM or OUSR.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_users_and_employees()
