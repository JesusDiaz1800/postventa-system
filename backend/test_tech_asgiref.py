import sys, os
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from apps.core.thread_local import set_current_country, get_current_country
from apps.sap_integration.views import get_technicians
from apps.users.models import User
from rest_framework.test import APIRequestFactory, force_authenticate

def test():
    print("--- Test de Vista get_technicians con asgiref.Local ---")
    set_current_country('PE')
    print(f"Contexto establecido: {get_current_country()}")
    
    factory = APIRequestFactory()
    user = User.objects.first()
    request = factory.get('/api/sap/technicians/', HTTP_X_COUNTRY_CODE='PE')
    force_authenticate(request, user=user)
    
    # Llamar a la vista
    response = get_technicians(request)
    
    print(f"Status Code: {response.status_code}")
    print(f"Total técnicos en respuesta: {len(response.data)}")
    
    if len(response.data) > 0:
        print("Primeros 5 técnicos:")
        for t in response.data[:5]:
            print(f"- {t['name']} ({t['id']})")
    else:
        print("Lista vacía")

if __name__ == "__main__":
    test()
