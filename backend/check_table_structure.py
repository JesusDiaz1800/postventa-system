#!/usr/bin/env python
"""
Script para verificar la estructura de las tablas
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

from django.db import connection

def check_table_structure():
    """Verificar estructura de tablas"""
    print("🔍 Verificando estructura de tablas...")
    
    try:
        with connection.cursor() as cursor:
            # Verificar estructura de la tabla users
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'users'
                ORDER BY ORDINAL_POSITION
            """)
            
            users_columns = cursor.fetchall()
            print("\n📊 Estructura de tabla 'users':")
            for col in users_columns:
                print(f"  - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
            
            # Verificar estructura de la tabla incidents_incident
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'incidents_incident'
                ORDER BY ORDINAL_POSITION
            """)
            
            incidents_columns = cursor.fetchall()
            print("\n📊 Estructura de tabla 'incidents_incident':")
            for col in incidents_columns:
                print(f"  - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
            
            return users_columns, incidents_columns
            
    except Exception as e:
        print(f"❌ Error verificando estructura: {str(e)}")
        return [], []

if __name__ == "__main__":
    check_table_structure()
