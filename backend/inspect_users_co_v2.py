import os
import django
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
import sys
sys.path.append(os.path.join(os.getcwd(), 'backend'))
django.setup()

from django.db import connections

def inspect_users_and_employees_v2():
    try:
        with connections['sap_db_co'].cursor() as cursor:
            print("--- INSPECCIONANDO USUARIOS (OUSR) ---")
            # Sin filtro GROUPS para evitar error de tipo, solo traer los primeros 50
            cursor.execute("SELECT USERID, USER_CODE, U_NAME FROM OUSR ORDER BY U_NAME")
            users = cursor.fetchall()
            print(f"Total Usuarios (OUSR): {len(users)}")
            for r in users[:30]:
                print(f"  ID: {r[0]}, Code: {r[1]}, Name: {r[2]}")

            print("\n--- INSPECCIONANDO EMPLEADOS (OHEM) ---")
            cursor.execute("SELECT empID, firstName, lastName, Active FROM OHEM ORDER BY firstName")
            employees = cursor.fetchall()
            print(f"Total Empleados (OHEM): {len(employees)}")
            for r in employees:
                print(f"  ID: {r[0]}, Name: {r[1]} {r[2]}, Active: {r[3]}")

            # Buscar especificamente el ID 22 (del screenshot)
            print("\n--- DETALLES ID 22 ---")
            cursor.execute("SELECT empID, firstName, lastName FROM OHEM WHERE empID = 22")
            row = cursor.fetchone()
            if row: print(f"  ID 22 is Employee: {row[1]} {row[2]}")
            
            cursor.execute("SELECT USERID, USER_CODE, U_NAME FROM OUSR WHERE USERID = 22")
            row = cursor.fetchone()
            if row: print(f"  ID 22 is User: {row[1]} (Code: {row[2]})")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_users_and_employees_v2()
