#!/usr/bin/env python
"""
Script para probar login directamente
"""
import requests
import json

def test_login_direct():
    """Probar login directamente"""
    try:
        print("Probando login directamente...")
        
        # Probar con diferentes formatos de datos
        login_url = "http://localhost:8000/api/auth/login/"
        
        # Formato 1: JSON
        print("Probando formato JSON...")
        data1 = {
            "username": "simpleuser",
            "password": "simple123"
        }
        
        response1 = requests.post(login_url, json=data1, timeout=10)
        print(f"JSON Status: {response1.status_code}")
        print(f"JSON Response: {response1.text}")
        
        # Formato 2: Form data
        print("\nProbando formato Form...")
        data2 = {
            "username": "simpleuser",
            "password": "simple123"
        }
        
        response2 = requests.post(login_url, data=data2, timeout=10)
        print(f"Form Status: {response2.status_code}")
        print(f"Form Response: {response2.text}")
        
        # Formato 3: Headers explícitos
        print("\nProbando con headers explícitos...")
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        response3 = requests.post(login_url, json=data1, headers=headers, timeout=10)
        print(f"Headers Status: {response3.status_code}")
        print(f"Headers Response: {response3.text}")
        
        # Verificar si el endpoint existe
        print("\nVerificando si el endpoint existe...")
        options_response = requests.options(login_url, timeout=10)
        print(f"OPTIONS Status: {options_response.status_code}")
        print(f"OPTIONS Headers: {dict(options_response.headers)}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_login_direct()
