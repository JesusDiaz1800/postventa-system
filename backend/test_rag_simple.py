import os
import django
import sys

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.ai.vector_store import get_vector_store
import logging

logging.basicConfig(level=logging.INFO)

def test_rag_simple():
    print("Testing VectorStore directly...")
    try:
        store = get_vector_store()
        print(f"Store initialized. Count: {store.count()}")
        
        query = "incidente"
        results = store.query(query, n_results=1)
        print(f"Query '{query}' returned {len(results['documents'][0])} docs.")
        print("Success!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_rag_simple()
