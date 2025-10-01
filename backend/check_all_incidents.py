import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from django.db import connection

def check_all_incident_tables():
    """Verificar todas las tablas que podrían contener incidencias"""
    print("=== VERIFICANDO TODAS LAS TABLAS DE INCIDENCIAS ===")
    
    try:
        with connection.cursor() as cursor:
            # 1. Verificar tabla incidents
            cursor.execute("SELECT COUNT(*) FROM incidents")
            incidents_count = cursor.fetchone()[0]
            print(f"Tabla 'incidents': {incidents_count} registros")
            
            if incidents_count > 0:
                cursor.execute("SELECT id, code, cliente, estado FROM incidents")
                incidents = cursor.fetchall()
                for incident in incidents:
                    print(f"  - ID: {incident[0]}, Código: {incident[1]}, Cliente: {incident[2]}, Estado: {incident[3]}")
            
            # 2. Verificar si hay otras tablas relacionadas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%incident%'")
            incident_tables = cursor.fetchall()
            print(f"\nTablas relacionadas con 'incident': {[table[0] for table in incident_tables]}")
            
            # 3. Verificar tabla incident_images
            try:
                cursor.execute("SELECT COUNT(*) FROM incident_images")
                images_count = cursor.fetchone()[0]
                print(f"Tabla 'incident_images': {images_count} registros")
            except:
                print("Tabla 'incident_images' no existe o tiene error")
            
            # 4. Verificar tabla incident_timeline
            try:
                cursor.execute("SELECT COUNT(*) FROM incident_timeline")
                timeline_count = cursor.fetchone()[0]
                print(f"Tabla 'incident_timeline': {timeline_count} registros")
            except:
                print("Tabla 'incident_timeline' no existe o tiene error")
            
            # 5. Verificar tabla incident_attachments
            try:
                cursor.execute("SELECT COUNT(*) FROM incident_attachments")
                attachments_count = cursor.fetchone()[0]
                print(f"Tabla 'incident_attachments': {attachments_count} registros")
            except:
                print("Tabla 'incident_attachments' no existe o tiene error")
            
            # 6. Verificar tabla lab_reports
            try:
                cursor.execute("SELECT COUNT(*) FROM lab_reports")
                lab_reports_count = cursor.fetchone()[0]
                print(f"Tabla 'lab_reports': {lab_reports_count} registros")
            except:
                print("Tabla 'lab_reports' no existe o tiene error")
            
            # 7. Verificar todas las tablas que contengan datos
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            all_tables = cursor.fetchall()
            print(f"\n=== TODAS LAS TABLAS EN LA BASE DE DATOS ===")
            for table in all_tables:
                table_name = table[0]
                if not table_name.startswith('sqlite_'):
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        count = cursor.fetchone()[0]
                        if count > 0:
                            print(f"Tabla '{table_name}': {count} registros")
                    except:
                        print(f"Tabla '{table_name}': Error al contar")
                        
    except Exception as e:
        print(f"Error al verificar tablas: {e}")

if __name__ == "__main__":
    check_all_incident_tables()
