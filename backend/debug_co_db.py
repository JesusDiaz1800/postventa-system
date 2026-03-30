import os
import django
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
import sys
sys.path.append(os.path.join(os.getcwd(), 'backend'))
django.setup()

from django.db import connections

def debug_co():
    try:
        with connections['sap_db_co'].cursor() as cursor:
            print("--- ANALIZANDO TABLAS MAESTRAS (CO) ---")
            
            # 1. Buscar tablas de CallType y ProblemType
            cursor.execute("SELECT name FROM sys.tables WHERE name LIKE 'O%CTP%' OR name LIKE 'O%TYP%' OR name LIKE 'O%TYP%'")
            tables = [r[0] for r in cursor.fetchall()]
            print(f"Tablas maestras potenciales found: {tables}")
            
            for table in tables:
                try:
                    cursor.execute(f"SELECT TOP 5 * FROM {table}")
                    cols = [d[0] for d in cursor.description]
                    print(f"\nTable {table} columns: {cols}")
                    rows = cursor.fetchall()
                    for r in rows: print(f"  {r}")
                except Exception as e:
                    print(f"  Error leyendo {table}: {e}")

            # 2. Buscar Orígenes (Origin)
            print("\n--- ANALIZANDO ORÍGENES ---")
            cursor.execute("SELECT name FROM sys.tables WHERE name LIKE 'O%ORN%' OR name LIKE 'O%SC%'")
            oscl_tables = [r[0] for r in cursor.fetchall()]
            print(f"Potential origin tables: {oscl_tables}")
            
            # 3. Listar empleados con rol de técnico real
            print("\n--- BUSCANDO TÉCNICOS VÁLIDOS ---")
            # En SAP RoleID 1 suele ser técnico. Veamos qué hay en HEM6.
            cursor.execute("SELECT h.empID, h.roleID, e.firstName, e.lastName FROM HEM6 h JOIN OHEM e ON h.empID = e.empID WHERE e.Active = 'Y'")
            roles = cursor.fetchall()
            print("Roles en HEM6 para empleados activos:")
            for r in roles:
                print(f"  EmpID: {r[0]}, RoleID: {r[1]}, Name: {r[2]} {r[3]}")

            # 4. Listar UDFs de OSCL si es posible
            print("\n--- COLUMNAS DE OSCL ---")
            cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'OSCL'")
            oscl_cols = [r[0] for r in cursor.fetchall()]
            print(f"OSCL Columns: {oscl_cols[:20]}... (Total: {len(oscl_cols)})")

    except Exception as e:
        print(f"Error general: {e}")

if __name__ == "__main__":
    debug_co()
