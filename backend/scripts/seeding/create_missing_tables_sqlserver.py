#!/usr/bin/env python
"""
Script para crear las tablas faltantes directamente en SQL Server
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def main():
    print("=== CREACION DE TABLAS FALTANTES (SQL SERVER) ===")
    
    # Configurar Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
    
    try:
        import django
        django.setup()
        print("✓ Django configurado correctamente")
    except Exception as e:
        print(f"✗ Error configurando Django: {e}")
        return False
    
    try:
        from django.db import connection
        
        print("\n[1/4] Verificando tablas existentes...")
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT TABLE_NAME 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_NAME IN ('incidents_incident', 'incidents_incidenttimeline')
                """)
                existing_tables = [row[0] for row in cursor.fetchall()]
                print(f"  Tablas existentes: {existing_tables}")
                
        except Exception as e:
            print(f"⚠ Error verificando tablas: {e}")
        
        print("\n[2/4] Creando tabla incidents_incident...")
        try:
            with connection.cursor() as cursor:
                # Crear tabla incidents_incident
                cursor.execute("""
                    CREATE TABLE incidents_incident (
                        id BIGINT IDENTITY(1,1) PRIMARY KEY,
                        code NVARCHAR(20) NOT NULL UNIQUE,
                        created_by_id BIGINT NULL,
                        provider NVARCHAR(200) NOT NULL,
                        obra NVARCHAR(200) NOT NULL,
                        cliente NVARCHAR(200) NOT NULL,
                        cliente_rut NVARCHAR(20) NULL,
                        direccion_cliente NTEXT NULL,
                        sku NVARCHAR(100) NOT NULL,
                        lote NVARCHAR(100) NULL,
                        factura_num NVARCHAR(100) NULL,
                        pedido_num NVARCHAR(100) NULL,
                        fecha_reporte DATETIME2 NOT NULL,
                        fecha_deteccion DATE NOT NULL,
                        hora_deteccion TIME NOT NULL,
                        descripcion NTEXT NOT NULL,
                        acciones_inmediatas NTEXT NULL,
                        categoria NVARCHAR(50) NOT NULL,
                        subcategoria NVARCHAR(100) NULL,
                        prioridad NVARCHAR(20) NOT NULL DEFAULT 'media',
                        estado NVARCHAR(20) NOT NULL DEFAULT 'abierto',
                        assigned_to_id BIGINT NULL,
                        lab_required BIT NOT NULL DEFAULT 0,
                        acciones_posteriores NTEXT NULL,
                        nc_number NVARCHAR(100) NULL,
                        np_number NVARCHAR(100) NULL,
                        ai_analysis NVARCHAR(MAX) NULL,
                        ai_analysis_accuracy FLOAT NULL,
                        fecha_cierre DATE NULL,
                        closed_by_id BIGINT NULL,
                        closed_at DATETIME2 NULL,
                        created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
                        updated_at DATETIME2 NOT NULL DEFAULT GETDATE()
                    )
                """)
                print("✓ Tabla incidents_incident creada")
                
        except Exception as e:
            print(f"⚠ Error creando incidents_incident: {e}")
        
        print("\n[3/4] Creando tabla incidents_incidenttimeline...")
        try:
            with connection.cursor() as cursor:
                # Crear tabla incidents_incidenttimeline
                cursor.execute("""
                    CREATE TABLE incidents_incidenttimeline (
                        id BIGINT IDENTITY(1,1) PRIMARY KEY,
                        incident_id BIGINT NOT NULL,
                        action NVARCHAR(50) NOT NULL,
                        description NTEXT NOT NULL,
                        user_id BIGINT NULL,
                        metadata NVARCHAR(MAX) NULL,
                        created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
                        FOREIGN KEY (incident_id) REFERENCES incidents_incident(id) ON DELETE CASCADE
                    )
                """)
                print("✓ Tabla incidents_incidenttimeline creada")
                
        except Exception as e:
            print(f"⚠ Error creando incidents_incidenttimeline: {e}")
        
        print("\n[4/4] Verificando tablas creadas...")
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT TABLE_NAME 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_NAME IN ('incidents_incident', 'incidents_incidenttimeline')
                """)
                final_tables = [row[0] for row in cursor.fetchall()]
                print(f"  Tablas finales: {final_tables}")
                
                if 'incidents_incident' in final_tables:
                    print("✓ Tabla incidents_incident disponible")
                else:
                    print("⚠ Tabla incidents_incident NO disponible")
                
                if 'incidents_incidenttimeline' in final_tables:
                    print("✓ Tabla incidents_incidenttimeline disponible")
                else:
                    print("⚠ Tabla incidents_incidenttimeline NO disponible")
                    
        except Exception as e:
            print(f"⚠ Error verificando tablas: {e}")
        
        print("\n✓ Proceso completado")
        return True
        
    except Exception as e:
        print(f"✗ Error en proceso: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    if success:
        print("\n=== TABLAS CREADAS ===")
    else:
        print("\n=== ERROR - REVISAR LOGS ===")
    
    input("\nPresiona Enter para continuar...")
