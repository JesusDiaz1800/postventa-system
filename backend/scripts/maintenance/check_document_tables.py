#!/usr/bin/env python
"""
Script para verificar las tablas de documentos
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

from django.db import connection

def check_document_tables():
    """Verificar tablas de documentos"""
    print("🔍 Verificando tablas de documentos...")
    
    try:
        with connection.cursor() as cursor:
            # Obtener tablas relacionadas con documentos
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME LIKE '%document%' OR TABLE_NAME LIKE '%report%'
                ORDER BY TABLE_NAME
            """)
            
            tables = cursor.fetchall()
            
            print(f"📊 Tablas de documentos encontradas: {len(tables)}")
            for table in tables:
                print(f"  - {table[0]}")
            
            # Verificar si existe la tabla 'documents' específicamente
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = 'documents'
            """)
            
            documents_exists = cursor.fetchone()[0] > 0
            print(f"\n🔍 Tabla 'documents' existe: {'✅ SÍ' if documents_exists else '❌ NO'}")
            
            # Verificar si hay alguna tabla que contenga 'documents' en el nombre
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME LIKE '%documents%'
                ORDER BY TABLE_NAME
            """)
            
            documents_tables = cursor.fetchall()
            print(f"\n📄 Tablas que contienen 'documents':")
            for table in documents_tables:
                print(f"  - {table[0]}")
            
            return documents_exists, [table[0] for table in tables]
            
    except Exception as e:
        print(f"❌ Error verificando tablas: {str(e)}")
        return False, []

if __name__ == "__main__":
    check_document_tables()
