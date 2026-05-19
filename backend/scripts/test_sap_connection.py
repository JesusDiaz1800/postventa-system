import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.core.settings'
django.setup()

from apps.users.models import User
from apps.sap_integration.sap_transaction_service import SAPTransactionService
from apps.core.thread_local import set_current_country

def test_connections():
    set_current_country('CL')
    print("--- Test de Conexión SAP SL (CHILE) ---")
    
    usernames = ['gerlog', 'gerpro']
    
    for username in usernames:
        try:
            user = User.objects.get(username=username)
            print(f"Probando usuario: {username} (SAP User: {user.sap_user})")
            
            # Instanciar servicio con el usuario específico
            sap_service = SAPTransactionService(request_user=user)
            
            # Forzar login
            success = sap_service._login()
            
            if success:
                print(f"  [OK] Login exitoso en SAP Service Layer ({sap_service.company_db})")
                # Cerrar sesión para no dejar sesiones colgadas (opcional pero limpio)
                sap_service.logout()
            else:
                print(f"  [FALLO] No se pudo autenticar en SAP. Revisa credenciales en sap_user/sap_password.")
                
        except User.DoesNotExist:
            print(f"  [ERROR] El usuario {username} no existe en la base de datos de Chile.")
        except Exception as e:
            print(f"  [ERROR] Excepción durante el test para {username}: {e}")

if __name__ == "__main__":
    test_connections()
