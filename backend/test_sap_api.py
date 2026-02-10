"""
Script para probar los endpoints de integracion SAP (simulacion interna)
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status
from apps.sap_integration import views
from apps.users.models import User

def test_sap_endpoints():
    print("=" * 60)
    print("PROBANDO ENDPOINTS DE API SAP")
    print("=" * 60)
    print()
    
    # Crear factory y usuario ficticio para autenticacion
    factory = APIRequestFactory()
    try:
        user = User.objects.first()
        if not user:
            print("[ERROR] No se encontro usuario para pruebas. Crea uno primero.")
            return
            
        print(f"Usando usuario de prueba: {user.email}")
    except Exception as e:
        print(f"[ERROR] Error obteniendo usuario: {e}")
        return

    # 1. Test Busqueda de Clientes
    print("\nTest 1: Buscar Clientes (query='CONST')")
    request = factory.get('/api/sap/customers/search/', {'q': 'CONST'})
    force_authenticate(request, user=user)
    response = views.search_sap_customers(request)
    
    if response.status_code == 200:
        count = response.data.get('count', 0)
        print(f"   [OK] Exito! {count} clientes encontrados.")
        if count > 0:
            print(f"   Primer resultado: {response.data['results'][0]['card_name']}")
    else:
        print(f"   [ERROR] Fallo: {response.status_code} - {response.data}")

    # 2. Test Proyectos (Obras) de un Cliente
    # Usaremos un ID de cliente conocido de la prueba anterior (C1000-6)
    customer_code = "C1000-6" 
    print(f"\nTest 2: Proyectos del Cliente {customer_code}")
    
    request = factory.get(f'/api/sap/customers/{customer_code}/projects/')
    force_authenticate(request, user=user)
    response = views.get_customer_projects(request, card_code=customer_code)
    
    if response.status_code == 200:
        count = response.data.get('count', 0)
        print(f"   [OK] Exito! {count} proyectos encontrados.")
    else:
        print(f"   [ERROR] Fallo: {response.status_code} - {response.data}")

    # 3. Test Llamadas Recientes
    print("\nTest 3: Llamadas de Servicio Recientes")
    request = factory.get('/api/sap/service-calls/recent/', {'limit': 5})
    force_authenticate(request, user=user)
    response = views.get_recent_service_calls(request)
    
    if response.status_code == 200:
        count = response.data.get('count', 0)
        print(f"   [OK] Exito! {count} llamadas recuperadas.")
        if count > 0:
            call = response.data['results'][0]
            print(f"   Ultima llamada: ID {call['call_id']} - {call['subject']}")
    else:
        print(f"   [ERROR] Fallo: {response.status_code} - {response.data}")

if __name__ == '__main__':
    test_sap_endpoints()
