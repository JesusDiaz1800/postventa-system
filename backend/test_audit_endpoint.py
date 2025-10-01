#!/usr/bin/env python
"""
Script para probar el endpoint de auditoría
"""
import os
import sys
import django
import requests
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

def test_audit_endpoint():
    """Probar el endpoint de auditoría"""
    try:
        # Obtener un usuario válido
        user = User.objects.first()
        if not user:
            print("❌ No hay usuarios en la base de datos")
            return
        
        print(f"✅ Usuario encontrado: {user.username}")
        
        # Generar token JWT
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        print(f"✅ Token generado: {access_token[:20]}...")
        
        # Probar el endpoint
        url = "http://localhost:8000/api/audit/logs/list/"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        print(f"🔍 Probando endpoint: {url}")
        
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Respuesta exitosa:")
            print(f"   - Success: {data.get('success', 'N/A')}")
            print(f"   - Count: {data.get('count', 'N/A')}")
            print(f"   - Results: {len(data.get('results', []))} elementos")
        else:
            print(f"❌ Error en la respuesta:")
            print(f"   - Status: {response.status_code}")
            print(f"   - Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_audit_endpoint()
