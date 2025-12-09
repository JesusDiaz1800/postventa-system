#!/usr/bin/env python3
"""
Script de limpieza usando Django ORM
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def setup_django():
    """Configurar Django"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
    django.setup()

def cleanup_database():
    """Limpiar base de datos usando Django"""
    print("🧹 Iniciando limpieza de base de datos...")
    
    try:
        from django.db import connection
        
        with connection.cursor() as cursor:
            # Verificar tablas existentes
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME IN ('document_templates', 'documents', 'document_versions', 'document_conversions')
            """)
            
            existing_tables = [row[0] for row in cursor.fetchall()]
            print(f"📋 Tablas encontradas: {existing_tables}")
            
            if not existing_tables:
                print("✅ No hay tablas para limpiar")
                return
            
            # Eliminar foreign keys primero
            print("🔧 Eliminando foreign keys...")
            
            foreign_keys_to_drop = [
                'document_versions_created_by_id_fk',
                'document_conversions_created_by_id_fk', 
                'document_templates_created_by_id_fk',
                'documents_created_by_id_fk',
                'documents_incident_id_fk'
            ]
            
            for fk_name in foreign_keys_to_drop:
                try:
                    cursor.execute(f"""
                        IF EXISTS (SELECT * FROM sys.foreign_keys WHERE name = '{fk_name}')
                            ALTER TABLE {fk_name.split('_')[0]} DROP CONSTRAINT {fk_name};
                    """)
                    print(f"  ✅ Eliminado constraint: {fk_name}")
                except Exception as e:
                    print(f"  ⚠️ No se pudo eliminar {fk_name}: {e}")
            
            # Eliminar tablas
            print("🗑️ Eliminando tablas...")
            
            tables_to_drop = [
                'document_versions',
                'document_conversions', 
                'document_templates',
                'documents'
            ]
            
            for table in tables_to_drop:
                try:
                    cursor.execute(f"""
                        IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{table}')
                            DROP TABLE {table};
                    """)
                    print(f"  ✅ Eliminada tabla: {table}")
                except Exception as e:
                    print(f"  ⚠️ No se pudo eliminar {table}: {e}")
            
            print("✅ Limpieza completada")
            
    except Exception as e:
        print(f"❌ Error durante la limpieza: {e}")

def verify_cleanup():
    """Verificar que la limpieza fue exitosa"""
    print("🔍 Verificando limpieza...")
    
    try:
        from django.db import connection
        
        with connection.cursor() as cursor:
            # Verificar tablas restantes
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE' 
                AND TABLE_NAME LIKE '%document%'
                ORDER BY TABLE_NAME
            """)
            
            remaining_tables = [row[0] for row in cursor.fetchall()]
            print(f"📋 Tablas de documentos restantes: {remaining_tables}")
            
            # Verificar índices en incidents
            cursor.execute("""
                SELECT COUNT(*) as total_indexes
                FROM sys.indexes 
                WHERE object_id = OBJECT_ID('incidents')
            """)
            
            indexes_count = cursor.fetchone()[0]
            print(f"📈 Índices en tabla incidents: {indexes_count}")
            
            print("✅ Verificación completada")
            
    except Exception as e:
        print(f"❌ Error durante verificación: {e}")

if __name__ == "__main__":
    setup_django()
    cleanup_database()
    verify_cleanup()
    print("🎉 Proceso de limpieza finalizado")
