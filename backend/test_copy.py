import os
import sys
import chromadb
# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# TEST DJANGO INTEGRATION
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
import django
django.setup()

from apps.ai.rag_utils import DummyEmbeddingFunction # Use app module

def check_chroma():
    print("=== TEST MINIMAL CHROMADB ===")
    
    try:
        persist_path = os.path.join(os.getcwd(), 'chroma_data') # Use local dir
        print(f"Path target: {persist_path}")
        sys.stdout.flush()
        
        if not os.path.exists(persist_path):
            print("Creating dir...")
            os.makedirs(persist_path)
            print("Dir created.")
        
        client = chromadb.PersistentClient(path=persist_path)
        print("Cliente conectado.")
        sys.stdout.flush()
        
        # dummy_ef = DummyEmbeddingFunction()
        # print("Dummy Class instantiated (from apps.ai.rag_utils).")
        
        from apps.ai.rag_utils import GeminiDocumentEmbeddingFunction
        # import os # Removed 
        api_key = os.getenv('GEMINI_API_KEY')
        print(f"Testing Gemini EF with Key: {api_key[:5]}...")
        real_ef = GeminiDocumentEmbeddingFunction(api_key=api_key)
        
        col = client.get_or_create_collection(
            name="test_collection_gemini",
            embedding_function=real_ef
        )
        print("Collection created with Gemini EF (should be dummy in real app but here we test EF)")
        
        print("Generating embedding for 48 docs...")
        dummy_docs = [f"Test document number {i}" for i in range(48)]
        embeddings = real_ef(dummy_docs)
        print(f"Generated {len(embeddings)} embeddings of length {len(embeddings[0])}")
        
        print(f"Colección creada: {col.name}")
        print("Intentando col.count()...")
        sys.stdout.flush()
        print(f"Count: {col.count()}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_chroma()
