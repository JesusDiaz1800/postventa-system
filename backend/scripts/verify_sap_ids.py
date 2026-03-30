from apps.incidents.models import Responsible, Category
print("--- Verificación de IDs SAP ---")
print("Responsables:")
for r in Responsible.objects.all():
    print(f"  - {r.name}: {r.sap_technician_id}")

print("\nCategorías:")
for c in Category.objects.all()[:5]: # Mostrar solo primeras 5
    print(f"  - {c.name}: {c.sap_problem_type_id}")
