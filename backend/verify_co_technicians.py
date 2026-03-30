import os
import django
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
import sys
sys.path.append(os.path.join(os.getcwd(), 'backend'))
django.setup()

from apps.sap_integration.sap_query_service import SAPQueryService
from apps.core.thread_local import set_current_country

def verify_co_technicians():
    set_current_country('CO')
    service = SAPQueryService()
    print("--- VERIFICANDO TÉCNICOS PARA COLOMBIA ---")
    technicians = service.get_technicians()
    print(f"Total técnicos encontrados: {len(technicians)}")
    for t in technicians:
        print(f"  ID: {t['id']}, Name: {t['name']}")

if __name__ == "__main__":
    verify_co_technicians()
