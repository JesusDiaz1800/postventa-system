#!/usr/bin/env python3
"""
Limpieza final de la tabla document_templates
"""

import os
import django

def setup_django():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
    django.setup()

def final_cleanup():
    print("🧹 Limpieza final de document_templates...")
    
    try:
        from django.db import connection
        
        with connection.cursor() as cursor:
            # Buscar todas las foreign keys que referencian document_templates
            cursor.execute("""
                SELECT 
                    fk.name as constraint_name,
                    OBJECT_NAME(fk.parent_object_id) as parent_table
                FROM sys.foreign_keys fk
                WHERE fk.referenced_object_id = OBJECT_ID('document_templates')
            """)
            
            foreign_keys = cursor.fetchall()
            print(f"🔍 Foreign keys encontradas: {foreign_keys}")
            
            # Eliminar cada foreign key
            for fk_name, parent_table in foreign_keys:
                try:
                    cursor.execute(f"ALTER TABLE {parent_table} DROP CONSTRAINT {fk_name}")
                    print(f"  ✅ Eliminado constraint: {fk_name} de tabla {parent_table}")
                except Exception as e:
                    print(f"  ⚠️ Error eliminando {fk_name}: {e}")
            
            # Ahora eliminar la tabla
            try:
                cursor.execute("DROP TABLE document_templates")
                print("✅ Tabla document_templates eliminada exitosamente")
            except Exception as e:
                print(f"⚠️ Error eliminando tabla: {e}")
            
            # Verificar tablas restantes
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME LIKE '%document%'
                ORDER BY TABLE_NAME
            """)
            
            remaining = [row[0] for row in cursor.fetchall()]
            print(f"📋 Tablas restantes: {remaining}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    setup_django()
    final_cleanup()
    print("🎉 Limpieza final completada")
