import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.core.settings'
import django; django.setup()
from apps.sap_integration.sap_query_service import SAPQueryService
s = SAPQueryService()
r = s.get_service_call(24688)
print("NEW FIELDS:")
print(f"  ship_address: {r.get('ship_address')}")
print(f"  sap_category: {r.get('sap_category')}")
print(f"  sap_subcategory: {r.get('sap_subcategory')}")
print(f"  sap_priority: {r.get('sap_priority')}")
print(f"  create_time: {r.get('create_time')}")
print(f"  description: {str(r.get('description'))[:50]}")
print(f"  address: {r.get('address')}")
