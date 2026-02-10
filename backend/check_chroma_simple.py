import os
import sys
import chromadb
from django.conf import settings

# Setup Django minimal to get settings
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
import django
django.setup()

def check_chroma():
    print("=== PING DE CHROMADB ===")
    persist_path = os.path.join(settings.BASE_DIR, 'chroma_data')
    print(f"Path esperado: {persist_path}")
    
    if not os.path.exists(persist_path):
        print("ERROR: El directorio de persistencia NO EXISTE.")
        return

    try:
        client = chromadb.PersistentClient(path=persist_path)
        print("Cliente ChromaDB conectado.")
        collections = client.list_collections()
        print(f"Colecciones encontradas: {len(collections)}")
        
        if not collections:
            print("ERROR: No se encontraron colecciones.")
            return

        col_found = None
        for col in collections:
            print(f"- Colección encontrada: {col.name}")
            if col.name == "postventa_knowledge":
                col_found = col

        if not col_found:
            print("ERROR: La colección 'postventa_knowledge' no existe.")
            return

        print(f"Colección 'postventa_knowledge' tiene {col_found.count()} documentos.")
        
        # Intentar Query manual
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("ERROR: No GEMINI_API_KEY env var.")
            return
            
        print(f"Usando API Key: {api_key[:5]}...")
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        try:
            # Emular embedding
            model = "models/gemini-embedding-001"
            res = genai.embed_content(
                model=model,
                content="incidente",
                task_type="retrieval_query"
            )
            emb = res['embedding']
            print(f"Embedding de prueba generado. Dim: {len(emb)}")
            
            # Query manual a la colección (sin pasar EF, pasamos embeddings directo)
            results = col_found.query(
                query_embeddings=[emb],
                n_results=3
            )
            print("\n--- RESULTADOS QUERY MANUAL ---")
            # print(results) # Don't print full dict, it might be huge or non-serializable
            
            if results['documents'] and results['documents'][0]:
                 print(f"Encontrados {len(results['documents'][0])} documentos.")
                 print(f"Doc 1: {results['documents'][0][0][:100]}...")
            else:
                 print("Resultados VACÍOS.")
            
        except Exception as e:
            print(f"ERROR GENERANDO EMBEDDING O CONSULTANDO: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    check_chroma()
