#!/usr/bin/env python
"""
Script para probar autenticación JWT
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from apps.users.models import User as CustomUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.test import RequestFactory

def test_jwt_auth():
    """Probar autenticación JWT"""
    try:
        print("Probando autenticación JWT...")
        
        # Obtener usuario
        user = CustomUser.objects.get(username='customuser')
        print(f"Usuario: {user.username} (ID: {user.id})")
        
        # Generar token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        print(f"Token generado: {access_token[:20]}...")
        
        # Probar autenticación JWT
        print("\nProbando autenticación JWT...")
        jwt_auth = JWTAuthentication()
        
        # Crear request con token
        factory = RequestFactory()
        request = factory.get('/api/audit/logs/list/')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
        
        # Autenticar
        auth_result = jwt_auth.authenticate(request)
        if auth_result:
            authenticated_user, token = auth_result
            print(f"Autenticación JWT exitosa: {authenticated_user.username}")
            print(f"Token válido: {token is not None}")
        else:
            print("Autenticación JWT falló")
        
        # Probar endpoint de auditoría con request autenticado
        print("\nProbando endpoint de auditoría...")
        from apps.audit.views_fixed import audit_logs_list_fixed
        
        # Crear request autenticado
        request.user = user
        response = audit_logs_list_fixed(request)
        
        print(f"Audit Response Status: {response.status_code}")
        print(f"Audit Response Data: {response.data}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_jwt_auth()
