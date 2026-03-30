import os
import django
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
import sys
sys.path.append(os.path.join(os.getcwd(), 'backend'))
django.setup()

from django.db import connections

def find_real_co_db():
    try:
        # 1. Listar todas las bases de datos en el servidor
        with connections['sap_db_co'].cursor() as cursor:
            print("--- BASES DE DATOS EN EL SERVIDOR ---")
            cursor.execute("SELECT name FROM sys.databases")
            for r in cursor.fetchall(): print(f"  DB: {r[0]}")
            
            # 2. Confirmar en qué DB estamos
            cursor.execute("SELECT DB_NAME()")
            print(f"\nESTAMOS EN LA DB: {cursor.fetchone()[0]}")

            # 3. Listar todas las tablas con sus esquemas
            print("\n--- TABLAS CON SCHEMAS ---")
            cursor.execute("SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME IN ('OTYP', 'OCTP', 'OSCL')")
            for r in cursor.fetchall(): print(f"  Schema: {r[0]}, Table: {r[1]}")

            # 4. Inspeccionar la tabla CUFD para campos de OSCL
            print("\n--- CAMPOS DE OSCL EN CUFD ---")
            cursor.execute("SELECT AliasID, Descr FROM CUFD WHERE TableID = 'OSCL'")
            for r in cursor.fetchall(): print(f"  UDF: {r[0]} ({r[1]})")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_real_co_db()
