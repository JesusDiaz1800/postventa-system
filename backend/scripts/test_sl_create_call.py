import os
import sys
import django

# Setup Django Environment
backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.sap_integration.sap_transaction_service import SAPTransactionService

def test_create_call():
    print("Initializing SAP Transaction Service (Service Layer)...")
    service = SAPTransactionService()
    
    # Usaremos el cliente C10198172-K (Activo) y Proyecto 1 (Sin Obra)
    card_code = "C10198172-K" 
    subject = "Prueba de Integracion IA - NO PROCESAR"
    description = "Esta es una llamada de servicio creada automaticamente desde el script de prueba de la App Postventa (Service Layer)."
    
    print(f"Target DB: {service.company_db}")
    print(f"Creating Service Call for Customer: {card_code}...")
    
    result = service.create_service_call(
        customer_code=card_code,
        subject=subject,
        description=description,
        priority='L',
        technician_code=4, # Marco Montenegro
        problem_type=7, # Motivo Visita
        bp_project_code="1" # Sin Obra
    )
    
    if result['success']:
        print("SUCCESS! Service Call Created.")
        print(f"Service Call ID: {result.get('service_call_id')}")
        print("Data Snapshot:", result.get('data'))
    else:
        print("FAILED.")
        print(f"Error: {result.get('error')}")

    # Logout explicit
    service.logout()

if __name__ == "__main__":
    test_create_call()
