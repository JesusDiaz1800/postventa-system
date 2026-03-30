"""
LangGraph Agent Implementation for Postventa System

This module implements a multi-step reasoning agent using LangGraph patterns.
The agent can:
1. Analyze problems (images/text)
2. Search knowledge base (RAG via ChromaDB and NotebookLM)
3. Generate professional responses

Architecture:
- Uses existing AIProviderManager for LLM calls (quota/fallback handling)
- Integrates with ChromaDB for vector search (when configured)
- Integrates with NotebookLM for deep architectural and quality knowledge
- Follows ReAct pattern: Reason -> Act -> Observe -> Repeat
"""

import logging
import json
from typing import TypedDict, Literal, Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

# Constants
ARCH_NOTEBOOK_ID = "39b5c9eb-289b-415a-bf39-e1cba88b5103" # 01. Arquitectura Empresarial Inalcanzable
QUALITY_NOTEBOOK_ID = "c55cee02-ef73-4282-b85d-6ec4b41afed7" # 06. Calidad, Testing & Fiabilidad Extrema
from apps.ai.vector_store import get_vector_store


# ============================================================================
# STATE DEFINITION
# ============================================================================

class AgentState(TypedDict):
    """State passed between agent nodes"""
    # Input
    query: str
    context: Optional[Dict[str, Any]]
    images: Optional[List[bytes]]
    
    # Processing
    reasoning: str
    knowledge_results: List[Dict[str, Any]]
    analysis_result: Optional[str]
    analysis_data: Optional[Dict[str, Any]]
    target_notebook: Optional[str] # New: ID of notebook to query
    
    # Output
    response: str
    confidence: float
    sources: List[str]
    
    # Control
    current_step: str
    error: Optional[str]
    iterations: int


# ============================================================================
# AGENT NODES (Functions)
# ============================================================================

class PostventaAgent:
    """
    Multi-step reasoning agent for the Postventa System.
    
    Uses a simplified LangGraph-like pattern without the full library,
    to avoid heavy dependencies. Can be upgraded to full LangGraph later.
    """
    
    def __init__(self):
        self._provider_manager = None
        self._chroma_client = None
        self._notebook_client = None
        self.max_iterations = 5
        
    @property
    def provider_manager(self):
        """Lazy load the AI provider manager"""
        if self._provider_manager is None:
            try:
                # Use the REAL orchestrator from providers.py, not the mock one
                from apps.ai_orchestrator.providers import get_orchestrator
                self._provider_manager = get_orchestrator()
            except ImportError as e:
                logger.warning(f"Could not import ai_provider_manager: {e}")
        return self._provider_manager
    
    @property
    def vector_store(self):
        """Lazy load the VectorStore (Lite)"""
        if self._chroma_client is None: # Reusamos el atributo privado por conveniencia
            try:
                from apps.ai.vector_store import get_vector_store
                self._chroma_client = get_vector_store()
                logger.info("VectorStoreLite initialized in Agent")
            except Exception as e:
                logger.error(f"Error initializing VectorStore: {e}")
        return self._chroma_client

    @property
    def notebook_client(self):
        """Lazy load NotebookLM client"""
        if self._notebook_client is None:
            try:
                from notebooklm_mcp.auth import load_cached_tokens
                from notebooklm_mcp.api_client import NotebookLMClient
                
                tokens = load_cached_tokens()
                if tokens:
                    self._notebook_client = NotebookLMClient(
                        cookies=tokens.cookies,
                        csrf_token=tokens.csrf_token,
                        session_id=tokens.session_id
                    )
                    logger.info("NotebookLM client initialized")
                else:
                    logger.warning("Could not load NotebookLM tokens")
            except ImportError as e:
                logger.warning(f"Could not import notebooklm_mcp: {e}")
        return self._notebook_client
    
    # -------------------------------------------------------------------------
    # Node: Understand Query
    # -------------------------------------------------------------------------
    def node_understand(self, state: AgentState) -> AgentState:
        """First step: Understand what the user is asking"""
        logger.info(f"[Agent] Understanding query: {state['query'][:100]}...")
        
        # Determine query type
        query_lower = state['query'].lower()
        
        # Keywords for routing
        image_keywords = ['imagen', 'foto', 'picture', 'image', 'adjunta', 'captura', 'veo']
        arch_keywords = ['arquitectura', 'diseño', 'patrón', 'microservicio', 'bff', 'cqrs', 'architecture', 'design', 'código', 'backend', 'frontend', 'api', 'servidor', 'base de datos']
        quality_keywords = ['falla', 'defecto', 'soldadura', 'polifusión', 'electro', 'norma', 'procedimiento', 'ensayo', 'tubería', 'accesorio', 'calidad', 'garantía', 'reclamo', 'pasos', 'instalar']
        doc_keywords = ['documento', 'pdf', 'manual', 'buscar', 'guía', 'incidente', 'reporte', 'obra', 'cliente', 'historial', 'caso', 'problema', 'solución', 'informe']

        # 0. Check for small talk or very short queries
        if len(state['query'].split()) < 3 and not state.get('images'):
            state['reasoning'] = "Consulta muy corta o saludo. Respuesta directa."
            state['current_step'] = 'generate_response'
            
        # 1. Check for images first
        elif state.get('images') and len(state.get('images', [])) > 0:
            state['reasoning'] = "La consulta incluye imágenes para análisis técnico."
            state['current_step'] = 'analyze_image'
            
        # 2. Check for image-related keywords without images
        elif any(word in query_lower for word in image_keywords):
            state['reasoning'] = "El usuario menciona imágenes pero no se han adjuntado. Procediendo a búsqueda general."
            state['current_step'] = 'search_knowledge'

        # 3. Check for quality/procedures (RAG)
        elif any(word in query_lower for word in quality_keywords):
            state['reasoning'] = "Consulta relacionada con estándares de calidad o procedimientos técnicos."
            state['target_notebook'] = QUALITY_NOTEBOOK_ID
            state['current_step'] = 'consult_notebook'

        # 4. Check for architecture (RAG)
        elif any(word in query_lower for word in arch_keywords):
            state['reasoning'] = "Consulta relacionada con la arquitectura del sistema."
            state['target_notebook'] = ARCH_NOTEBOOK_ID
            state['current_step'] = 'consult_notebook'
            
        # 5. Check for database queries (When was the last..., what incidents...)
        elif any(word in query_lower for word in ['cuándo', 'cuando', 'último', 'ultimo', 'última', 'ultima', 'cuántas', 'cuantos', 'ranking', 'historial']):
            state['reasoning'] = "Consulta sobre el historial o datos específicos de la base de datos."
            state['current_step'] = 'query_database'
            
        # 6. Check for documents/incidents (Local RAG)
        elif any(word in query_lower for word in doc_keywords):
            state['reasoning'] = "Se requiere búsqueda en el historial de documentos e incidentes."
            state['current_step'] = 'search_knowledge'
            
        # 7. Fallback
        else:
            state['reasoning'] = "Pregunta directa sin contexto específico de RAG inmediato."
            state['current_step'] = 'generate_response'
        
        state['iterations'] += 1
        return state
    
    # -------------------------------------------------------------------------
    # Node: Query Database (Django Models)
    # -------------------------------------------------------------------------
    def node_query_database(self, state: AgentState) -> AgentState:
        """Query the Django database for live incident data"""
        logger.info(f"[Agent] Querying database for: {state['query']}")
        
        try:
            from apps.incidents.models import Incident
            from django.db.models import Q
            
            # Extract keywords (clean query)
            clean_query = state['query'].lower()
            stop_words = [
                'cuándo', 'cuando', 'fue', 'la', 'última', 'ultima', 'incidencia', 
                'con', 'el', 'de', 'del', 'qué', 'que', 'pasó', 'en', 'hay', 'sobre'
            ]
            for stop in stop_words:
                clean_query = clean_query.replace(f" {stop} ", " ")
            
            keywords = [w.strip() for w in clean_query.split() if len(w.strip()) > 2]
            
            # Query incidents
            query = Q()
            if keywords:
                for word in keywords:
                    query |= Q(code__icontains=word)
                    query |= Q(descripcion__icontains=word)
                    query |= Q(sku__icontains=word)
                    query |= Q(cliente__icontains=word)
                    query |= Q(obra__icontains=word)
            
            # Get last 10 relevant incidents
            incidents = Incident.objects.filter(query).order_by('-fecha_reporte')[:10]
            
            db_results = []
            for inc in incidents:
                db_results.append({
                    'id': inc.code,
                    'fecha': inc.fecha_reporte.strftime('%Y-%m-%d %H:%M') if inc.fecha_reporte else 'N/A',
                    'cliente': inc.cliente,
                    'sku': inc.sku,
                    'estado': inc.estado,
                    'descripcion': inc.descripcion[:200] if inc.descripcion else ''
                })
            
            if db_results:
                msg = f"Se encontraron {len(db_results)} registros relevantes en el historial:\n"
                msg += "\n".join([f"- {r['id']} ({r['fecha']}): Cliente {r['cliente']}, SKU {r['sku']}, Estado {r['estado']}. Resumen: {r['descripcion']}" for r in db_results])
                
                state['knowledge_results'] = state.get('knowledge_results', []) + [
                    {
                        'source': 'Base de Datos (En Vivo)',
                        'content': msg
                    }
                ]
                state['reasoning'] += f" | {len(db_results)} registros encontrados en BD"
            else:
                state['reasoning'] += " | No se encontraron registros específicos en BD"
            
        except Exception as e:
            logger.error(f"Database query error: {e}")
            state['reasoning'] += f" | Error en consulta BD: {str(e)}"
            
        # Continue to search_knowledge to complement with manuals or older context
        state['current_step'] = 'search_knowledge'
        state['iterations'] += 1
        return state

    # -------------------------------------------------------------------------
    # Node: Search Knowledge Base (Local ChromaDB)
    # -------------------------------------------------------------------------
    def node_search_knowledge(self, state: AgentState) -> AgentState:
        """Search the local knowledge base using VectorStoreLite"""
        logger.info("[Agent] Searching local knowledge base via VectorStoreLite...")
        
        try:
            store = self.vector_store
            if not store:
                state['reasoning'] += " | VectorStore not available"
                state['current_step'] = 'generate_response'
                return state

            # Query the store
            results = store.query(
                query_text=state['query'],
                n_results=5
            )
            
            if results and results.get('documents') and len(results['documents'][0]) > 0:
                docs = results['documents'][0]
                metas = results.get('metadatas', [[]])[0]
                
                state['knowledge_results'] = []
                for doc, meta in zip(docs, metas):
                    state['knowledge_results'].append({
                        'content': doc,
                        'source': f"RAG: {meta.get('code', 'Reporte')} - {meta.get('cliente', 'Cliente')}",
                        'incident_id': meta.get('incident_id')
                    })
                    
                state['reasoning'] += f" | Found {len(state['knowledge_results'])} relevant cases in knowledge base"
            else:
                state['reasoning'] += " | No relevant documents found in knowledge base"
                state['knowledge_results'] = []
                
        except Exception as e:
            logger.error(f"Knowledge search error: {e}")
            state['knowledge_results'] = []
            state['error'] = str(e)
        
        state['current_step'] = 'generate_response'
        state['iterations'] += 1
        return state
    
    # -------------------------------------------------------------------------
    # Node: Analyze Image
    # -------------------------------------------------------------------------
    def node_analyze_image(self, state: AgentState) -> AgentState:
        """Analyze images using Gemini Service"""
        logger.info("[Agent] Analyzing images...")
        
        if not state.get('images'):
            state['analysis_result'] = "No image provided for analysis"
            state['current_step'] = 'generate_response'
            return state
        
        try:
            # Use GeminiService directly for advanced multi-image analysis
            from apps.ai.gemini_service import get_gemini_service
            gemini = get_gemini_service()
            
            if gemini:
                logger.info(f"[Agent] Sending {len(state['images'])} images to GeminiService")
                
                # GeminiService.analyze_real_image expects list of bytes or file-like objects
                result = gemini.analyze_real_image(
                    image_files=state['images'],
                    context=str(state.get('context', {})),
                    analysis_type='technical_agent'
                )
                
                if result.get('success'):
                    analysis_data = result.get('analysis', {})
                    state['analysis_data'] = analysis_data
                    
                    # Convert unstructured analysis dict to string for the prompt
                    import json
                    try:
                        state['analysis_result'] = json.dumps(analysis_data, ensure_ascii=False, indent=2)
                    except:
                        state['analysis_result'] = str(analysis_data)
                        
                    state['reasoning'] += f" | {len(state['images'])} images analyzed successfully"
                else:
                    state['analysis_result'] = f"Analysis failed: {result.get('error')}"
                    state['error'] = result.get('error')
            else:
                state['analysis_result'] = "Gemini Service not available"
                
        except Exception as e:
            logger.error(f"Image analysis error: {e}")
            state['analysis_result'] = f"Error analyzing image: {str(e)}"
            state['error'] = str(e)
        
        state['current_step'] = 'generate_response'
        state['iterations'] += 1
        return state

    # -------------------------------------------------------------------------
    # Node: Consult NotebookLM
    # -------------------------------------------------------------------------
    def node_consult_notebook(self, state: AgentState) -> AgentState:
        """Consult a specific Notebook in NotebookLM"""
        target_id = state.get('target_notebook')
        logger.info(f"[Agent] Consulting NotebookLM ({target_id})...")

        if not self.notebook_client:
            state['reasoning'] += " | NotebookLM client unavailable (no credentials)"
            state['current_step'] = 'search_knowledge' # Fallback to local search
            return state
            
        if not target_id:
             state['reasoning'] += " | No target notebook specified"
             state['current_step'] = 'search_knowledge'
             return state

        try:
            # Query NotebookLM
            response = self.notebook_client.query(
                target_id, 
                state['query']
            )
            
            answer = ""
            if isinstance(response, dict):
                answer = response.get('answer', str(response))
            else:
                answer = str(response)

            if answer and len(answer) > 10:
                 source_name = "Arquitectura" if target_id == ARCH_NOTEBOOK_ID else "Calidad"
                 state['knowledge_results'].append({
                    'content': answer,
                    'source': f'Cuaderno de {source_name} (NotebookLM)'
                 })
                 state['reasoning'] += f" | Información recuperada de NotebookLM ({source_name})"
            else:
                 state['reasoning'] += " | NotebookLM no retornó información relevante. Intentando búsqueda local."
                 state['current_step'] = 'search_knowledge'
                 state['iterations'] += 1
                 return state

        except Exception as e:
            logger.error(f"NotebookLM query error: {e}")
            state['reasoning'] += f" | Error en NotebookLM: {str(e)[:50]}"
            state['current_step'] = 'search_knowledge' # Fallback
            state['iterations'] += 1
            return state
        
        state['current_step'] = 'generate_response'
        state['iterations'] += 1
        return state
    
    # -------------------------------------------------------------------------
    # Node: Generate Response
    # -------------------------------------------------------------------------
    def node_generate_response(self, state: AgentState) -> AgentState:
        """Generate the final response using all gathered information"""
        logger.info("[Agent] Generating response...")
        
        # Build context from gathered information
        context_parts = []
        
        if state.get('knowledge_results'):
            context_parts.append("INFORMACIÓN DE BASE DE CONOCIMIENTO (Prioritaria):")
            for i, result in enumerate(state['knowledge_results'], 1):
                context_parts.append(f"Fuente: {result.get('source')}\nContenido: {result['content']}\n")
                state['sources'].append(result.get('source', 'Base de conocimiento'))
        
        if state.get('analysis_result'):
            context_parts.append(f"ANÁLISIS TÉCNICO DE IMAGEN (Estructurado):\n{state['analysis_result']}")
        
        # Merge analysis_data into context if it exists for extra grounding
        if state.get('analysis_data'):
             context_parts.append(f"DATOS DE FALLA IDENTIFICADOS: {json.dumps(state['analysis_data'], ensure_ascii=False)}")
        
        # Generate response using AI
        try:
            if self.provider_manager:
                prompt = f"""
Eres un Asistente Técnico Senior Multimodal experto del sistema de Postventa. 
Tu misión es asistir al personal técnico en diagnósticos, consultas de normativa y arquitectura, o cualquier duda general.

REGLAS DE ORO:
1. Si se te proporciona CONTEXTO RECUPERADO, úsalo como fuente de verdad prioritaria y cita fuentes (ej: INC-XXXX).
2. Si se te proporcionan ANÁLISIS DE IMAGEN, intégralos en tu respuesta técnica.
3. Si el usuario hace preguntas generales o de cortesía, responde de forma amable y profesional, sin forzar tecnicismos si no son necesarios.
4. Si no tienes la información exacta en el contexto, usa tu conocimiento general de ingeniería y construcción mencionando que es una estimación técnica.

Consulta del usuario: {state['query']}

CONTEXTO RECUPERADO DE LA EMPRESA:
{chr(10).join(context_parts) if context_parts else 'No se encontró información histórica específica. Responde basándote en estándares técnicos generales de postventa e ingeniería.'}

Instrucciones de Respuesta:
- Tono: Profesional, ejecutivo y orientado a la solución.
- Estructura: 
    * Resumen de hallazgos (si hay contexto).
    * Análisis técnico / Recomendaciones.
    * Conclusión / Siguiente paso sugerido.
- Si no sabes la respuesta y no hay contexto, indícalo honestamente y sugiere consultar a un experto de área.
"""
                result = self.provider_manager.generate_text(
                    prompt
                )
                
                logger.info(f"[Agent] Generate text result type: {type(result)}")
                
                # Robust handling of response types
                if isinstance(result, str):
                    response_text = result
                elif isinstance(result, dict):
                    response_text = result.get('generated_text') or result.get('text')
                    if not response_text:
                        # Fallback: if no expected keys, dump the whole dict as string
                        logger.warning(f"[Agent] Unexpected dict structure: {result.keys()}")
                        response_text = str(result)
                else:
                    response_text = str(result) if result is not None else "No se pudo generar respuesta"
                    
                state['response'] = response_text
                state['confidence'] = 0.85
            else:
                state['response'] = "El servicio de IA no está disponible en este momento."
                state['confidence'] = 0.0
                
        except Exception as e:
            logger.error(f"Response generation error: {e}")
            state['response'] = f"Error al generar respuesta: {str(e)}"
            state['confidence'] = 0.0
            state['error'] = str(e)
        
        state['current_step'] = 'done'
        state['iterations'] += 1
        return state
    
    # -------------------------------------------------------------------------
    # Main Execution
    # -------------------------------------------------------------------------
    def run(self, query: str, context: Optional[Dict[str, Any]] = None, 
            images: Optional[List[bytes]] = None) -> Dict[str, Any]:
        """
        Execute the agent workflow
        
        Args:
            query: User's question or request
            context: Optional additional context
            images: Optional list of image bytes to analyze
            
        Returns:
            Dict with response, confidence, sources, and reasoning
        """
        # Initialize state
        state: AgentState = {
            'query': query,
            'context': context or {},
            'images': images or [],
            'reasoning': '',
            'knowledge_results': [],
            'analysis_result': None,
            'analysis_data': None,
            'target_notebook': None,
            'response': '',
            'confidence': 0.0,
            'sources': [],
            'current_step': 'understand',
            'error': None,
            'iterations': 0,
        }
        
        # Node routing
        nodes = {
            'understand': self.node_understand,
            'query_database': self.node_query_database,
            'search_knowledge': self.node_search_knowledge,
            'consult_notebook': self.node_consult_notebook,
            'analyze_image': self.node_analyze_image,
            'generate_response': self.node_generate_response,
        }
        
        # Execute workflow
        while state['current_step'] != 'done' and state['iterations'] < self.max_iterations:
            node_fn = nodes.get(state['current_step'])
            if node_fn:
                state = node_fn(state)
            else:
                logger.error(f"Unknown step: {state['current_step']}")
                break
        
        return {
            'response': state['response'],
            'confidence': state['confidence'],
            'sources': state['sources'],
            'reasoning': state['reasoning'],
            'iterations': state['iterations'],
            'analysis_data': state.get('analysis_data'),
            'error': state['error'],
        }


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_agent_instance = None

def get_agent() -> PostventaAgent:
    """Get the singleton agent instance"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = PostventaAgent()
    return _agent_instance
