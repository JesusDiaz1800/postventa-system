import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SAP_SERVER = "192.168.1.237"
SAP_PORT = 50000
SAP_COMPANY_DB = "TESTPOLIFUSION"
SAP_USER = "ccalidad"
SAP_PASSWORD = "Plf5647**"

BASE_URL = f"https://{SAP_SERVER}:{SAP_PORT}/b1s/v1"

def inspect_structure():
    login_url = f"{BASE_URL}/Login"
    session = requests.Session()
    session.verify = False
    
    # Login
    resp = session.post(login_url, json={"CompanyDB": SAP_COMPANY_DB, "UserName": SAP_USER, "Password": SAP_PASSWORD})
    if resp.status_code != 200:
        print("Login Failed")
        return

    # Get one Service Call to see fields (UDFs start with U_)
    print("Fetching one Service Call...")
    url = f"{BASE_URL}/ServiceCalls?$top=1"
    
    resp = session.get(url)
    if resp.status_code == 200:
        data = resp.json()
        calls = data.get('value', [])
        if calls:
            sample = calls[0]
            print("--- All Fields ---")
            print(json.dumps(sample, indent=2))
        else:
            print("No Service Calls found to inspect.")
    else:
        print(f"Error fetching calls: {resp.text}")

if __name__ == "__main__":
    inspect_structure()
