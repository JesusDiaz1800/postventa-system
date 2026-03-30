import os
import sys
import django

# Añadir el path del backend
backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from django.db import connections
from apps.sap_integration.models import ServiceCall

def check_call_in_all_dbs(call_id):
    dbs = ['sap_db', 'sap_db_pe', 'sap_db_co']
    print(f"--- FINGING CALL {call_id} IN SAP DBS ---")
    
    for db in dbs:
        try:
            print(f"Checking {db}...")
            call = ServiceCall.objects.using(db).get(call_id=call_id)
            print(f"  [FOUND!] In {db}: Subject: {call.subject}, Customer: {call.customer_name}")
        except ServiceCall.DoesNotExist:
            print(f"  [NOT FOUND] In {db}")
        except Exception as e:
            print(f"  [ERROR] In {db}: {str(e)}")

    print("--- END OF SEARCH ---")

if __name__ == "__main__":
    check_call_in_all_dbs(1124)
    # También probar con 11242 que aparecía en los logs del usuario
    check_call_in_all_dbs(11242)
