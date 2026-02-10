import os
import sys
import django
import numpy as np

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.ai.vector_store import get_vector_store

def inspect_chroma():
    print("=== INSPECCIÓN PROFUNDA DE CHROMADB ===")
    store = get_vector_store()
    collection = store._collection
    
    count = collection.count()
    print(f"Total documentos: {count}")
    
    if count == 0:
        print("La colección está vacía.")
        return

    # Obtener los primeros 5 items incluyendo embeddings
    data = collection.get(limit=5, include=['embeddings', 'documents', 'metadatas'])
    
    print(f"\n--- Muestra de {len(data['ids'])} documentos ---")
    try:
        if not data['embeddings']:
            print("LA CONSULTA NO RETORNÓ EMBEDDINGS. VERIFICA 'include=['embeddings']'")
            
        for i, doc_id in enumerate(data['ids']):
            print(f"\nID: {doc_id}")
            # print(f"Metadata: {data['metadatas'][i]}")
            # print(f"Document Preview: {data['documents'][i][:100]}...")
            
            if data['embeddings'] and i < len(data['embeddings']):
                emb = data['embeddings'][i]
                if emb:
                    emb_np = np.array(emb)
                    print(f"Embedding Shape: {emb_np.shape}")
                    print(f"Embedding Norm: {np.linalg.norm(emb_np)}")
                    print(f"Embedding Stats: min={emb_np.min():.4f}, max={emb_np.max():.4f}, mean={emb_np.mean():.4f}")
                    
                    if np.allclose(emb_np, 0):
                        print("⚠ ALERTA: El embedding es todo CEROS.")
                else:
                    print("⚠ ALERTA: Embedding es None o vacío.")
            else:
                print("⚠ ALERTA: No hay embedding para este índice.")
    except Exception as e:
        print(f"ERROR INSPECCIONANDO DATA: {e}")

if __name__ == "__main__":
    inspect_chroma()
