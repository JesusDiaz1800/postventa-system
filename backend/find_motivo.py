import os
import django
from django.db import connections

os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.core.settings'
django.setup()

def find_motivo_field():
    alias = 'sap_db_pe'
    try:
        print(f"Connecting to {alias} and searching for 'MOTIVO' fields...")
        with connections[alias].cursor() as cursor:
            # Buscar en sys.columns y sys.objects
            query = """
            SELECT t.name AS TableName, c.name AS ColumnName
            FROM sys.columns c
            JOIN sys.tables t ON c.object_id = t.object_id
            WHERE c.name LIKE '%MOTIVO%' OR c.name LIKE '%VISITA%'
            ORDER BY TableName, ColumnName
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            
            if not rows:
                print("No se encontraron campos relacionados con 'MOTIVO' o 'VISITA'")
            else:
                for row in rows:
                    if row[0] in ['OSCL', 'OSLT', 'OHEM', 'RDR1', 'ORDR', 'OASCL']:
                        print(f"TABLA: {row[0]}, COLUMNA: {row[1]}")
                    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    find_motivo_field()
