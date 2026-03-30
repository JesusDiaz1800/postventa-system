import smtplib
import sys

def test_smtp():
    host = 'smtp.office365.com'
    port = 587
    user = 'sapbopolifusion@polifusion.cl'
    password = 'Sb_Plfsn_3875002'
    
    print(f"Probando conexión a {host}:{port} con usuario {user}...")
    try:
        server = smtplib.SMTP(host, port, timeout=10)
        server.set_debuglevel(1)
        server.starttls()
        print("TLS establecido. Intentando login...")
        server.login(user, password)
        print("¡Login exitoso!")
        server.quit()
    except smtplib.SMTPAuthenticationError as e:
        print(f"Error de Autenticación (535): {e}")
        print("\nPosibles causas:")
        print("1. La contraseña o el correo son incorrectos.")
        print("2. La cuenta tiene Autenticación de Múltiples Factores (MFA) activada. (Requiere una Contraseña de Aplicación).")
        print("3. 'Autenticación SMTP' está deshabilitada para este buzón en el panel de administrador de Exchange/Office 365.")
    except Exception as e:
        print(f"Otro error: {e}")

if __name__ == "__main__":
    test_smtp()
