from __future__ import annotations
import os
import logging
import json
import numpy as np
from typing import Optional, List, Dict, Any
from django.conf import settings

logger = logging.getLogger(__name__)

class VectorStore:
    """
    Versión LITE del VectorStore que utiliza Numpy y JSON para evitar 
    los crashes de ChromaDB en este entorno Windows.
    Perfectamente escalable para cientos de documentos.
    """
    _instance = None
    
    INDEX_FILE = "knowledge_index.json"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorStore, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not getattr(self, '_initialized', False):
            self.persist_path = os.path.join(settings.BASE_DIR, self.INDEX_FILE)
            self._initialized = True
            logger.info(f"VectorStoreLite inicializado en: {self.persist_path}")

    def _load_data(self) -> List[Dict]:
        if not os.path.exists(self.persist_path):
            return []
        try:
            with open(self.persist_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error cargando índice RAG: {e}")
            return []

    def _save_data(self, data: List[Dict]):
        try:
            with open(self.persist_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error guardando índice RAG: {e}")

    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        """
        Añade documentos generando embeddings con Gemini.
        """
        try:
            api_key = getattr(settings, 'GEMINI_API_KEY', os.getenv('GEMINI_API_KEY'))
            from apps.ai.rag_utils import GeminiDocumentEmbeddingFunction
            ef = GeminiDocumentEmbeddingFunction(api_key=api_key)
            
            raw_embeddings = ef(documents) # Esto genera los embeddings
            
            # Convertir a listas de Python (si vienen como ndarrays)
            embeddings = [emb.tolist() if hasattr(emb, "tolist") else list(emb) for emb in raw_embeddings]
            
            existing_data = self._load_data()
            
            # Evitar duplicados por ID
            existing_ids = {item["id"] for item in existing_data}
            
            for i in range(len(documents)):
                doc_id = ids[i]
                if doc_id in existing_ids:
                    # Encontrar y actualizar
                    for item in existing_data:
                        if item["id"] == doc_id:
                            item.update({
                                "document": documents[i],
                                "metadata": metadatas[i],
                                "embedding": embeddings[i]
                            })
                            break
                else:
                    existing_data.append({
                        "id": doc_id,
                        "document": documents[i],
                        "metadata": metadatas[i],
                        "embedding": embeddings[i]
                    })
            
            self._save_data(existing_data)
            logger.info(f"Ingestados {len(documents)} fragmentos en VectorStoreLite. Total: {len(existing_data)}")
        except Exception as e:
            logger.error(f"Error en add_documents (Lite): {e}")
            raise

    def query(self, query_text: str, n_results: int = 5, where: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Busca documentos semánticamente similares usando Numpy (Similitud de Coseno).
        """
        try:
            data = self._load_data()
            if not data:
                return {"documents": [], "metadatas": [], "distances": []}

            # Aplicar filtros (where) si existen (básico: match de keys en metadata)
            filtered_data = data
            if where:
                filtered_data = []
                for item in data:
                    match = True
                    for k, v in where.items():
                        if item["metadata"].get(k) != v:
                            match = False
                            break
                    if match:
                        filtered_data.append(item)
            
            if not filtered_data:
                return {"documents": [], "metadatas": [], "distances": []}

            # 1. Obtener embedding de la consulta
            api_key = getattr(settings, 'GEMINI_API_KEY', os.getenv('GEMINI_API_KEY'))
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            
            res_emb = genai.embed_content(
                model="models/gemini-embedding-001",
                content=query_text,
                task_type="retrieval_query"
            )
            query_vec = np.array(res_emb['embedding'])
            query_norm = query_vec / np.linalg.norm(query_vec)

            # 2. Construir matriz de embeddings
            doc_embeddings = np.array([item["embedding"] for item in filtered_data])
            # Normalizar matriz
            norms = np.linalg.norm(doc_embeddings, axis=1, keepdims=True)
            doc_embeddings_norm = doc_embeddings / norms
            
            # 3. Calcular similitudes de coseno (Dot product de vectores normalizados)
            similarities = np.dot(doc_embeddings_norm, query_norm)
            
            # 4. Obtener los top N
            top_indices = np.argsort(similarities)[::-1][:n_results]
            
            results = {
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]] # En RAG usualmente es 1 - similitud o similar
            }
            
            for idx in top_indices:
                results["documents"][0].append(filtered_data[idx]["document"])
                results["metadatas"][0].append(filtered_data[idx]["metadata"])
                results["distances"][0].append(float(1.0 - similarities[idx])) # Distancia de coseno
                
            return results
        except Exception as e:
            logger.error(f"Error en búsqueda RAG (Lite): {e}")
            return {"documents": [], "metadatas": [], "distances": []}

    def count(self) -> int:
        return len(self._load_data())

def get_vector_store() -> VectorStore:
    return VectorStore()
