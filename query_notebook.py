import sys
from notebooklm_mcp.auth import load_cached_tokens
from notebooklm_mcp.api_client import NotebookLMClient

# Configuration
NOTEBOOK_ID = "39b5c9eb-289b-415a-bf39-e1cba88b5103" # 01. Arquitectura Empresarial
PROMPT = """
Descríbeme detalladamente los lineamientos de diseño UI/UX para la interfaz 'Premium' del sistema Postventa, 
especificamente para el módulo de Soporte IA y Reportes. 
Incluye detalles sobre:
1. Paleta de colores y Estilo Visual (Glassmorphism, gradientes, sombras).
2. Tipografía y Espaciado.
3. Componentes UI (Tarjetas, Botones, Modales).
4. Disposición de la información en reportes de análisis de IA.
5. Lineamientos arquitectónicos para la integración de Agentes AI (RAG, Modelos).
"""

def main():
    try:
        print(f"Connecting to NotebookLM (ID: {NOTEBOOK_ID})...")
        tokens = load_cached_tokens()
        if not tokens:
            print("Error: Could not load tokens.")
            return

        client = NotebookLMClient(
            cookies=tokens.cookies,
            csrf_token=tokens.csrf_token,
            session_id=tokens.session_id
        )
        
        print("Sending query...")
        response = client.query(NOTEBOOK_ID, PROMPT)
        
        print("\n--- NOTEBOOKLM RESPONSE ---\n")
        print(response)
        print("\n---------------------------\n")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
