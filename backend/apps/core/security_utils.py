import base64
import hashlib
from cryptography.fernet import Fernet
from django.conf import settings

def get_cipher():
    # Usar el SECRET_KEY de Django para derivar una clave de 32 bytes para Fernet
    key = base64.urlsafe_b64encode(hashlib.sha256(settings.SECRET_KEY.encode()).digest())
    return Fernet(key)

def encrypt_value(value: str) -> str:
    if not value:
        return ""
    cipher = get_cipher()
    return cipher.encrypt(value.encode()).decode()

def decrypt_value(encrypted_value: str) -> str:
    if not encrypted_value:
        return ""
    try:
        cipher = get_cipher()
        return cipher.decrypt(encrypted_value.encode()).decode()
    except Exception:
        # Si falla (ej. si el valor no estaba encriptado), devolver tal cual
        # Útil para la transición de texto plano a encriptado
        return encrypted_value
