"""
Script para corregir el schema de SQL Server
PERMITE NULL en campos opcionales de la tabla incidents
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
import django
django.setup()

from django.db import connection

print("=" * 80)
print("CORRECCION DE SCHEMA: incidents")
print("=" * 80)

# Lista de campos a corregir
fields_to_fix = [
    'subcategoria',
    'cliente_rut',
    'customer_code', 
    'project_code',
    'salesperson',
    'lote',
    'factura_num',
    'pedido_num',
    'acciones_inmediatas',
    'nc_number',
    'np_number'
]

print(f"\nCampos a modificar (permitir NULL): {len(fields_to_fix)}")
for field in fields_to_fix:
    print(f"  - {field}")

print("\nEjecutando ALTER TABLE...")
print("-" * 80)

with connection.cursor() as cursor:
    for field in fields_to_fix:
        try:
            # ALTER COLUMN para permitir NULL
            sql = f"ALTER TABLE incidents ALTER COLUMN {field} nvarchar(max) NULL"
            print(f"Ejecutando: {sql[:60]}...")
            cursor.execute(sql)
            print(f"[OK] {field}")
        except Exception as e:
            print(f"[ERROR] {field}: {e}")

print("\n" + "=" * 80)
print("CORRECCION COMPLETADA")
print("=" * 80)
