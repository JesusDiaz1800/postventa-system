from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.http import FileResponse
import logging
import os

logger = logging.getLogger(__name__)

from .models import Incident, IncidentImage, LabReport, IncidentTimeline
from .serializers import (
    IncidentListSerializer, IncidentDetailSerializer, IncidentCreateUpdateSerializer,
    IncidentImageSerializer, LabReportSerializer, IncidentTimelineSerializer,
    IncidentImageUploadSerializer, LabReportCreateSerializer,
    IncidentStatusUpdateSerializer, IncidentCloseSerializer
)
from .filters import IncidentFilter
from .permissions import CanManageIncidents, CanViewIncidents


class IncidentListCreateView(generics.ListCreateAPIView):
    """List and create incidents"""
    permission_classes = [permissions.IsAuthenticated, CanViewIncidents]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = IncidentFilter
    search_fields = ['code', 'cliente', 'provider', 'obra', 'sku', 'lote']
    ordering_fields = ['created_at', 'fecha_reporte', 'prioridad', 'estado']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return IncidentCreateUpdateSerializer
        return IncidentListSerializer
    
    def get_queryset(self):
        user = self.request.user
        logger.info(f"Getting incidents for user: {user.username} (role: {user.role})")

        # Base queryset
        queryset = Incident.objects.all()

        # Filter based on user role
        if user.role == 'provider':
            # Providers can only see incidents related to their products
            queryset = queryset.filter(provider__icontains=user.username)
        
        # Apply state filter if provided
        estado = self.request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)

        # Optimize query to prevent N+1 problems
        return queryset.select_related(
            'created_by', 'assigned_to', 'closed_by'
        ).annotate(
            images_count=Count('images', distinct=True),
            documents_count=Count('attachments', distinct=True)
        )
    
    def perform_create(self, serializer):
        incident = serializer.save()
        
        # Create timeline entry
        IncidentTimeline.objects.create(
            incident=incident,
            action='created',
            description=f'Incidencia creada por {self.request.user.full_name}',
            user=self.request.user,
            metadata={'status': incident.estado}
        )


class IncidentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update and delete incidents"""
    permission_classes = [permissions.IsAuthenticated, CanViewIncidents]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return IncidentCreateUpdateSerializer
        return IncidentDetailSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'provider':
            return Incident.objects.filter(provider__icontains=user.username)
        else:
            return Incident.objects.all()
    
    def perform_update(self, serializer):
        old_incident = self.get_object()
        incident = serializer.save()
        
        # Create timeline entry for updates
        changes = []
        for field in serializer.validated_data:
            old_value = getattr(old_incident, field)
            new_value = getattr(incident, field)
            if old_value != new_value:
                changes.append(f"{field}: {old_value} → {new_value}")
        
        if changes:
            IncidentTimeline.objects.create(
                incident=incident,
                action='updated',
                description=f'Incidencia actualizada: {", ".join(changes)}',
                user=self.request.user,
                metadata={'changes': changes}
            )
    
    def perform_destroy(self, instance):
        """Override destroy to handle related objects"""
        try:
            # Create timeline entry before deletion using existing action
            IncidentTimeline.objects.create(
                incident=instance,
                action='closed',  # Use existing action
                description=f'Incidencia eliminada: {instance.code}',
                user=self.request.user
            )
            
            # Delete the incident (related objects will be deleted by CASCADE)
            instance.delete()
            
        except Exception as e:
            logger.error(f"Error deleting incident {instance.id}: {e}")
            # Delete without timeline entry if there's an error
            instance.delete()


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, CanManageIncidents])
def upload_incident_image(request, incident_id):
    """Upload image for an incident"""
    incident = get_object_or_404(Incident, id=incident_id)
    
    if 'image' not in request.FILES:
        return Response(
            {'error': 'No se proporcionó imagen'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    image_file = request.FILES['image']
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if image_file.content_type not in allowed_types:
        return Response(
            {'error': 'Tipo de archivo no permitido'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create incident image record
    incident_image = IncidentImage.objects.create(
        incident=incident,
        filename=image_file.name,
        path=f"incidents/{incident_id}/images/{image_file.name}",
        file_size=image_file.size,
        mime_type=image_file.content_type,
        uploaded_by=request.user
    )
    
    # Create timeline entry
    IncidentTimeline.objects.create(
        incident=incident,
        action='image_uploaded',
        description=f'Imagen subida: {image_file.name}',
        user=request.user,
        metadata={'filename': image_file.name, 'size': image_file.size}
    )
    
    serializer = IncidentImageSerializer(incident_image)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, CanManageIncidents])
def analyze_image(request, image_id):
    """Trigger AI analysis for an image"""
    from apps.ai_orchestrator.tasks import analyze_image_task
    
    image = get_object_or_404(IncidentImage, id=image_id)
    
    # Trigger AI analysis task
    task = analyze_image_task.delay(image.id)
    
    return Response({
        'message': 'Análisis de IA iniciado',
        'task_id': task.id
    }, status=status.HTTP_202_ACCEPTED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, CanManageIncidents])
def update_incident_status(request, incident_id):
    """Update incident status"""
    incident = get_object_or_404(Incident, id=incident_id)
    serializer = IncidentStatusUpdateSerializer(data=request.data)
    
    if serializer.is_valid():
        old_status = incident.estado
        old_assigned = incident.assigned_to
        
        incident.estado = serializer.validated_data['estado']
        if 'assigned_to' in serializer.validated_data:
            incident.assigned_to_id = serializer.validated_data['assigned_to']
        incident.save()
        
        # Create timeline entry
        description = f'Estado cambiado de {old_status} a {incident.estado}'
        if old_assigned != incident.assigned_to:
            if incident.assigned_to:
                description += f' y asignado a {incident.assigned_to.get_full_name()}'
            else:
                description += ' y desasignado'
        
        if 'description' in serializer.validated_data:
            description += f". {serializer.validated_data['description']}"
        
        IncidentTimeline.objects.create(
            incident=incident,
            action='status_changed',
            description=description,
            user=request.user,
            metadata={
                'old_status': old_status,
                'new_status': incident.estado,
                'old_assigned': old_assigned.id if old_assigned else None,
                'new_assigned': incident.assigned_to.id if incident.assigned_to else None
            }
        )
        
        return Response({'message': 'Estado actualizado exitosamente'})
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, CanManageIncidents])
def close_incident(request, incident_id):
    """Close an incident"""
    incident = get_object_or_404(Incident, id=incident_id)
    serializer = IncidentCloseSerializer(data=request.data)
    
    if serializer.is_valid():
        incident.close(request.user)
        
        # Create timeline entry
        IncidentTimeline.objects.create(
            incident=incident,
            action='closed',
            description=f'Incidencia cerrada: {serializer.validated_data["description"]}',
            user=request.user,
            metadata={
                'actions_taken': serializer.validated_data['actions_taken'],
                'closed_at': incident.closed_at.isoformat()
            }
        )
        
        return Response({'message': 'Incidencia cerrada exitosamente'})
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, CanManageIncidents])
def create_lab_report(request, incident_id):
    """Create a lab report for an incident"""
    incident = get_object_or_404(Incident, id=incident_id)
    serializer = LabReportCreateSerializer(
        data=request.data, 
        context={'incident_id': incident_id, 'request': request}
    )
    
    if serializer.is_valid():
        lab_report = serializer.save()
        
        # Create timeline entry
        IncidentTimeline.objects.create(
            incident=incident,
            action='lab_report_added',
            description=f'Reporte de laboratorio agregado por {lab_report.expert_name}',
            user=request.user,
            metadata={'lab_report_id': lab_report.id}
        )
        
        return Response(LabReportSerializer(lab_report).data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, CanViewIncidents])
def incident_dashboard(request):
    """Get dashboard data for incidents"""
    user = request.user
    
    # Base queryset
    if user.role == 'provider':
        incidents = Incident.objects.filter(provider__icontains=user.username)
    else:
        incidents = Incident.objects.all()
    
    # KPIs
    total_incidents = incidents.count()
    open_incidents = incidents.filter(estado__in=['abierto', 'triage', 'inspeccion']).count()
    closed_incidents = incidents.filter(estado='cerrado').count()
    # lab_required field removed
    
    # Incidents by status
    status_counts = incidents.values('estado').annotate(count=Count('id')).order_by('estado')
    
    # Incidents by priority
    priority_counts = incidents.values('prioridad').annotate(count=Count('id')).order_by('prioridad')
    
    # Recent incidents (separate query to avoid SQL Server issues)
    recent_incidents = incidents.order_by('-created_at')[:10]
    
    return Response({
        'kpis': {
            'total_incidents': total_incidents,
            'open_incidents': open_incidents,
            'closed_incidents': closed_incidents,
            # 'lab_required': lab_required,  # Field removed
        },
        'status_distribution': list(status_counts),
        'priority_distribution': list(priority_counts),
        'recent_incidents': IncidentListSerializer(recent_incidents, many=True).data
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_incident_images(request, incident_id):
    """Listar imágenes de una incidencia"""
    try:
        incident = get_object_or_404(Incident, id=incident_id)
        images = IncidentImage.objects.filter(incident=incident)
        
        serializer = IncidentImageSerializer(images, many=True)
        
        return Response({
            'success': True,
            'images': serializer.data
        })
        
    except Exception as e:
        logger.error(f"Error listando imágenes: {e}")
        return Response(
            {'error': 'Error interno del servidor'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def view_incident_image(request, incident_id, image_id):
    """Ver imagen de una incidencia de forma segura"""
    from django.conf import settings
    import os

    try:
        image = get_object_or_404(IncidentImage, id=image_id, incident_id=incident_id)
        
        # --- SECURITY FIX: Path Traversal --- 
        # 1. Sanitize the filename to prevent directory traversal attacks.
        safe_filename = os.path.basename(image.path)
        
        # 2. Construct the full, safe path by joining the secure base directory with the sanitized filename.
        # NOTE: This assumes image.path stores a relative path like 'incidents/123/images/file.jpg'
        # If image.path stores an absolute path, this logic needs adjustment.
        # Based on the upload logic, it seems to be relative.
        safe_path = os.path.join(settings.SHARED_DOCUMENTS_PATH, safe_filename)

        # 3. Verify that the final resolved path is actually within the shared documents directory.
        if not os.path.abspath(safe_path).startswith(os.path.abspath(settings.SHARED_DOCUMENTS_PATH)):
            logger.warning(f"Path traversal attempt blocked for image {image.id} by user {request.user.username}")
            return Response(
                {'error': 'Acceso denegado'}, 
                status=status.HTTP_403_FORBIDDEN
            )

        if not os.path.exists(safe_path):
            logger.error(f"Image file not found at safe path: {safe_path} for image record {image.id}")
            return Response(
                {'error': 'Archivo de imagen no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        response = FileResponse(
            open(safe_path, 'rb'),
            content_type=image.mime_type
        )
        response['Content-Disposition'] = f'inline; filename="{image.filename}"'
        
        return response
        
    except Exception as e:
        logger.error(f"Error viewing image: {e}")
        return Response(
            {'error': 'Error interno del servidor'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def escalated_incidents(request):
    """Obtener incidencias escaladas, especialmente desde reportes internos de calidad"""
    try:
        # Parámetros de filtrado
        without_quality_report = request.GET.get('without_quality_report', 'false').lower() == 'true'
        report_type = request.GET.get('report_type', '')
        from_quality_reports = request.GET.get('from_quality_reports', 'false').lower() == 'true'
        ready_for_supplier = request.GET.get('ready_for_supplier', 'false').lower() == 'true'
        
        # Base queryset - usar campos que existen en el modelo
        queryset = Incident.objects.all()
        
        # Filtrar por escalación si el campo existe
        if hasattr(Incident, 'escalated_to_quality'):
            queryset = queryset.filter(escalated_to_quality=True)
        
        # Filtros específicos usando campos existentes
        if without_quality_report:
            # Incidencias sin reporte de calidad - filtrar por campo relacionado si existe
            pass  # Implementar cuando tengamos el campo relacionado
        
        if from_quality_reports:
            # Incidencias escaladas desde reportes internos de calidad
            if hasattr(Incident, 'escalated_to_quality'):
                queryset = queryset.filter(escalated_to_quality=True)
        
        if ready_for_supplier:
            # Incidencias listas para escalamiento a proveedor
            if hasattr(Incident, 'escalated_to_quality') and hasattr(Incident, 'escalated_to_supplier'):
                queryset = queryset.filter(
                    escalated_to_quality=True,
                    escalated_to_supplier=False
                )
        
        # Ordenar por fecha de escalamiento
        if hasattr(Incident, 'escalation_date'):
            queryset = queryset.order_by('-escalation_date', '-created_at')
        else:
            queryset = queryset.order_by('-created_at')
        
        # Serializar datos usando campos que existen
        incidents_data = []
        for incident in queryset:
            incidents_data.append({
                'id': incident.id,
                'code': incident.code,
                'cliente': incident.cliente,
                'provider': incident.provider,
                'obra': incident.obra,
                'categoria': incident.categoria.name if incident.categoria else '',
                'description': getattr(incident, 'description', ''),
                'estado': incident.estado,
                'prioridad': incident.prioridad,
                'escalation_date': getattr(incident, 'escalation_date', None),
                'escalated_to_quality': getattr(incident, 'escalated_to_quality', False),
                'escalated_to_supplier': getattr(incident, 'escalated_to_supplier', False),
                'created_at': incident.created_at,
                'updated_at': incident.updated_at
            })
        
        return Response({
            'success': True,
            'incidents': incidents_data,
            'count': len(incidents_data)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo incidencias escaladas: {e}")
        return Response(
            {'error': f'Error interno del servidor: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def escalate_to_supplier(request, incident_id):
    """Escalar incidencia a proveedor desde reporte interno de calidad"""
    try:
        incident = get_object_or_404(Incident, id=incident_id)
        
        # Verificar que la incidencia esté escalada a calidad (si el campo existe)
        if hasattr(incident, 'escalated_to_quality') and not incident.escalated_to_quality:
            return Response(
                {'error': 'La incidencia debe estar escalada a calidad primero'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Actualizar la incidencia usando campos que existen
        if hasattr(incident, 'escalated_to_supplier'):
            incident.escalated_to_supplier = True
        if hasattr(incident, 'escalation_date'):
            incident.escalation_date = timezone.now()
        if hasattr(incident, 'escalation_reason'):
            incident.escalation_reason = request.data.get('reason', 'Escalado desde reporte interno de calidad')
        incident.save()
        
        # Registrar en auditoría
        try:
            from apps.audit.models import AuditLogManager
            AuditLogManager.log_action(
                user=request.user,
                action='escalar',
                description=f'Escaló incidencia {incident.code} a proveedor desde reporte interno de calidad',
                details={
                    'escalation_type': 'proveedor',
                    'escalated_to_supplier': True,
                    'reason': request.data.get('reason', 'Escalado desde reporte interno de calidad'),
                    'incident_code': incident.code,
                    'client': incident.cliente,
                    'provider': incident.provider
                }
            )
        except Exception as audit_error:
            logger.warning(f"Error registrando auditoría: {audit_error}")
        
        # TODO: Aquí se podría enviar un correo al proveedor
        # send_supplier_notification_email(incident)
        
        return Response({
            'success': True,
            'message': f'Incidencia {incident.code} escalada a proveedor exitosamente',
            'incident': {
                'id': incident.id,
                'code': incident.code,
                'escalated_to_supplier': getattr(incident, 'escalated_to_supplier', False),
                'escalation_date': getattr(incident, 'escalation_date', None)
            }
        })
        
    except Exception as e:
        logger.error(f"Error escalando incidencia a proveedor: {e}")
        return Response(
            {'error': 'Error interno del servidor'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
