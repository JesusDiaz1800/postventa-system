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


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def test_incidents_endpoint(request):
    """Test endpoint to debug incidents API"""
    logger.info(f"Test endpoint called by user: {request.user.username}")
    
    try:
        # Get all incidents without filters
        incidents = Incident.objects.all()
        logger.info(f"Total incidents in DB: {incidents.count()}")
        
        # Serialize
        serializer = IncidentListSerializer(incidents, many=True)
        logger.info(f"Serialized incidents count: {len(serializer.data)}")
        
        return Response({
            'success': True,
            'count': incidents.count(),
            'incidents': serializer.data,
            'user': request.user.username,
            'user_role': request.user.role
        })
        
    except Exception as e:
        logger.error(f"Error in test endpoint: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def simple_incidents_list(request):
    """Simple incidents list without complex filters"""
    logger.info(f"Simple incidents list called by user: {request.user.username}")
    
    try:
        # Get all incidents
        incidents = Incident.objects.all().order_by('-created_at')
        logger.info(f"Total incidents in DB: {incidents.count()}")
        
        # Serialize
        serializer = IncidentListSerializer(incidents, many=True)
        logger.info(f"Serialized incidents count: {len(serializer.data)}")
        
        # Return in the format expected by the frontend
        return Response({
            'results': serializer.data,
            'count': incidents.count(),
            'next': None,
            'previous': None
        })
        
    except Exception as e:
        logger.error(f"Error in simple incidents list: {e}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def debug_incidents_list(request):
    """Debug endpoint to see raw data"""
    logger.info(f"Debug incidents list called by user: {request.user.username}")
    
    try:
        # Get all incidents
        incidents = Incident.objects.all()
        logger.info(f"Total incidents in DB: {incidents.count()}")
        
        # Return raw data for debugging
        incidents_data = []
        for incident in incidents:
            incidents_data.append({
                'id': incident.id,
                'code': incident.code,
                'cliente': incident.cliente,
                'provider': incident.provider,
                'estado': incident.estado,
                'prioridad': incident.prioridad,
                'descripcion': incident.descripcion[:100] if incident.descripcion else '',
                'created_at': incident.created_at.isoformat() if incident.created_at else None
            })
        
        return Response({
            'success': True,
            'count': incidents.count(),
            'incidents': incidents_data,
            'user': request.user.username,
            'user_role': request.user.role
        })
        
    except Exception as e:
        logger.error(f"Error in debug incidents list: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return Response({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class IncidentListCreateView(generics.ListCreateAPIView):
    """List and create incidents"""
    permission_classes = [permissions.IsAuthenticated, CanViewIncidents]
    # Temporarily disable complex filters to debug
    # filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_class = IncidentFilter
    # search_fields = ['code', 'cliente', 'provider', 'obra', 'sku', 'lote']
    # ordering_fields = ['created_at', 'fecha_reporte', 'prioridad', 'estado']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return IncidentCreateUpdateSerializer
        return IncidentListSerializer
    
    def get_queryset(self):
        user = self.request.user
        logger.info(f"Getting incidents for user: {user.username} (role: {user.role})")
        
        # Filter based on user role
        if user.role == 'provider':
            # Providers can only see incidents related to their products
            queryset = Incident.objects.filter(provider__icontains=user.username)
        elif user.role in ['customer_service']:
            # Customer service can see all incidents
            queryset = Incident.objects.all()
        else:
            # Other roles can see all incidents
            queryset = Incident.objects.all()
        
        # Apply state filter if provided
        estado = self.request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
            logger.info(f"Filtered by estado '{estado}': {queryset.count()} incidents")
        
        logger.info(f"Base queryset count: {queryset.count()}")
        return queryset
    
    def list(self, request, *args, **kwargs):
        """Override list method to add logging"""
        logger.info(f"IncidentListCreateView.list called by user: {request.user.username}")
        logger.info(f"Request filters: {request.GET}")
        
        # Get the queryset
        queryset = self.filter_queryset(self.get_queryset())
        logger.info(f"Filtered queryset count: {queryset.count()}")
        
        # Serialize the data
        serializer = self.get_serializer(queryset, many=True)
        logger.info(f"Serialized data count: {len(serializer.data)}")
        
        # Return response
        response = super().list(request, *args, **kwargs)
        logger.info(f"Response data type: {type(response.data)}")
        logger.info(f"Response data: {response.data}")
        
        return response
    
    def create(self, request, *args, **kwargs):
        """Override create method to add detailed logging"""
        logger.info(f"IncidentListCreateView.create called by user: {request.user.username}")
        logger.info(f"Request data: {request.data}")
        logger.info(f"Request content type: {request.content_type}")
        
        try:
            # Get serializer
            serializer = self.get_serializer(data=request.data)
            logger.info(f"Serializer data: {serializer.initial_data}")
            
            # Validate data
            if serializer.is_valid():
                logger.info("Serializer is valid")
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                logger.info(f"Incident created successfully: {serializer.data}")
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            else:
                logger.error(f"Serializer validation errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error in create method: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return Response({
                'error': str(e),
                'detail': 'Error interno del servidor'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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
    """Ver imagen de una incidencia"""
    try:
        incident = get_object_or_404(Incident, id=incident_id)
        image = get_object_or_404(IncidentImage, id=image_id, incident=incident)
        
        if not os.path.exists(image.path):
            return Response(
                {'error': 'Imagen no encontrada'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        response = FileResponse(
            open(image.path, 'rb'),
            content_type=image.mime_type
        )
        response['Content-Disposition'] = f'inline; filename="{image.filename}"'
        
        return response
        
    except Exception as e:
        logger.error(f"Error viendo imagen: {e}")
        return Response(
            {'error': 'Error interno del servidor'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
