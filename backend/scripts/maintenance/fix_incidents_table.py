#!/usr/bin/env python
"""
Script para corregir la tabla de incidencias
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from django.db import connection

def fix_incidents_table():
    """Corregir la tabla de incidencias"""
    try:
        print("Verificando estructura de la tabla incidents...")
        
        with connection.cursor() as cursor:
            # Verificar si la tabla existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='incidents'")
            table_exists = cursor.fetchone()
            
            if not table_exists:
                print("Tabla incidents no existe. Creándola...")
                # Crear tabla incidents básica
                cursor.execute("""
                    CREATE TABLE incidents (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        code VARCHAR(50) UNIQUE NOT NULL,
                        provider VARCHAR(200),
                        obra VARCHAR(200),
                        cliente VARCHAR(200),
                        cliente_rut VARCHAR(20),
                        direccion_cliente TEXT,
                        sku VARCHAR(100),
                        lote VARCHAR(100),
                        factura_num VARCHAR(100),
                        pedido_num VARCHAR(100),
                        fecha_reporte DATE,
                        fecha_deteccion DATE,
                        hora_deteccion TIME,
                        descripcion TEXT,
                        acciones_inmediatas TEXT,
                        categoria VARCHAR(100),
                        subcategoria VARCHAR(100),
                        prioridad VARCHAR(50),
                        estado VARCHAR(50) DEFAULT 'abierto',
                        responsable VARCHAR(200),
                        escalated_to_quality BOOLEAN DEFAULT 0,
                        escalated_to_supplier BOOLEAN DEFAULT 0,
                        escalation_date DATE,
                        escalation_reason TEXT,
                        acciones_posteriores TEXT,
                        nc_number VARCHAR(100),
                        np_number VARCHAR(100),
                        ai_analysis TEXT,
                        ai_analysis_accuracy DECIMAL(5,2),
                        fecha_cierre DATE,
                        closed_at DATETIME,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                print("Tabla incidents creada exitosamente")
            else:
                print("Tabla incidents ya existe")
                
                # Verificar columnas existentes
                cursor.execute("PRAGMA table_info(incidents)")
                columns = cursor.fetchall()
                print(f"Columnas existentes: {len(columns)}")
                for col in columns:
                    print(f"  - {col[1]} ({col[2]})")
                
                # Verificar si faltan columnas críticas
                column_names = [col[1] for col in columns]
                required_columns = ['id', 'code', 'estado', 'prioridad', 'created_at']
                
                missing_columns = []
                for req_col in required_columns:
                    if req_col not in column_names:
                        missing_columns.append(req_col)
                
                if missing_columns:
                    print(f"Columnas faltantes: {missing_columns}")
                    # Agregar columnas faltantes
                    for col in missing_columns:
                        if col == 'id':
                            continue  # ID ya existe
                        elif col == 'code':
                            cursor.execute("ALTER TABLE incidents ADD COLUMN code VARCHAR(50)")
                        elif col == 'estado':
                            cursor.execute("ALTER TABLE incidents ADD COLUMN estado VARCHAR(50) DEFAULT 'abierto'")
                        elif col == 'prioridad':
                            cursor.execute("ALTER TABLE incidents ADD COLUMN prioridad VARCHAR(50)")
                        elif col == 'created_at':
                            cursor.execute("ALTER TABLE incidents ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP")
                    print("Columnas faltantes agregadas")
                else:
                    print("Todas las columnas requeridas están presentes")
            
            # Verificar datos existentes
            cursor.execute("SELECT COUNT(*) FROM incidents")
            count = cursor.fetchone()[0]
            print(f"Registros en la tabla: {count}")
            
            if count == 0:
                print("Insertando datos de prueba...")
                cursor.execute("""
                    INSERT INTO incidents (
                        code, provider, obra, cliente, cliente_rut, descripcion, 
                        categoria, prioridad, estado, created_at
                    ) VALUES (
                        'INC-001', 'Proveedor Test', 'Obra Test', 'Cliente Test', '12345678-9',
                        'Descripción de prueba', 'Calidad', 'Alta', 'abierto',
                        datetime('now')
                    )
                """)
                print("Datos de prueba insertados")
            
        print("Tabla incidents verificada y corregida")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_incidents_table()
