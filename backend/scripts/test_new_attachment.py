import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.core.settings'

import django; django.setup()

from apps.sap_integration.sap_transaction_service import SAPTransactionService
from django.conf import settings

def test_upload():
    print("--- Test de Subida de Adjuntos en SAP ---")
    
    # Crea un archivo básico temporal en MEDIA_ROOT
    test_file_path = os.path.join(settings.MEDIA_ROOT, 'test_adjunto_integration.txt')
    with open(test_file_path, 'w') as f:
         f.write("Archivo de prueba para servicio transaccional SAP.")
         
    # Asume callID = 26480 para la prueba temporal (o alguna otra que exista)
    call_id = 26480 # Este callID parece valido segun scripts anteriores
    
    svc = SAPTransactionService()
    print(f"Subiendo a llamada: {call_id}...")
    res = svc.upload_attachment_to_service_call(call_id, test_file_path, 'test_adjunto_integration.txt')
    
    print(f"Respuesta del servicio:")
    print(res)

    try:
        os.remove(test_file_path)
    except:
        pass

if __name__ == '__main__':
    test_upload()
