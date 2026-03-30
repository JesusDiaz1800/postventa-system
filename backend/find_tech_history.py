import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def find_tech_in_history():
    base_url = "https://192.168.1.237:50000/b1s/v1"
    login_payload = {
        "CompanyDB": "PRDPOLCOLOMBIA", 
        "UserName": "jefsertec_pco",
        "Password": "Js2024**"
    }
    
    session = requests.Session()
    try:
        print(f"Logging in to {login_payload['CompanyDB']}...")
        login_res = session.post(f"{base_url}/Login", json=login_payload, verify=False, timeout=10)
        if login_res.status_code != 200:
            print(f"Login failed")
            return
            
        print("Buscando en histórico de ServiceCalls...")
        # Buscamos en el asunto o descripción
        queries = [
            "$filter=contains(Subject, 'Cristian')",
            "$filter=contains(Subject, 'Peña')",
            "$top=100&$orderby=CreationDate desc"
        ]
        
        found_ids = set()
        
        for q in queries:
            url = f"{base_url}/ServiceCalls?{q}&$select=TechnicianCode,Subject,CustomerCode"
            res = session.get(url, verify=False)
            if res.status_code == 200:
                calls = res.json().get('value', [])
                for c in calls:
                    tech_code = c.get('TechnicianCode')
                    subject = c.get('Subject')
                    if tech_code and tech_code != -1:
                        print(f"Encontrada llamada: '{subject}' | TechnicianCode: {tech_code}")
                        found_ids.add(tech_code)
            else:
                print(f"Query failed: {res.status_code}")
        
        if found_ids:
            print(f"\nIDs de técnicos detectado en histórico: {found_ids}")
        else:
            print("\nNo se detectaron IDs de técnicos en las últimas llamadas.")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    find_tech_in_history()
