"""
API Views for AI Agents

Exposes the PostventaAgent functionality via REST endpoints.
"""

import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .agent import get_agent

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def agent_query(request):
    """
    Send a query to the AI Agent
    
    POST /api/ai-agents/query/
    {
        "query": "¿Cuáles son los pasos para una soldadura por polifusión?",
        "context": {"incident_id": 123}  // optional
    }
    
    Returns:
    {
        "success": true,
        "response": "Los pasos para una soldadura...",
        "confidence": 0.85,
        "sources": ["Manual de Instalación"],
        "reasoning": "Query is a direct question | Found 2 relevant documents"
    }
    """
    try:
        data = request.data
        query = data.get('query', '').strip()
        
        if not query:
            return Response(
                {'error': 'La consulta es requerida'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        context = data.get('context', {})
        
        # Add user info to context
        context['user_id'] = request.user.id
        context['username'] = request.user.username
        
        # Get agent and run query
        agent = get_agent()
        result = agent.run(query=query, context=context)
        
        if result.get('error'):
            logger.warning(f"Agent query warning: {result['error']}")
        
        return Response({
            'success': True,
            'response': result['response'],
            'confidence': result['confidence'],
            'sources': result['sources'],
            'reasoning': result['reasoning'],
            'iterations': result['iterations'],
        })
        
    except Exception as e:
        logger.error(f"Agent query error: {e}")
        return Response(
            {'error': f'Error del agente: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def agent_analyze_image(request):
    """
    Analyze an image using the AI Agent
    
    POST /api/ai-agents/analyze-image/
    FormData:
        - image: File
        - query: String (optional question about the image)
    """
    try:
        if 'image' not in request.FILES:
            return Response(
                {'error': 'No se ha enviado ninguna imagen'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        image_file = request.FILES['image']
        query = request.data.get('query', 'Analiza esta imagen de manera técnica')
        
        # Read image bytes
        image_bytes = image_file.read()
        
        # Get agent and run with image
        agent = get_agent()
        result = agent.run(query=query, images=[image_bytes])
        
        return Response({
            'success': True,
            'response': result['response'],
            'confidence': result['confidence'],
            'reasoning': result['reasoning'],
        })
        
    except Exception as e:
        logger.error(f"Agent image analysis error: {e}")
        return Response(
            {'error': f'Error al analizar imagen: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def agent_status(request):
    """
    Get the status of the AI Agent system
    
    GET /api/ai-agents/status/
    """
    try:
        agent = get_agent()
        
        # Check provider availability
        provider_available = agent.provider_manager is not None
        
        # Check Knowledge Base availability
        kb_available = False
        try:
            from apps.ai.vector_store import get_vector_store
            store = get_vector_store()
            kb_available = store.count() > 0
        except:
            pass
        
        return Response({
            'success': True,
            'agent_ready': True,
            'provider_available': provider_available,
            'knowledge_base_available': kb_available,
            'knowledge_engine': 'VectorStoreLite (Numpy)',
            'max_iterations': agent.max_iterations,
        })
        
    except Exception as e:
        logger.error(f"Agent status error: {e}")
        return Response({
            'success': False,
            'agent_ready': False,
            'error': str(e),
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
