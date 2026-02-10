import os
import logging
import pypdf
import docx
from django.conf import settings

logger = logging.getLogger(__name__)

class DocumentExtractor:
    """
    Servicio para extraer texto plano de documentos PDF y DOCX.
    Usado para alimentar al sistema RAG.
    """
    
    @staticmethod
    def extract_text(file_path):
        """
        Determina el tipo de archivo y extrae su texto.
        Retorna: str (texto extraído) o None si falla/no soportado
        """
        if not os.path.exists(file_path):
            logger.error(f"Archivo no encontrado para extracción: {file_path}")
            return None
            
        ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if ext == '.pdf':
                return DocumentExtractor._extract_from_pdf(file_path)
            elif ext in ['.docx', '.doc']: # .doc might not work with python-docx but try
                return DocumentExtractor._extract_from_docx(file_path)
            elif ext == '.txt':
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            else:
                logger.warning(f"Formato no soportado para extracción: {ext}")
                return None
        except Exception as e:
            logger.error(f"Error extrayendo texto de {file_path}: {e}")
            return None

    @staticmethod
    def _extract_from_pdf(pdf_path):
        text = ""
        try:
            with open(pdf_path, 'rb') as f:
                reader = pypdf.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error pyPDF: {e}")
            return None

    @staticmethod
    def _extract_from_docx(docx_path):
        text = ""
        try:
            doc = docx.Document(docx_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error python-docx: {e}")
            return None
