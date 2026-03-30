import os
import sys
import django

# Add the backend directory to sys.path
backend_dir = r"c:\Users\jdiaz\Desktop\postventa-system\backend"
sys.path.append(backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.core.thread_local import set_current_country
from apps.sap_integration.sap_query_service import SAPQueryService

def check_techs():
    set_current_country('PE')
    qs = SAPQueryService()
    techs = qs.get_technicians()
    ids = [t['id'] for t in techs]
    print(f"Tech IDs in PE: {ids}")
    
    fallback = qs.get_fallback_technician_id()
    print(f"Fallback ID: {fallback}")
    
    # Check if 1 is in the list
    if 1 in ids:
        print("CRITICAL: ID 1 is still in the list, but it has NO position!")
    else:
        print("SUCCESS: ID 1 filtered out because it lacks position.")

if __name__ == "__main__":
    check_techs()
