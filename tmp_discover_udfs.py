import os
import django
import sys

# Setup django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from apps.sap_integration.sap_query_service import SAPQueryService
from apps.core.thread_local import set_current_country

def discover_udfs():
    service = SAPQueryService()
    countries = ['CL', 'PE', 'CO']
    
    for country in countries:
        set_current_country(country)
        print(f"\n--- UDFs with descriptions for OSCL in {country} ---")
        try:
            from django.db import connections
            with connections[service._get_db_alias()].cursor() as cursor:
                query = "SELECT AliasID, Descr FROM CUFD WHERE TableID = 'OSCL'"
                cursor.execute(query)
                rows = cursor.fetchall()
                for alias, descr in rows:
                    print(f"U_{alias}: {descr}")
        except Exception as e:
            print(f"Error in {country}: {e}")

if __name__ == "__main__":
    discover_udfs()
