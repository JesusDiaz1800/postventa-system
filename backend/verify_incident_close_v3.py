import os
import django
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
sys.path.append(os.path.join(os.getcwd(), 'backend'))
django.setup()

from apps.incidents.models import Incident
from apps.core.thread_local import set_current_country, clear_current_country
from django.contrib.auth import get_user_model

User = get_user_model()

def test_incident_close_v3():
    print("=== TEST LÓGICA Incident.close() COLOMBIA (INC-2026-0025) v3 ===")
    
    try:
        incident = Incident.objects.get(code='INC-2026-0025')
        print(f"Probando con incidencia: {incident.code} (SAP CallID: {incident.sap_call_id}, Sap DocNum: {incident.sap_doc_num})")
        
        user = User.objects.first() or User.objects.create_user(username='admin_test')
        
        # Seteamos país Colombia
        set_current_country('CO')
        
        # Reset local estado
        if incident.estado == 'cerrado':
            incident.estado = 'abierto'
            incident.save()
            print("Reset estado to 'abierto'.")

        print("\nEjecutando incident.close()...")
        # Esto debería emitir los nuevos logs y NO CRASHAR
        incident.close(user=user)
        
        print("\nVerificando resultado...")
        incident.refresh_from_db()
        print(f"Estado final en DB local: {incident.estado}")
        
    except Exception as e:
        print(f"Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
    finally:
        clear_current_country()

if __name__ == "__main__":
    test_incident_close_v3()
