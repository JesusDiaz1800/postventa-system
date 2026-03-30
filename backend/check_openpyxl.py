try:
    import openpyxl
    print("SUCCESS: openpyxl is installed version:", openpyxl.__version__)
except ImportError:
    print("FAILURE: openpyxl is NOT installed")
except Exception as e:
    print(f"FAILURE: Error importing openpyxl: {e}")
