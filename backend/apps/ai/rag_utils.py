from chromadb import Documents, EmbeddingFunction, Embeddings
import google.generativeai as genai
import time
import logging

logger = logging.getLogger(__name__)

class DummyEmbeddingFunction(EmbeddingFunction):
    """
    Dummy function to bypass Chroma's default ONNX loading which crashes on Windows.
    We supply values manually, so this is just a placeholder to satisfy Chroma's interface.
    """
    def __call__(self, input: Documents) -> Embeddings:
        # Return fake 3072-dim embeddings (Matched to Gemini 001/004 output)
        return [[0.0]*3072 for _ in input]
        
    def name(self):
        return "dummy_embedding_function"

class GeminiDocumentEmbeddingFunction(EmbeddingFunction):
    """
    Función de embedding sintonizada para DOCUMENTOS.
    Uso: Ingesta de datos.
    Task Type: retrieval_document
    """
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Gemini API Key es necesaria para embeddings.")
        genai.configure(api_key=api_key)
        
    def __call__(self, input: Documents) -> Embeddings:
        try:
            model = "models/gemini-embedding-001" 
            embeddings = []
            for i, text in enumerate(input):
                clean_text = text.replace("\n", " ")
                try:
                    logger.info(f"Embedding doc {i}/{len(input)}. Length: {len(clean_text)}. Preview: {clean_text[:50]}...")
                    result = genai.embed_content(
                        model=model,
                        content=clean_text,
                        task_type="retrieval_document",
                        title="Postventa Document"
                    )
                    logger.info(f"Embedding doc {i} OK.")
                    embeddings.append(result['embedding'])
                    
                    if i < len(input) - 1:
                        time.sleep(1) 
                        
                except Exception as inner_e:
                    logger.error(f"Error en embedding item {i}: {inner_e}")
                    raise inner_e
            return embeddings
        except Exception as e:
            logger.error(f"Error generand embeddings Gemini (Doc): {e}")
            raise e
