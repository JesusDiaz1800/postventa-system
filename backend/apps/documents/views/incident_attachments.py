"""
Vistas para gestión de adjuntos de incidencias
Permite subir, listar, descargar y eliminar archivos adjuntos de incidencias
"""
import os
import json
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from apps.incidents.models import Incident
from apps.documents.models import Document
from apps.documents.serializers import DocumentAttachmentListSerializer
from apps.documents.attachment_service import attachment_service
from apps.core.thread_local import get_current_country
import logging

logger = logging.getLogger(__name__)
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from apps.core.mixins import UnifiedSearchMixin

class IncidentAttachmentListCreateView(UnifiedSearchMixin, generics.ListCreateAPIView):
    """
    Lista y sube adjuntos de una incidencia (Refactorizado a CBV)
    """
    model = Document
    serializer_class = DocumentAttachmentListSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    default_select_related = ['created_by']
    search_fields_map = ['title', 'filename', 'description']
    
    def get_queryset(self):
        incident_id = self.kwargs.get('incident_id')
        queryset = self.get_optimized_queryset().filter(
            incident_id=incident_id,
            document_type='incident_attachment'
        ).order_by('-created_at')
        
        return self.apply_search(queryset)
    
    def perform_create(self, serializer):
        incident_id = self.kwargs.get('incident_id')
        incident = get_object_or_404(Incident, id=incident_id)
        
        file = self.request.FILES.get('file')
        title = self.request.data.get('title', file.name if file else 'Adjunto')
        description = self.request.data.get('description', '')
        is_public = self.request.data.get('is_public', 'false').lower() == 'true'
        
        # Crear directorio de forma segura usando el servicio
        country = get_current_country()
        incident_dir = os.path.join(settings.SHARED_DOCUMENTS_PATH, country, 'incident_attachments', f'incident_{incident_id}')
        if not os.path.exists(incident_dir):
            os.makedirs(incident_dir, exist_ok=True)
            
        file_path = os.path.join(incident_dir, file.name)
        with open(file_path, 'wb') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
                
        serializer.save(
            incident=incident,
            title=title,
            filename=file.name,
            description=description,
            document_type='incident_attachment',
            file_path=file_path,
            size=file.size,
            created_by=self.request.user,
            is_public=is_public
        )

class IncidentAttachmentDetailView(generics.RetrieveDestroyAPIView):
    """
    Obtiene detalles o elimina un adjunto de incidencia
    """
    queryset = Document.objects.filter(document_type='incident_attachment')
    serializer_class = DocumentAttachmentListSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'attachment_id'
    
    def perform_destroy(self, instance):
        # Eliminar archivo físico si existe antes de borrar el registro
        if instance.file_path and os.path.exists(instance.file_path):
            try:
                os.remove(instance.file_path)
            except Exception as e:
                logger.error(f"Error removiendo archivo físico: {e}")
        instance.delete()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_incident_attachment(request, incident_id, attachment_id):
    """Descarga de archivo (Mantenido como FBV por simplicidad de FileResponse)"""
    document = get_object_or_404(Document, id=attachment_id, incident_id=incident_id, document_type='incident_attachment')
    
    file_path = attachment_service.resolve_file_path(
        document.file_path,
        sub_folder='incident_attachments',
        incident_id=incident_id
    )
    
    if not file_path or not os.path.exists(file_path):
        return Response({'error': 'Archivo físico no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
    return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=document.filename)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_incident_attachment(request, incident_id, attachment_id):
    """Visualización de archivo en navegador"""
    document = get_object_or_404(Document, id=attachment_id, incident_id=incident_id, document_type='incident_attachment')
    
    file_path = attachment_service.resolve_file_path(
        document.file_path,
        sub_folder='incident_attachments',
        incident_id=incident_id
    )
    
    if not file_path or not os.path.exists(file_path):
        return Response({'error': 'Archivo físico no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    content_type = 'application/octet-stream'
    ext = document.filename.lower()
    if ext.endswith('.pdf'): content_type = 'application/pdf'
    elif ext.endswith(('.jpg', '.jpeg')): content_type = 'image/jpeg'
    elif ext.endswith('.png'): content_type = 'image/png'
    
    return FileResponse(open(file_path, 'rb'), content_type=content_type, filename=document.filename)
