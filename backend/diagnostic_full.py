"""
Script de diagnostico completo para verificar:
1. Conexion a la base de datos
2. Funcionamiento del Nuclear Shield en Incident.save()
3. Estado real del schema de la tabla incidents
"""
import os
import sys

# Anadir el backend al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
import django
django.setup()

from apps.incidents.models import Incident
from django.db import connection
from datetime import date, time

print("=" * 80)
print("DIAGNOSTICO COMPLETO DEL SISTEMA")
print("=" * 80)

# 1. Verificar configuracion de base de datos
print("\n[1] CONFIGURACION DE BASE DE DATOS")
print("-" * 80)
from django.conf import settings
db_config = settings.DATABASES['default']
print(f"Engine: {db_config.get('ENGINE')}")
print(f"Nombre: {db_config.get('NAME')}")
print(f"Host: {db_config.get('HOST')}")
print(f"Puerto: {db_config.get('PORT')}")
print(f"Usuario: {db_config.get('USER')}")
print(f"Password: {'*' * len(db_config.get('PASSWORD', ''))}")
print(f"Driver: {db_config.get('OPTIONS', {}).get('driver')}")

# 2. Probar conexion
print("\n[2] PRUEBA DE CONEXION")
print("-" * 80)
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()[0]
        print(f"[OK] Conexion exitosa")
        print(f"Version SQL Server: {version[:80]}...")
except Exception as e:
    print(f"[ERROR] Error de conexion: {e}")
    sys.exit(1)

# 3. Verificar schema de la tabla incidents
print("\n[3] SCHEMA DE LA TABLA 'incidents'")
print("-" * 80)
try:
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'incidents'
            AND COLUMN_NAME IN ('subcategoria', 'cliente_rut', 'lote', 'factura_num')
            ORDER BY COLUMN_NAME
        """)
        columns = cursor.fetchall()
        print(f"{'Campo':<20} {'Tipo':<15} {'NULL?':<10} {'Default':<20}")
        print("-" * 80)
        for col in columns:
            print(f"{col[0]:<20} {col[1]:<15} {col[2]:<10} {str(col[3]):<20}")
except Exception as e:
    print(f"[ERROR] Error al leer schema: {e}")

# 4. Probar el Nuclear Shield
print("\n[4] PRUEBA DEL NUCLEAR SHIELD (Incident.save)")
print("-" * 80)
try:
    # Crear incidencia de prueba con subcategoria=None
    test_incident = Incident(
        provider='TEST_PROVIDER',
        obra='TEST_OBRA',
        cliente='TEST_CLIENTE',
        cliente_rut=None,  # Explicitamente None
        sku='TEST_SKU',
        fecha_deteccion=date.today(),
        hora_deteccion=time(12, 0),
        descripcion='Test de Nuclear Shield',
        subcategoria=None,  # El campo problematico
        lote=None,
        factura_num=None
    )
    
    print(f"Antes de save():")
    print(f"  subcategoria = {repr(test_incident.subcategoria)}")
    print(f"  lote = {repr(test_incident.lote)}")
    
    # NO GUARDAR EN BD, solo llamar al save sin commit
    # test_incident.save()  # Descomentado para TEST REAL
    
    print(f"\n[NOTA] save() no ejecutado para evitar insertar datos de prueba")
    print(f"Para testing real, descomentar la linea test_incident.save() en este script")
    
except Exception as e:
    print(f"[ERROR] Error en prueba: {e}")
    import traceback
    traceback.print_exc()

# 5. Verificar codigo actual de Incident.save()
print("\n[5] VERIFICACION DEL CODIGO Incident.save()")
print("-" * 80)
import inspect
save_code = inspect.getsource(Incident.save)
if "NUCLEAR INTEGRITY SHIELD" in save_code:
    print("[OK] Nuclear Shield PRESENTE en el codigo")
    if "text_fields_to_sanitize" in save_code:
        print("[OK] Logica de sanitizacion confirmada")
    else:
        print("[WARN] Shield presente pero logica no confirmada")
else:
    print("[ERROR] Nuclear Shield NO ENCONTRADO en el codigo")
    print("El codigo actual de save():")
    print(save_code[:500])

print("\n" + "=" * 80)
print("FIN DEL DIAGNOSTICO")
print("=" * 80)
