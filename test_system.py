#!/usr/bin/env python
"""
Script para verificar que el sistema esté funcionando
"""
import requests
import time
import sys

def test_backend():
    """Probar que el backend esté funcionando"""
    try:
        response = requests.get('http://localhost:8000/api/incidents/', timeout=5)
        print(f"✅ Backend funcionando - Status: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Backend no disponible: {e}")
        return False

def test_frontend():
    """Probar que el frontend esté funcionando"""
    try:
        response = requests.get('http://localhost:5173/', timeout=5)
        print(f"✅ Frontend funcionando - Status: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Frontend no disponible: {e}")
        return False

def test_dashboard_endpoint():
    """Probar el endpoint de dashboard"""
    try:
        # Primero necesitamos autenticarnos
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        # Intentar login
        login_response = requests.post('http://localhost:8000/api/auth/login/', json=login_data)
        
        if login_response.status_code == 200:
            token = login_response.json().get('access')
            headers = {'Authorization': f'Bearer {token}'}
            
            # Probar dashboard
            dashboard_response = requests.get('http://localhost:8000/api/dashboard/metrics/', headers=headers)
            print(f"✅ Dashboard endpoint funcionando - Status: {dashboard_response.status_code}")
            return True
        else:
            print(f"❌ No se pudo autenticar: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando dashboard: {e}")
        return False

def main():
    print("🔍 Verificando sistema...")
    print("=" * 50)
    
    # Esperar un poco para que los servicios se inicien
    print("⏳ Esperando que los servicios se inicien...")
    time.sleep(5)
    
    # Probar backend
    backend_ok = test_backend()
    
    # Probar frontend
    frontend_ok = test_frontend()
    
    # Probar dashboard
    dashboard_ok = test_dashboard_endpoint()
    
    print("=" * 50)
    
    if backend_ok and frontend_ok and dashboard_ok:
        print("🎉 ¡Sistema funcionando correctamente!")
        print("📱 Frontend: http://localhost:5173")
        print("🔧 Backend: http://localhost:8000")
        print("📊 Dashboard: http://localhost:8000/api/dashboard/metrics/")
    else:
        print("❌ Algunos servicios no están funcionando")
        if not backend_ok:
            print("   - Backend no disponible")
        if not frontend_ok:
            print("   - Frontend no disponible")
        if not dashboard_ok:
            print("   - Dashboard endpoint no disponible")

if __name__ == '__main__':
    main()
