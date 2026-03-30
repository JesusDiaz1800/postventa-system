import os
import sys
import django

# Add the backend directory to sys.path
backend_dir = r"c:\Users\jdiaz\Desktop\postventa-system\backend"
sys.path.append(backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.core.thread_local import set_current_country
from apps.sap_integration.sap_transaction_service import SAPTransactionService

def live_test_pe_service():
    set_current_country('PE')
    sap_tx = SAPTransactionService()
    
    # Datos de prueba reales para Perú llamando al método oficial
    result = sap_tx.create_service_call(
        customer_code='CL20101095747',
        subject='TEST FINAL METODO - PE',
        description='Prueba llamando al metodo create_service_call con todos los parametros.',
        priority='scp_Medium',
        technician_code=1, # Luis (Sera TechnicialCode=1 y AssigneeCode=13 por logica interna)
        bp_project_code='3390', # Las Doñas
        obra_name='LAS DOÑAS',
        problem_type=13
    )
    
    if result.get('success'):
        print(f"¡EXITO! DocNum: {result.get('doc_num')}")
    else:
        print(f"FALLO: {result.get('error')}")

if __name__ == "__main__":
    live_test_pe_service()
