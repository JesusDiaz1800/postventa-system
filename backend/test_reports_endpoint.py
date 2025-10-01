#!/usr/bin/env python
"""
Script para probar el endpoint de reportes
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

from apps.reports.views import reports_dashboard
from django.test import RequestFactory
from apps.users.models import User

def test_reports_endpoint():
    """Probar el endpoint de reportes"""
    print("🚀 Probando endpoint de reportes...")
    
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
        request = factory.get('/api/reports/dashboard/')
        request.user = user
        
        # Llamar al endpoint
        response = reports_dashboard(request)
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"📊 Response Data Keys: {list(response.data.keys()) if hasattr(response, 'data') else 'No data'}")
        
        if response.status_code == 200:
            print("🎉 ¡Endpoint de reportes funcionando correctamente!")
            print(f"📈 Datos disponibles: {list(response.data.keys())}")
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
    success = test_reports_endpoint()
    if success:
        print("\n✅ Endpoint de reportes configurado correctamente")
    else:
        print("\n❌ Error configurando endpoint de reportes")
