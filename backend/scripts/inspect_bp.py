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

CARD_CODE = "C10198172-K"

def inspect_bp():
    login_url = f"{BASE_URL}/Login"
    session = requests.Session()
    session.verify = False
    
    resp = session.post(login_url, json={"CompanyDB": SAP_COMPANY_DB, "UserName": SAP_USER, "Password": SAP_PASSWORD})
    if resp.status_code != 200:
        print("Login Failed")
        return

    print(f"Inspecting Customer {CARD_CODE}...")
    url = f"{BASE_URL}/BusinessPartners('{CARD_CODE}')"
    
    resp = session.get(url)
    if resp.status_code == 200:
        data = resp.json()
        print(f"CardName: {data.get('CardName')}")
        print(f"ProjectCode: {data.get('ProjectCode')}")
        
        # Check if there are any specific properties or UDFs for checks
        print("--- Relevant UDFs ---")
        udfs = {k: v for k, v in data.items() if k.startswith('U_')}
        print(json.dumps(udfs, indent=2))
        
    else:
        print(f"Error: {resp.text}")

    # Also list some projects just in case
    print("\nFetching some Projects...")
    url_proj = f"{BASE_URL}/Projects?$top=5"
    resp = session.get(url_proj)
    if resp.status_code == 200:
        for p in resp.json().get('value', []):
            print(f"Project: {p['Code']} - {p['Name']}")

if __name__ == "__main__":
    inspect_bp()
