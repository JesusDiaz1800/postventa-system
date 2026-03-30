import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_sc_techs():
    base_url = "https://192.168.1.237:50000/b1s/v1"
    login_payload = {
        "CompanyDB": "TSTPOLCOLOMBIA_2",
        "UserName": "jefsertec_pco",
        "Password": "Js2024**"
    }
    
    session = requests.Session()
    try:
        login_res = session.post(f"{base_url}/Login", json=login_payload, verify=False, timeout=10)
        if login_res.status_code != 200:
            print(f"Login failed: {login_res.text}")
            return
            
        # Query existing Service Calls to see their TechnicianCode
        query_url = f"{base_url}/ServiceCalls?$top=5&$select=ServiceCallID,TechnicianCode"
        
        res = session.get(query_url, verify=False, timeout=15)
        if res.status_code == 200:
            data = res.json()
            calls = data.get('value', [])
            if not calls:
                print("No se encontraron Service Calls en Colombia para extraer técnicos.")
            else:
                for sc in calls:
                    print(f"SC ID: {sc.get('ServiceCallID')}, Technican ID: {sc.get('TechnicianCode')}")
        else:
            print(f"Query failed: {res.status_code} - {res.text}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    get_sc_techs()
