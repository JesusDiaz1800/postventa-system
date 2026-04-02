from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count
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

from ..models import DocumentTemplate, Document, DocumentVersion, DocumentConversion, VisitReport, LabReport, SupplierReport
from apps.incidents.models import Incident
from ..serializers import (
    DocumentTemplateSerializer, DocumentListSerializer, DocumentDetailSerializer,
    DocumentCreateUpdateSerializer, DocumentGenerateSerializer, DocumentEditSerializer,
    DocumentConvertSerializer, DocumentVersionSerializer, DocumentConversionSerializer,
    VisitReportSerializer, VisitReportCreateSerializer, LabReportSerializer, 
    LabReportCreateSerializer, SupplierReportSerializer, SupplierReportCreateSerializer,
    DocumentWorkflowSerializer
)
from ..filters import DocumentFilter
from ..tasks import generate_document_task, convert_document_task
from ..document_generator import document_generator


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
    """Get documents organized by incidents with optimized prefetching and pagination"""
    logger.info(f"Optimized documents by incidents called by user: {request.user.username}")
    
    try:
        from rest_framework.pagination import PageNumberPagination
        
        # Get filter parameters
        search = request.GET.get('search', '')
        
        # Base Incident Queryset with Prefetching
        queryset = Incident.objects.all()
        
        # Filter by search if provided
        if search:
            queryset = queryset.filter(
                Q(code__icontains=search) | 
                Q(cliente__icontains=search) | 
                Q(obra__icontains=search)
            )
            
        # Optimization: select_related and prefetch everything related to documents
        queryset = queryset.select_related('created_by').prefetch_related(
            'documents', 
            'visit_reports', 
            'lab_reports', 
            'supplier_reports'
        ).order_by('-created_at')
        
        # Pagination
        paginator = PageNumberPagination()
        paginator.page_size = 10  # Process 10 incidents at a time
        page = paginator.paginate_queryset(queryset, request)
        
        incidents_list = []
        for incident in (page if page is not None else queryset):
            incident_docs = []
            
            # 1. Regular Documents
            for doc in incident.documents.all():
                incident_docs.append({
                    'id': doc.id,
                    'title': doc.title,
                    'document_type': doc.document_type,
                    'document_type_display': doc.get_document_type_display(),
                    'created_at': doc.created_at,
                    'pdf_path': doc.pdf_path,
                })
                
            # 2. Visit Reports
            for vr in incident.visit_reports.all():
                incident_docs.append({
                    'id': f"vr_{vr.id}",
                    'title': f"Reporte Visita: {vr.report_number}",
                    'document_type': 'visit_report',
                    'document_type_display': 'Reporte de Visita',
                    'created_at': vr.created_at,
                    'report_number': vr.report_number,
                    'pdf_path': vr.pdf_path
                })
                
            # 3. Lab Reports
            for lr in incident.lab_reports.all():
                incident_docs.append({
                    'id': f"lr_{lr.id}",
                    'title': f"Reporte Lab: {lr.report_number}",
                    'document_type': 'lab_report',
                    'document_type_display': 'Reporte Lab',
                    'created_at': lr.created_at,
                    'pdf_path': lr.pdf_path
                })

            # 4. Supplier Reports
            for sr in incident.supplier_reports.all():
                incident_docs.append({
                    'id': f"sr_{sr.id}",
                    'title': f"Reporte Proveedor: {sr.report_number}",
                    'document_type': 'supplier_report',
                    'document_type_display': 'Reporte Proveedor',
                    'created_at': sr.created_at,
                    'pdf_path': sr.pdf_path
                })
            
            if incident_docs:
                incidents_list.append({
                    'incident': {
                        'id': incident.id,
                        'code': incident.code,
                        'cliente': incident.cliente,
                        'estado': incident.estado,
                    },
                    'documents': incident_docs
                })
        
        if page is not None:
            return paginator.get_paginated_response(incidents_list)
            
        return Response({
            'success': True,
            'incidents': incidents_list
        })
        
    except Exception as e:
        logger.error(f"Error in optimized documents_by_incidents: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)

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


from django.views.decorators.cache import cache_page

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@cache_page(60 * 15)
def document_dashboard(request):
    """Get document dashboard data"""
    try:
        user = request.user
        
        # Base queryset - usar solo campos que existen
        documents = Document.objects.all()
        
        # KPIs básicos
        total_documents = documents.count()
        final_documents = documents.filter(is_final=True).count() if hasattr(Document, 'is_final') else 0
        
        # Documents by type - usar campos que existen
        try:
            if hasattr(Document, 'document_type'):
                type_counts = documents.values('document_type').annotate(count=Count('id'))
            else:
                type_counts = []
        except Exception:
            type_counts = []
        
        # Recent documents
        recent_documents = documents.order_by('-created_at')[:10]
        
        return Response({
            'kpis': {
                'total_documents': total_documents,
                'final_documents': final_documents,
                'pending_conversions': 0,  # Simplificado
            },
            'type_distribution': list(type_counts),
            'recent_documents': DocumentListSerializer(recent_documents, many=True).data if recent_documents.exists() else []
        })
        
    except Exception as e:
        logger.error(f"Error en document_dashboard: {e}")
        return Response({
            'kpis': {
                'total_documents': 0,
                'final_documents': 0,
                'pending_conversions': 0,
            },
            'type_distribution': [],
            'recent_documents': []
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
    Formato: RV-YYYY-XXX (donde XXX viene del código de la incidencia)
    
    Query params:
    - incident_id: ID de la incidencia para vincular el número de reporte
    """
    try:
        from django.utils import timezone
        from apps.incidents.models import Incident
        
        year = timezone.now().year
        incident_id = request.query_params.get('incident_id')
        
        # Si se proporciona incident_id, extraer el número secuencial de la incidencia
        if incident_id:
            try:
                incident = Incident.objects.get(id=incident_id)
                if incident.code:
                    parts = incident.code.split('-')
                    if len(parts) >= 3:
                        incident_seq = parts[-1].lstrip('0') or '1'
                        incident_number = int(incident_seq)
                    else:
                        incident_number = incident.id
                    
                    order_number = f"RV-{year}-{incident_number:03d}"
                    return Response({'order_number': order_number})
            except Incident.DoesNotExist:
                pass  # Continuar con el fallback
        
        # Fallback: generar número secuencial basado en reportes existentes
        last_report = VisitReport.objects.filter(
            report_number__startswith=f"RV-{year}"
        ).order_by('-report_number').first()
        
        if last_report:
            try:
                last_number = int(last_report.report_number.split('-')[-1])
                new_number = last_number + 1
            except (ValueError, IndexError):
                new_number = 1
        else:
            new_number = 1
        
        order_number = f"RV-{year}-{new_number:03d}"
        
        return Response({
            'order_number': order_number
        })
        
    except Exception as e:
        logger.error(f"Error generando número de orden: {str(e)}")
        return Response({
            'error': f'Error generando número de orden: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
