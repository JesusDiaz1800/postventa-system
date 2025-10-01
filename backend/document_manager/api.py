"""
API REST para el módulo de gestión de documentos
Integra con Django REST Framework
"""

import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import FileResponse, HttpResponse
from django.conf import settings
import os
import json

from .core import DocumentManager
from .ai_processor import AIProcessor
from .file_manager import FileManager

logger = logging.getLogger(__name__)

# Inicializar gestores
document_manager = DocumentManager()
ai_processor = AIProcessor()
file_manager = FileManager(document_manager.base_path)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generar_documento_completo(request):
    """
    Generar documento completo (Word + PDF) con imágenes
    """
    try:
        # Obtener datos del request
        contexto = request.data.get('contexto', {})
        imagenes = request.data.get('imagenes', [])
        tipo_documento = request.data.get('tipo_documento', 'incident_report')
        
        # Agregar información del usuario
        contexto['generated_by'] = request.user.username
        contexto['generation_date'] = document_manager.template_manager.render_template(
            '{{ "now" | strftime("%d/%m/%Y %H:%M") }}', {}
        )
        
        # Generar documento completo
        resultado = document_manager.generar_documento_completo(contexto, imagenes)
        
        return Response({
            'success': True,
            'message': 'Documento generado exitosamente',
            'files': resultado
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error generando documento completo: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generar_docx(request):
    """
    Generar solo documento Word
    """
    try:
        contexto = request.data.get('contexto', {})
        template_name = request.data.get('template_name', 'incident_report')
        
        # Agregar información del usuario
        contexto['generated_by'] = request.user.username
        
        # Generar documento Word
        docx_path = document_manager.generar_docx(contexto, template_name)
        
        return Response({
            'success': True,
            'message': 'Documento Word generado exitosamente',
            'file_path': docx_path
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error generando documento Word: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def convertir_a_pdf(request):
    """
    Convertir documento Word a PDF
    """
    try:
        docx_path = request.data.get('docx_path')
        pdf_path = request.data.get('pdf_path')
        
        if not docx_path or not os.path.exists(docx_path):
            return Response({
                'success': False,
                'error': 'Archivo Word no encontrado'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Convertir a PDF
        pdf_path = document_manager.guardar_pdf(docx_path, pdf_path)
        
        return Response({
            'success': True,
            'message': 'PDF generado exitosamente',
            'file_path': pdf_path
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error convirtiendo a PDF: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def insertar_imagen(request):
    """
    Insertar imagen en documento Word
    """
    try:
        docx_path = request.data.get('docx_path')
        imagen_file = request.FILES.get('imagen')
        descripcion = request.data.get('descripcion', '')
        
        if not docx_path or not imagen_file:
            return Response({
                'success': False,
                'error': 'Archivo Word e imagen requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Guardar imagen temporalmente
        temp_path = os.path.join(document_manager.base_path, 'temp', imagen_file.name)
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        
        with open(temp_path, 'wb') as f:
            for chunk in imagen_file.chunks():
                f.write(chunk)
        
        # Insertar imagen
        docx_path = document_manager.insertar_imagen(docx_path, temp_path, descripcion)
        
        # Limpiar archivo temporal
        os.remove(temp_path)
        
        return Response({
            'success': True,
            'message': 'Imagen insertada exitosamente',
            'file_path': docx_path
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error insertando imagen: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analizar_imagenes(request):
    """
    Analizar imágenes con IA
    """
    try:
        imagenes = request.data.get('imagenes', [])
        
        if not imagenes:
            return Response({
                'success': False,
                'error': 'Lista de imágenes requerida'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Analizar imágenes
        analisis = document_manager.analizar_imagenes(imagenes)
        
        return Response({
            'success': True,
            'message': 'Análisis completado',
            'analisis': analisis
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error analizando imágenes: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_biblioteca(request):
    """
    Obtener lista de documentos en la biblioteca
    """
    try:
        # Obtener parámetros de filtrado
        tipo_documento = request.GET.get('tipo_documento')
        fecha_desde = request.GET.get('fecha_desde')
        fecha_hasta = request.GET.get('fecha_hasta')
        
        # Obtener documentos
        documentos = document_manager.obtener_biblioteca_documentos()
        
        # Aplicar filtros
        if tipo_documento:
            documentos = [d for d in documentos if d.get('tipo_documento') == tipo_documento]
        
        if fecha_desde:
            documentos = [d for d in documentos if d.get('fecha_creacion', '') >= fecha_desde]
        
        if fecha_hasta:
            documentos = [d for d in documentos if d.get('fecha_creacion', '') <= fecha_hasta]
        
        return Response({
            'success': True,
            'documentos': documentos,
            'total': len(documentos)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error obteniendo biblioteca: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def descargar_documento(request, tipo, filename):
    """
    Descargar documento desde la biblioteca
    """
    try:
        # Construir ruta del archivo
        file_path = os.path.join(document_manager.base_path, 'library', tipo, filename)
        
        if not os.path.exists(file_path):
            return Response({
                'success': False,
                'error': 'Archivo no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Determinar tipo de contenido
        if filename.endswith('.pdf'):
            content_type = 'application/pdf'
        elif filename.endswith('.docx'):
            content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        else:
            content_type = 'application/octet-stream'
        
        # Retornar archivo
        response = FileResponse(
            open(file_path, 'rb'),
            content_type=content_type,
            as_attachment=True,
            filename=filename
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error descargando documento: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_estadisticas(request):
    """
    Obtener estadísticas de la biblioteca
    """
    try:
        estadisticas = file_manager.obtener_estadisticas()
        
        return Response({
            'success': True,
            'estadisticas': estadisticas
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def buscar_documentos(request):
    """
    Buscar documentos por criterios
    """
    try:
        criterios = request.data.get('criterios', {})
        
        documentos = file_manager.buscar_documentos(criterios)
        
        return Response({
            'success': True,
            'documentos': documentos,
            'total': len(documentos)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error buscando documentos: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def exportar_biblioteca(request):
    """
    Exportar biblioteca completa
    """
    try:
        destino = request.data.get('destino')
        
        if not destino:
            return Response({
                'success': False,
                'error': 'Ruta de destino requerida'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Exportar biblioteca
        success = file_manager.exportar_biblioteca(destino)
        
        if success:
            return Response({
                'success': True,
                'message': 'Biblioteca exportada exitosamente',
                'destino': destino
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': 'Error exportando biblioteca'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except Exception as e:
        logger.error(f"Error exportando biblioteca: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def importar_biblioteca(request):
    """
    Importar biblioteca desde ubicación externa
    """
    try:
        origen = request.data.get('origen')
        
        if not origen:
            return Response({
                'success': False,
                'error': 'Ruta de origen requerida'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Importar biblioteca
        success = file_manager.importar_biblioteca(origen)
        
        if success:
            return Response({
                'success': True,
                'message': 'Biblioteca importada exitosamente',
                'origen': origen
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': 'Error importando biblioteca'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except Exception as e:
        logger.error(f"Error importando biblioteca: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
