import os
import django
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
import sys
sys.path.append(os.path.join(os.getcwd(), 'backend'))
django.setup()

from django.db import connections

def inspect_co_status_v2():
    try:
        print("=== INVESTIGANDO STATUS EN COLOMBIA (sap_db_co) v2 ===")
        with connections['sap_db_co'].cursor() as cursor:
            # 1. Consultar columnas de OSTS
            print("\n--- COLUMNAS DE OSTS ---")
            cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'OSTS'")
            for r in cursor.fetchall(): print(f"  Col: {r[0]}")

            # 2. Consultar contenido si encontramos columnas
            cursor.execute("SELECT * FROM OSTS")
            rows = cursor.fetchall()
            print(f"\n--- CONTENIDO DE OSTS ({len(rows)} filas) ---")
            for r in rows: print(f"  Row: {r}")

            # 3. Consultar algunas llamadas reales
            print("\n--- ÚLTIMAS 5 LLAMADAS DE SERVICIO (OSCL) ---")
            cursor.execute("SELECT TOP 5 callID, DocNum, Status, Subject FROM OSCL ORDER BY callID DESC")
            calls = cursor.fetchall()
            for c in calls:
                print(f"  CallID: {c[0]}, DocNum: {c[1]}, Status: {c[2]}, Subject: {c[3]}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_co_status_v2()
