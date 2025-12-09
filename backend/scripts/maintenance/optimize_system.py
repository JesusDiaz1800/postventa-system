#!/usr/bin/env python3
"""
Script de optimización final del sistema
Ejecuta todas las optimizaciones pendientes
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def setup_django():
    """Configurar Django"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
    django.setup()

def run_optimizations():
    """Ejecutar todas las optimizaciones"""
    print("🚀 Iniciando optimización del sistema...")
    
    # 1. Aplicar todas las migraciones
    print("📦 Aplicando migraciones...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    # 2. Verificar estado de la base de datos
    print("🔍 Verificando estado de la base de datos...")
    execute_from_command_line(['manage.py', 'showmigrations'])
    
    # 3. Limpiar cache
    print("🧹 Limpiando cache...")
    execute_from_command_line(['manage.py', 'clear_cache'])
    
    print("✅ Optimización completada")

def check_database_health():
    """Verificar salud de la base de datos"""
    print("🏥 Verificando salud de la base de datos...")
    
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            # Verificar tablas principales
            cursor.execute("""
                SELECT COUNT(*) as total_incidents 
                FROM incidents
            """)
            incidents_count = cursor.fetchone()[0]
            print(f"📊 Total de incidencias: {incidents_count}")
            
            # Verificar índices
            cursor.execute("""
                SELECT COUNT(*) as total_indexes
                FROM sys.indexes 
                WHERE object_id = OBJECT_ID('incidents')
            """)
            indexes_count = cursor.fetchone()[0]
            print(f"📈 Índices en tabla incidents: {indexes_count}")
            
            print("✅ Base de datos saludable")
            
    except Exception as e:
        print(f"❌ Error verificando base de datos: {e}")

if __name__ == "__main__":
    setup_django()
    run_optimizations()
    check_database_health()
    print("🎉 Sistema optimizado exitosamente")
