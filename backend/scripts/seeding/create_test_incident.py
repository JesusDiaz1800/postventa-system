#!/usr/bin/env python
"""
Script para crear incidencia de prueba con todos los campos requeridos
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from django.db import connection

def create_test_incident():
    """Crear incidencia de prueba con todos los campos"""
    try:
        print("Creando incidencia de prueba...")
        
        with connection.cursor() as cursor:
            # Insertar incidencia con todos los campos requeridos
            cursor.execute("""
                INSERT INTO incidents (
                    code, provider, obra, cliente, cliente_rut, direccion_cliente,
                    sku, lote, factura_num, pedido_num, fecha_reporte, descripcion, 
                    categoria, prioridad, estado, created_at
                ) VALUES (
                    'INC-001', 'Proveedor Test', 'Obra Test', 'Cliente Test', '12345678-9',
                    'Dirección Test', 'SKU-001', 'LOTE-001', 'FAC-001', 'PED-001',
                    datetime('now'), 'Descripción de prueba', 'Calidad', 'Alta', 'abierto',
                    datetime('now')
                )
            """)
            print("[OK] Incidencia de prueba creada exitosamente")
            
            # Verificar que se creó
            cursor.execute("SELECT COUNT(*) FROM incidents")
            count = cursor.fetchone()[0]
            print(f"[OK] Total de incidencias: {count}")
            
    except Exception as e:
        print(f"[ERROR] Error creando incidencia: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_test_incident()