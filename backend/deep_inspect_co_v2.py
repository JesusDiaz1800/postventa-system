import os
import django
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
import sys
sys.path.append(os.path.join(os.getcwd(), 'backend'))
django.setup()

from django.db import connections

def deep_inspect_record_6():
    try:
        with connections['sap_db_co'].cursor() as cursor:
            print("--- INSPECCIONANDO TODOS LOS CAMPOS DE OSCL PARA CALLID 6 ---")
            cursor.execute("SELECT * FROM OSCL WHERE callID = 6")
            row = cursor.fetchone()
            if row:
                cols = [d[0] for d in cursor.description]
                data = dict(zip(cols, row))
                # Buscar el valor 33 or 'Post-Venta' en cualquier campo
                for k, v in data.items():
                    if v == 33 or v == '33' or (isinstance(v, str) and 'Post-Venta' in v):
                        print(f"  FOUND IN FIELD: {k} = {v}")
                
                print("\nValores de campos clave:")
                for k in ['problemTyp', 'callType', 'origin', 'status', 'Series', 'DocNum']:
                        print(f"  {k}: {data.get(k)}")
            else:
                print("Record callID = 6 not found.")

            print("\n--- BUSCANDO TABLAS MAESTRAS OTYP/OCTP ---")
            # Probar con esquema explícito si es necesario, o buscar en sysobjects
            cursor.execute("SELECT name FROM sysobjects WHERE name IN ('OTYP', 'OCTP', 'OSCLPR', 'OSCLTP', 'OPRB')")
            for r in cursor.fetchall():
                t = r[0]
                try:
                    cursor.execute(f"SELECT * FROM {t}")
                    print(f"  Table {t} exists and has content: {cursor.fetchone()}")
                except:
                    print(f"  Table {t} found in sysobjects but failed to SELECT.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    deep_inspect_record_6()
