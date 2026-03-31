import os
import django
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
import sys
# Asegurarse de que el path al backend esté disponible
sys.path.append(os.path.join(os.getcwd(), 'backend'))
django.setup()

from django.db import connections

def inspect_co_status():
    try:
        print("=== INVESTIGANDO STATUS EN COLOMBIA (sap_db_co) ===")
        with connections['sap_db_co'].cursor() as cursor:
            # 1. Consultar la tabla OSTS (Service Call Status)
            print("\n--- TABLA OSTS (Estados de LLamadas) ---")
            cursor.execute("SELECT statusID, Name FROM OSTS")
            statuses = cursor.fetchall()
            for r in statuses:
                print(f"  ID: {r[0]}, Name: {r[1]}")

            # 2. Consultar algunas llamadas reales para ver qué estados tienen
            print("\n--- ÚLTIMAS 5 LLAMADAS DE SERVICIO (OSCL) ---")
            # En SAP, Status suele ser: -3 (Open), -2 (Closed), -1 (Closed), etc.
            # Pero depende de la localización.
            cursor.execute("SELECT TOP 5 callID, DocNum, Status, Subject FROM OSCL ORDER BY callID DESC")
            calls = cursor.fetchall()
            for c in calls:
                print(f"  CallID: {c[0]}, DocNum: {c[1]}, Status: {c[2]}, Subject: {c[3]}")

            # 3. Verificar si existe el campo DocNum vs callID (DocEntry)
            # En Service Layer se requiere DocEntry (callID)
            print("\n--- VERIFICACIÓN DocEntry vs DocNum ---")
            cursor.execute("SELECT TOP 1 callID, DocNum FROM OSCL ORDER BY callID DESC")
            row = cursor.fetchone()
            if row:
                print(f"  Ejemplo real en CO: DocEntry (callID)={row[0]}, DocNum={row[1]}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_co_status()
