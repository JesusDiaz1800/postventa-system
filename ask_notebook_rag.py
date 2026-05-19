import sys
from notebooklm_mcp.auth import load_cached_tokens
from notebooklm_mcp.api_client import NotebookLMClient

# Configuration
NOTEBOOK_ID = "39b5c9eb-289b-415a-bf39-e1cba88b5103" 

PROMPT = """
Actúa como un arquitecto de software experto en IA y RAG (Retrieval Augmented Generation).
El usuario quiere llevar la aplicación al "siguiente nivel" implementando RAG con ChromaDB.

Explícame detalladamente cómo debo integrar ChromaDB en este sistema Django/React existente.
Cubre los siguientes puntos técnicos:
1.  **Estructura de la Colección**: ¿Qué metadatos debo guardar junto con los embeddings (por ejemplo, ID de documento, rut cliente, fecha)?
2.  **Estrategia de Embeddings**: ¿Qué modelo de embedding recomiendas (OpenAI, Gemini, o local como SentenceTransformers)? Considera que el sistema corre en Windows Server y busca eficiencia.
3.  **Flujo de Ingesta**: ¿Cómo y cuándo debo procesar los documentos PDF/DOCX para generar embeddings? (¿Al subirlo? ¿En background?).
4.  **Flujo de Consulta (Chat)**: ¿Cómo debe interactuar el Frontend con ChromaDB? Describe el prompt del sistema para el "retrieval".
5.  **Persistencia**: ¿Dónde debe guardarse la base de datos de Chroma en el sistema de archivos para asegurar que no se pierda?

Dame un plan de implementación técnico y concreto.
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
        
        print("Sending technical consultation on RAG/ChromaDB...")
        response = client.query(NOTEBOOK_ID, PROMPT)
        
        print("\n--- NOTEBOOKLM ARCHITECTURE GUIDE ---\n")
        print(response)
        print("\n-------------------------------------\n")
        
    except Exception as e:
        print(f"Error querying NotebookLM: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
