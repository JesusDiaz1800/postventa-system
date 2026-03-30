import os
import django

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.incidents.models import Incident, IncidentTimeline

def check_timelines():
    print("--- Errores de Sincronizacion en POSTVENTA_PE ---")
    inc_codes = ['INC-2026-0008', 'INC-2026-0009', 'INC-2026-0010']
    incidents = Incident.objects.using('default_pe').filter(code__in=inc_codes)
    
    for inc in incidents:
        print(f"\nIncidencia: {inc.code} (ID: {inc.id})")
        timeline = IncidentTimeline.objects.using('default_pe').filter(incident=inc).order_by('created_at')
        for entry in timeline:
            print(f"[{entry.created_at}] {entry.action}: {entry.description}")
            if entry.metadata:
                try:
                    print(f"   Metadata: {entry.metadata}")
                except:
                    print("   Metadata: [Error decoding metadata]")

if __name__ == "__main__":
    check_timelines()
