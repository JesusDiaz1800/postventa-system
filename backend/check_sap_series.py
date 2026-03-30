import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
import sys
sys.path.append(os.path.join(os.getcwd(), 'backend'))
django.setup()

from django.db import connections

def check_sap_series():
    try:
        with connections['sap_db_co'].cursor() as cursor:
            # Series de Llamadas de Servicio son ObjectCode 191
            print("--- SERIES DISPONIBLES (Object 191 - Service Calls) ---")
            cursor.execute("SELECT Series, SeriesName, IsManual, NextNumber FROM NNM1 WHERE ObjectCode = '191'")
            for r in cursor.fetchall():
                print(f"  Series: {r[0]}, Name: {r[1]}, Manual: {r[2]}, Next: {r[3]}")
                
            print("\n--- TIPOS DE PROBLEMA (OTYP) ---")
            try:
                cursor.execute("SELECT PrblmID, Name FROM OTYP")
                for r in cursor.fetchall(): print(f"  ID: {r[0]}, Name: {r[1]}")
            except: print("  Table OTYP not found.")

            print("\n--- TIPOS DE LLAMADA (OCTP) ---")
            try:
                cursor.execute("SELECT CallTypeID, Name FROM OCTP")
                for r in cursor.fetchall(): print(f"  ID: {r[0]}, Name: {r[1]}")
            except: print("  Table OCTP not found.")

            print("\n--- ORÍGENES (OSCO) ---")
            try:
                cursor.execute("SELECT OriginID, Name FROM OSCO")
                for r in cursor.fetchall(): print(f"  ID: {r[0]}, Name: {r[1]}")
            except: print("  Table OSCO not found.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_sap_series()
