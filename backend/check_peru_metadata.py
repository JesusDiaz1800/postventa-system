import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_metadata():
    base_url = "https://192.168.1.237:50000/b1s/v1"
    login_payload = {
        "CompanyDB": "TSTPOLPERU",
        "UserName": "jefsertec_ppe",
        "Password": "tec006"
    }
    
    session = requests.Session()
    try:
        login_res = session.post(f"{base_url}/Login", json=login_payload, verify=False, timeout=10)
        if login_res.status_code != 200:
            print(f"Login failed: {login_res.text}")
            return
            
        print("--- Problem Types (Peru) ---")
        res = session.get(f"{base_url}/ServiceCallProblemTypes", verify=False)
        if res.status_code == 200:
            print(json.dumps(res.json().get('value', []), indent=2))
        else:
            print(f"Failed to fetch ProblemTypes: {res.status_code}")
            
        print("\n--- Call Types (Peru) ---")
        res = session.get(f"{base_url}/ServiceCallTypes", verify=False)
        if res.status_code == 200:
            print(json.dumps(res.json().get('value', []), indent=2))
        else:
            print(f"Failed to fetch CallTypes: {res.status_code}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    check_metadata()
