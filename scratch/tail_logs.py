import os

log_files = [
    r'c:\Users\jdiaz\Desktop\postventa-system\backend\logs\backend-error.log',
    r'c:\Users\jdiaz\Desktop\postventa-system\backend\logs\backend-out.log',
    r'c:\Users\jdiaz\Desktop\postventa-system\backend\logs\postventa.log'
]

for lf in log_files:
    print(f"\n--- Ultimas lineas de {lf} ---")
    if os.path.exists(lf):
        with open(lf, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            for line in lines[-30:]:
                print(line.strip())
    else:
        print("Archivo no existe.")
