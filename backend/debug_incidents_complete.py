import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from apps.incidents.models import Incident
from django.db import connection

def debug_incidents_complete():
    """Debug completo de incidencias"""
    print("=== DEBUG COMPLETO DE INCIDENCIAS ===")
    
    try:
        # 1. Verificar modelo Django
        print("1. VERIFICANDO MODELO DJANGO")
        incidents_django = Incident.objects.all()
        print(f"Incident.objects.all().count(): {incidents_django.count()}")
        
        for incident in incidents_django:
            print(f"  - ID: {incident.id}, Código: {incident.code}, Cliente: {incident.cliente}")
        
        # 2. Verificar tabla SQLite directamente
        print("\n2. VERIFICANDO TABLA SQLITE DIRECTAMENTE")
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM incidents")
            count = cursor.fetchone()[0]
            print(f"SELECT COUNT(*) FROM incidents: {count}")
            
            if count > 0:
                cursor.execute("SELECT id, code, cliente, estado FROM incidents")
                records = cursor.fetchall()
                for record in records:
                    print(f"  - ID: {record[0]}, Código: {record[1]}, Cliente: {record[2]}, Estado: {record[3]}")
        
        # 3. Verificar si hay incidencias en otras tablas
        print("\n3. VERIFICANDO OTRAS TABLAS")
        with connection.cursor() as cursor:
            # Buscar todas las tablas que podrían contener incidencias
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            all_tables = cursor.fetchall()
            
            for table in all_tables:
                table_name = table[0]
                if 'incident' in table_name.lower() and table_name != 'incidents':
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        count = cursor.fetchone()[0]
                        if count > 0:
                            print(f"  - Tabla '{table_name}': {count} registros")
                            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                            records = cursor.fetchall()
                            for record in records:
                                print(f"    Registro: {record}")
                    except Exception as e:
                        print(f"    Error en tabla '{table_name}': {e}")
        
        # 4. Verificar si hay incidencias con diferentes estados
        print("\n4. VERIFICANDO INCIDENCIAS POR ESTADO")
        with connection.cursor() as cursor:
            cursor.execute("SELECT estado, COUNT(*) FROM incidents GROUP BY estado")
            estado_counts = cursor.fetchall()
            for estado, count in estado_counts:
                print(f"  - Estado '{estado}': {count} incidencias")
        
        # 5. Verificar si hay incidencias creadas por diferentes usuarios
        print("\n5. VERIFICANDO INCIDENCIAS POR USUARIO")
        with connection.cursor() as cursor:
            cursor.execute("SELECT created_by_id, COUNT(*) FROM incidents GROUP BY created_by_id")
            user_counts = cursor.fetchall()
            for user_id, count in user_counts:
                print(f"  - Usuario ID {user_id}: {count} incidencias")
        
        # 6. Verificar si hay incidencias con fechas diferentes
        print("\n6. VERIFICANDO INCIDENCIAS POR FECHA")
        with connection.cursor() as cursor:
            cursor.execute("SELECT fecha_reporte, COUNT(*) FROM incidents GROUP BY DATE(fecha_reporte)")
            date_counts = cursor.fetchall()
            for date, count in date_counts:
                print(f"  - Fecha '{date}': {count} incidencias")
        
        # 7. Verificar si hay incidencias en la tabla de migraciones
        print("\n7. VERIFICANDO MIGRACIONES")
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM django_migrations WHERE app='incidents'")
            migrations = cursor.fetchall()
            print(f"  - Migraciones de incidents: {len(migrations)}")
            for migration in migrations:
                print(f"    - {migration[0]}")
        
    except Exception as e:
        print(f"Error en debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_incidents_complete()
