import os
import sys
import django

# Configurar Django para usar SQL Server
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

from apps.incidents.models import Incident
from django.db import connection

def check_sqlserver_incidents():
    """Verificar incidencias en SQL Server Express"""
    print("=== VERIFICANDO INCIDENCIAS EN SQL SERVER EXPRESS ===")
    
    try:
        # 1. Verificar conexión a SQL Server
        print("1. VERIFICANDO CONEXIÓN A SQL SERVER")
        with connection.cursor() as cursor:
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()[0]
            print(f"Versión SQL Server: {version[:100]}...")
        
        # 2. Verificar tabla incidents en SQL Server
        print("\n2. VERIFICANDO TABLA INCIDENTS EN SQL SERVER")
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM incidents")
            count = cursor.fetchone()[0]
            print(f"Total incidencias en SQL Server: {count}")
            
            if count > 0:
                cursor.execute("SELECT id, code, cliente, estado FROM incidents")
                records = cursor.fetchall()
                for record in records:
                    print(f"  - ID: {record[0]}, Código: {record[1]}, Cliente: {record[2]}, Estado: {record[3]}")
        
        # 3. Verificar modelo Django con SQL Server
        print("\n3. VERIFICANDO MODELO DJANGO CON SQL SERVER")
        incidents = Incident.objects.all()
        print(f"Incident.objects.all().count(): {incidents.count()}")
        
        for incident in incidents:
            print(f"  - ID: {incident.id}, Código: {incident.code}, Cliente: {incident.cliente}")
        
        # 4. Verificar todas las tablas en SQL Server
        print("\n4. VERIFICANDO TODAS LAS TABLAS EN SQL SERVER")
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """)
            tables = cursor.fetchall()
            print(f"Tablas encontradas: {len(tables)}")
            for table in tables:
                print(f"  - {table[0]}")
        
    except Exception as e:
        print(f"Error conectando a SQL Server: {e}")
        print("Posibles causas:")
        print("1. SQL Server Express no está ejecutándose")
        print("2. La instancia 'NB-JDIAZ25\\SQLEXPRESS' no existe")
        print("3. No hay permisos para acceder a la base de datos")
        print("4. El driver ODBC no está instalado")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_sqlserver_incidents()
