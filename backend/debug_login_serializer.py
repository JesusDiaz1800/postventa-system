#!/usr/bin/env python
"""
Script para debuggear el serializer de login
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from apps.users.serializers import LoginSerializer
from django.contrib.auth import authenticate
from apps.users.models import User as CustomUser

def debug_login_serializer():
    """Debuggear el serializer de login"""
    try:
        print("Debuggeando serializer de login...")
        
        # Crear datos de prueba
        data = {
            "username": "customuser",
            "password": "custom123"
        }
        
        print(f"Datos de prueba: {data}")
        
        # Probar serializer
        serializer = LoginSerializer(data=data)
        print(f"Serializer is_valid: {serializer.is_valid()}")
        
        if not serializer.is_valid():
            print(f"Serializer errors: {serializer.errors}")
        else:
            print(f"Serializer validated_data: {serializer.validated_data}")
            
            # Probar autenticación
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            print(f"Autenticando con username: {username}")
            user = authenticate(username=username, password=password)
            
            if user:
                print(f"Autenticación exitosa: {user.username}")
                print(f"Usuario activo: {user.is_active}")
            else:
                print("Autenticación falló")
                
                # Verificar si el usuario existe
                try:
                    user_obj = CustomUser.objects.get(username=username)
                    print(f"Usuario encontrado: {user_obj.username}")
                    print(f"Usuario activo: {user_obj.is_active}")
                    
                    # Probar autenticación con el objeto
                    if user_obj.check_password(password):
                        print("Contraseña correcta")
                    else:
                        print("Contraseña incorrecta")
                        
                except CustomUser.DoesNotExist:
                    print("Usuario no encontrado")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_login_serializer()
