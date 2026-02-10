import os
import django
import sys

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)
django.setup()

from apps.ai_agents.agent import get_agent
from apps.incidents.models import Incident

def test_agent_rag():
    print("=== Testing Agent RAG Capability ===")
    
    # Check if we have incidents
    count = Incident.objects.count()
    print(f"Total Incidents in DB: {count}")
    
    if count == 0:
        print("No incidents to test with.")
        return

    # Pick an incident to ask about
    last_inc = Incident.objects.last()
    query = f"¿Qué pasó en el incidente {last_inc.code}?"
    print(f"Query: {query}")
    
    agent = get_agent()
    
    # Run agent
    try:
        result = agent.run(query=query)
        
        print("\n--- Result ---")
        print(f"Response: {result['response'][:200]}...")
        print(f"Sources: {result['sources']}")
        print(f"Reasoning: {result['reasoning']}")
        
        if result['sources'] and any('RAG' in s for s in result['sources']):
            print("\nSUCCESS: Agent used RAG!")
        else:
            print("\nWARNING: Agent did not use RAG (or no relevant docs found).")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_agent_rag()
