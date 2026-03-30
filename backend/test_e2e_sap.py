import requests
import json
import os
import time

BASE_URL = "http://localhost:8000/api"
USER = "jdiaz"
PASS = "Plf2025**"

def test_e2e():
    print(f"--- Iniciando Prueba E2E SAP (CORREGIDA) ---")
    
    # 1. Login
    print("\n1. Autenticando...")
    login_res = requests.post(f"{BASE_URL}/users/login/", json={"username": USER, "password": PASS})
    if login_res.status_code != 200:
        print(f"Error login: {login_res.text}")
        return
    token = login_res.json()['access']
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Country-Code": "CL"
    }
    print("Login exitoso.")

    # 2. Crear Incidencia (Sincronización SAP)
    print("\n2. Creando Incidencia (Sincronización SAP)...")
    incident_data = {
        "cliente": "Jesus Diaz - Test E2E",
        "customer_code": "C88201900-4",
        "asunto": f"Test E2E SAP {int(time.time())}",
        "descripcion": "Validación de respuesta fluida y anexos asíncronos.",
        "prioridad": "media",
        "asignado_a": 1,
        "categoria": "Calidad",
        "subcategoria": "Producto defectuoso"
    }
    start_time = time.time()
    inc_res = requests.post(f"{BASE_URL}/incidents/", json=incident_data, headers=headers)
    end_time = time.time()
    
    if inc_res.status_code != 201:
        print(f"Error creando incidencia: {inc_res.text}")
        return
    
    incident = inc_res.json()
    incident_id = incident['id']
    sap_doc = incident.get('sap_doc_num', 'N/A')
    print(f"Incidencia creada ID: {incident_id}")
    print(f"SAP DocNum: {sap_doc}")
    print(f"Tiempo de respuesta: {end_time - start_time:.2f} segundos")

    # 3. Subir Imágenes (Asíncronas)
    print("\n3. Subiendo imágenes adjuntas a la incidencia...")
    for i in range(2):
        img_name = f"test_img_{i}.jpg"
        with open(img_name, "rb") as f:
            # Field name is 'image' in views.py
            files = {"image": (img_name, f, "image/jpeg")}
            img_res = requests.post(f"{BASE_URL}/incidents/{incident_id}/images/", files=files, headers=headers)
            if img_res.status_code == 201:
                print(f"Imagen {img_name} enviada exitosamente.")
            else:
                print(f"Error subiendo imagen {img_name}: {img_res.text}")

    # 4. Crear Reporte de Visita (Asíncrono para anexos y SAP)
    print("\n4. Creando Reporte de Visita...")
    # visit_reports expects images in 'images' key as a list
    report_data = {
        "related_incident_id": incident_id,
        "visit_date": "2026-03-20",
        "contact_person": "Juan Perez",
        "visit_reason": "Inspección técnica E2E",
        "findings": "Todo validado tras optimizaciones.",
        "conclusions": "Sincronización fluida confirmada.",
        "status": "closed"
    }
    
    # We can also attach images directly to the visit report
    with open("test_img_0.jpg", "rb") as f:
        files = [
            ("images", ("report_img_0.jpg", f, "image/jpeg"))
        ]
        rep_res = requests.post(f"{BASE_URL}/documents/visit-reports/", data=report_data, files=files, headers=headers)
    
    if rep_res.status_code == 201:
        report = rep_res.json()
        print(f"Reporte de Visita creado ID: {report['id']}")
        print(f"Report Number: {report.get('report_number')}")
    else:
        print(f"Error creando reporte ({rep_res.status_code}): {rep_res.text}")

    print("\n--- Prueba Finalizada. Revisa los logs para confirmar hilos de fondo ---")

if __name__ == "__main__":
    # Asegurar imágenes dummy
    for i in range(2):
        if not os.path.exists(f"test_img_{i}.jpg"):
            with open(f"test_img_{i}.jpg", "wb") as f:
                f.write(b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xFF\xDB\x00C\x00\x03\x02\x02\x03\x02\x02\x03\x03\x03\x03\x04\x03\x03\x04\x05\x08\x05\x05\x04\x04\x05\n\x07\x07\x06\x08\x0C\n\x0C\x0C\x0B\n\x0B\x0B\r\x0E\x12\x10\r\x0E\x11\x0E\x0B\x0B\x10\x16\x10\x11\x13\x14\x15\x15\x15\x0C\x0F\x17\x18\x16\x14\x18\x12\x14\x15\x14\xFF\xC0\x00\x11\x08\x00\x01\x00\x01\x03\x01\"\x00\x02\x11\x01\x03\x11\x01\xFF\xC4\x00\x1F\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0B\xFF\xC4\x00\xB5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07\"q\x142\x81\x91\xA1\x08#B\xB1\xC1\x15R\xD1\xF0$3br\x82\x16\x92\xB2\xE1\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1A&'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8A\x93\x94\x95\x96\x97\x98\x99\x9A\xA2\xA3\xA4\xA5\xA6\xA7\xA8\xA9\xAA\xB3\xB4\xB5\xB6\xB7\xB8\xB9\xBA\xC2\xC3\xC4\xC5\xC6\xC7\xC8\xC9\xCA\xD2\xD3\xD4\xD5\xD6\xD7\xD8\xD9\xDA\xE2\xE3\xE4\xE5\xE6\xE7\xE8\xE9\xEA\xF2\xF3\xF4\xF5\xF6\xF7\xF8\xF9\xFA\xFF\xDA\x00\x0C\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xED\xFC\xCF\x11\xFF\xD9")
    
    test_e2e()
