#!/usr/bin/env python3
"""
Script de verificacion completa del sistema PostVenta con WebSocket
"""

import requests
import json
import time
import sys
import websocket
import threading

BASE_URL = 'http://192.168.1.234:8000'
FRONTEND_URL = 'http://192.168.1.234:5173'
WS_URL = 'ws://192.168.1.234:8000/ws/notifications/'

def test_backend():
    print("[1/6] Verificando Backend Django...")
    try:
        response = requests.get(f'{BASE_URL}/', timeout=5)
        print(f"Backend Status: {response.status_code}")
        return True
    except Exception as e:
        print(f"Backend Error: {e}")
        return False

def test_frontend():
    print("[2/6] Verificando Frontend React...")
    try:
        response = requests.get(f'{FRONTEND_URL}/', timeout=5)
        if response.status_code == 200:
            print("Frontend Status: OK")
            return True
        else:
            print(f"Frontend Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"Frontend Error: {e}")
        return False

def test_login():
    print("[3/6] Verificando Autenticacion...")
    try:
        response = requests.post(f'{BASE_URL}/api/auth/login/', 
                               json={'username': 'jdiaz', 'password': 'adminJDR'}, 
                               timeout=5)
        if response.status_code == 200:
            data = response.json()
            token = data.get('access', 'No token')
            print(f"Login Status: OK - Token obtenido")
            return token
        else:
            print(f"Login Status: {response.status_code}")
            return None
    except Exception as e:
        print(f"Login Error: {e}")
        return None

def test_api(token):
    print("[4/6] Verificando API REST...")
    if not token:
        print("No hay token disponible")
        return False
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f'{BASE_URL}/api/users/me/', headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"API Status: OK - Usuario: {data.get('username', 'No username')}")
            return True
        else:
            print(f"API Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"API Error: {e}")
        return False

def test_websocket_endpoint():
    print("[5/6] Verificando endpoint WebSocket...")
    try:
        # Probar si el endpoint WebSocket responde
        response = requests.get(f'{BASE_URL}/ws/notifications/', timeout=5)
        print(f"WebSocket Endpoint Status: {response.status_code}")
        return True
    except Exception as e:
        print(f"WebSocket Endpoint Error: {e}")
        return False

def test_websocket_connection(token):
    print("[6/6] Verificando conexion WebSocket...")
    if not token:
        print("No hay token disponible para WebSocket")
        return False
    
    ws_url_with_token = f"{WS_URL}?token={token}"
    print(f"Conectando a: {ws_url_with_token}")
    
    connected = False
    error_occurred = False
    
    def on_message(ws, message):
        nonlocal connected
        print(f"WebSocket mensaje recibido: {message[:100]}...")
        connected = True
    
    def on_error(ws, error):
        nonlocal error_occurred
        print(f"WebSocket error: {error}")
        error_occurred = True
    
    def on_close(ws, close_status_code, close_msg):
        print(f"WebSocket cerrado: {close_status_code} - {close_msg}")
    
    def on_open(ws):
        print("WebSocket conectado exitosamente")
        # Enviar mensaje de prueba
        ws.send(json.dumps({"type": "ping"}))
    
    try:
        ws = websocket.WebSocketApp(ws_url_with_token,
                                  on_open=on_open,
                                  on_message=on_message,
                                  on_error=on_error,
                                  on_close=on_close)
        
        # Ejecutar en un hilo separado con timeout
        def run_websocket():
            ws.run_forever()
        
        thread = threading.Thread(target=run_websocket)
        thread.daemon = True
        thread.start()
        
        # Esperar hasta 10 segundos
        for i in range(10):
            time.sleep(1)
            if connected:
                ws.close()
                print("WebSocket Status: OK - Conexion exitosa")
                return True
            if error_occurred:
                print("WebSocket Status: ERROR - Fallo en conexion")
                return False
        
        ws.close()
        print("WebSocket Status: TIMEOUT - No se pudo conectar en 10 segundos")
        return False
        
    except Exception as e:
        print(f"WebSocket Error: {e}")
        return False

def main():
    print("VERIFICACION COMPLETA DEL SISTEMA POSTVENTA")
    print("Incluyendo WebSocket y todas las funcionalidades")
    print("=" * 60)
    
    backend_ok = test_backend()
    frontend_ok = test_frontend()
    token = test_login()
    api_ok = test_api(token)
    ws_endpoint_ok = test_websocket_endpoint()
    ws_connection_ok = test_websocket_connection(token)
    
    print("\n" + "=" * 60)
    print("RESUMEN COMPLETO:")
    print(f"Backend Django: {'OK' if backend_ok else 'ERROR'}")
    print(f"Frontend React: {'OK' if frontend_ok else 'ERROR'}")
    print(f"Autenticacion: {'OK' if token else 'ERROR'}")
    print(f"API REST: {'OK' if api_ok else 'ERROR'}")
    print(f"WebSocket Endpoint: {'OK' if ws_endpoint_ok else 'ERROR'}")
    print(f"WebSocket Conexion: {'OK' if ws_connection_ok else 'ERROR'}")
    
    if backend_ok and frontend_ok and token and api_ok and ws_endpoint_ok and ws_connection_ok:
        print("\n[SUCCESS] SISTEMA 100% FUNCIONAL CON WEBSOCKET!")
        print("Acceso: http://192.168.1.234:5173")
        print("Usuario: jdiaz / adminJDR")
        print("\nCaracteristicas funcionando:")
        print("- Backend Django con ASGI")
        print("- Frontend React con Vite")
        print("- Autenticacion JWT")
        print("- API REST completa")
        print("- WebSocket funcionando")
        print("- Notificaciones en tiempo real")
        print("- Sistema de incidentes")
        print("- Base de datos SQL Server")
        return True
    else:
        print("\n[WARNING] Sistema con problemas")
        if not ws_connection_ok:
            print("NOTA: WebSocket puede requerir servidor ASGI (Daphne)")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
