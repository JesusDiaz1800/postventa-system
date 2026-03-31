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

def test_incident_close_logic():
    print("=== TEST LÓGICA Incident.close() COLOMBIA ===")
    
    # Buscar una incidencia de prueba en Colombia
    # Usaremos INC-2026-0009 que es la que falló en el log del usuario
    try:
        incident = Incident.objects.get(code='INC-2026-0009')
        print(f"Probando con incidencia: {incident.code} (Status actual: {incident.status}, SAP Call ID: {incident.sap_call_id})")
        
        # Simular usuario
        user = User.objects.first()
        
        set_current_country('CO')
        
        # Debemos resetear el estado para poder cerrarla si ya estaba cerrada en DB local
        if incident.status == 'cerrado':
            incident.status = 'abierto'
            incident.save()
            print("Reseted status to 'abierto' for testing.")

        # Intentar cerrar
        print("\nEjecutando incident.close()...")
        incident.close(user=user)
        
        print("\nVerificando resultado...")
        incident.refresh_from_db()
        print(f"Estado en DB local: {incident.status}")
        
    except Incident.DoesNotExist:
        print("No se encontró la incidencia INC-2026-0009 para la prueba.")
    except Exception as e:
        print(f"Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
    finally:
        clear_current_country()

if __name__ == "__main__":
    test_incident_close_logic()
