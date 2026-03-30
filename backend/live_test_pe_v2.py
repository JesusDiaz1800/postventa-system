import os
import sys
import django
import json

# Add the backend directory to sys.path
backend_dir = r"c:\Users\jdiaz\Desktop\postventa-system\backend"
sys.path.append(backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.core.thread_local import set_current_country
from apps.sap_integration.sap_transaction_service import SAPTransactionService

def live_test_pe_v2():
    set_current_country('PE')
    sap_tx = SAPTransactionService()
    
    # Datos de prueba reales para Perú (V2: Usando Albert Quezada 13)
    customer_code = 'CL20101095747' 
    subject = 'TEST LIVE - ALBERT (13) - ESTABILIZACION PERU'
    description = 'Prueba con Albert Quezada, quien sabemos que funciona por la inspeccion inicial.'
    priority = 'scp_Medium'
    technician_code = 13 # Albert Quezada
    problem_type = 13 # Post Venta
    
    print(f"Enviando solicitud real a SAP PE Service Layer...")
    
    result = sap_tx.create_service_call(
        customer_code=customer_code,
        subject=subject,
        description=description,
        priority=priority,
        technician_code=technician_code,
        problem_type=problem_type
    )
    
    if result.get('success'):
        print(f"¡EXITO! DocNum: {result.get('doc_num')}")
    else:
        print(f"FALLO: {result.get('error')}")

if __name__ == "__main__":
    live_test_pe_v2()
