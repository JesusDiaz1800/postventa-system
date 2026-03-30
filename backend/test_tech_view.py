import sys, os
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from django.test import RequestFactory
from apps.sap_integration.views import get_technicians
from apps.users.models import User
from rest_framework.request import Request
from rest_framework.test import force_authenticate

def test_view():
    print("--- Disparando Vista API get_technicians con Pais PE para Log ---")
    factory = RequestFactory()
    # Crear un request de prueba de Django
    django_req = factory.get('/api/sap/technicians/', HTTP_X_COUNTRY_CODE='PE')
    
    # Envolver en Request de DRF (lo que espera la vista decorada con @api_view)
    user = User.objects.first()
    
    # Nota: @api_view transforma el request internamente, 
    # pero para llamar a la función directamente necesitamos pasar el objeto correcto
    from rest_framework.test import APIRequestFactory
    api_factory = APIRequestFactory()
    req = api_factory.get('/api/sap/technicians/', HTTP_X_COUNTRY_CODE='PE')
    force_authenticate(req, user=user)
    
    response = get_technicians(req)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Encontrados {len(response.data)} técnicos")

if __name__ == "__main__":
    test_view()
