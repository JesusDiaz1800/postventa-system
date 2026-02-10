import logging
import traceback
from apps.documents.services.document_extractor import DocumentExtractor
from apps.ai.vector_store import get_vector_store

logger = logging.getLogger(__name__)

class RAGService:
    """
    Servicio de alto nivel para gestionar la indexación RAG de documentos nuevos.
    Coordina Extracción -> Embeddings -> ChromaDB.
    """
    
    @staticmethod
    def index_report(report_instance, report_type):
        """
        Indexa un reporte recién creado o actualizado en la base de conocimientos.
        
        Args:
            report_instance: Instancia del modelo (VisitReport, LabReport, etc.)
            report_type: String identificador ('visit_report', 'lab_report', etc.)
        """
        try:
            # 1. Identificar archivo fuente
            file_path = ""
            if hasattr(report_instance, 'docx_path') and report_instance.docx_path:
                file_path = report_instance.docx_path
            elif hasattr(report_instance, 'pdf_path') and report_instance.pdf_path:
                file_path = report_instance.pdf_path
                
            if not file_path:
                logger.warning(f"RAG: No se encontró archivo indexable para reporte {report_instance.id}")
                return False

            # 2. Extraer texto
            logger.info(f"RAG: Extrayendo texto de {file_path}...")
            text_content = DocumentExtractor.extract_text(file_path)
            
            if not text_content or len(text_content) < 50:
                logger.warning(f"RAG: Texto insuficiente ({len(text_content) if text_content else 0} chars) en {file_path}")
                return False

            # 3. Preparar metadatos enriquecidos
            incident = report_instance.related_incident
            
            meta = {
                "source": "rag_auto_index",
                "report_type": report_type,
                "report_id": str(report_instance.id),
                "incident_id": str(incident.id) if incident else "N/A",
                "code": str(incident.code) if incident else "N/A",
                "cliente": str(incident.cliente) if incident else "N/A",
                "fecha": str(getattr(report_instance, 'created_at', '')) 
            }

            # 4. Construir contenido semántico
            # Incluir cabecera contextualmente rica
            full_content = f"""
            TIPO DOCUMENTO: {report_type.upper().replace('_', ' ')}
            INCIDENTE: {meta['code']} - {meta['cliente']}
            FECHA: {meta['fecha']}
            
            CONTENIDO EXTRAÍDO:
            {text_content}
            """

            # 5. Indexar en ChromaDB
            store = get_vector_store()
            
            # ID único para el documento en vector store
            doc_id = f"{report_type}_{report_instance.id}"
            
            store.add_documents(
                documents=[full_content],
                metadatas=[meta],
                ids=[doc_id]
            )
            
            logger.info(f"RAG: Documento {doc_id} indexado exitosamente.")
            return True

        except Exception as e:
            logger.error(f"RAG: Error indexando reporte {report_instance.id}: {e}")
            traceback.print_exc()
            return False
