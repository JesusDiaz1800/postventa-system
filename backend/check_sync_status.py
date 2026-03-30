import os
import django
import sys

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.incidents.models import Incident
from apps.documents.models import VisitReport

def check_status():
    print("--- Últimos 5 Incidentes ---")
    incidents = Incident.objects.order_by('-id')[:5]
    for inc in incidents:
        print(f"ID: {inc.id}, Code: {inc.code}, SAP Doc: {inc.sap_doc_num}, Status: {inc.estado}, Created: {inc.created_at}")
        
    print("\n--- Últimos 5 Reportes de Visita ---")
    reports = VisitReport.objects.order_by('-id')[:5]
    for rep in reports:
        print(f"ID: {rep.id}, Incident ID: {rep.incident_id}, SAP Sync: {rep.sap_sync_status}, Technician: {rep.technician_id}")

if __name__ == "__main__":
    check_status()
