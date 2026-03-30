import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def exhaustive_search_co():
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
            
        objects_to_check = [
            ("Users", "UserName"),
            ("SalesPersons", "SalesEmployeeName"),
            ("BusinessPartners", "CardName"), # Maybe he is a BP for some reason?
        ]
        
        for obj, field in objects_to_check:
            print(f"\n--- Searching in {obj} ({field} contains 'Cristian') ---")
            url = f"{base_url}/{obj}?$filter=contains({field}, 'Cristian')"
            res = session.get(url, verify=False)
            if res.status_code == 200:
                vals = res.json().get('value', [])
                if not vals:
                    print(f"No results in {obj}")
                for v in vals:
                    print(json.dumps(v, indent=2))
            else:
                print(f"Failed in {obj} ({res.status_code}): {res.text}")
                
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    exhaustive_search_co()
