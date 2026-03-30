import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def find_employee():
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
            
        # Search for Cristian Peña
        # filter = "contains(FirstName, 'Cristian') or contains(LastName, 'Peña') or contains(LastName, 'Pena')"
        # Usamos filter format URL encoded
        query_url = f"{base_url}/EmployeesInfo?$filter=contains(FirstName,'Cristian') or contains(LastName,'Peña') or contains(LastName,'Pena')&$select=EmployeeID,FirstName,LastName,JobTitle,ExternalEmployeeNumber"
        
        res = session.get(query_url, verify=False, timeout=15)
        if res.status_code == 200:
            data = res.json()
            employees = data.get('value', [])
            if not employees:
                print("No se encontró a Cristian Peña")
            else:
                for emp in employees:
                    print(f"ID: {emp.get('EmployeeID')}, Nombre: {emp.get('FirstName')} {emp.get('LastName')}, Cargo: {emp.get('JobTitle')}")
        else:
            print(f"Query failed: {res.status_code} - {res.text}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    find_employee()
