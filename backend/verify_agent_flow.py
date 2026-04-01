import os
import sys
import django
import logging
import time

# Add the project directory to the sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.ai_agents.agent import get_agent

# Configure logging to see our new logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_agent_flow():
    agent = get_agent()
    
    print("\n=== TEST 1: Simple Text Query ===")
    query = "Hola, ¿quién eres y cómo puedes ayudarme con las soldaduras?"
    start = time.time()
    result = agent.run(query=query)
    end = time.time()
    
    print(f"Response: {result['response'][:200]}...")
    print(f"Provider: {result['engine_provider']}")
    print(f"Time: {end - start:.2f}s")
    print(f"Reasoning: {result['reasoning']}")

    print("\n=== TEST 2: Image Analysis (Simulated) ===")
    # Using a dummy byte string as "image" just to trigger the node logic
    # Note: real GeminiService will fail if bytes are not a valid image, 
    # but we want to see the Agent's node transitions and logs.
    dummy_image = b"fake-image-data"
    query = "Analiza esta imagen de soldadura"
    start = time.time()
    result = agent.run(query=query, images=[dummy_image])
    end = time.time()
    
    print(f"Response Summary: {result['response'][:200]}...")
    print(f"Error (Expected if dummy): {result['error']}")
    print(f"Time: {end - start:.2f}s")

if __name__ == "__main__":
    test_agent_flow()
