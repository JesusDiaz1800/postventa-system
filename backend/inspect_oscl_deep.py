"""
Script para inspeccionar PROFUNDAMENTE la tabla OSCL en SAP (PRDPOLIFUSION)
Buscaremos columnas especificas mencionadas por el usuario.
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from django.db import connections

def inspect_oscl_deep():
    print("=" * 60)
    print("ANALISIS PROFUNDO DE TABLA OSCL (Llamadas de Servicio)")
    print("=" * 60)
    
    target_columns = [
        'U_NX_MEZCLADO', 
        'U_NX_NOM_PRO', 
        'U_NX_VENDEDOR', 
        'BProjCode', 
        'customer'
    ]
    
    try:
        with connections['sap_db'].cursor() as cursor:
            # 1. Buscar columnas especificas
            print("\n1. Buscando columnas objetivo:")
            for col in target_columns:
                cursor.execute(f"""
                    SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = 'OSCL' AND COLUMN_NAME = '{col}'
                """)
                result = cursor.fetchone()
                if result:
                    print(f"   [ENCONTRADO] {col}: {result[1]} ({result[2]})")
                else:
                    print(f"   [NO ENCONTRADO] {col} - Buscando parecidos...")
                    # Buscar parecidos
                    cursor.execute(f"""
                        SELECT COLUMN_NAME 
                        FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_NAME = 'OSCL' AND COLUMN_NAME LIKE '%{col.split('_')[-1]}%'
                    """)
                    matches = cursor.fetchall()
                    if matches:
                        print(f"      Posibles coincidencias: {[m[0] for m in matches]}")

            # 2. Muestreo de datos reales para entender el contenido
            print("\n2. Muestreo de datos (Ultimas 3 llamadas):")
            cursor.execute(f"""
                SELECT TOP 3 
                    callID, 
                    subject, 
                    {', '.join([c for c in target_columns if c != 'customer'])} -- customer ya esta
                    , custmrName
                FROM OSCL
                ORDER BY callID DESC
            """)
            
            # Obtener nombres de columnas del cursor
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            
            for row in rows:
                print("-" * 40)
                for i, value in enumerate(row):
                    print(f"{columns[i]}: {value}")
                    
    except Exception as e:
        print(f"\n[ERROR] {e}")

if __name__ == '__main__':
    inspect_oscl_deep()
