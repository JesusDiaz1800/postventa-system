import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from django.conf import settings
from django.db import connection
from apps.incidents.models import Incident

def check_real_database():
    """Verificar qué base de datos está usando realmente Django"""
    print("=== VERIFICANDO BASE DE DATOS REAL ===")
    
    try:
        # 1. Verificar configuración de Django
        print("1. CONFIGURACIÓN DE DJANGO")
        print(f"ENGINE: {settings.DATABASES['default']['ENGINE']}")
        print(f"NAME: {settings.DATABASES['default']['NAME']}")
        print(f"HOST: {settings.DATABASES['default'].get('HOST', 'No especificado')}")
        print(f"PORT: {settings.DATABASES['default'].get('PORT', 'No especificado')}")
        print(f"USER: {settings.DATABASES['default'].get('USER', 'No especificado')}")
        
        # 2. Verificar conexión real
        print("\n2. CONEXIÓN REAL")
        with connection.cursor() as cursor:
            # Obtener información de la base de datos
            cursor.execute("SELECT sqlite_version()")
            version = cursor.fetchone()[0]
            print(f"Versión SQLite: {version}")
            
            # Verificar si es realmente SQLite
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"Tablas encontradas: {len(tables)}")
            
            # Verificar tabla incidents
            cursor.execute("SELECT COUNT(*) FROM incidents")
            count = cursor.fetchone()[0]
            print(f"Incidencias en SQLite: {count}")
            
            if count > 0:
                cursor.execute("SELECT id, code, cliente FROM incidents")
                records = cursor.fetchall()
                for record in records:
                    print(f"  - ID: {record[0]}, Código: {record[1]}, Cliente: {record[2]}")
        
        # 3. Verificar modelo Django
        print("\n3. MODELO DJANGO")
        incidents = Incident.objects.all()
        print(f"Incident.objects.all().count(): {incidents.count()}")
        
        for incident in incidents:
            print(f"  - ID: {incident.id}, Código: {incident.code}, Cliente: {incident.cliente}")
        
        # 4. Verificar si hay configuración de SQL Server
        print("\n4. VERIFICANDO CONFIGURACIÓN SQL SERVER")
        if 'mssql' in settings.DATABASES['default']['ENGINE'].lower():
            print("✅ Configurado para SQL Server")
        elif 'sqlite' in settings.DATABASES['default']['ENGINE'].lower():
            print("⚠️  Configurado para SQLite (no SQL Server)")
        else:
            print(f"❓ Configurado para: {settings.DATABASES['default']['ENGINE']}")
        
        # 5. Verificar variables de entorno
        print("\n5. VARIABLES DE ENTORNO")
        env_vars = ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT']
        for var in env_vars:
            value = os.environ.get(var, 'No definida')
            print(f"  - {var}: {value}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_real_database()
