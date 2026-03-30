import os
import django
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
import sys
sys.path.append(os.path.join(os.getcwd(), 'backend'))
django.setup()

from django.db import connections

def search_post_venta():
    try:
        with connections['sap_db_co'].cursor() as cursor:
            # 1. Buscar el texto 'Post-Venta' en sysobjects/syscolumns no es eficiente, pero buscaremos en tablas probables
            probable_tables = ['OTYP', 'OCTP', 'OPRB', 'OSCLPR', 'OSCLTP', 'OOSC', 'OSCP', 'OSCO', 'OCMT', 'OCM1']
            
            print("--- BUSCANDO 'Post-Venta' EN TABLAS PROBABLES ---")
            for t in probable_tables:
                try:
                    cursor.execute(f"SELECT * FROM {t}")
                    cols = [d[0] for d in cursor.description]
                    rows = cursor.fetchall()
                    for r in rows:
                        if any('Post-Venta' in str(val) for val in r):
                            print(f"  FOUND IN TABLE {t}!! Record: {dict(zip(cols, r))}")
                except:
                    pass

            # 2. Buscar por ID 33 en las mismas tablas
            print("\n--- BUSCANDO ID 33 EN TABLAS PROBABLES ---")
            for t in probable_tables:
                try:
                    cursor.execute(f"SELECT * FROM {t}")
                    rows = cursor.fetchall()
                    for r in rows:
                        if any(val == 33 for val in r):
                            print(f"  FOUND ID 33 IN TABLE {t}!!")
                except:
                    pass
            
            # 3. Listar TODAS las tablas que empiecen por O y tengan 4 letras (Standard SAP master tables)
            print("\n--- TABLAS DE 4 LETRAS (Standard SAP) ---")
            cursor.execute("SELECT name FROM sys.tables WHERE name LIKE 'O___'")
            all_4_letter_tables = [r[0] for r in cursor.fetchall()]
            print(f"Total 4-letter tables: {len(all_4_letter_tables)}")
            # Filtrar las que tengan relación con Service Calls
            for t in all_4_letter_tables:
                 if any(x in t for x in ['PRB', 'TYP', 'SCL', 'SRV', 'OCT', 'OTY']):
                     print(f"  Candidate: {t}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    search_post_venta()
