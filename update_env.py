
import os

env_path = 'backend/.env'
marker = 'ODBC_DRIVER'
new_line = 'ODBC_DRIVER=ODBC Driver 17 for SQL Server\n'
host_line = 'DB_HOST=localhost\\SQLEXPRESS\n'

with open(env_path, 'r') as f:
    lines = f.readlines()

new_lines = []
driver_found = False
host_found = False

for line in lines:
    if line.startswith('ODBC_DRIVER='):
        new_lines.append(new_line)
        driver_found = True
    elif line.startswith('DB_HOST='):
        new_lines.append(host_line)
        host_found = True
    else:
        new_lines.append(line)

if not driver_found:
    new_lines.append(new_line)
if not host_found:
    new_lines.append(host_line)

with open(env_path, 'w') as f:
    f.writelines(new_lines)

print("Updated .env successfully")
