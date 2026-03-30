import os
import django
from django.db import connections

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def check_sap_positions():
    print("--- Posiciones definidas en SAP (OHPS) ---")
    try:
        with connections['sap_db_pe'].cursor() as cursor:
            cursor.execute("SELECT posID, name, descr from OHPS")
            for row in cursor.fetchall():
                print(f"ID: {row[0]}, Name: {row[1]}, Descr: {row[2]}")
            
            print("\n--- Empleados por posición ---")
            cursor.execute("""
                SELECT T0.position, T1.name, COUNT(*) 
                FROM OHEM T0 
                LEFT JOIN OHPS T1 ON T0.position = T1.posID 
                WHERE T0.Active = 'Y' 
                GROUP BY T0.position, T1.name
            """)
            for row in cursor.fetchall():
                print(f"PosID: {row[0]}, Name: {row[1]}, Count: {row[2]}")
    except Exception as e:
        print(f"Error consultando posiciones: {e}")

if __name__ == "__main__":
    check_sap_positions()
