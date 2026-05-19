from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
import logging

from .vector_store import get_vector_store

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search_incidents(request):
    """
    Busca incidentes similares usando RAG (Retrieval Augmented Generation).
    Query params:
    - query: Texto a buscar
    - limits: Cantidad de resultados (default 5)
    """
    query = request.data.get('query', '')
    limit = int(request.data.get('limit', 5))
    
    if not query:
        return Response({'error': 'Query parameter is required'}, status=400)

    try:
        store = get_vector_store()
        
        # Realizar búsqueda
        results = store.query(query, n_results=limit)
        
        if not results['documents']:
            return Response({'results': []})
            
        # Formatear respuesta
        formatted_results = []
        
        # Chroma devuelve listas de listas (una lista por cada query)
        docs = results['documents'][0]
        metas = results['metadatas'][0]
        distances = results['distances'][0] if 'distances' in results else []
        
        for i, doc in enumerate(docs):
            meta = metas[i]
            # Convertir distancia a similitud (aproximado) si es necesario
            # Chroma usa L2 o Cosine distance por defecto. 
            # Si es cosine distance: 0 es idéntico, 1 es opuesto.
            # Similitud = 1 - distancia (si es cosine)
            score = distances[i] if i < len(distances) else 0
            
            formatted_results.append({
                'content': doc,
                'metadata': meta,
                'score': score,
                'incident_id': meta.get('incident_id'),
                'code': meta.get('code'),
                'cliente': meta.get('cliente')
            })
            
        return Response({
            'query': query,
            'results': formatted_results,
            'total': len(formatted_results)
        })
        
    except Exception as e:
        logger.error(f"Error en búsqueda RAG: {e}")
        return Response({'error': str(e)}, status=500)
