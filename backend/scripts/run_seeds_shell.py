from apps.incidents.models import Responsible, Category
from apps.sap_integration.sap_query_service import SAPQueryService

print("Iniciando actualización de IDs SAP (Shell Mode)...")

try:
    sap_service = SAPQueryService()

    # 1. Actualizar Responsables (Técnicos)
    print("\n--- Actualizando Responsables ---")
    responsibles = Responsible.objects.all()

    for resp in responsibles:
        print(f"Procesando: {resp.name}")
        
        # Si es Marco, forzar 4 (Validado en pruebas)
        if "Marco" in resp.name and "Montenegro" in resp.name:
            resp.sap_technician_id = 4
            resp.save()
            print(f"  -> Asignado ID 4 (Marco Montenegro)")
            continue
            
        # Si es Patricio Morales, asignar según usuario anterior (Validar ID real en futuro)
        # Por ahora lo dejamos pasar o le asignamos si tuviéramos id.
        
    # 2. Actualizar Categorías (Problem Types)
    print("\n--- Actualizando Categorías ---")
    # Asignar 7 (Visita Técnica) a todas las categorías por defecto
    categories = Category.objects.all()
    updated_count = categories.update(sap_problem_type_id=7)
    print(f"  -> Asignado ProblemType 7 a {updated_count} categorías.")

    print("\nActualización completada.")
except Exception as e:
    print(f"Error en script: {e}")
