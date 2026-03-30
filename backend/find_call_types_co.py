import os
import django
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
import sys
sys.path.append(os.path.join(os.getcwd(), 'backend'))
django.setup()

from django.db import connections

def find_call_types():
    try:
        with connections['sap_db_co'].cursor() as cursor:
            print("--- BUSCANDO TABLA PARA CALLTYPE ---")
            # Buscar tablas que contengan registros sugeridos en el screenshot (Tipo de llamada)
            # En el screenshot no se ve el valor de CallType, pero probaremos tablas comunes
            for t in ['OCTP', 'OSCLTP', 'OCMT', 'OCM1', 'OTOP']:
                try:
                    cursor.execute(f"SELECT * FROM {t}")
                    print(f"  Table {t} found!! Sample: {cursor.fetchone()}")
                except:
                    pass
            
            # Buscar en sysobjects tablas con nombres parecidos
            cursor.execute("SELECT name FROM sysobjects WHERE name LIKE '%TYPE%' AND (name LIKE '%CALL%' OR name LIKE '%SCL%')")
            for r in cursor.fetchall():
                t = r[0]
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {t}")
                    print(f"  Candidate table {t}: {cursor.fetchone()[0]} records")
                except: pass

            # Inspeccionar la tabla OSCL para ver qué valores de callType existen
            print("\n--- VALORES DE CALLTYPE EN OSCL ---")
            cursor.execute("SELECT DISTINCT callType FROM OSCL WHERE callType IS NOT NULL")
            for r in cursor.fetchall(): print(f"  ID: {r[0]}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_call_types()
