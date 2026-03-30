import os, sys, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.core.settings'
import django; django.setup()

from apps.core.thread_local import set_current_country
from apps.sap_integration.sap_query_service import SAPQueryService

def test():
    set_current_country('PE')
    sap_query = SAPQueryService()
    udfs = sap_query.get_available_udfs('OSCL')
    print("UDFs in PE OSCL:")
    for u in sorted(udfs):
        print(f" - {u}")

if __name__ == "__main__":
    test()
