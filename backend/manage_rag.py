import os
import sys
import django
import logging
import json
import traceback

# Setup environment
sys.path.insert(0, os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.ai.vector_store import get_vector_store
from apps.incidents.models import Incident

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('rag_manager')

def ingest_existing_documents():
    """Recorre todos los incidentes con análisis de IA e indexa su contenido en ChromaDB"""
    try:
        store = get_vector_store()
        try:
            # count_initial = store.count()
            # logger.info(f"Conectado a VectorStore. Documentos actuales en índice: {count_initial}")
            logger.info("Conectado a VectorStore - Skipping count check for stability.")
        except Exception as e:
            logger.error(f"Error conectando a VectorStore: {e}")
            return

        # Obtener incidentes (incluso sin análisis de IA, usamos la descripción raw)
        incidents = Incident.objects.all()
        logger.info(f"Escaneando {incidents.count()} incidentes totales.")
        
        batch_docs = []
        batch_metas = []
        batch_ids = []
        
        count = 0
        skipped = 0
        
        for inc in incidents:
            try:
                # Extraer datos de IA si existen, si no, usar defaults
                data = inc.ai_analysis or {}
                if isinstance(data, str):
                    try: data = json.loads(data)
                    except: data = {}
                    
                # Validar que tenga ALGO de contenido
                if not inc.descripcion and not data:
                    skipped += 1
                    continue

                # Construir contenido semántico híbrido (Humano + IA)
                descripcion = inc.descripcion or "Sin descripción detallada"
                analisis_ia = data.get('resumen_ejecutivo', '') or data.get('descripcion_problema', '')
                
                # Formato enriquecido para el embedding
                content = f"""
                TIPO: Reporte de Incidencia Postventa
                CODIGO: {inc.code}
                CLIENTE: {inc.cliente}
                OBRA: {inc.obra}
                PRODUCTO: {inc.sku} ({inc.categoria.name if inc.categoria else 'General'})
                
                DESCRIPCIÓN DEL PROBLEMA (Reporte Original):
                {descripcion}
                
                ACCIONES INMEDIATAS:
                {inc.acciones_inmediatas}
                
                ANÁLISIS TÉCNICO (IA):
                {analisis_ia}
                {data.get('causas_probables', '')}
                {data.get('solucion_recomendada', '')}
                
                RESOLUCIÓN:
                {inc.closure_summary}
                """
                
                # Metadata para filtros
                meta = {
                    "incident_id": str(inc.id),
                    "code": str(inc.code),
                    "cliente": str(inc.cliente),
                    "categoria": str(inc.categoria.name if inc.categoria else 'Sin Categoría'),
                    "fecha": str(inc.created_at.date())
                }
                
                batch_docs.append(content)
                batch_metas.append(meta)
                batch_ids.append(f"inc_{inc.id}")
                
                count += 1
                
                # Ingestar en lotes de 50
                if len(batch_docs) >= 50:
                    logger.info(f"Ingestando lote de {len(batch_docs)} documentos...")
                    store.add_documents(batch_docs, batch_metas, batch_ids)
                    logger.info(f"Indexados lote de 50 incidentes...")
                    batch_docs = []
                    batch_metas = []
                    batch_ids = []
                    
            except Exception as e:
                logger.error(f"Error procesando incidente {inc.code}: {e}")
                traceback.print_exc()
                skipped += 1
                continue

        # Remanentes
        if batch_docs:
            try:
                logger.info(f"Procesando lote final de {len(batch_docs)} documentos...")
                store.add_documents(batch_docs, batch_metas, batch_ids)
                logger.info(f"Indexados lote final de {len(batch_docs)} documentos.")
            except Exception as e:
                logger.error(f"FATAL ERROR en lote final: {str(e)}")
                traceback.print_exc()

        # try:
        #     total = store.count()
        # except:
        #     total = "Desconocido"
        total = "Skipped"

        logger.info(f"Proceso finalizado. Total Ingresados: {count}. Omitidos: {skipped}. Total en índice: {total}")
    except Exception as G:
        logger.error(f"Error Global en script: {G}")
        traceback.print_exc()

def query_rag(text):
    try:
        store = get_vector_store()
        results = store.query(text, n_results=3)
        print(f"\n--- Resultados para RAG: '{text}' ---")
        
        if not results['documents']:
            print("No se encontraron coincidencias.")
            return

        # Chroma devuelve listas de listas
        docs = results['documents'][0]
        metas = results['metadatas'][0]
        
        for i, doc in enumerate(docs):
            meta = metas[i]
            print(f"\n[Resultado {i+1}] Incidente: {meta.get('code')} | Cliente: {meta.get('cliente')}")
            print("-" * 50)
            print(doc.strip()[:400].replace('\n', ' ') + "...") 
            print("-" * 50)
    except Exception as e:
        print(f"Error querying RAG: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "ingest":
            ingest_existing_documents()
        elif cmd == "query" and len(sys.argv) > 2:
            query_rag(sys.argv[2])
        else:
            print("Uso: python manage_rag.py [ingest | query 'texto']")
    else:
        print("Uso: python manage_rag.py ingest")
