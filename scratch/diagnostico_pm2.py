import os
import subprocess

# Localizar logs de PM2
pm2_log_dir = os.path.expanduser("~/.pm2/logs/")
if os.path.exists(pm2_log_dir):
    print(f"Buscando logs en: {pm2_log_dir}")
    files = os.listdir(pm2_log_dir)
    for f in files:
        if "postventa-unificado" in f:
            print(f"\n--- LOG: {f} ---")
            with open(os.path.join(pm2_log_dir, f), 'r') as log_file:
                lines = log_file.readlines()
                for line in lines[-20:]:
                    print(line.strip())
else:
    print("No se encontró el directorio de logs de PM2.")

# Verificar si daphne esta presente
try:
    python_exe = r"C:\Users\jdiaz\Desktop\postventa-system\python-portable\python\python.exe"
    res = subprocess.run([python_exe, "-m", "daphne", "--version"], capture_output=True, text=True)
    print(f"\nDaphne version: {res.stdout}")
except Exception as e:
    print(f"Error comprobando Daphne: {e}")
