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

def find_active_customer():
    login_url = f"{BASE_URL}/Login"
    session = requests.Session()
    session.verify = False
    
    resp = session.post(login_url, json={"CompanyDB": SAP_COMPANY_DB, "UserName": SAP_USER, "Password": SAP_PASSWORD})
    if resp.status_code != 200:
        print("Login Failed")
        return

    # Find active customer
    print("Fetching active customer...")
    url = f"{BASE_URL}/BusinessPartners?$select=CardCode,CardName&$filter=Frozen eq 'tNO' and CardType eq 'cCustomer'&$top=5"
    
    resp = session.get(url)
    if resp.status_code == 200:
        data = resp.json()
        for bp in data.get('value', []):
            print(f"Active Customer: {bp['CardCode']} - {bp['CardName']}")
            # Just return the first one
            return bp['CardCode']
    else:
        print(f"Error: {resp.text}")

if __name__ == "__main__":
    find_active_customer()
