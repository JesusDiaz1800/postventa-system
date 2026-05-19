import os
import sys
import django
import json

# Setup Django environment
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.core.settings'
django.setup()

from apps.users.models import User
from apps.sap_integration.sap_transaction_service import SAPTransactionService
from apps.core.thread_local import set_current_country

def verify_creation():
    set_current_country('CL')
    print("--- Verificación de Creación en SAP SL (CHILE) ---")
    
    username = 'gerlog' # Probaremos con gerlog
    try:
        user = User.objects.get(username=username)
        print(f"Probando creación con usuario: {username}")
        
        # Instanciar servicio con el usuario específico
        sap_service = SAPTransactionService(request_user=user)
        
        # Datos de prueba para crear una Service Call
        test_payload = {
            'customer_code': 'C1000-6', # Requerimiento Interno
            'subject': 'TEST INTEGRACION - NUEVAS CREDENCIALES',
            'description': 'Prueba funcional de creación vía Service Layer con usuario gerlog. Por favor ignorar.',
            'priority': 'media',
            'bp_project_code': '1',
            'technician_code': 1 # ID de técnico válido en OHEM
        }
        
        print(f"Intentando crear Service Call para Cliente {test_payload['customer_code']}...")
        result = sap_service.create_service_call(**test_payload)
        
        if result.get('success'):
            print(f"\n[EXITO] Llamada de Servicio creada exitosamente!")
            print(f"  - DocNum SAP: {result.get('doc_num')}")
            print(f"  - ServiceCallID: {result.get('service_call_id')}")
            
            # Limpiar (Cerrar la llamada para no dejar basura abierta?)
            # O mejor dejarla así para que el usuario la vea.
            print("\nPrueba completada. La llamada es visible en el cliente de SAP Business One.")
        else:
            print(f"\n[FALLO] No se pudo crear la llamada de servicio.")
            print(f"  - Error: {result.get('error')}")
                
    except User.DoesNotExist:
        print(f"  [ERROR] El usuario {username} no existe en la base de datos de Chile.")
    except Exception as e:
        print(f"  [ERROR] Excepción durante el test: {e}")

if __name__ == "__main__":
    verify_creation()
