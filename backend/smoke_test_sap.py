import os
import sys
import django
from unittest.mock import MagicMock

# Add the backend directory to sys.path
backend_dir = r"c:\Users\jdiaz\Desktop\postventa-system\backend"
sys.path.append(backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.sap_integration.sap_transaction_service import SAPTransactionService
from apps.core.thread_local import set_current_country

def smoke_test():
    set_current_country('PE')
    service = SAPTransactionService()
    
    # Mock de requests.post para no ir realmente a SAP
    import requests
    requests.post = MagicMock()
    # Mock de login
    service._login = MagicMock(return_value=True)
    service.session_cookies = {"B1SESSION": "fake"}
    
    print("Probando llamada con TODOS los parámetros de views.py...")
    try:
        service.create_service_call(
            customer_code="C123",
            subject="Test",
            description="Test desc",
            priority="media",
            technician_code=1,
            problem_type=13,
            bp_project_code="P001",
            salesperson_code=5,
            salesperson_name="Vendor",
            ship_address="Street 123",
            obra_name="Obra Alpha",
            start_date="2024-03-24",
            start_time="1200",
            category_name="Cat",
            subcategory_name="Subcat"
        )
        print("¡ÉXITO! La firma es compatible.")
    except TypeError as e:
        print(f"¡ERROR DE TIPO!: {e}")
    except Exception as e:
        print(f"Otro error (esperado si no hay SAP): {e}")

if __name__ == "__main__":
    smoke_test()
