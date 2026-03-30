import os
import django
from datetime import datetime, date

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.incidents.models import Incident
from apps.documents.models import VisitReport

def check_pe_status():
    print("--- Incidencias en POSTVENTA_PE (Hoy 24/Mar) ---")
    try:
        incidents = Incident.objects.using('default_pe').filter(created_at__date=date(2026, 3, 24))
        
        if not incidents.exists():
            print("No se encontraron incidencias creadas hoy en PE.")
            incidents = Incident.objects.using('default_pe').order_by('-id')[:5]
        
        for inc in incidents:
            print(f"ID: {inc.id}, Code: {inc.code}, SAP Doc: {inc.sap_doc_num}, Status: {inc.estado}, Created: {inc.created_at}")

        print("\n--- Ultimos 5 Reportes de Visita en POSTVENTA_PE ---")
        reports = VisitReport.objects.using('default_pe').order_by('-id')[:5]
        for rep in reports:
            incident_code = "N/A"
            try:
                # En muchos modelos de este sistema el campo se llama 'related_incident' o 'incident'
                # Vamos a intentar detectar el campo de la relación
                for field in rep._meta.get_fields():
                    if field.is_relation and field.related_model == Incident:
                        rel_obj = getattr(rep, field.name)
                        if rel_obj: incident_code = rel_obj.code
                        break
            except: pass
            
            print(f"ID: {rep.id}, Incident: {incident_code}, SAP Status: {rep.sap_sync_status}, Tech ID: {rep.technician_id}")
    except Exception as e:
        print(f"Error consultando DB PE: {e}")

if __name__ == "__main__":
    check_pe_status()
