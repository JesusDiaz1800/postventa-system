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

def list_employees():
    # Login
    login_url = f"{BASE_URL}/Login"
    session = requests.Session()
    session.verify = False
    
    resp = session.post(login_url, json={"CompanyDB": SAP_COMPANY_DB, "UserName": SAP_USER, "Password": SAP_PASSWORD})
    if resp.status_code != 200:
        print("Login Failed")
        return

    # Query EmployeesInfo
    # We want a technician. Usually they are in OHEM table using EmployeesInfo service.
    # Let's get top 5 active employees.
    print("Fetching employees...")
    url = f"{BASE_URL}/EmployeesInfo?$select=EmployeeID,FirstName,LastName,Active&$filter=Active eq 'tYES'&$top=5"
    
    resp = session.get(url)
    if resp.status_code == 200:
        data = resp.json()
        print("--- Active Employees ---")
        for emp in data.get('value', []):
            print(f"ID: {emp['EmployeeID']} - Name: {emp['FirstName']} {emp['LastName']}")
    else:
        print(f"Error fetching employees: {resp.text}")

if __name__ == "__main__":
    list_employees()
