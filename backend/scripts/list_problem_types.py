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

def list_problem_types():
    login_url = f"{BASE_URL}/Login"
    session = requests.Session()
    session.verify = False
    
    resp = session.post(login_url, json={"CompanyDB": SAP_COMPANY_DB, "UserName": SAP_USER, "Password": SAP_PASSWORD})
    if resp.status_code != 200:
        print("Login Failed")
        return

    print("Fetching Problem Types...")
    url = f"{BASE_URL}/ServiceProblemTypes?$top=10"
    
    resp = session.get(url)
    if resp.status_code == 200:
        data = resp.json()
        print("--- Problem Types ---")
        for item in data.get('value', []):
            print(f"ID: {item['ProblemTypeID']} - Name: {item['Name']} - Description: {item.get('Description','')}")
            
    else:
        print(f"Error fetching problem types: {resp.text}")

    # Also check Call Origins just in case "Motivo" refers to Origin
    print("\nFetching Service Call Origins...")
    url_origins = f"{BASE_URL}/ServiceCallOrigins?$top=10"
    resp = session.get(url_origins)
    if resp.status_code == 200:
        data = resp.json()
        for item in data.get('value', []):
             print(f"ID: {item['OriginID']} - Name: {item['Name']}")

if __name__ == "__main__":
    list_problem_types()
