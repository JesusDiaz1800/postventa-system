try:
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    print("Import success")
except ImportError:
    print("Import failed")
except Exception as e:
    print(f"Other error: {e}")
