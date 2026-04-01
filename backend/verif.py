from apps.ai_agents.agent import get_agent
import time

try:
    print("\n--- INICIANDO PRUEBA DE AGENTE ---")
    agent = get_agent()
    start = time.time()
    result = agent.run(query="Hola, ¿estás operativo?")
    elapsed = time.time() - start
    
    print(f"RESPONSE: {result['response'][:150]}...")
    print(f"PROVIDER: {result['engine_provider']}")
    print(f"TIME: {elapsed:.2f}s")
    print("--- PRUEBA FINALIZADA ---")
except Exception as e:
    print(f"ERROR: {str(e)}")
