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
SERVICE_CALL_ID = 26480

def verify_call():
    login_url = f"{BASE_URL}/Login"
    session = requests.Session()
    session.verify = False
    
    # Login
    print(f"Logging in to {SAP_COMPANY_DB}...")
    resp = session.post(login_url, json={"CompanyDB": SAP_COMPANY_DB, "UserName": SAP_USER, "Password": SAP_PASSWORD})
    if resp.status_code != 200:
        print("Login Failed")
        return

    # Fetch the specific call
    print(f"Fetching Service Call ID {SERVICE_CALL_ID}...")
    url = f"{BASE_URL}/ServiceCalls({SERVICE_CALL_ID})"
    
    resp = session.get(url)
    if resp.status_code == 200:
        data = resp.json()
        print("\n--- Integrity Check ---")
        print(f"ID: {data.get('ServiceCallID')}")
        print(f"Customer: {data.get('CustomerCode')} - {data.get('CustomerName')}")
        print(f"Subject: {data.get('Subject')}")
        print(f"Technician: {data.get('TechnicianCode')}")
        print(f"ProblemType: {data.get('ProblemType')}")
        print(f"Project: {data.get('BPProjectCode')}")
        print(f"CreationDate: {data.get('CreationDate')}")
        print(f"Status: {data.get('Status')} (Should be -3/Open)")
        print("\n✅ Record exists and is readable.")
    else:
        print(f"❌ Error fetching call: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    verify_call()
