
import requests
import json
import sys

# URL base del backend (ajustar si es necesario)
BASE_URL = "http://127.0.0.1:8000"

def test_login(username, password):
    url = f"{BASE_URL}/api/auth/login/"
    payload = {
        "username": username,
        "password": password
    }
    headers = {
        "Content-Type": "application/json"
    }

    print(f"Probando login en: {url}")
    print(f"Usuario: {username}")
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        try:
            data = response.json()
            print("Respuesta JSON:", json.dumps(data, indent=2))
        except:
            print("Respuesta texto:", response.text)
            
        if response.status_code == 500:
            print("\n!!! ERROR 500 DETECTADO !!!")
            print("Revisa los logs del backend INMEDIATAMENTE.")
            
    except Exception as e:
        print(f"Error de conexión: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python reproduce_login_error.py <usuario> <password>")
        # Default de prueba
        test_login("rcruz", "Polifusion2024!") 
    else:
        test_login(sys.argv[1], sys.argv[2])
