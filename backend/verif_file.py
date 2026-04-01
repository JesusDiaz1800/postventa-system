from apps.ai_agents.agent import get_agent
import time
import os

output_file = "verif_result.txt"

with open(output_file, "w", encoding="utf-8") as f:
    f.write("--- INICIANDO PRUEBA DE AGENTE ---\n")
    try:
        agent = get_agent()
        start = time.time()
        result = agent.run(query="Hola, ¿estás operativo?")
        elapsed = time.time() - start
        
        f.write(f"RESPONSE: {result['response'][:200]}\n")
        f.write(f"PROVIDER: {result['engine_provider']}\n")
        f.write(f"TIME: {elapsed:.2f}s\n")
        f.write("--- PRUEBA FINALIZADA ---\n")
        print("Verification completed. Results written to verif_result.txt")
    except Exception as e:
        f.write(f"ERROR: {str(e)}\n")
        print(f"Error during verification: {e}")
