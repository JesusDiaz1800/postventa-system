import os
import django
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
import sys
sys.path.append(os.path.join(os.getcwd(), 'backend'))
django.setup()

from django.db import connections

def thorough_inspection():
    try:
        with connections['sap_db_co'].cursor() as cursor:
            print("--- INSPECCIONANDO REGISTRO CALLID 6 (S screenshot) ---")
            cursor.execute("SELECT callID, docNum, origin, callType, problemTyp, technician, assignee FROM OSCL WHERE callID = 6")
            row = cursor.fetchone()
            if row:
                cols = [d[0] for d in cursor.description]
                print(f"Columns: {cols}")
                print(f"Values: {row}")
            else:
                print("Record callID = 6 not found.")

            print("\n--- BUSCANDO TODAS LAS TABLAS QUE TENGAN PRB O TYP ---")
            cursor.execute("SELECT name FROM sys.tables WHERE name LIKE '%PRB%' OR name LIKE '%TYP%' OR name LIKE '%CALL%' OR name LIKE '%ORIGIN%'")
            tables = [r[0] for r in cursor.fetchall()]
            print(f"Tables found: {tables}")
            
            for t in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {t}")
                    count = cursor.fetchone()[0]
                    print(f"  Table {t}: {count} records")
                    if count > 0:
                        cursor.execute(f"SELECT TOP 3 * FROM {t}")
                        print(f"    Sample: {cursor.fetchone()}")
                except:
                    pass

            print("\n--- METADATA DE OSCL EN CUFD ---")
            try:
                cursor.execute("SELECT AliasID, Descr, TypeID FROM CUFD WHERE TableID = 'OSCL' AND (AliasID LIKE '%Typ%' OR AliasID LIKE '%Ori%')")
                for r in cursor.fetchall(): print(f"  Field: {r[0]}, Descr: {r[1]}, Type: {r[2]}")
            except:
                print("  CUFD query failed.")

            print("\n--- METADATA DE PROBLEM EN OPRB O SIMILAR ---")
            # En algunas localizaciones se usa OPRB o OSCLPR
            for t in ['OPRB', 'OSCLPR', 'OOSC', 'OSCP', 'OKTP', 'OTYP', 'OCTP']:
                try:
                    cursor.execute(f"SELECT * FROM {t}")
                    print(f"  Table {t} found content: {cursor.fetchone()}")
                except:
                    pass

    except Exception as e:
        print(f"Error general: {e}")

if __name__ == "__main__":
    thorough_inspection()
