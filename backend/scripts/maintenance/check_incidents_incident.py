import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from django.db import connection

def check_incidents_incident_table():
    """Verificar la tabla incidents_incident"""
    print("=== VERIFICANDO TABLA incidents_incident ===")
    
    try:
        with connection.cursor() as cursor:
            # Verificar si la tabla existe y tiene datos
            cursor.execute("SELECT COUNT(*) FROM incidents_incident")
            count = cursor.fetchone()[0]
            print(f"Tabla 'incidents_incident': {count} registros")
            
            if count > 0:
                # Obtener la estructura de la tabla
                cursor.execute("PRAGMA table_info(incidents_incident)")
                columns = cursor.fetchall()
                print(f"Columnas de la tabla: {[col[1] for col in columns]}")
                
                # Obtener todos los registros
                cursor.execute("SELECT * FROM incidents_incident")
                records = cursor.fetchall()
                
                print(f"\n=== REGISTROS EN incidents_incident ===")
                for i, record in enumerate(records):
                    print(f"Registro {i+1}: {record}")
            
            # Verificar si hay diferencias entre las tablas
            print(f"\n=== COMPARACIÓN DE TABLAS ===")
            
            # Contar en incidents
            cursor.execute("SELECT COUNT(*) FROM incidents")
            incidents_count = cursor.fetchone()[0]
            print(f"Tabla 'incidents': {incidents_count} registros")
            
            # Contar en incidents_incident
            cursor.execute("SELECT COUNT(*) FROM incidents_incident")
            incidents_incident_count = cursor.fetchone()[0]
            print(f"Tabla 'incidents_incident': {incidents_incident_count} registros")
            
            if incidents_incident_count > incidents_count:
                print("⚠️  HAY MÁS REGISTROS EN incidents_incident QUE EN incidents")
                print("Esto podría explicar por qué no se muestran todas las incidencias en la app")
                
                # Mostrar los registros de incidents_incident
                cursor.execute("SELECT * FROM incidents_incident")
                records = cursor.fetchall()
                print(f"\n=== TODOS LOS REGISTROS EN incidents_incident ===")
                for i, record in enumerate(records):
                    print(f"Registro {i+1}: {record}")
            
    except Exception as e:
        print(f"Error al verificar tabla incidents_incident: {e}")

if __name__ == "__main__":
    check_incidents_incident_table()
