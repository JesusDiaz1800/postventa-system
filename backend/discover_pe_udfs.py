import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from apps.sap_integration.sap_query_service import SAPQueryService
from apps.core.thread_local import set_current_country

def discover():
    set_current_country('PE')
    qs = SAPQueryService()
    print(f"Buscando UDFs para OSCL en PE...")
    udfs = qs.get_available_udfs('OSCL')
    for u in sorted(udfs):
        print(f" - {u}")

if __name__ == "__main__":
    discover()
