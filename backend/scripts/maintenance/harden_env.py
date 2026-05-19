
import os
import secrets

env_path = 'backend/.env'

def generate_secret():
    return secrets.token_urlsafe(50)

with open(env_path, 'r') as f:
    lines = f.readlines()

new_lines = []
has_secret = False
has_debug = False
has_hosts = False

for line in lines:
    key = line.split('=')[0].strip()
    if key == 'DJANGO_DEBUG':
        new_lines.append('DJANGO_DEBUG=False\n')
        has_debug = True
    elif key == 'DJANGO_ALLOWED_HOSTS':
        new_lines.append('DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost,192.168.1.234,testserver\n')
        has_hosts = True
    elif key == 'DJANGO_SECRET_KEY':
        # Don't overwrite if it looks long/secure, but this is a cleanup, so maybe rotate?
        # Let's keep existing if present to avoid breaking sessions, unless it's default.
        if 'insecure-default' in line:
            new_lines.append(f"DJANGO_SECRET_KEY={generate_secret()}\n")
        else:
            new_lines.append(line)
        has_secret = True
    else:
        new_lines.append(line)

if not has_debug:
    new_lines.append('DJANGO_DEBUG=False\n')
if not has_hosts:
    new_lines.append('DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost,192.168.1.234,testserver\n')
if not has_secret:
    new_lines.append(f"DJANGO_SECRET_KEY={generate_secret()}\n")

with open(env_path, 'w') as f:
    f.writelines(new_lines)

print("Secure .env written successfully.")
