import os
import django
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
import sys
sys.path.append(os.path.join(os.getcwd(), 'backend'))
django.setup()

from django.db import connections

def deep_debug_co():
    try:
        with connections['sap_db_co'].cursor() as cursor:
            # 1. Orígenes en OSCO
            print("--- ORÍGENES (OSCO) ---")
            try:
                cursor.execute("SELECT OriginID, Name FROM OSCO")
                for r in cursor.fetchall(): print(f"  ID: {r[0]}, Name: {r[1]}")
            except: print("  Table OSCO not found.")

            # 2. Tipos de Llamada en OCTP o similar
            print("\n--- TIPOS DE LLAMADA ---")
            try:
                cursor.execute("SELECT CallTypeID, Name FROM OCTP")
                for r in cursor.fetchall(): print(f"  ID: {r[0]}, Name: {r[1]}")
            except: print("  Table OCTP not found.")

            # 3. Tipos de Problema en OTYP o similar
            print("\n--- TIPOS DE PROBLEMA ---")
            try:
                cursor.execute("SELECT PrblmID, Name FROM OTYP")
                for r in cursor.fetchall(): print(f"  ID: {r[0]}, Name: {r[1]}")
            except: print("  Table OTYP not found.")

            # 4. Ver registros existentes de OSCL
            print("\n--- REGISTROS EXISTENTES EN OSCL ---")
            cursor.execute("SELECT TOP 5 callID, customer, origin, callType, problemTyp, technician, assignee FROM OSCL ORDER BY callID DESC")
            cols = [d[0] for d in cursor.description]
            print(f"Columns: {cols}")
            for r in cursor.fetchall():
                print(f"  {r}")

            # 5. Listar tablas que empiecen por O (SAP standard)
            print("\n--- LISTANDO TODAS LAS TABLAS ---")
            cursor.execute("SELECT name FROM sys.tables WHERE name LIKE 'O%' AND (name LIKE '%CALL%' OR name LIKE '%SERV%')")
            for r in cursor.fetchall(): print(f"  Table: {r[0]}")

    except Exception as e:
        print(f"Error general: {e}")

if __name__ == "__main__":
    deep_debug_co()
