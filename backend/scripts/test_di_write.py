import os
import sys
import django

# Setup Django Environment
backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.sap_integration.sap_di_service import SAPDIService

def test_service_creation():
    print("Initializing SAP DI Service...")
    service = SAPDIService()
    
    # Datos de prueba
    # Usar un cliente real que sepamos que existe (del log anterior):
    # C78289580-K (INSAC LTDA) o similar.
    # O usar uno genérico si se conoce. 
    # Voy a usar C78289580-K que vi en mensajes anteriores, o 'C99999999'.
    # Mejor usar uno seguro. Voy a intentar leer uno primero si pudiera, pero este es servicio de escritura.
    # Usaré un código dummy que suele existir o fallará validación de negocio (que es un buen test también).
    
    card_code = "C78289580-K" 
    subject = "Prueba Integracion API - NO PROCESAR"
    description = "Esta es una prueba de creación de llamada de servicio desde la App Postventa mediante DI API."
    
    print(f"Attempting to create Service Call for {card_code}...")
    
    result = service.create_service_call(
        customer_code=card_code, 
        subject=subject, 
        description=description,
        priority='L'
    )
    
    if result['success']:
        print(f"✅ SUCCESS! Service Call ID: {result['service_call_id']}")
    else:
        print(f"❌ FAILED. Error: {result.get('error')}")

if __name__ == "__main__":
    test_service_creation()
