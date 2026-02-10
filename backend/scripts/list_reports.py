from apps.documents.models import SupplierReport
reports = SupplierReport.objects.all()
print(f"Total reportes: {reports.count()}")
for r in reports:
    print(f"ID: {r.id} | Numero: {r.report_number} | Incidencia: {r.related_incident_id} | Estado: {r.status}")
