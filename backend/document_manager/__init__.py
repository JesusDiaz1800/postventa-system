"""
Módulo de Gestión de Documentos para Sistema de Control de Calidad
Desarrollado con WeasyPrint, Jinja2 y python-docx
"""

__version__ = "1.0.0"
__author__ = "Sistema de Control de Calidad"

from .core import DocumentManager
from .templates import TemplateManager
from .ai_processor import AIProcessor
from .file_manager import FileManager

__all__ = [
    'DocumentManager',
    'TemplateManager', 
    'AIProcessor',
    'FileManager'
]
