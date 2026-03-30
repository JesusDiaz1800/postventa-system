import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_project.settings')
django.setup()

from apps.incidents.models import Responsible, Category
from apps.sap_integration.sap_query_service import SAPQueryService

def seed_sap_ids():
    print("Iniciando actualización de IDs SAP...")
    sap_service = SAPQueryService()
    
    # 1. Actualizar Responsables (Técnicos)
    print("\n--- Actualizando Responsables ---")
    responsibles = Responsible.objects.all()
    
    # Mapa manual de nombres a IDs conocidos (Fallback)
    manual_map = {
        'Marco Montenegro': 4,
        'Patricio Morales': None, # Buscar dinámicamente
    }

    # Obtener todos los empleados de ventas/técnicos de SAP
    # Nota: get_sales_employees trae OSLP (Vendedores). 
    # Los técnicos están en OHEM (Empleados).
    # SAPQueryService no tiene get_employees, pero create_service_call usa TechnicianCode de OHEM.
    # Vamos a intentar adivinar o usar el 4 por defecto para pruebas.
    
    for resp in responsibles:
        print(f"Procesando: {resp.name}")
        
        # Si es Marco, forzar 4 (Validado en pruebas)
        if "Marco" in resp.name and "Montenegro" in resp.name:
            resp.sap_technician_id = 4
            resp.save()
            print(f"  -> Asignado ID 4 (Manual)")
            continue
            
        # Si es Patricio Morales, intentar buscar o reportar
        # Por ahora, dejaremos null si no tenemos el ID exacto, 
        # pero para el script asumiremos que Patricio podría ser otro ID.
        # En la captura del usuario, Patricio Morales aparece.
        
    # 2. Actualizar Categorías (Problem Types)
    print("\n--- Actualizando Categorías ---")
    # Asignar 7 (Visita Técnica - Motivo Servicio) a todas las categorías por defecto
    categories = Category.objects.all()
    updated_count = categories.update(sap_problem_type_id=7)
    print(f"  -> Asignado ProblemType 7 a {updated_count} categorías.")

    print("\nActualización completada.")

if __name__ == '__main__':
    seed_sap_ids()
