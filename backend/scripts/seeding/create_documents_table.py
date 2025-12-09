#!/usr/bin/env python
"""
Script para crear la tabla documents manualmente
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

from django.db import connection

def create_documents_table():
    """Crear la tabla documents manualmente"""
    print("🔧 Creando tabla documents...")
    
    try:
        with connection.cursor() as cursor:
            # Verificar si la tabla ya existe
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = 'documents'
            """)
            
            exists = cursor.fetchone()[0] > 0
            
            if exists:
                print("✅ La tabla 'documents' ya existe")
                return True
            
            # Crear la tabla documents
            cursor.execute("""
                CREATE TABLE documents (
                    id bigint IDENTITY(1,1) PRIMARY KEY,
                    title nvarchar(200) NOT NULL,
                    document_type nvarchar(20) NOT NULL DEFAULT 'oficial',
                    version int NOT NULL DEFAULT 1,
                    docx_path nvarchar(500) NULL,
                    pdf_path nvarchar(500) NULL,
                    content_html ntext NULL,
                    placeholders_data ntext NULL,
                    notes ntext NULL,
                    is_final bit NOT NULL DEFAULT 0,
                    created_at datetime2 NOT NULL DEFAULT GETDATE(),
                    updated_at datetime2 NOT NULL DEFAULT GETDATE(),
                    created_by_id bigint NULL,
                    incident_id bigint NULL,
                    FOREIGN KEY (created_by_id) REFERENCES users(id),
                    FOREIGN KEY (incident_id) REFERENCES incidents_incident(id)
                )
            """)
            
            print("✅ Tabla 'documents' creada exitosamente")
            
            # Verificar que se creó correctamente
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = 'documents'
            """)
            
            created = cursor.fetchone()[0] > 0
            
            if created:
                print("✅ Verificación exitosa: tabla 'documents' existe")
                return True
            else:
                print("❌ Error: tabla 'documents' no se creó")
                return False
                
    except Exception as e:
        print(f"❌ Error creando tabla: {str(e)}")
        return False

if __name__ == "__main__":
    create_documents_table()
