from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from apps.core.filters import SmartSearchFilter
from django.http import FileResponse
import logging
import os

logger = logging.getLogger(__name__)

from .models import Incident, IncidentImage, LabReport, IncidentTimeline
from .serializers import (
    IncidentListSerializer, IncidentDetailSerializer, IncidentCreateUpdateSerializer,
    IncidentImageSerializer, LabReportSerializer, IncidentTimelineSerializer,
    IncidentImageUploadSerializer, LabReportCreateSerializer,
    IncidentStatusUpdateSerializer, IncidentCloseSerializer,
    EscalatedIncidentSerializer
)
from .filters import IncidentFilter
from .permissions import CanManageIncidents, CanViewIncidents


class IncidentListCreateView(generics.ListCreateAPIView):
    """List and create incidents"""
    permission_classes = [permissions.IsAuthenticated, CanViewIncidents]
    filter_backends = [DjangoFilterBackend, SmartSearchFilter, OrderingFilter]
    filterset_class = IncidentFilter
    search_fields = ['code', 'cliente', 'provider', 'obra', 'sku', 'lote']
    ordering_fields = ['created_at', 'fecha_reporte', 'fecha_deteccion', 'prioridad', 'estado']
    ordering = ['-fecha_deteccion', '-created_at']  # Primero por fecha de detección, luego por creación
    
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
        
        # Ocultar canceladas por defecto (Soft Delete / Papelera)
        # Solo se muestran las canceladas si se solicita explícitamente vía filtro de estado
        estado = self.request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        else:
            # Si no hay filtro de estado, excluimos las canceladas (comportamiento por defecto)
            queryset = queryset.exclude(estado='cancelada')

        # Optimize query to prevent N+1 problems
        return queryset.select_related(
            'created_by', 'assigned_to', 'closed_by', 'categoria', 'responsable'
        ).annotate(
            images_count=Count('images', distinct=True),
            documents_count=Count('attachments', distinct=True)
        )
    def create(self, request, *args, **kwargs):
        """Sobrescribimos create para retornar la data fresca con sap_doc_num incluido"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Al finalizar perform_create, la BD ya tiene los Folios SAP
        incident = serializer.instance
        headers = self.get_success_headers(serializer.data)
        
        # Re-serializamos para capturar 'sap_doc_num' y 'sap_call_id' generados
        refresh_serializer = self.get_serializer(incident)
        return Response(refresh_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        incident = serializer.save()
        
        # Sincronización con SAP Service Layer (Síncrona para feedback inmediato)
        try:
            from apps.sap_integration.sap_transaction_service import SAPTransactionService
            from apps.incidents.models import IncidentTimeline
            
            if incident.customer_code:
                sap_service = SAPTransactionService()
                # 1. Prioridad: el ID técnico asignado explícitamente a la incidencia (capturado del UI)
                technician_code = incident.technician_code
                # 2. Respaldo histórico: si está vacío, intentar deducirlo del responsable asignado
                if not technician_code and incident.responsable and hasattr(incident.responsable, 'sap_technician_id'):
                    technician_code = incident.responsable.sap_technician_id
                problem_type = incident.categoria.sap_problem_type_id if incident.categoria and incident.categoria.sap_problem_type_id else 1
                
                result = sap_service.create_service_call(
                    customer_code=incident.customer_code,
                    subject=f"Incidencia App: {incident.code}",
                    description=incident.descripcion or "Generada desde App Postventa",
                    priority=incident.prioridad,
                    technician_code=technician_code,
                    problem_type=problem_type,
                    bp_project_code=incident.project_code,
                    salesperson_code=incident.salesperson_code,
                    salesperson_name=incident.salesperson,
                    ship_address=incident.direccion_cliente,
                    obra_name=incident.obra,
                    start_date=incident.fecha_deteccion,
                    start_time=incident.hora_deteccion.strftime('%H%M') if incident.hora_deteccion else None,
                    category_name=incident.categoria.name if incident.categoria else None,
                    subcategory_name=incident.subcategoria,
                )
                
                if result.get('success'):
                    incident.sap_call_id = result.get('service_call_id')
                    incident.sap_doc_num = result.get('doc_num')
                    incident.save(update_fields=['sap_call_id', 'sap_doc_num'])
                    
                    IncidentTimeline.objects.create(
                        incident=incident,
                        action='sap_synced',
                        description=f'Sincronizado con SAP exitosamente. Folio SAP (DocNum): {incident.sap_doc_num}',
                        user=incident.created_by,
                        metadata={'sap_id': incident.sap_call_id, 'sap_doc_num': incident.sap_doc_num}
                    )
                else:
                    IncidentTimeline.objects.create(
                        incident=incident,
                        action='sap_sync_failed',
                        description=f'Error al sincronizar con SAP: {result.get("error")}',
                        user=incident.created_by,
                        metadata={'error': result.get('error')}
                    )
        except Exception as e:
            logger.error(f"Error en sincronización síncrona con SAP: {e}")


class IncidentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update and delete incidents"""
    permission_classes = [permissions.IsAuthenticated, CanViewIncidents]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return IncidentCreateUpdateSerializer
        return IncidentDetailSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        # Optimize query for detail view to prevent N+1 problems
        queryset = Incident.objects.all()
        
        if user.role == 'provider':
            queryset = queryset.filter(provider__icontains=user.username)
            
        return queryset.select_related(
            'created_by', 'assigned_to', 'closed_by', 'categoria', 'responsable'
        ).prefetch_related(
            'images', 'timeline', 'timeline__user', 'attachments'
        )
    
    def perform_update(self, serializer):
        old_incident = self.get_object()
        
        # PRE-SAVE: Capturar valores antiguos antes de que serializer.save() mute la instancia en memoria
        old_values = {}
        for field in serializer.validated_data:
            val = getattr(old_incident, field, None)
            # Extraer IDs para llaves foráneas para comparación segura
            old_values[field] = val.pk if hasattr(val, 'pk') else val

        incident = serializer.save()
        
        # Create timeline entry for updates
        changes = []
        for field in serializer.validated_data:
            old_value = old_values.get(field)
            new_val_obj = getattr(incident, field, None)
            new_value = new_val_obj.pk if hasattr(new_val_obj, 'pk') else new_val_obj
            
            if old_value != new_value:
                # Para el log en BD, humanizamos un poco si es un objeto
                old_display = getattr(old_incident, field, None)
                new_display = getattr(incident, field, None)
                old_str = old_display.name if hasattr(old_display, 'name') else old_value
                new_str = new_display.name if hasattr(new_display, 'name') else new_value
                
                changes.append(f"{field}: {old_str} → {new_str}")
        
        if changes:
            IncidentTimeline.objects.create(
                incident=incident,
                action='updated',
                description=f'Incidencia actualizada: {", ".join(changes)}',
                user=self.request.user,
                metadata={'changes': changes}
            )
            
            # Sincronizar Cambios Hacia SAP SL si existe llamada
            if incident.sap_call_id:
                try:
                    from apps.sap_integration.sap_transaction_service import SAPTransactionService
                    sap = SAPTransactionService(request_user=self.request.user)
                    # Parchearemos algunos campos básicos que impactan en SAP:
                    # Priority, Subject, Description
                    update_payload = {}
                    
                    for field in serializer.validated_data:
                        if field == 'prioridad':
                            prio_map = {'baja': 'scp_Low', 'media': 'scp_Medium', 'alta': 'scp_High'}
                            update_payload["Priority"] = prio_map.get(incident.prioridad, 'scp_Low')
                        elif field == 'descripcion':
                            update_payload["Description"] = incident.descripcion
                    
                    logger.info(f"== PATCH TO SAP ATTEMPT == Validated_Data: {list(serializer.validated_data.keys())} | Payload generado: {update_payload}")
                    if update_payload:
                        from apps.sap_integration.sap_query_service import SAPQueryService
                        sap_query = SAPQueryService()
                        internal_call_id = incident.sap_call_id
                        call_data = sap_query.get_service_call(incident.sap_call_id)
                        if call_data and 'call_id' in call_data:
                            internal_call_id = call_data['call_id']
                            
                        res = sap.update_service_call(internal_call_id, update_payload)
                        logger.info(f"SAP Patch response: {res}")
                except Exception as e:
                    logger.error(f"Error sincronizando actualización de incidencia con SAP: {e}")
    
    def destroy(self, request, *args, **kwargs):
        """Override destroy to perform 'Soft Delete' (Cancellation)"""
        try:
            # 1. Permisos de eliminación/cancelación
            if request.user.role not in ['admin', 'administrador', 'coordinador']:
                 return Response(
                     {"error": "No tienes permisos suficientes para cancelar esta incidencia."},
                     status=status.HTTP_403_FORBIDDEN
                 )

            instance = self.get_object()
            
            # 2. Preparar mensaje de resolución
            resolution_text = request.data.get('resolution_text', 'Sin motivo especificado.')
            resolution_msg = f"Cancelada por eliminacion de la app. Motivo: {resolution_text}"

            # 3. Cancelar en SAP si aplica
            if instance.sap_call_id:
                import logging
                logger = logging.getLogger(__name__)
                try:
                    from apps.sap_integration.sap_transaction_service import SAPTransactionService
                    from apps.sap_integration.sap_query_service import SAPQueryService
                    from apps.core.thread_local import get_current_country
                    
                    country = get_current_country()
                    sap = SAPTransactionService()
                    sap_query = SAPQueryService()
                    
                    # 1. Resolver el CallID Interno (DocEntry) a partir del DocNum guardado
                    internal_call_id = instance.sap_call_id
                    try:
                        call_data = sap_query.get_service_call(instance.sap_call_id)
                        if call_data and 'call_id' in call_data:
                            internal_call_id = call_data['call_id']
                            logger.info(f"SAP-TX: DocNum {instance.sap_call_id} resuelto a DocEntry {internal_call_id} para cancelacion en {country}")
                        else:
                            logger.warning(f"SAP-TX: No se pudo resolver DocEntry para {instance.sap_call_id} en {country}. Usando {internal_call_id} como fallback.")
                    except Exception as e:
                        logger.error(f"SAP-TX: Error resolviendo CallID interno: {e}")
                        
                    # Sincronizar cancelación
                    res = sap.cancel_service_call(internal_call_id, resolution=resolution_msg)
                    if not res.get('success'):
                         logger.warning(f"No se pudo cancelar en SAP ({country}) la llamada {instance.sap_call_id}: {res.get('error')}")
                    else:
                         logger.info(f"Cancelacion SAP ({country}) exitosa para incidencia {instance.code}")
                         
                except Exception as sap_err:
                    logger.error(f"Excepcion al intentar cancelar servicio SAP {instance.sap_call_id}: {sap_err}")

            # 4. Aplicar Soft Delete (Cancelación) en DB Local
            instance.estado = 'cancelada'
            instance.closure_summary = resolution_msg
            instance.closed_at = timezone.now()
            instance.closed_by = request.user
            instance.save()
            
            # 5. Registrar en timeline
            from .models import IncidentTimeline
            IncidentTimeline.objects.create(
                incident=instance,
                user=request.user,
                action='cancelled',
                description=resolution_msg
            )

            # 5. Crear DeletedItem para que aparezca en Auditoría -> Papelera
            try:
                from apps.audit.models import DeletedItem
                from django.core import serializers
                import json
                
                # Serializar el estado actual (cancelado)
                serialized_data = serializers.serialize('json', [instance])
                json_data = json.loads(serialized_data)
                
                # Eliminar backup previo si existiera para este ID
                DeletedItem.objects.filter(original_id=str(instance.pk), model_name='incident').delete()
                
                DeletedItem.objects.create(
                    original_id=str(instance.pk),
                    model_name='incident',
                    app_label='incidents',
                    object_repr=str(instance),
                    serialized_data=json_data,
                    deleted_by=request.user
                )
            except Exception as e:
                logger.error(f"Error creating DeletedItem for soft-delete: {e}")

            # Usamos el serializer de detalle para retornar la instancia actualizada
            serializer = IncidentDetailSerializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            logger.error(f"Error cancelling incident {kwargs.get('pk')}: {str(e)}\n{traceback.format_exc()}")
            return Response(
                {"error": f"Error al procesar la cancelación: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

    def perform_destroy(self, instance):
        """Override destroy to handle related objects"""
        print(f"DEBUG: perform_destroy called for incident {instance.id}")
        try:
            # No creamos IncidentTimeline porque se eliminará en cascada con la incidencia
            # Intentar eliminar la incidencia
            instance.delete()
            
        except Exception as e:
            logger.error(f"Error deleting incident {instance.id}: {e}")
            logger.error(f"DEBUG: Exception in perform_destroy: {e}")
            raise e  # Let destroy catch it


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
    
    try:
        from apps.core.thread_local import get_current_country
        country = get_current_country()
        
        # Define relative path and absolute path per country
        relative_path = f"{country}/incidents/{incident_id}/images/{image_file.name}"
        
        # Ensure directory exists in SHARED_DOCUMENTS_PATH
        from django.conf import settings
        full_path = os.path.join(settings.SHARED_DOCUMENTS_PATH, country, "incidents", str(incident_id), "images")
        os.makedirs(full_path, exist_ok=True)
        
        # Save file physically
        final_path = os.path.join(full_path, image_file.name)
        with open(final_path, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)
                
        # Create incident image record with Verified Path
        incident_image = IncidentImage.objects.create(
            incident=incident,
            filename=image_file.name,
            path=relative_path, # Guardamos el path relativo con país
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

    except Exception as e:
        logger.error(f"Error saving image file: {e}")
        return Response(
            {'error': 'Error al guardar el archivo de imagen'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


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
    """
    Close an incident with required summary
    
    Requires:
    - stage: Stage where the incident is being closed (incidencia, reporte_visita, calidad, proveedor)
    - closure_summary: Required description of actions, conclusions and decisions (min 10 chars)
    - closure_attachment: Optional path to closure attachment file
    """
    incident = get_object_or_404(Incident, id=incident_id)
    serializer = IncidentCloseSerializer(data=request.data)
    
    if serializer.is_valid():
        # Call the improved close method with all parameters
        incident.close(
            user=request.user,
            stage=serializer.validated_data['stage'],
            summary=serializer.validated_data['closure_summary'],
            attachment_path=serializer.validated_data.get('closure_attachment', ''),
            technician_code=serializer.validated_data.get('technician_code')
        )
        
        # Create detailed timeline entry
        IncidentTimeline.objects.create(
            incident=incident,
            action='closed',
            description=f'Incidencia cerrada en etapa "{incident.get_closed_at_stage_display()}": {serializer.validated_data["closure_summary"][:100]}...',
            user=request.user,
            metadata={
                'stage': serializer.validated_data['stage'],
                'closure_summary': serializer.validated_data['closure_summary'],
                'closure_attachment': serializer.validated_data.get('closure_attachment', ''),
                'closed_at': incident.closed_at.isoformat(),
                'resolution_time_hours': incident.resolution_time_hours,
                'sla_breached': incident.sla_breached
            }
        )
        
        return Response({
            'success': True,
            'message': 'Incidencia cerrada exitosamente',
            'incident': {
                'id': incident.id,
                'code': incident.code,
                'closed_at': incident.closed_at,
                'closed_at_stage': incident.closed_at_stage,
                'resolution_time_hours': incident.resolution_time_hours,
                'sla_breached': incident.sla_breached
            }
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, CanManageIncidents])
def reopen_incident(request, incident_id):
    """
    Reopen a closed incident
    """
    incident = get_object_or_404(Incident, id=incident_id)
    
    if incident.estado != 'cerrado':
        return Response(
            {'error': 'La incidencia no está cerrada'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
            
    # Reopen logic
    old_status = incident.estado
    incident.estado = 'abierto'
    # We keep historical data but clear current closure status
    # Alternatively we can keep them for record. 
    # But usually reopening means it's active again.
    incident.closed_at = None
    incident.closed_by = None
    # We might want to keep the stage or summary, but usually we clear specific closure metadata
    # unless we want to keep history. Timeline keeps history.
    incident.save()
    
    # Create timeline entry
    IncidentTimeline.objects.create(
        incident=incident,
        action='reopened',
        description='Incidencia reabierta',
        user=request.user,
        metadata={
            'previous_status': old_status
        }
    )
    
    return Response({
        'success': True,
        'message': 'Incidencia reabierta exitosamente',
        'incident': {
            'id': incident.id,
            'code': incident.code,
            'status': incident.estado
        }
    })


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


from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, CanViewIncidents])
@cache_page(60 * 15) # Cache for 15 minutes
def incident_dashboard(request):
    """Get dashboard data for incidents - Returns data structure for ReportsPage"""
    from django.db.models.functions import TruncMonth, ExtractYear, ExtractMonth
    from collections import defaultdict
    import calendar
    
    user = request.user
    
    # Get query parameters
    year_param = request.GET.get('year')
    category_param = request.GET.get('category')
    
    # Base queryset
    if user.role == 'provider':
        incidents = Incident.objects.filter(provider__icontains=user.username)
    else:
        incidents = Incident.objects.all()
    
    # Filter by year if provided
    if year_param:
        try:
            year_int = int(year_param)
            incidents = incidents.filter(fecha_deteccion__year=year_int)
        except ValueError:
            pass
    
    # Filter by category if provided (for drill-down)
    if category_param:
        incidents = incidents.filter(categoria__name__icontains=category_param)
    
    # KPIs by Estado
    abiertos = incidents.filter(estado__in=['abierto', 'triage', 'inspeccion']).count()
    laboratorio = incidents.filter(estado__in=['laboratorio', 'calidad', 'en_calidad']).count()
    proveedor = incidents.filter(estado='proveedor').count()
    cerrados = incidents.filter(estado='cerrado').count()
    
    # Monthly Stats (for current year or selected year)
    # Si no hay filtro, usar el año más reciente con datos
    if year_param:
        current_year = int(year_param)
    else:
        # Obtener el año más reciente que tenga incidencias
        latest_incident = incidents.order_by('-fecha_deteccion').first()
        current_year = latest_incident.fecha_deteccion.year if latest_incident else timezone.now().year
    
    monthly_data = incidents.filter(
        fecha_deteccion__year=current_year
    ).annotate(
        month=ExtractMonth('fecha_deteccion')
    ).values('month').annotate(
        total=Count('id')
    ).order_by('month')
    
    # Create monthly stats array with all 12 months
    monthly_stats = []
    month_counts = {item['month']: item['total'] for item in monthly_data}
    for m in range(1, 13):
        monthly_stats.append({
            'name': calendar.month_abbr[m],
            'total': month_counts.get(m, 0)
        })
    
    # Yearly Stats - TODO el histórico disponible
    yearly_data = Incident.objects.all().annotate(
        year=ExtractYear('fecha_deteccion')
    ).values('year').annotate(
        count=Count('id')
    ).order_by('year')
    
    # Crear array con todos los años que tienen datos
    yearly_stats_data = []
    for item in yearly_data:
        if item['year']:  # Ignorar nulls
            yearly_stats_data.append({
                'name': str(item['year']),
                'value': item['count']
            })
    
    # Get available years for dropdown
    all_years = Incident.objects.annotate(
        year=ExtractYear('fecha_deteccion')
    ).values_list('year', flat=True).distinct().order_by('-year')
    years = list(all_years)
    
    # Top Clients (by incident count)
    top_clients_data = incidents.values('cliente').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    top_clients = [[item['cliente'] or 'Sin Cliente', item['count']] for item in top_clients_data]
    
    # Top Providers (by incident count)
    top_providers_data = incidents.values('provider').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    top_providers = [[item['provider'] or 'Sin Proveedor', item['count']] for item in top_providers_data]
    
    # Category Tree (for drill-down)
    category_tree = {}
    if not category_param:
        # Top-level categories
        categories_data = incidents.values('categoria__name').annotate(
            count=Count('id')
        ).order_by('-count')
        
        for item in categories_data:
            cat_name = item['categoria__name'] or 'Sin Categoría'
            category_tree[cat_name] = {
                'count': item['count'],
                'total': item['count'],  # Compatibilidad con PieChart
                'subcategories': {}
            }
    else:
        # Subcategories for selected category
        subcategories_data = incidents.values('subcategoria').annotate(
            count=Count('id')
        ).order_by('-count')
        
        for item in subcategories_data:
            subcat_name = item['subcategoria'] or 'Sin Subcategoría'
            category_tree[subcat_name] = {
                'count': item['count']
            }
    
    return Response({
        'abiertos': abiertos,
        'laboratorio': laboratorio,
        'proveedor': proveedor,
        'cerrados': cerrados,
        'monthlyStats': monthly_stats,
        'yearlyStatsData': yearly_stats_data,
        'years': years,
        'topClients': top_clients,
        'topProviders': top_providers,
        'categoryTree': category_tree
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def global_search(request):
    """
    Búsqueda global multi-tipo para el componente GlobalSearch del frontend.
    Busca en Incidencias, Reportes de Visita, Reportes de Calidad y Reportes de Proveedor.
    Acepta: ?q=<query>
    """
    q = request.GET.get('q', '').strip()
    if not q or len(q) < 2:
        return Response({'results': []})

    results = []
    limit_each = 5  # Máximo 5 por tipo

    # Incidencias
    try:
        incidents = Incident.objects.filter(
            Q(code__icontains=q) | Q(cliente__icontains=q) | Q(obra__icontains=q) | Q(sku__icontains=q)
        ).order_by('-created_at')[:limit_each]
        for inc in incidents:
            results.append({
                'id': inc.id,
                'type': 'incident',
                'title': f'{inc.code} - {inc.cliente}',
                'subtitle': inc.obra or inc.descripcion[:60] if inc.descripcion else 'Sin descripción',
                'url': f'/incidents/{inc.id}',
            })
    except Exception as e:
        logger.warning(f"GlobalSearch error (incidents): {e}")

    # Reportes de visita
    try:
        from apps.documents.models import VisitReport
        visit_reports = VisitReport.objects.filter(
            Q(report_number__icontains=q) | Q(incident__cliente__icontains=q) | Q(incident__obra__icontains=q)
        ).select_related('incident').order_by('-created_at')[:limit_each]
        for vr in visit_reports:
            results.append({
                'id': vr.id,
                'type': 'visit_report',
                'title': f'Reporte Visita #{vr.report_number}',
                'subtitle': vr.incident.cliente if vr.incident else 'Sin cliente',
                'url': f'/visit-reports/{vr.id}',
            })
    except Exception as e:
        logger.warning(f"GlobalSearch error (visit_reports): {e}")

    # Reportes de calidad (QualityReport)
    try:
        from apps.documents.models import QualityReport
        q_reports = QualityReport.objects.filter(
            Q(report_number__icontains=q) | Q(incident__cliente__icontains=q)
        ).select_related('incident').order_by('-created_at')[:limit_each]
        for qr in q_reports:
            results.append({
                'id': qr.id,
                'type': 'quality_report',
                'title': f'Reporte Calidad #{qr.report_number}',
                'subtitle': qr.incident.cliente if qr.incident else 'Sin cliente',
                'url': f'/quality-reports/{qr.id}',
            })
    except Exception as e:
        logger.warning(f"GlobalSearch error (quality_reports): {e}")

    # Reportes de proveedor (SupplierReport)
    try:
        from apps.documents.models import SupplierReport
        s_reports = SupplierReport.objects.filter(
            Q(report_number__icontains=q) | Q(incident__cliente__icontains=q) | Q(supplier_name__icontains=q)
        ).select_related('incident').order_by('-created_at')[:limit_each]
        for sr in s_reports:
            results.append({
                'id': sr.id,
                'type': 'supplier_report',
                'title': f'Reporte Proveedor #{sr.report_number}',
                'subtitle': sr.supplier_name or (sr.incident.cliente if sr.incident else 'Sin proveedor'),
                'url': f'/supplier-reports/{sr.id}',
            })
    except Exception as e:
        logger.warning(f"GlobalSearch error (supplier_reports): {e}")

    return Response({'results': results[:20]})  # máximo 20 total




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
        
        # 2. Construct the full, safe path 
        # image.path should contain "incidents/{id}/images/{filename}"
        safe_path = os.path.join(settings.SHARED_DOCUMENTS_PATH, image.path)
        
        # Normpath to resolve any .. components
        safe_path = os.path.normpath(safe_path)

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


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated, CanManageIncidents])
def delete_incident_image(request, incident_id, image_id):
    """Delete an incident image"""
    try:
        image = get_object_or_404(IncidentImage, id=image_id, incident_id=incident_id)
        
        # Store info for logging
        filename = image.filename
        
        # Delete physical file
        if image.path:
            from django.conf import settings
            full_path = os.path.join(settings.SHARED_DOCUMENTS_PATH, image.path)
            # Normalize path to prevent issues
            full_path = os.path.normpath(full_path)
            if os.path.exists(full_path):
                os.remove(full_path)
                
        # Delete record
        image.delete()
        
        # Log action
        IncidentTimeline.objects.create(
            incident=image.incident,
            action='image_deleted',
            description=f'Imagen eliminada: {filename}',
            user=request.user
        )
        
        return Response({'message': 'Imagen eliminada exitosamente'}, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error deleting image: {e}")
        return Response(
            {'error': 'Error interno al eliminar la imagen'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def escalated_incidents(request):
    """Obtener incidencias escaladas, especialmente desde reportes internos de calidad"""
    try:
        # Parámetros de filtrado
        without_quality_report = request.GET.get('without_quality_report', 'false').lower() == 'true'
        escalated_to_internal = request.GET.get('escalated_to_internal', 'false').lower() == 'true'
        from_quality_reports = request.GET.get('from_quality_reports', 'false').lower() == 'true'
        ready_for_supplier = request.GET.get('ready_for_supplier', 'false').lower() == 'true'
        report_type = request.GET.get('report_type', None)
        
        # Base queryset - usar campos que existen en el modelo
        queryset = Incident.objects.select_related('categoria').all()
        
        # LOGICA PRINCIPAL DE FILTRADO POR TIPO
        if report_type == 'cliente':
            # Solo mostrar incidencias que hayan sido escaladas a calidad (cliente)
            queryset = queryset.filter(
                Q(escalated_to_quality=True) | 
                Q(estado__in=['laboratorio', 'calidad', 'en_calidad'])
            )
        elif report_type == 'interno' or escalated_to_internal:
            # Mostrar incidencias escaladas a calidad (general o interna)
            queryset = queryset.filter(
                Q(escalated_to_internal_quality=True) | 
                Q(escalated_to_quality=True)
            )
            
        elif ready_for_supplier:
             # Incidencias listas para escalamiento a proveedor
            queryset = queryset.filter(
                escalated_to_quality=True,
                escalated_to_supplier=False
            )
            
        elif from_quality_reports:
             queryset = queryset.filter(escalated_to_quality=True)
             
        else:
             # Default fallback prevention: If no explicit filter matches, return EMPTY
             # or only basic escalated ones to prevent leaking all incidents
             queryset = queryset.filter(
                Q(escalated_to_quality=True) | 
                Q(escalated_to_internal_quality=True) |
                Q(escalated_to_supplier=True)
             )
        
        
        
        # Filtros específicos usando campos existentes
        if without_quality_report:
            # Incidencias sin reporte de calidad
            # Excluir las que ya tienen un quality_report asociado
            try:
                from apps.documents.models import QualityReport
                # Filtramos las incidencias que ya tienen un reporte interno
                existing_report_incidents = QualityReport.objects.filter(
                    report_type='interno'
                ).values_list('related_incident_id', flat=True)
                
                queryset = queryset.exclude(id__in=existing_report_incidents)
            except Exception as e:
                logger.error(f"Error filtering quality reports: {e}") 
        
        # Ordenar por fecha de escalamiento
        if hasattr(Incident, 'escalation_date'):
            queryset = queryset.order_by('-escalation_date', '-created_at')
        else:
            queryset = queryset.order_by('-created_at')
        
        # Serializar datos de forma eficiente
        serializer = EscalatedIncidentSerializer(queryset, many=True)
        
        return Response({
            'success': True,
            'incidents': serializer.data,
            'count': len(serializer.data)
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
        
        try:
            # from .services.email_service import EmailService
            # email_service = EmailService()
            # # Buscar si hay un reporte de calidad para adjuntar
            # quality_report_path = None
            # if hasattr(incident, 'quality_reports') and incident.quality_reports.exists():
            #     last_report = incident.quality_reports.filter(report_type='cliente', pdf_path__isnull=False).last()
            #     if last_report and last_report.pdf_path:
            #         quality_report_path = last_report.pdf_path
            
            # email_service.send_escalation_to_supplier_email(incident, quality_report_path)
            pass
        except Exception as email_err:
            logger.warning(f"Error enviando correo al proveedor: {email_err}")
        
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

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def fix_escalation(request, incident_id):
    """
    Corregir escalamiento accidental (Admin only).
    Deshace el ÚLTIMO paso de escalamiento realizado.
    """
    try:
        # Verificar que el usuario sea admin
        if not request.user.role == 'admin':
             return Response(
                {'error': 'No tienes permisos para realizar esta acción'}, 
                status=status.HTTP_403_FORBIDDEN
            )

        incident = get_object_or_404(Incident, id=incident_id)
        
        # Guardar estado anterior para log
        old_status = incident.estado
        msg = ""

        # Lógica de deshacer paso a paso (orden inverso al flujo)
        
        # 1. Si está en Proveedor -> Volver a Interno
        if getattr(incident, 'escalated_to_supplier', False):
            incident.escalated_to_supplier = False
            # Volver a estado de laboratorio/calidad
            incident.estado = 'laboratorio' 
            msg = "Se deshizo el escalamiento a Proveedor. Regresado a Calidad Interna."
            
        # 2. Si está en Interno (y no proveedor) -> Volver a Cliente
        elif getattr(incident, 'escalated_to_internal_quality', False):
            incident.escalated_to_internal_quality = False
            # El estado sigue siendo laboratorio, pero sin el flag interno
            # esto lo hace visible solo en reportes de cliente
            incident.estado = 'laboratorio'
            msg = "Se deshizo el escalamiento a Calidad Interna. Regresado a Calidad Cliente."

        # 3. Si está en Cliente (y no interno) -> Volver a Visita o Abierto
        elif getattr(incident, 'escalated_to_quality', False) or incident.estado in ['laboratorio', 'calidad', 'en_calidad']:
            incident.escalated_to_quality = False
            
            # Verificar si existe reporte de visita para saber a qué estado volver
            has_visit_report = hasattr(incident, 'documents_visit_reports') and incident.documents_visit_reports.exists()
            
            if has_visit_report:
                incident.estado = 'reporte_visita'
                msg = "Se deshizo el escalamiento a Calidad. Regresado a Reporte de Visita."
            else:
                incident.estado = 'abierto'
                msg = "Se deshizo el escalamiento a Calidad. Regresado a 'Abierto' (No hay reporte de visita)."
            
        else:
            return Response({
                'error': 'No se detectó un estado de escalamiento corregible o la incidencia ya está en estado base.'
            }, status=status.HTTP_400_BAD_REQUEST)

        incident.save()
        
        # Log timeline
        try:
            IncidentTimeline.objects.create(
                incident=incident,
                action='status_changed',
                description=f'Escalamiento corregido (undo): {msg}',
                user=request.user,
                metadata={'old_status': old_status, 'new_status': incident.estado}
            )
        except Exception as e:
            logger.error(f"Error logging timeline for fix_escalation: {e}")
        
        logger.info(f"Escalamiento corregido (paso atrás) por admin {request.user.username} para incidencia {incident.code}. Estado: {old_status} -> {incident.estado}. Acción: {msg}")
        
        return Response({
            'success': True,
            'message': msg,
            'new_status': incident.estado
        })
        
    except Exception as e:
        logger.error(f"Error corrigiendo escalamiento: {e}")
        return Response(
            {'error': f'Error interno: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
