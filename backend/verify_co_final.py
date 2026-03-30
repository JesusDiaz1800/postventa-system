import os
import django
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
import sys
sys.path.append(os.path.join(os.getcwd(), 'backend'))
django.setup()

from apps.sap_integration.sap_query_service import SAPQueryService
from apps.sap_integration.sap_transaction_service import SAPTransactionService
from apps.core.thread_local import set_current_country

def verify_final():
    set_current_country('CO')
    
    # 1. Verificar lista de técnicos (Usuarios)
    print("--- VERIFICANDO LISTA DE RESPONSABLES (CO) ---")
    q_service = SAPQueryService()
    techs = q_service.get_technicians()
    print(f"Total encontrados: {len(techs)}")
    # Buscar a Claudia Nieto (ID 16)
    claudia = next((t for t in techs if t['id'] == 16), None)
    if claudia: print(f"  Claudia Nieto encontrada (ID 16): {claudia['name']}")
    else: print("  Claudia Nieto NO encontrada.")
    
    # 2. Prueba de creación Real (E2E)
    print("\n--- PROBANDO CREACIÓN E2E CON CLAUDIA NIETO (ID 16) ---")
    tx_service = SAPTransactionService()
    res = tx_service.create_service_call(
        customer_code="901663921",
        subject="FINAL E2E TEST - CLAUDIA",
        description="PRUEBA FINAL DE INTEGRACIÓN CON ASIGNACIÓN DE USUARIO",
        technician_code=16 # Claudia Nieto
    )
    
    if res.get('success'):
        print(f"Success! DocNum: {res.get('doc_num')}")
        print(f"Payload enviado: {res.get('data')}")
    else:
        print(f"Failed: {res.get('error')}")

if __name__ == "__main__":
    verify_final()
