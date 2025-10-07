from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from django.http import FileResponse, Http404
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
import os
import mimetypes
import logging

logger = logging.getLogger(__name__)

def find_real_filename(document_type, incident_id, report_number):
    """
    Buscar el nombre real del archivo en la carpeta de documentos del proyecto
    """
    documents_base = getattr(settings, 'DOCUMENTS_PATH', None)
    if not documents_base:
        return None
    
    # Mapear tipos de documento a carpetas
    folder_mapping = {
        'visit_report': 'visit_reports',
        'lab_report': 'lab_reports', 
        'supplier_report': 'supplier_reports',
        'quality_report': 'quality_reports'
    }
    
    folder_name = folder_mapping.get(document_type)
    if not folder_name:
        return None
    
    folder_path = os.path.join(documents_base, folder_name)
    incident_folder = os.path.join(folder_path, f'incident_{incident_id}')
    
    if not os.path.exists(incident_folder):
        return None
    
    try:
        files = os.listdir(incident_folder)
        if not files:
            return None
        
        # Buscar archivos que contengan el report_number o el tipo de documento
        for file in files:
            if (str(report_number) in file or 
                document_type.replace('_', '') in file.lower() or
                'report' in file.lower()):
                return file
        
        # Si no encuentra coincidencia específica, usar el primer archivo disponible
        if files:
            return files[0]
            
    except Exception:
        pass
    
    return None

def get_direct_file_url(document_type, incident_id, filename):
    """
    Generar URL directa para acceder al archivo del proyecto
    """
    documents_url = getattr(settings, 'DOCUMENTS_URL', '/documents/')
    
    # Mapear tipos de documento a carpetas
    folder_mapping = {
        'visit_report': 'visit_reports',
        'lab_report': 'lab_reports', 
        'supplier_report': 'supplier_reports',
        'quality_report': 'quality_reports'
    }
    
    folder_name = folder_mapping.get(document_type, 'documents')
    
    # Construir URL directa
    direct_url = f"{documents_url}{folder_name}/incident_{incident_id}/{filename}"
    return direct_url

from .models import DocumentTemplate, Document, DocumentVersion, DocumentConversion, VisitReport, LabReport, SupplierReport
from apps.incidents.models import Incident
from .serializers import (
    DocumentTemplateSerializer, DocumentListSerializer, DocumentDetailSerializer,
    DocumentCreateUpdateSerializer, DocumentGenerateSerializer, DocumentEditSerializer,
    DocumentConvertSerializer, DocumentVersionSerializer, DocumentConversionSerializer,
    VisitReportSerializer, VisitReportCreateSerializer, LabReportSerializer, 
    LabReportCreateSerializer, SupplierReportSerializer, SupplierReportCreateSerializer,
    DocumentWorkflowSerializer
)
from .filters import DocumentFilter
from .tasks import generate_document_task, convert_document_task
from .document_generator import document_generator


class DocumentTemplateListCreateView(generics.ListCreateAPIView):
    """List and create document templates"""
    queryset = DocumentTemplate.objects.filter(is_active=True)
    serializer_class = DocumentTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def documents_by_incidents(request):
    """Get documents organized by incidents"""
    logger.info(f"Documents by incidents called by user: {request.user.username}")
    
    try:
        # Get filter parameters
        document_type = request.GET.get('document_type', '')
        search = request.GET.get('search', '')
        
        # Base queryset - incluir documentos y reportes de visita
        from .models import VisitReport, LabReport, SupplierReport
        
        # Obtener documentos
        documents_queryset = Document.objects.select_related('incident', 'created_by').all()
        
        # Obtener reportes de visita
        visit_reports_queryset = VisitReport.objects.select_related('related_incident').all()
        
        # Obtener reportes de laboratorio
        lab_reports_queryset = LabReport.objects.select_related('related_incident').all()
        
        # Obtener reportes de proveedores
        supplier_reports_queryset = SupplierReport.objects.select_related('related_incident').all()
        
        # Organize by incidents
        incidents_data = {}
        
        # Procesar documentos regulares
        for document in documents_queryset.order_by('-created_at'):
            if document.incident:
                incident_id = document.incident.id
                if incident_id not in incidents_data:
                    incidents_data[incident_id] = {
                        'incident': {
                            'id': document.incident.id,
                            'code': document.incident.code,
                            'cliente': document.incident.cliente,
                            'provider': document.incident.provider,
                            'estado': document.incident.estado,
                            'prioridad': document.incident.prioridad,
                        },
                        'documents': []
                    }
                incidents_data[incident_id]['documents'].append({
                    'id': document.id,
                    'title': document.title,
                    'document_type': document.document_type,
                    'document_type_display': document.get_document_type_display(),
                    'version': document.version,
                    'is_final': document.is_final,
                    'created_by': {
                        'id': document.created_by.id,
                        'username': document.created_by.username,
                        'first_name': document.created_by.first_name,
                        'last_name': document.created_by.last_name,
                    },
                    'created_at': document.created_at,
                    'updated_at': document.updated_at,
                })
        
        # Procesar reportes de visita
        for report in visit_reports_queryset.order_by('-created_at'):
            if report.related_incident:
                incident_id = report.related_incident.id
                if incident_id not in incidents_data:
                    incidents_data[incident_id] = {
                        'incident': {
                            'id': report.related_incident.id,
                            'code': report.related_incident.code,
                            'cliente': report.related_incident.cliente,
                            'provider': report.related_incident.provider,
                            'estado': report.related_incident.estado,
                            'prioridad': report.related_incident.prioridad,
                        },
                        'documents': []
                    }
                # Buscar el archivo real en la carpeta compartida
                real_filename = find_real_filename('visit_report', incident_id, report.report_number)
                filename = real_filename or f"visit_report_{report.report_number}.pdf"
                
                # Generar URL directa al archivo
                direct_url = get_direct_file_url('visit_report', incident_id, filename)
                
                incidents_data[incident_id]['documents'].append({
                    'id': f"visit_report_{report.id}",
                    'title': f"Reporte de Visita - {report.report_number}",
                    'filename': filename,
                    'direct_url': direct_url,
                    'type': 'visit_report',
                    'document_type': 'visit_report',
                    'document_type_display': 'Reporte de Visita',
                    'version': '1.0',
                    'is_final': True,
                    'incident_id': incident_id,
                    'created_by': {
                        'id': report.created_by.id if hasattr(report, 'created_by') and report.created_by else None,
                        'username': report.created_by.username if hasattr(report, 'created_by') and report.created_by else 'Sistema',
                        'first_name': report.created_by.first_name if hasattr(report, 'created_by') and report.created_by else '',
                        'last_name': report.created_by.last_name if hasattr(report, 'created_by') and report.created_by else '',
                    },
                    'created_at': report.created_at,
                    'updated_at': report.updated_at,
                    'report_number': report.report_number,
                    'order_number': report.order_number,
                    'client_name': report.client_name,
                    'visit_date': report.visit_date,
                })
        
        # Procesar reportes de laboratorio
        for report in lab_reports_queryset.order_by('-created_at'):
            if report.related_incident:
                incident_id = report.related_incident.id
                if incident_id not in incidents_data:
                    incidents_data[incident_id] = {
                        'incident': {
                            'id': report.related_incident.id,
                            'code': report.related_incident.code,
                            'cliente': report.related_incident.cliente,
                            'provider': report.related_incident.provider,
                            'estado': report.related_incident.estado,
                            'prioridad': report.related_incident.prioridad,
                        },
                        'documents': []
                    }
                # Buscar el archivo real en la carpeta compartida
                real_filename = find_real_filename('lab_report', incident_id, report.report_number)
                filename = real_filename or f"lab_report_{report.report_number}.pdf"
                
                # Generar URL directa al archivo
                direct_url = get_direct_file_url('lab_report', incident_id, filename)
                
                incidents_data[incident_id]['documents'].append({
                    'id': f"lab_report_{report.id}",
                    'title': f"Reporte de Laboratorio - {report.report_number}",
                    'filename': filename,
                    'direct_url': direct_url,
                    'type': 'lab_report',
                    'document_type': 'lab_report',
                    'document_type_display': 'Reporte de Laboratorio',
                    'version': '1.0',
                    'is_final': True,
                    'incident_id': incident_id,
                    'created_by': {
                        'id': report.created_by.id if hasattr(report, 'created_by') and report.created_by else None,
                        'username': report.created_by.username if hasattr(report, 'created_by') and report.created_by else 'Sistema',
                        'first_name': report.created_by.first_name if hasattr(report, 'created_by') and report.created_by else '',
                        'last_name': report.created_by.last_name if hasattr(report, 'created_by') and report.created_by else '',
                    },
                    'created_at': report.created_at,
                    'updated_at': report.updated_at,
                    'report_number': report.report_number,
                    'client_name': report.client_name,
                })
        
        # Procesar reportes de proveedores
        for report in supplier_reports_queryset.order_by('-created_at'):
            if report.related_incident:
                incident_id = report.related_incident.id
                if incident_id not in incidents_data:
                    incidents_data[incident_id] = {
                        'incident': {
                            'id': report.related_incident.id,
                            'code': report.related_incident.code,
                            'cliente': report.related_incident.cliente,
                            'provider': report.related_incident.provider,
                            'estado': report.related_incident.estado,
                            'prioridad': report.related_incident.prioridad,
                        },
                        'documents': []
                    }
                # Buscar el archivo real en la carpeta compartida
                real_filename = find_real_filename('supplier_report', incident_id, report.report_number)
                filename = real_filename or f"supplier_report_{report.report_number}.pdf"
                
                # Generar URL directa al archivo
                direct_url = get_direct_file_url('supplier_report', incident_id, filename)
                
                incidents_data[incident_id]['documents'].append({
                    'id': f"supplier_report_{report.id}",
                    'title': f"Reporte de Proveedor - {report.report_number}",
                    'filename': filename,
                    'direct_url': direct_url,
                    'type': 'supplier_report',
                    'document_type': 'supplier_report',
                    'document_type_display': 'Reporte de Proveedor',
                    'version': '1.0',
                    'is_final': True,
                    'incident_id': incident_id,
                    'created_by': {
                        'id': report.created_by.id if hasattr(report, 'created_by') and report.created_by else None,
                        'username': report.created_by.username if hasattr(report, 'created_by') and report.created_by else 'Sistema',
                        'first_name': report.created_by.first_name if hasattr(report, 'created_by') and report.created_by else '',
                        'last_name': report.created_by.last_name if hasattr(report, 'created_by') and report.created_by else '',
                    },
                    'created_at': report.created_at,
                    'updated_at': report.updated_at,
                    'report_number': report.report_number,
                    'client_name': report.client_name,
                })
        
        # Convert to list and sort by incident code
        incidents_list = list(incidents_data.values())
        incidents_list.sort(key=lambda x: x['incident']['code'])
        
        return Response({
            'success': True,
            'incidents': incidents_list,
            'total_incidents': len(incidents_list),
            'total_documents': sum(len(inc['documents']) for inc in incidents_list),
            'filters_applied': {
                'document_type': document_type,
                'search': search,
            }
        })
        
    except Exception as e:
        logger.error(f"Error in documents_by_incidents: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DocumentTemplateRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update and delete document templates"""
    queryset = DocumentTemplate.objects.all()
    serializer_class = DocumentTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]


class DocumentListCreateView(generics.ListCreateAPIView):
    """List and create documents"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = DocumentFilter
    search_fields = ['title', 'notes', 'incident__code', 'incident__cliente', 'incident__provider']
    ordering_fields = ['created_at', 'updated_at', 'title', 'document_type']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DocumentCreateUpdateSerializer
        return DocumentListSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        # Filter based on user role and permissions
        if user.role == 'provider':
            # Providers can only see documents related to their incidents
            return Document.objects.filter(
                incident__provider__icontains=user.username
            )
        else:
            return Document.objects.all()


class DocumentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update and delete documents"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return DocumentCreateUpdateSerializer
        return DocumentDetailSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'provider':
            return Document.objects.filter(
                incident__provider__icontains=user.username
            )
        else:
            return Document.objects.all()


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_document(request, incident_id=None):
    """Generate document from template"""
    serializer = DocumentGenerateSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Get template
    template = get_object_or_404(
        DocumentTemplate,
        id=serializer.validated_data['template_id'],
        is_active=True
    )
    
    # Get incident if provided
    incident = None
    if incident_id:
        from apps.incidents.models import Incident
        incident = get_object_or_404(Incident, id=incident_id)
    
    # Create document record
    document = Document.objects.create(
        incident=incident,
        template=template,
        title=serializer.validated_data['title'],
        document_type=serializer.validated_data['document_type'],
        placeholders_data=serializer.validated_data['placeholders_data'],
        created_by=request.user
    )
    
    # Trigger document generation task
    task = generate_document_task.delay(document.id)
    
    return Response({
        'message': 'Generación de documento iniciada',
        'document_id': document.id,
        'task_id': task.id
    }, status=status.HTTP_202_ACCEPTED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def edit_document(request, document_id):
    """Edit document content"""
    document = get_object_or_404(Document, id=document_id)
    serializer = DocumentEditSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Create new version
    new_version = DocumentVersion.objects.create(
        document=document,
        version=document.get_next_version(),
        docx_path=document.docx_path,
        pdf_path=document.pdf_path,
        content_html=serializer.validated_data['content_html'],
        change_description=serializer.validated_data['change_description'],
        created_by=request.user
    )
    
    # Update document
    document.version = new_version.version
    document.content_html = serializer.validated_data['content_html']
    document.save()
    
    return Response({
        'message': 'Documento actualizado exitosamente',
        'new_version': new_version.version
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def convert_document(request, document_id):
    """Convert document to PDF"""
    document = get_object_or_404(Document, id=document_id)
    serializer = DocumentConvertSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if PDF already exists and not forcing regeneration
    if document.pdf_path and not serializer.validated_data['force_regenerate']:
        return Response({
            'message': 'PDF ya existe',
            'pdf_path': document.pdf_path
        })
    
    # Create conversion record
    conversion = DocumentConversion.objects.create(
        document=document,
        source_path=document.docx_path,
        target_path=f"{document.docx_path.rsplit('.', 1)[0]}.pdf",
        status='pending'
    )
    
    # Trigger conversion task
    task = convert_document_task.delay(conversion.id)
    
    return Response({
        'message': 'Conversión a PDF iniciada',
        'conversion_id': conversion.id,
        'task_id': task.id
    }, status=status.HTTP_202_ACCEPTED)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def document_versions(request, document_id):
    """Get document versions"""
    document = get_object_or_404(Document, id=document_id)
    versions = document.versions.all().order_by('-version')
    serializer = DocumentVersionSerializer(versions, many=True)
    
    return Response({
        'versions': serializer.data,
        'current_version': document.version
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def document_conversions(request, document_id):
    """Get document conversions"""
    document = get_object_or_404(Document, id=document_id)
    conversions = document.conversions.all().order_by('-created_at')
    serializer = DocumentConversionSerializer(conversions, many=True)
    
    return Response({
        'conversions': serializer.data
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def search_documents(request):
    """Search documents by content"""
    query = request.GET.get('q', '')
    document_type = request.GET.get('type', '')
    
    if not query:
        return Response({'error': 'Query parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Base queryset
    documents = Document.objects.all()
    
    # Filter by type if provided
    if document_type:
        documents = documents.filter(document_type=document_type)
    
    # Search in title, content, and notes
    documents = documents.filter(
        Q(title__icontains=query) |
        Q(content_html__icontains=query) |
        Q(notes__icontains=query)
    )
    
    # Limit results
    documents = documents[:50]
    
    serializer = DocumentListSerializer(documents, many=True)
    
    return Response({
        'documents': serializer.data,
        'count': documents.count(),
        'query': query
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def document_dashboard(request):
    """Get document dashboard data"""
    user = request.user
    
    # Base queryset
    if user.role == 'provider':
        documents = Document.objects.filter(
            incident__provider__icontains=user.username
        )
    else:
        documents = Document.objects.all()
    
    # KPIs
    total_documents = documents.count()
    final_documents = documents.filter(is_final=True).count()
    pending_conversions = DocumentConversion.objects.filter(
        document__in=documents,
        status='pending'
    ).count()
    
    # Documents by type
    type_counts = documents.values('document_type').annotate(count=models.Count('id'))
    
    # Recent documents
    recent_documents = documents.order_by('-created_at')[:10]
    
    return Response({
        'kpis': {
            'total_documents': total_documents,
            'final_documents': final_documents,
            'pending_conversions': pending_conversions,
        },
        'type_distribution': list(type_counts),
        'recent_documents': DocumentListSerializer(recent_documents, many=True).data
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_polifusion_lab_report(request):
    """Generate Polifusión laboratory report"""
    try:
        # Validate required fields
        required_fields = ['solicitante', 'cliente', 'proyecto', 'experto_nombre']
        for field in required_fields:
            if not request.data.get(field):
                return Response({
                    'error': f'El campo {field} es requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get incident if provided
        incident = None
        if request.data.get('incident_id'):
            from apps.incidents.models import Incident
            try:
                incident = Incident.objects.get(id=request.data['incident_id'])
            except Incident.DoesNotExist:
                return Response({
                    'error': 'Incidencia no encontrada'
                }, status=status.HTTP_404_NOT_FOUND)
        
        # Prepare incident data for document generation
        incident_data = {
            # Información del solicitante
            'solicitante': request.data.get('solicitante', 'POLIFUSION'),
            'fecha_solicitud': request.data.get('fecha_solicitud', timezone.now().strftime('%d/%m/%Y')),
            'cliente': request.data.get('cliente', 'POLIFUSION'),
            
            # Información técnica
            'diametro': request.data.get('diametro', '160'),
            'proyecto': request.data.get('proyecto', ''),
            'ubicacion': request.data.get('ubicacion', ''),
            'presion': request.data.get('presion', ''),
            'temperatura': request.data.get('temperatura', 'No registrada'),
            'informante': request.data.get('informante', ''),
            
            # Ensayos
            'ensayos_adicionales': request.data.get('ensayos_adicionales', ''),
            
            # Comentarios detallados
            'comentarios_detallados': request.data.get('comentarios_detallados', ''),
            
            # Conclusiones
            'conclusiones_detalladas': request.data.get('conclusiones_detalladas', ''),
            
            # Experto
            'experto_nombre': request.data.get('experto_nombre', ''),
            
            # Análisis detallado
            'analisis_detallado': request.data.get('analisis_detallado', ''),
            
            # Incident data if available
            'id': incident.id if incident else None,
            'title': incident.title if incident else 'Informe de Laboratorio',
            'description': incident.description if incident else '',
        }
        
        # Generate document using Polifusión template
        result = document_generator.generate_polifusion_lab_report(incident_data)
        
        if not result['success']:
            return Response({
                'error': f'Error al generar el documento: {result["error"]}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Create document record in database
        document = Document.objects.create(
            incident=incident,
            title=f"Informe de Laboratorio - {incident_data['proyecto']}",
            document_type='oficial',
            docx_path=result['docx_path'],
            pdf_path=result['pdf_path'],
            placeholders_data=result['context_used'],
            notes=f"Generado automáticamente desde plantilla Polifusión. Template: {result['template_used']}",
            created_by=request.user
        )
        
        return Response({
            'message': 'Informe de laboratorio generado exitosamente',
            'document_id': document.id,
            'filename': result['filename'],
            'docx_path': result['docx_path'],
            'pdf_path': result['pdf_path'],
            'template_used': result['template_used']
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': f'Error interno del servidor: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_polifusion_incident_report(request):
    """Generate Polifusión incident report"""
    try:
        # Validate required fields
        required_fields = ['proveedor', 'cliente', 'descripcion_problema', 'acciones_inmediatas']
        for field in required_fields:
            if not request.data.get(field):
                return Response({
                    'error': f'El campo {field} es requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get incident if provided
        incident = None
        if request.data.get('incident_id'):
            from apps.incidents.models import Incident
            try:
                incident = Incident.objects.get(id=request.data['incident_id'])
            except Incident.DoesNotExist:
                return Response({
                    'error': 'Incidencia no encontrada'
                }, status=status.HTTP_404_NOT_FOUND)
        
        # Prepare incident data for document generation
        incident_data = {
            # Información del informe
            'report_number': request.data.get('report_number', ''),
            'report_date': request.data.get('report_date', timezone.now().strftime('%d/%m/%Y')),
            
            # Registro de información
            'proveedor': request.data.get('proveedor', ''),
            'obra': request.data.get('obra', ''),
            'produccion': request.data.get('produccion', ''),
            'cliente': request.data.get('cliente', ''),
            'servicio': request.data.get('servicio', ''),
            'rut': request.data.get('rut', ''),
            'direccion': request.data.get('direccion', ''),
            'otros': request.data.get('otros', ''),
            'contactos': request.data.get('contactos', ''),
            'fecha_deteccion': request.data.get('fecha_deteccion', ''),
            'hora': request.data.get('hora', ''),
            
            # Descripción del problema
            'descripcion_problema': request.data.get('descripcion_problema', ''),
            
            # Acciones inmediatas
            'acciones_inmediatas': request.data.get('acciones_inmediatas', ''),
            
            # Evolución/Acciones posteriores
            'evolucion_acciones': request.data.get('evolucion_acciones', []),
            
            # Observaciones y cierre
            'observaciones': request.data.get('observaciones', ''),
            'fecha_cierre': request.data.get('fecha_cierre', ''),
            
            # Incident data if available
            'id': incident.id if incident else None,
            'title': incident.title if incident else 'Informe de Incidencia',
            'description': incident.description if incident else '',
        }
        
        # Generate document using Polifusión template
        result = document_generator.generate_polifusion_incident_report(incident_data)
        
        if not result['success']:
            return Response({
                'error': f'Error al generar el documento: {result["error"]}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Create document record in database
        document = Document.objects.create(
            incident=incident,
            title=f"Informe de Incidencia - {incident_data['cliente']}",
            document_type='oficial',
            docx_path=result['docx_path'],
            pdf_path=result['pdf_path'],
            placeholders_data=result['context_used'],
            notes=f"Generado automáticamente desde plantilla Polifusión. Template: {result['template_used']}",
            created_by=request.user
        )
        
        return Response({
            'message': 'Informe de incidencia generado exitosamente',
            'document_id': document.id,
            'filename': result['filename'],
            'docx_path': result['docx_path'],
            'pdf_path': result['pdf_path'],
            'template_used': result['template_used']
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': f'Error interno del servidor: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_polifusion_visit_report(request):
    """Generate Polifusión visit report"""
    try:
        # Validate required fields
        required_fields = ['obra', 'cliente', 'vendedor', 'tecnico']
        for field in required_fields:
            if not request.data.get(field):
                return Response({
                    'error': f'El campo {field} es requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get incident if provided
        incident = None
        if request.data.get('incident_id'):
            from apps.incidents.models import Incident
            try:
                incident = Incident.objects.get(id=request.data['incident_id'])
            except Incident.DoesNotExist:
                return Response({
                    'error': 'Incidencia no encontrada'
                }, status=status.HTTP_404_NOT_FOUND)
        
        # Prepare visit data for document generation
        visit_data = {
            # Información del reporte
            'orden_number': request.data.get('orden_number', ''),
            'fecha_visita': request.data.get('fecha_visita', timezone.now().strftime('%d/%m/%Y')),
            
            # Información general de la obra
            'obra': request.data.get('obra', ''),
            'cliente': request.data.get('cliente', ''),
            'direccion': request.data.get('direccion', ''),
            'administrador': request.data.get('administrador', ''),
            'constructor': request.data.get('constructor', ''),
            'motivo_visita': request.data.get('motivo_visita', '01-Visita Técnica'),
            
            # Información del personal
            'vendedor': request.data.get('vendedor', ''),
            'comuna': request.data.get('comuna', ''),
            'ciudad': request.data.get('ciudad', ''),
            'instalador': request.data.get('instalador', ''),
            'fono_instalador': request.data.get('fono_instalador', ''),
            'tecnico': request.data.get('tecnico', ''),
            
            # Roles y contactos
            'encargado_calidad': request.data.get('encargado_calidad', ''),
            'profesional_obra': request.data.get('profesional_obra', ''),
            'inspector_tecnico': request.data.get('inspector_tecnico', ''),
            'otro_contacto': request.data.get('otro_contacto', ''),
            
            # Uso de maquinaria
            'maquinaria': request.data.get('maquinaria', []),
            'retiro_maq': request.data.get('retiro_maq', 'No'),
            'numero_reporte': request.data.get('numero_reporte', ''),
            
            # Observaciones
            'obs_muro_tabique': request.data.get('obs_muro_tabique', ''),
            'obs_matriz': request.data.get('obs_matriz', ''),
            'obs_loza': request.data.get('obs_loza', ''),
            'obs_almacenaje': request.data.get('obs_almacenaje', ''),
            'obs_pre_armados': request.data.get('obs_pre_armados', ''),
            'obs_exteriores': request.data.get('obs_exteriores', ''),
            'obs_generales': request.data.get('obs_generales', ''),
            
            # Firmas
            'firma_tecnico': request.data.get('firma_tecnico', ''),
            'firma_instalador': request.data.get('firma_instalador', ''),
            
            # Incident data if available
            'id': incident.id if incident else None,
            'title': incident.title if incident else 'Reporte de Visita',
            'description': incident.description if incident else '',
        }
        
        # Generate document using Polifusión template
        result = document_generator.generate_polifusion_visit_report(visit_data)
        
        if not result['success']:
            return Response({
                'error': f'Error al generar el documento: {result["error"]}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Create document record in database
        document = Document.objects.create(
            incident=incident,
            title=f"Reporte de Visita - {visit_data['obra']}",
            document_type='oficial',
            docx_path=result['docx_path'],
            pdf_path=result['pdf_path'],
            placeholders_data=result['context_used'],
            notes=f"Generado automáticamente desde plantilla Polifusión. Template: {result['template_used']}",
            created_by=request.user
        )
        
        return Response({
            'message': 'Reporte de visita generado exitosamente',
            'document_id': document.id,
            'filename': result['filename'],
            'docx_path': result['docx_path'],
            'pdf_path': result['pdf_path'],
            'template_used': result['template_used']
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': f'Error interno del servidor: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def generate_order_number(request):
    """
    Genera un número de orden automáticamente para reportes de visita
    """
    try:
        from django.utils import timezone
        
        # Generar número de orden usando la misma lógica del modelo
        year = timezone.now().year
        month = timezone.now().month
        day = timezone.now().day
        
        # Contar reportes del día actual
        today_reports = VisitReport.objects.filter(
            created_at__date=timezone.now().date()
        ).count()
        
        sequence = today_reports + 1
        order_number = f"OV-{year}{month:02d}{day:02d}-{sequence:03d}"
        
        return Response({
            'order_number': order_number
        })
        
    except Exception as e:
        logger.error(f"Error generando número de orden: {str(e)}")
        return Response({
            'error': f'Error generando número de orden: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
