import os
import django
from django.db import connections

os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.core.settings'
django.setup()

def find_udfs():
    with connections['sap_db_pe'].cursor() as cursor:
        cursor.execute("SELECT AliasID, Descr FROM CUFD WHERE TableID = 'OSCL'")
        rows = cursor.fetchall()
        print("--- UDFs for OSCL in Peru ---")
        for row in rows:
            print(f"Alias: {row[0]}, Description: {row[1]}")
            
        # Also check valid values for any likely UDF
        cursor.execute("""
            SELECT T0.AliasID, T1.FldValue, T1.Descr 
            FROM CUFD T0 
            JOIN UFD1 T1 ON T0.TableID = T1.TableID AND T0.FieldID = T1.FieldID 
            WHERE T0.TableID = 'OSCL' AND (T0.Descr LIKE '%MOTIVO%' OR T0.AliasID LIKE '%SIGLAS%')
        """)
        values = cursor.fetchall()
        print("\n--- Valid Values for potential Motivo fields ---")
        for val in values:
            print(f"Field: {val[0]}, Value: {val[1]}, Description: {val[2]}")

if __name__ == "__main__":
    find_udfs()
