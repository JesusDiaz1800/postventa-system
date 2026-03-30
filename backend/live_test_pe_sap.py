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

def live_test_pe():
    set_current_country('PE')
    sap_tx = SAPTransactionService()
    
    # Datos de prueba reales para Perú
    customer_code = 'CL20101095747' # COMPAÑIA CONSTRUCTORA ATLAS S.A.C.
    subject = 'TEST LIVE AGENTE - ESTABILIZACION PERU'
    description = 'Prueba automatizada de creacion de llamada de servicio en Peru via Service Layer.'
    priority = 'scp_Medium'
    technician_code = 31 # Percy Luey (SERTEC)
    problem_type = 13 # Post Venta
    
    print(f"Enviando solicitud real a SAP PE Service Layer...")
    print(f"Customer: {customer_code} | Tech: {technician_code} | Status: 1 | Series: 36")
    
    result = sap_tx.create_service_call(
        customer_code=customer_code,
        subject=subject,
        description=description,
        priority=priority,
        technician_code=technician_code,
        problem_type=problem_type
    )
    
    if result.get('success'):
        print(f"¡EXITO! Llamada creada en SAP PE.")
        print(f"DocNum: {result.get('doc_num')}")
        print(f"SAP ID: {result.get('sap_id')}")
    else:
        print(f"FALLO en creacion SAP PE.")
        print(f"Error: {result.get('error')}")
        if 'last_payload' in result:
            print(f"Payload final intentado: {json.dumps(result['last_payload'], indent=2)}")

if __name__ == "__main__":
    live_test_pe()
