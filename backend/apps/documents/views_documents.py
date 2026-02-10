"""
Vistas para manejo de documentos con mejor funcionalidad
"""
import os
import logging
from django.conf import settings
from django.http import FileResponse, Http404, JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_document_info(request, document_type, incident_id, document_id):
    """
    Obtiene información de un documento específico
    """
    try:
        # Construir ruta del documento
        shared_base = getattr(settings, 'SHARED_DOCUMENTS_PATH', None)
        if not shared_base:
            return Response(
                {'error': 'Carpeta compartida no configurada'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        folder_name = document_type.replace('-', '_')
        document_folder = os.path.join(shared_base, folder_name, f'incident_{incident_id}')
        
        # Buscar archivos en la carpeta
        if not os.path.exists(document_folder):
            return Response({
                'found': False,
                'message': 'No se encontraron documentos para esta incidencia',
                'folder_path': document_folder
            })
        
        # Listar archivos disponibles
        files = []
        for filename in os.listdir(document_folder):
            file_path = os.path.join(document_folder, filename)
            if os.path.isfile(file_path) and filename.lower().endswith('.pdf'):
                file_stat = os.stat(file_path)
                files.append({
                    'filename': filename,
                    'size': file_stat.st_size,
                    'size_human': f"{file_stat.st_size / 1024:.1f} KB",
                    'created_at': file_stat.st_ctime,
                    'modified_at': file_stat.st_mtime,
                    'download_url': f'/api/documents/open/{document_type}/{incident_id}/{filename}'
                })
        
        # Ordenar por fecha de modificación (más recientes primero)
        files.sort(key=lambda x: x['modified_at'], reverse=True)
        
        return Response({
            'found': len(files) > 0,
            'files': files,
            'folder_path': document_folder,
            'count': len(files)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo información del documento: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Error interno del servidor: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def open_document_direct(request, document_type, incident_id, filename):
    """
    Abre un documento directamente desde la carpeta compartida
    """
    try:
        shared_base = getattr(settings, 'SHARED_DOCUMENTS_PATH', None)
        if not shared_base:
            shared_base = settings.MEDIA_ROOT
        
        folder_name = document_type.replace('-', '_')
        base_target_folder = os.path.join(shared_base, folder_name, f'incident_{incident_id}')
        file_path = os.path.join(base_target_folder, filename)
        
        # --- Protección contra Path Traversal ---
        # Normalizar rutas para evitar '..'
        file_path = os.path.abspath(file_path)
        base_target_folder = os.path.abspath(base_target_folder)
        
        # Verificar que el archivo esté realmente dentro de la carpeta destinada
        if not file_path.startswith(base_target_folder):
            logger.warning(f"Intento de Path Traversal detectado: {file_path}")
            raise Http404("Acceso denegado")
            
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            raise Http404("Archivo no encontrado")
        
        return FileResponse(open(file_path, 'rb'), as_attachment=False)
        
    except Http404 as e:
        logger.warning(f"Archivo no encontrado: {file_path} - {e}")
        raise
    except Exception as e:
        logger.error(f"Error al abrir documento: {str(e)}", exc_info=True)
        raise Http404("Error interno del servidor al abrir el documento")

from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@cache_page(60)
def list_incident_documents(request, incident_id):
    """
    Lista todos los documentos de una incidencia
    """
    try:
        logger.info(f"=== LISTANDO DOCUMENTOS PARA INCIDENCIA {incident_id} ===")
        
        # Usar carpeta compartida de red si está configurada, sino MEDIA_ROOT
        shared_base = getattr(settings, 'SHARED_DOCUMENTS_PATH', None)
        if not shared_base:
            # Fallback a MEDIA_ROOT si no hay carpeta compartida configurada
            shared_base = settings.MEDIA_ROOT
            if not os.path.exists(shared_base):
                os.makedirs(shared_base, exist_ok=True)
        
        logger.info(f"Base path para documentos: {shared_base}")
        logger.info(f"Base path existe: {os.path.exists(shared_base)}")
        
        document_types = ['visit_report', 'lab_report', 'supplier_report', 'quality_report', 'quality_reports_cliente', 'quality_reports_interno']
        all_documents = []
        
        for doc_type in document_types:
            folder_path = os.path.join(shared_base, doc_type, f'incident_{incident_id}')
            logger.info(f"Buscando en carpeta: {folder_path}")
            logger.info(f"Carpeta existe: {os.path.exists(folder_path)}")
            
            if os.path.exists(folder_path):
                files_in_folder = os.listdir(folder_path)
                logger.info(f"Archivos encontrados en {doc_type}: {files_in_folder}")
                
                for filename in files_in_folder:
                    file_path = os.path.join(folder_path, filename)
                    if os.path.isfile(file_path):
                        file_stat = os.stat(file_path)
                        logger.info(f"Agregando archivo: {filename} (tamaño: {file_stat.st_size} bytes)")
                        all_documents.append({
                            'type': doc_type,
                            'type_name': doc_type.replace('_', ' ').title(),
                            'filename': filename,
                            'size': file_stat.st_size,
                            'size_human': f"{file_stat.st_size / 1024:.1f} KB",
                            'created_at': file_stat.st_ctime,
                            'modified_at': file_stat.st_mtime,
                            'download_url': f'/api/documents/open/{doc_type.replace("_", "-")}/{incident_id}/{filename}'
                        })
        
        # Ordenar por fecha de modificación (más recientes primero)
        all_documents.sort(key=lambda x: x['modified_at'], reverse=True)
        
        logger.info(f"Total documentos encontrados: {len(all_documents)}")
        logger.info(f"Documentos: {[doc['filename'] for doc in all_documents]}")
        
        return Response({
            'documents': all_documents,
            'count': len(all_documents),
            'incident_id': incident_id
        })
        
    except Exception as e:
        logger.error(f"Error listando documentos de incidencia: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Error interno del servidor: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
