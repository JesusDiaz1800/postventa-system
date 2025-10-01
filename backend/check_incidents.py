import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from apps.incidents.models import Incident

def check_incidents():
    """Verificar las incidencias en la base de datos"""
    print("=== VERIFICANDO INCIDENCIAS EN LA BASE DE DATOS ===")
    
    try:
        # Contar total de incidencias
        total_count = Incident.objects.count()
        print(f"Total de incidencias: {total_count}")
        
        if total_count > 0:
            # Mostrar todas las incidencias
            incidents = Incident.objects.all()
            print("\n=== DETALLES DE INCIDENCIAS ===")
            for incident in incidents:
                print(f"ID: {incident.id}")
                print(f"Código: {incident.code}")
                print(f"Cliente: {incident.cliente}")
                print(f"Estado: {incident.estado}")
                print(f"Prioridad: {incident.prioridad}")
                print(f"Fecha Reporte: {incident.fecha_reporte}")
                print(f"Fecha Detección: {incident.fecha_deteccion}")
                print(f"Descripción: {incident.descripcion[:100]}...")
                print("-" * 50)
        else:
            print("No hay incidencias en la base de datos.")
            
        # Verificar la tabla específica
        print(f"\n=== INFORMACIÓN DE LA TABLA ===")
        print(f"Tabla utilizada: {Incident._meta.db_table}")
        print(f"Modelo: {Incident.__name__}")
        
    except Exception as e:
        print(f"Error al verificar incidencias: {e}")

if __name__ == "__main__":
    check_incidents()
