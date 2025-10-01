
"""
URLs para el módulo de gestión de documentos
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import *

app_name = 'document_manager'

urlpatterns = [
    # Generación de documentos
    path('generate/', generar_documento_completo, name='generate_document'),
    path('generate-docx/', generar_docx, name='generate_docx'),
    path('convert-pdf/', convertir_a_pdf, name='convert_pdf'),
    path('insert-image/', insertar_imagen, name='insert_image'),
    
    # Análisis con IA
    path('analyze-images/', analizar_imagenes, name='analyze_images'),
    
    # Biblioteca de documentos
    path('library/', obtener_biblioteca, name='get_library'),
    path('library/stats/', obtener_estadisticas, name='get_stats'),
    path('library/search/', buscar_documentos, name='search_documents'),
    path('library/export/', exportar_biblioteca, name='export_library'),
    path('library/import/', importar_biblioteca, name='import_library'),
    
    # Descarga de documentos
    path('download/<str:tipo>/<str:filename>/', descargar_documento, name='download_document'),
]
