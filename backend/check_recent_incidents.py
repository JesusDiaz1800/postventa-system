import os
import django
from datetime import datetime, timedelta

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.incidents.models import Incident

def check_recent_incidents():
    one_hour_ago = datetime.now() - timedelta(hours=1)
    print(f"--- Incidencias creadas desde {one_hour_ago} ---")
    incidents = Incident.objects.filter(created_at__gte=one_hour_ago)
    if not incidents.exists():
        print("No se encontraron incidencias en la última hora.")
        # Ver las últimas 3 de todas formas
        incidents = Incident.objects.order_by('-id')[:3]
    
    for inc in incidents:
        print(f"ID: {inc.id}, Code: {inc.code}, SAP: {inc.sap_doc_num}, User: {inc.created_by}, Created: {inc.created_at}")

if __name__ == "__main__":
    check_recent_incidents()
