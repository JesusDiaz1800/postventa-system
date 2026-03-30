import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def search_emp_sl():
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
            
        # Search employees by name
        # We try filter with contains
        search_query = "$filter=contains(FirstName, 'Cristian') or contains(LastName, 'Peña') or contains(LastName, 'Pena')"
        url = f"{base_url}/EmployeesInfo?{search_query}"
        
        res = session.get(url, verify=False)
        if res.status_code == 200:
            emps = res.json().get('value', [])
            if not emps:
                print("No se encontró a Cristian Peña vía Service Layer en Colombia.")
                # List first 5 active
                res2 = session.get(f"{base_url}/EmployeesInfo?$top=5&$select=EmployeeID,FirstName,LastName", verify=False)
                print("\nPrimeros 5 empleados en SL Colombia:")
                print(json.dumps(res2.json().get('value', []), indent=2))
            else:
                for e in emps:
                    print(f"ID: {e.get('EmployeeID')}, Nombre: {e.get('FirstName')} {e.get('LastName')}, Active: {e.get('Active')}")
        else:
            print(f"Search failed ({res.status_code}): {res.text}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    search_emp_sl()
