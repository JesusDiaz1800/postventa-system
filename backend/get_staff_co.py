import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_staff_co():
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
            
        print("\n--- Sales Persons (Colombia) ---")
        res = session.get(f"{base_url}/SalesPersons?$select=SalesEmployeeCode,SalesEmployeeName", verify=False)
        if res.status_code == 200:
            print(json.dumps(res.json().get('value', []), indent=2))
        else:
            print(f"Failed: {res.status_code}")
            
        print("\n--- Users (Colombia) ---")
        res = session.get(f"{base_url}/Users?$select=InternalKey,UserCode,UserName", verify=False)
        if res.status_code == 200:
            print(json.dumps(res.json().get('value', []), indent=2))
        else:
            print(f"Failed: {res.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_staff_co()
