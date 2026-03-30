import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_chile_metadata():
    base_url = "https://192.168.1.237:50000/b1s/v1"
    login_payload = {
        "CompanyDB": "TESTPOLIFUSION",
        "UserName": "ccalidad",
        "Password": "Plf5647**"
    }
    
    session = requests.Session()
    try:
        login_res = session.post(f"{base_url}/Login", json=login_payload, verify=False, timeout=10)
        if login_res.status_code != 200:
            print(f"Login failed: {login_res.text}")
            return
            
        print("\n--- Service Call Problem Types (Chile) ---")
        res = session.get(f"{base_url}/ServiceCallProblemTypes", verify=False)
        if res.status_code == 200:
            print(json.dumps(res.json().get('value', []), indent=2))
        else:
            print(f"Failed: {res.status_code}")
            
        # Also check for UDFs in OSCL if ProblemType doesn't show "Motivo Visita"
        # OSCL is table 191
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_chile_metadata()
