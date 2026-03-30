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

def test_name_lookup():
    set_current_country('PE')
    qs = SAPQueryService()
    
    name = "PERCY LUEY"
    emp_id = qs.get_employee_id_by_name(name)
    print(f"Buscando '{name}': ID {emp_id}")
    
    name2 = "ALBERT QUEZADA"
    emp_id2 = qs.get_employee_id_by_name(name2)
    print(f"Buscando '{name2}': ID {emp_id2}")

if __name__ == "__main__":
    test_name_lookup()
