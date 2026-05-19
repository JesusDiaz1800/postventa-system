#!/usr/bin/env python
"""
Script para crear incidencia con TODOS los campos
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from django.db import connection

def create_full_incident():
    """Crear incidencia con TODOS los campos"""
    try:
        print("Creando incidencia con todos los campos...")
        
        with connection.cursor() as cursor:
            # Insertar incidencia con TODOS los campos
            cursor.execute("""
                INSERT INTO incidents (
                    code, provider, obra, cliente, cliente_rut, direccion_cliente,
                    sku, lote, factura_num, pedido_num, fecha_reporte, fecha_deteccion, hora_deteccion,
                    descripcion, acciones_inmediatas, categoria, subcategoria, prioridad, estado, created_at
                ) VALUES (
                    'INC-001', 'Proveedor Test', 'Obra Test', 'Cliente Test', '12345678-9',
                    'Dirección Test', 'SKU-001', 'LOTE-001', 'FAC-001', 'PED-001',
                    datetime('now'), date('now'), time('now'), 'Descripción de prueba', 'Acciones inmediatas',
                    'Calidad', 'Subcategoría Test', 'Alta', 'abierto', datetime('now')
                )
            """)
            print("[OK] Incidencia completa creada exitosamente")
            
            # Verificar que se creó
            cursor.execute("SELECT COUNT(*) FROM incidents")
            count = cursor.fetchone()[0]
            print(f"[OK] Total de incidencias: {count}")
            
            # Mostrar la incidencia creada
            cursor.execute("SELECT code, cliente, estado FROM incidents LIMIT 1")
            incident = cursor.fetchone()
            if incident:
                print(f"[OK] Incidencia creada: {incident[0]} - {incident[1]} - {incident[2]}")
            
    except Exception as e:
        print(f"[ERROR] Error creando incidencia: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_full_incident()
