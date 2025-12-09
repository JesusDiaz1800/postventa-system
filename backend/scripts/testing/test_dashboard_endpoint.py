#!/usr/bin/env python
"""
Script para probar el endpoint de dashboard
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

from apps.dashboard.views import get_metrics
from django.test import RequestFactory
from apps.users.models import User

def test_dashboard_endpoint():
    """Probar el endpoint de dashboard"""
    print("🚀 Probando endpoint de dashboard...")
    
    try:
        # Crear un usuario de prueba
        user, created = User.objects.get_or_create(
            username='test_user',
            defaults={
                'email': 'test@polifusion.cl',
                'first_name': 'Test',
                'last_name': 'User',
                'role': 'admin'
            }
        )
        
        # Crear request factory
        factory = RequestFactory()
        request = factory.get('/api/dashboard/metrics/')
        request.user = user
        
        # Llamar al endpoint
        response = get_metrics(request)
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"📊 Response Data: {response.data}")
        
        if response.status_code == 200:
            print("🎉 ¡Endpoint de dashboard funcionando correctamente!")
            return True
        else:
            print(f"❌ Error en el endpoint: {response.data}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_dashboard_endpoint()
    if success:
        print("\n✅ Dashboard endpoint configurado correctamente")
    else:
        print("\n❌ Error configurando dashboard endpoint")
