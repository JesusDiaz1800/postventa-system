"""
Script para inspeccionar columnas de tabla @FRMOBRAS
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from django.db import connections

def inspect_obras():
    print("Inspeccionando tabla @FRMOBRAS...")
    try:
        with connections['sap_db'].cursor() as cursor:
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = '@FRMOBRAS'
                ORDER BY ORDINAL_POSITION
            """)
            columns = cursor.fetchall()
            print(f"Columnas encontradas: {len(columns)}")
            for col_name, col_type in columns:
                print(f" - {col_name} ({col_type})")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    inspect_obras()
