from apps.documents.models import SupplierReport
r = SupplierReport.objects.first()
print(f"Estado actual: {r.status}")
r.status = 'closed'
r.save()
print(f"Estado nuevo: {r.status}")
print("Reporte actualizado a cerrado")
