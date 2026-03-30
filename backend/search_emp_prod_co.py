import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def search_emp_prod_co():
    base_url = "https://192.168.1.237:50000/b1s/v1"
    # Testing with Production DB name from .env
    login_payload = {
        "CompanyDB": "PRDPOLCOLOMBIA", 
        "UserName": "jefsertec_pco",
        "Password": "Js2024**"
    }
    
    session = requests.Session()
    try:
        print(f"Logging in to {login_payload['CompanyDB']}...")
        login_res = session.post(f"{base_url}/Login", json=login_payload, verify=False, timeout=10)
        if login_res.status_code != 200:
            print(f"Login failed: {login_res.text}")
            return
            
        print("Login Successful. Searching for 'Cristian'...")
        # Search employees
        search_query = "$filter=contains(FirstName, 'Cristian') or contains(LastName, 'Peña') or contains(LastName, 'Pena')"
        url = f"{base_url}/EmployeesInfo?{search_query}"
        
        res = session.get(url, verify=False)
        if res.status_code == 200:
            emps = res.json().get('value', [])
            if not emps:
                print("No se encontró a Cristian Peña en PROD via Service Layer.")
                # List first 10
                res2 = session.get(f"{base_url}/EmployeesInfo?$top=10&$select=EmployeeID,FirstName,LastName", verify=False)
                print("\nPrimeros 10 empleados en PROD:")
                print(json.dumps(res2.json().get('value', []), indent=2))
            else:
                for e in emps:
                    print(f"ID: {e.get('EmployeeID')}, Nombre: {e.get('FirstName')} {e.get('LastName')}, Active: {e.get('Active')}")
        else:
            print(f"Search failed ({res.status_code}): {res.text}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    search_emp_prod_co()
