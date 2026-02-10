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
                from apps.ai_orchestrator.orchestrator import ai_provider_manager
                self._provider_manager = ai_provider_manager
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
        image_keywords = ['imagen', 'foto', 'picture', 'image', 'adjunta']
        arch_keywords = ['arquitectura', 'diseño', 'patrón', 'microservicio', 'bff', 'cqrs', 'architecture', 'design', 'código', 'backend', 'frontend', 'api']
        quality_keywords = ['falla', 'defecto', 'soldadura', 'polifusión', 'electro', 'norma', 'procedimiento', 'ensayo', 'tubería', 'accesorio', 'calidad', 'garantía', 'reclamo']
        doc_keywords = ['documento', 'pdf', 'manual', 'buscar', 'guía', 'incidente', 'reporte', 'obra', 'cliente', 'historial', 'caso', 'problema', 'solución']

        if state.get('images') or any(word in query_lower for word in image_keywords):
            if state.get('images'):
                state['reasoning'] = "Query includes image for analysis"
                state['current_step'] = 'analyze_image'
            else:
                 # User mentions image but didn't upload one, treat as manual search or general query
                 if any(word in query_lower for word in quality_keywords):
                    state['reasoning'] = "Question about quality/defects (no image uploaded)"
                    state['target_notebook'] = QUALITY_NOTEBOOK_ID
                    state['current_step'] = 'consult_notebook'
                 else:
                    state['reasoning'] = "User mentioned images but none provided."
                    state['current_step'] = 'generate_response'

        elif any(word in query_lower for word in quality_keywords):
            state['reasoning'] = "Query related to quality standards or defects"
            state['target_notebook'] = QUALITY_NOTEBOOK_ID
            state['current_step'] = 'consult_notebook'

        elif any(word in query_lower for word in arch_keywords):
            state['reasoning'] = "Query related to system architecture"
            state['target_notebook'] = ARCH_NOTEBOOK_ID
            state['current_step'] = 'consult_notebook'
            
        elif any(word in query_lower for word in doc_keywords):
            state['reasoning'] = "Query requires document search"
            state['current_step'] = 'search_knowledge' # Fallback to local chroma or generic
        else:
            state['reasoning'] = "Query is a direct question"
            state['current_step'] = 'generate_response'
        
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
        """Analyze an image using the AI provider"""
        logger.info("[Agent] Analyzing image...")
        
        if not state.get('images'):
            state['analysis_result'] = "No image provided for analysis"
            state['current_step'] = 'generate_response'
            return state
        
        try:
            if self.provider_manager:
                result = self.provider_manager.analyze_image(
                    state['images'][0],
                    consent_external=True
                )
                
                # Robust handling of analysis result
                if isinstance(result, dict):
                    analysis_data = result.get('analysis', 'Analysis failed')
                    # If analysis data is itself a dict (structured analysis), dump it to string for prompt
                    if isinstance(analysis_data, dict):
                        import json
                        try:
                            state['analysis_data'] = analysis_data
                            state['analysis_result'] = json.dumps(analysis_data, ensure_ascii=False, indent=2)
                        except:
                             state['analysis_result'] = str(analysis_data)
                    else:
                        state['analysis_result'] = str(analysis_data)
                elif isinstance(result, str):
                    state['analysis_result'] = result
                else:
                    state['analysis_result'] = str(result)
                    
                state['reasoning'] += f" | Image analyzed successfully"
            else:
                state['analysis_result'] = "AI provider not available"
                
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
            state['reasoning'] += " | NotebookLM client unavailable"
            state['current_step'] = 'generate_response'
            return state
            
        if not target_id:
             state['reasoning'] += " | No target notebook specified"
             state['current_step'] = 'generate_response'
             return state

        try:
            # Query NotebookLM
            response = self.notebook_client.query(
                target_id, 
                state['query']
            )
            
            # NotebookLM returns a dict with 'answer' key usually, or just string depending on wrapper
            # Assuming format based on previous tests
            answer = ""
            if isinstance(response, dict):
                answer = response.get('answer', str(response))
            else:
                answer = str(response)

            if answer:
                 source_name = "Arquitectura" if target_id == ARCH_NOTEBOOK_ID else "Calidad"
                 state['knowledge_results'].append({
                    'content': answer,
                    'source': f'NotebookLM ({source_name})'
                 })
                 state['reasoning'] += f" | Retrieved info from NotebookLM ({source_name})"
            else:
                 state['reasoning'] += " | No answer from NotebookLM"

        except Exception as e:
            logger.error(f"NotebookLM query error: {e}")
            state['error'] = f"NotebookLM Error: {e}"
            # Don't fail completely, just move on
        
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
            context_parts.append(f"ANÁLISIS TÉCNICO DE IMAGEN:\n{state['analysis_result']}")
        
        # Generate response using AI
        try:
            if self.provider_manager:
                prompt = f"""
Eres un experto asistente técnico senior para el sistema de Postventa de la empresa. 
Tu misión es ayudar al personal técnico basándote en la evidencia histórica y los estándares de calidad.

IMPORTANTE: 
1. Usa la información proporcionada abajo como tu fuente de verdad principal.
2. Si la información proviene de 'RAG: INC-XXXX', cita el código del incidente en tu respuesta.
3. Si la información proviene de NotebookLM, dale máxima prioridad para temas de normativa y arquitectura.

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
                    prompt,
                    tone='professional',
                    consent_external=True
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
