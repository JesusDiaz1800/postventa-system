import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
import sys
sys.path.append(os.path.join(os.getcwd(), 'backend'))
django.setup()

from django.db import connections

def inspect_oscl_columns():
    try:
        print("=== COLUMNAS DE OSCL EN COLOMBIA ===")
        with connections['sap_db_co'].cursor() as cursor:
            cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'OSCL'")
            cols = [r[0] for r in cursor.fetchall()]
            
            # Buscar UDFs específicos
            udfs = [c for c in cols if c.startswith('U_')]
            print(f"Total Columnas: {len(cols)}")
            print(f"UDFs detectados: {udfs}")
            
            # Verificar campos críticos
            critical = ['Status', 'Resolution', 'TechnicianCode', 'U_NX_FECHAVISITA']
            for c in critical:
                print(f"  ¿Existe {c}?: {'SI' if c in cols else 'NO'}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_oscl_columns()
