
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__)))

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
except ImportError:
    print("python-dotenv no instalado.")

def check():
    print("--- Verificacion de Configuracion de IA ---")
    
    # 1. Check Package
    try:
        import google.generativeai as genai
        print("[OK] google-generativeai instalado version:", genai.__version__)
    except ImportError:
        print("[ERROR] google-generativeai NO esta instalado.")
        print("    Ejecute: pip install google-generativeai")
        return

    # 2. Check API Key
    key = os.getenv('GEMINI_API_KEY')
    if not key:
        print("[ERROR] GEMINI_API_KEY no encontrada en .env")
        print("    Por favor agregue GEMINI_API_KEY=su_clave_aqui en backend/.env")
    elif key == 'your-gemini-api-key-here':
        print("[ERROR] GEMINI_API_KEY tiene el valor por defecto.")
        print("    Edite backend/.env y ponga su clave real.")
    else:
        print(f"[OK] GEMINI_API_KEY encontrada ({key[:4]}...{key[-4:]})")
        
        # 3. Test Connection
        print("\nProbando conexion con Gemini...")
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-flash-latest')
            response = model.generate_content("Hola, responde 'OK' si recibes esto.")
            print(f"[OK] Respuesta de Gemini: {response.text}")
        except Exception as e:
            print(f"[ERROR] Fallo la conexion con Gemini: {e}")

if __name__ == "__main__":
    check()
