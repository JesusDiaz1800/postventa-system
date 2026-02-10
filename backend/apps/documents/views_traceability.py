"""
Vistas para trazabilidad documental completa
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from apps.core.filters import SmartSearchFilter
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
from apps.incidents.models import Incident
import logging

from .models import VisitReport, LabReport, SupplierReport
from .serializers import (
    VisitReportSerializer, VisitReportCreateSerializer, VisitReportListSerializer,
    LabReportSerializer, LabReportCreateSerializer,
    SupplierReportSerializer, SupplierReportCreateSerializer, SupplierReportListSerializer,
    DocumentWorkflowSerializer
)

logger = logging.getLogger(__name__)

# ==================== REPORTES DE VISITA ====================

class VisitReportListCreateView(generics.ListCreateAPIView):
    """
    Lista y crea reportes de visita
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SmartSearchFilter, OrderingFilter]
    search_fields = ['report_number', 'project_name', 'client_name', 'order_number']
    ordering_fields = ['visit_date', 'created_at', 'report_number']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = VisitReport.objects.select_related('related_incident', 'created_by').order_by('-created_at')
        
        # Filtrar por incidencia relacionada
        incident_id = self.request.query_params.get('incident_id')
        if incident_id:
            queryset = queryset.filter(related_incident_id=incident_id)
        
        # Filtrar por estado
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        # Búsqueda general (100% funcional)
        search_query = self.request.query_params.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(report_number__icontains=search_query) |
                Q(project_name__icontains=search_query) |
                Q(client_name__icontains=search_query) |
                Q(order_number__icontains=search_query) |
                Q(related_incident__code__icontains=search_query)
            )
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return VisitReportCreateSerializer
        return VisitReportListSerializer
    
    def create(self, request, *args, **kwargs):
        """Override create to handle file upload and log debug info"""
        logger.info(f"=== Visit Report Create Request ===")
        # Log keys only to avoid sensitive info, but log FILES explicitly
        logger.info(f"Data keys: {list(request.data.keys())}")
        logger.info(f"FILES keys: {list(request.FILES.keys())}")
        
        # Inspect 'images' specifically if present
        if 'images' in request.FILES:
             images_list = request.FILES.getlist('images')
             logger.info(f"Received {len(images_list)} images under 'images' key.")
             for img in images_list:
                 logger.info(f"Image: {img.name}, size: {img.size}, type: {img.content_type}")
        else:
             logger.warning("No 'images' key found in request.FILES")

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"VisitReport validation errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        from apps.incidents.models import Incident
        from django.utils import timezone
        
        # Get incident from ID
        related_incident_id = serializer.validated_data.get('related_incident_id') or self.request.data.get('related_incident_id')
        related_incident = None
        
        if related_incident_id:
            try:
                related_incident = Incident.objects.get(id=related_incident_id)
            except Incident.DoesNotExist:
                from rest_framework.exceptions import ValidationError
                raise ValidationError({'related_incident_id': 'Incidencia no encontrada'})
            
            # Check if report already exists
            existing_report = VisitReport.objects.filter(related_incident=related_incident).first()
            if existing_report:
                from rest_framework.exceptions import ValidationError
                raise ValidationError({
                    'related_incident': f'Ya existe un reporte de visita para la incidencia {related_incident.code}. '
                                      f'Reporte existente: {existing_report.report_number}'
                })
        
        # Set defaults if not provided
        save_kwargs = {
            'created_by': self.request.user,
            'related_incident': related_incident
        }
        
        # Set default visit_date if not provided
        if not serializer.validated_data.get('visit_date'):
            save_kwargs['visit_date'] = timezone.now().date()
        
        # Set default status if not provided  
        if not serializer.validated_data.get('status'):
            save_kwargs['status'] = 'completed'
        
        # PRE-GENERATE report_number para evitar IntegrityError
        # Usar SECUENCIAL PURO - simple, robusto y predecible
        from django.utils import timezone as tz
        year = tz.now().year
        
        # Buscar el último reporte del año actual
        last_report = VisitReport.objects.filter(
            report_number__startswith=f"RV-{year}"
        ).order_by('-report_number').first()
        
        if last_report:
            try:
                last_number = int(last_report.report_number.split('-')[-1])
                new_number = last_number + 1
            except (ValueError, IndexError):
                # Si hay error parseando, usar timestamp como fallback
                new_number = int(tz.now().strftime('%m%d%H%M'))
        else:
            # Primer reporte del año
            new_number = 1
        
        report_number = f"RV-{year}-{new_number:03d}"
        
        # Asignar el mismo número para ambos campos
        save_kwargs['report_number'] = report_number
        save_kwargs['order_number'] = report_number
        logger.info(f"🔍 PRE-GENERATION: Generated report_number = {report_number}")
        logger.info(f"🔍 save_kwargs = {save_kwargs}")
        
        # Create the report
        report = serializer.save(**save_kwargs)
        logger.info(f"✅ Report created successfully with report_number = {report.report_number}")
        
        # IMPORTANTE: Importar adjuntos de SAP automáticamente
        # Si el reporte tiene un ID de llamada SAP, intentamos traer los adjuntos
        if report.sap_call_id:
            try:
                # Obtener descripciones personalizadas si fueron enviadas
                image_descriptions_json = self.request.data.get('image_descriptions', '{}')
                # Deserializar el JSON a diccionario
                import json
                image_descriptions = json.loads(image_descriptions_json) if isinstance(image_descriptions_json, str) else image_descriptions_json
                self._import_sap_attachments(report, image_descriptions)
                
                # REGENERACIÓN FORZADA DEL PDF
                # El signal post_save generó el PDF ANTES de importar los adjuntos SAP.
                # Debemos regenerarlo ahora para que incluya las imágenes de SAP.
                try:
                    logger.info(f"Regenerando PDF tras importación SAP para reporte {report.report_number}")
                    from .services.professional_pdf_generator import ProfessionalPDFGenerator
                    from .serializers import VisitReportSerializer as VisitReportSerializerRegen
                    from django.core.files.base import ContentFile
                    import io
                    
                    # Refrescar para asegurar que los adjuntos son visibles
                    report.refresh_from_db()
                    
                    # Serializar datos actualizados
                    # Asegurar que el serializer incluye los attachments recién creados
                    serializer_regen = VisitReportSerializerRegen(report)
                    report_data = serializer_regen.data
                    
                    # Regenerar
                    generator = ProfessionalPDFGenerator()
                    pdf_buffer = io.BytesIO()
                    success = generator.generate_visit_report_pdf(report_data, pdf_buffer)
                    
                    if success:
                        filename = f"reporte_visita_{report.report_number}.pdf"
                        report.pdf_file.save(filename, ContentFile(pdf_buffer.getvalue()), save=True)
                        logger.info(f"PDF regenerado exitosamente con imágenes SAP para {report.report_number}")
                except Exception as pdf_error:
                    logger.error(f"Error regenerando PDF post-SAP: {pdf_error}", exc_info=True)
                    
            except Exception as e:
                logger.error(f"Error importando adjuntos SAP para reporte {report.report_number}: {e}")
        
        # Verificar si se subió un archivo directamente
        uploaded_file = self.request.FILES.get('uploaded_pdf') or self.request.FILES.get('file')
        
        # Procesar imágenes adjuntas (para incluirlas en el PDF generado)
        uploaded_images = self.request.FILES.getlist('images')
        if uploaded_images:
            try:
                from apps.documents.models import DocumentAttachment
                import json
                
                # Obtener descripciones personalizadas para imágenes manuales
                image_descriptions_json = self.request.data.get('image_descriptions', '{}')
                image_descriptions = json.loads(image_descriptions_json) if isinstance(image_descriptions_json, str) else image_descriptions_json
                
                logger.info(f"Procesando {len(uploaded_images)} imágenes adjuntas para el reporte {report.report_number}")
                logger.info(f"Descripciones disponibles: {list(image_descriptions.keys())}")
                
                for image in uploaded_images:
                    # Obtener descripción personalizada o usar default
                    custom_description = image_descriptions.get(image.name, "Evidencia Fotográfica")
                    
                    DocumentAttachment.objects.create(
                        document_type='visit_report',
                        document_id=report.id,
                        file=image,
                        filename=image.name,
                        file_type=image.content_type,
                        file_size=image.size,
                        description=custom_description,  # Usar descripción personalizada
                        uploaded_by=self.request.user
                    )
                logger.info("Imágenes guardadas exitosamente con descripciones personalizadas")
                
            except Exception as e:
                logger.error(f"Error guardando imágenes adjuntas: {str(e)}", exc_info=True)
                
            # IMPORTANTE: Regenerar el PDF para incluir las imágenes recién subidas
            # El signal post_save ya generó un PDF, pero sin las imágenes porque aún no existían
            try:
                from .services.professional_pdf_generator import ProfessionalPDFGenerator
                from django.core.files.base import ContentFile
                import io
                from apps.documents.serializers import VisitReportSerializer
                
                # Recargar instancia para asegurar que trae los adjuntos
                report.refresh_from_db()
                
                # Serializar datos actualizados (incluyendo attachments)
                serializer_updated = VisitReportSerializer(report)
                report_data = serializer_updated.data
                
                # Regenerar PDF
                generator = ProfessionalPDFGenerator()
                pdf_buffer = io.BytesIO()
                success = generator.generate_visit_report_pdf(report_data, pdf_buffer)
                
                if success:
                    # Guardar el nuevo PDF (sobrescribiendo el anterior)
                    filename = f"reporte_visita_{report.report_number}.pdf"
                    report.pdf_file.save(filename, ContentFile(pdf_buffer.getvalue()), save=True)
                    logger.info(f"PDF regenerado exitosamente con imágenes para reporte {report.report_number}")
                else:
                    logger.warning(f"No se pudo regenerar el PDF con imágenes para reporte {report.report_number}")
                    
            except Exception as e:
                logger.error(f"Error regenerando PDF con imágenes: {str(e)}", exc_info=True)

        # Verificar si se subió un archivo PDF directamente
        uploaded_file = self.request.FILES.get('uploaded_pdf') or self.request.FILES.get('file')
        
        if uploaded_file:
            # IMPORTANTE: Si el usuario sube un PDF, usar ESE archivo en lugar de generar uno nuevo
            try:
                from django.core.files.base import ContentFile
                
                # Guardar el archivo subido directamente en el campo pdf_file
                # Esto REEMPLAZA el PDF generado automáticamente por el signal
                filename = uploaded_file.name or f"reporte_visita_{report.report_number}.pdf"
                
                # Leer el contenido del archivo
                file_content = uploaded_file.read()
                
                # Guardar en pdf_file (FileField)
                report.pdf_file.save(filename, ContentFile(file_content), save=True)
                logger.info(f"Archivo PDF adjuntado directamente y guardado en pdf_file: {filename}")
                
            except Exception as e:
                logger.error(f"Error guardando archivo PDF adjuntado: {str(e)}", exc_info=True)

        # NOTA: Este bloque else está comentado porque es redundante.
        # El PDF ya se genera correctamente mediante:
        # 1. Signal post_save (generación inicial)
        # 2. Líneas 131-166 (importación SAP + regeneración con imágenes)
        # Este bloque causaba una TERCERA generación que sobrescribía el PDF correcto
        
        # else:
        #     # Generar PDF automáticamente si no se subió un archivo
        #     try:
        #         from .services.professional_pdf_generator import ProfessionalPDFGenerator
        #         from apps.documents.models import DocumentAttachment
        #         from django.conf import settings
        #         import os
        #         
        #         # Fetch images linked to this report
        #         images = []
        #         attachments = DocumentAttachment.objects.filter(
        #             document_id=report.id,
        #             document_type='visit_report'
        #         ).exclude(file='').order_by('uploaded_at')
        #         
        #         for att in attachments:
        #             if att.file:
        #                 # NO verificar existencia aquí, dejar que el generador PDF maneje la resolución de rutas
        #                 # esto soluciona problemas si el path absoluto difiere (e.g. docker vs local)
        #                 ext = os.path.splitext(att.filename)[1].lower()
        #                 if ext in ['.jpg', '.jpeg', '.png', '.bmp']:
        #                     images.append({
        #                         'path': att.file.path,
        #                         'description': att.description or att.filename
        #                     })
        #         
        #         # Preparar datos COMPLETOS para el PDF
        #         incident = report.related_incident
        #         
        #         # Intentar obtener datos FRESCOS de SAP si hay ID de llamada
        #         # Esto corrige nombres de técnicos (ID vs Nombre) y datos de obra faltantes
        #         sap_data = {}
        #         if report.sap_call_id:
        #             try:
        #                 from apps.sap_integration.sap_query_service import SAPQueryService
        #                 sap_service = SAPQueryService()
        #                 sap_data = sap_service.get_service_call(report.sap_call_id) or {}
        #             except Exception as e:
        #                 logger.error(f"Error fetching SAP data for PDF: {e}")
        # 
        #         # Helper para obtener valor de SAP o del reporte local
        #         def get_val(sap_key, report_attr, default=''):
        #             if sap_data and sap_data.get(sap_key):
        #                 return sap_data.get(sap_key)
        #             val = getattr(report, report_attr, default)
        #             return val if val else default
        # 
        #         pdf_data = {
        #             # === Información básica del reporte ===
        #             'order_number': report.order_number,
        #             'sap_call_id': report.sap_call_id,
        #             'visit_date': report.visit_date.strftime('%d/%m/%Y') if report.visit_date else '',
        #             'status': report.get_status_display(),
        #             
        #             # === Información de la incidencia (si existe) ===
        #             'incident_code': incident.code if incident else '',
        #             'incident_description': incident.descripcion if incident else '',
        #             'incident_priority': incident.prioridad if incident else '',
        #             'incident_detection_date': str(incident.fecha_deteccion) if incident and incident.fecha_deteccion else '',
        #             'incident_detection_time': str(incident.hora_deteccion) if incident and incident.hora_deteccion else '',
        #             'incident_responsible': str(incident.responsable) if incident and incident.responsable else '',
        #             'incident_immediate_actions': incident.acciones_inmediatas if incident else '',
        #             
        #             # === Información del producto (desde incidencia o reporte) ===
        #             'product_category': str(incident.categoria) if incident and incident.categoria else getattr(report, 'product_category', ''),
        #             'product_subcategory': incident.subcategoria if incident else getattr(report, 'product_subcategory', ''),
        #             'product_sku': incident.sku if incident else getattr(report, 'product_sku', ''),
        #             'product_lot': incident.lote if incident else getattr(report, 'product_lot', ''),
        #             'product_provider': incident.provider if incident else getattr(report, 'product_provider', ''),
        #             
        #             # === Información del cliente/proyecto (SAP PRIORITY) ===
        #             'client_name': get_val('customer_name', 'client_name'),
        #             'client_rut': get_val('customer_code', 'client_rut') or (incident.cliente_rut if incident else ''),
        #             'project_name': get_val('project_name', 'project_name'),
        #             'project_id': get_val('project_code', 'project_id'),
        #             
        #             'address': get_val('address', 'address'),
        #             'commune': get_val('commune', 'commune'),
        #             'city': get_val('city', 'city'),
        #             'construction_company': get_val('construction_company', 'construction_company'),
        #             
        #             # === Personal en terreno (SAP PRIORITY) ===
        #             'salesperson': get_val('salesperson', 'salesperson'),
        #             'technician': get_val('technician', 'technician'), # Esto traerá el NOMBRE real desde SAP
        #             'installer': get_val('installer_name', 'installer'),
        #             'installer_phone': get_val('installer_phone', 'installer_phone'),
        #             
        #             'prof_obra': get_val('prof_obra', 'professional_name'),
        #             'ito': get_val('ito', 'technical_inspector'),
        #             'otros_nom': get_val('otros_nom', 'contact_observations'), # Mapping tentativo
        #             
        #             # === Motivo de visita ===
        #             'visit_reason': report.visit_reason,
        #             
        #             # === Equipos/Maquinaria ===
        #             'machine_data': report.machine_data,
        #             
        #             # === Observaciones técnicas ===
        #             'wall_observations': report.wall_observations,
        #             'matrix_observations': report.matrix_observations,
        #             'slab_observations': report.slab_observations,
        #             'storage_observations': report.storage_observations,
        #             'pre_assembled_observations': report.pre_assembled_observations,
        #             'exterior_observations': report.exterior_observations,
        #             'general_observations': report.general_observations,
        #             
        #             # === Imágenes (solo incluir si fue creado desde formulario, NO si es archivo adjunto) ===
        #             'include_images': True,
        #             'images': images
        #         }
        #         
        #         # Generar PDF
        #         pdf_generator = ProfessionalPDFGenerator()
        #         
        #         # Guardar PDF en carpeta compartida
        #         shared_path = getattr(settings, 'SHARED_DOCUMENTS_PATH', None)
        #         if shared_path:
        #             incident_folder = os.path.join(shared_path, 'visit_reports', f'incident_{report.related_incident.id}')
        #             os.makedirs(incident_folder, exist_ok=True)
        #             
        #             pdf_path = os.path.join(incident_folder, f"{report.order_number}.pdf")
        #             pdf_content = pdf_generator.generate_visit_report_pdf(pdf_data, pdf_path)
        #             
        #             if pdf_content:
        #                 report.pdf_path = pdf_path
        #                 report.save(update_fields=['pdf_path'])
        #                 logger.info(f"PDF generado y guardado: {pdf_path}")
        #             else:
        #                 logger.error("Error generando PDF profesional")
        #         else:
        #             # Fallback: save in MEDIA_ROOT if SHARED_DOCUMENTS_PATH not defined
        #             media_folder = os.path.join(getattr(settings, 'MEDIA_ROOT', ''), 'visit_reports', f'incident_{report.related_incident.id}')
        #             os.makedirs(media_folder, exist_ok=True)
        #             
        #             pdf_path = os.path.join(media_folder, f"{report.order_number}.pdf")
        #             pdf_content = pdf_generator.generate_visit_report_pdf(pdf_data, pdf_path)
        #             
        #             if pdf_content:
        #                 report.pdf_path = pdf_path
        #                 report.save(update_fields=['pdf_path'])
        #                 logger.info(f"PDF generado en MEDIA_ROOT: {pdf_path}")
        #         
        #     except Exception as e:
        #         logger.error(f"Error generando PDF automáticamente: {str(e)}", exc_info=True)
        #         # No fallar la creación del reporte si hay error en el PDF

    def _import_sap_attachments(self, report, custom_descriptions=None):
        """
        Importa adjuntos desde SAP y los guarda como DocumentAttachment
        custom_descriptions: dict con {filename: description} para sobrescribir descripciones
        """
        from apps.sap_integration.sap_query_service import SAPQueryService
        from apps.documents.models import DocumentAttachment
        from django.core.files.base import ContentFile
        
        # Obtener lista de adjuntos desde SAP
        sap_service = SAPQueryService()
        attachments = sap_service.get_attachments(report.sap_call_id)
        
        if not attachments:
            return
            
        logger.info(f"Encontrados {len(attachments)} adjuntos en SAP para llamada {report.sap_call_id}")
        
        imported_count = 0
        for attach in attachments:
            try:
                # Descargar contenido del archivo
                content, mime_type, filename = sap_service.get_attachment_file(
                    attach['atc_entry'], 
                    attach['line']
                )
                
                if content:
                    # Usar nombre del archivo sin extensión como descripción
                    import os
                    file_base = os.path.splitext(filename)[0]
                    # Limpiar guiones bajos y números de versión
                    description = file_base.replace('_', ' ').replace('-', ' ')
                    # Remover sufijos comunes de duplicados como (1), (2), etc.
                    import re
                    description = re.sub(r'\s*\(\d+\)\s*$', '', description).strip()
                    
                    # Usar descripción personalizada si fue proporcionada
                    if custom_descriptions and filename in custom_descriptions:
                        description = custom_descriptions[filename]
                    
                    # Crear adjunto local
                    doc_attachment = DocumentAttachment(
                        document_type='visit_report',
                        document_id=report.id,
                        filename=filename,
                        file_type=mime_type,
                        file_size=len(content),
                        description=description,  # Descripción profesional en lugar de fecha SAP
                        uploaded_by=self.request.user if self.request.user.is_authenticated else None
                    )
                    
                    # Guardar archivo usando el FileField
                    doc_attachment.file.save(
                        filename,
                        ContentFile(content),
                        save=True
                    )
                    imported_count += 1
                    logger.info(f"Adjunto SAP importado: {filename}")
                    
            except Exception as e:
                logger.error(f"Error procesando adjunto SAP {attach.get('filename')}: {e}")
                
        logger.info(f"Importación SAP finalizada. Total importados: {imported_count}")

class VisitReportRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Obtiene, actualiza o elimina un reporte de visita específico
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return VisitReport.objects.select_related('related_incident', 'created_by').all()
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return VisitReportCreateSerializer
        return VisitReportSerializer


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_visit_report(request, pk):
    """
    Descarga el PDF del reporte de visita
    """
    import os
    from django.http import FileResponse, HttpResponse
    
    try:
        report = get_object_or_404(VisitReport, id=pk)
        
        # Priorizar pdf_file (generado por signal) sobre pdf_path (legacy)
        if report.pdf_file:
            # PDF generado por signal y guardado como FileField
            try:
                file_handle = report.pdf_file.open('rb')
                response = FileResponse(
                    file_handle,
                    content_type='application/pdf',
                    as_attachment=False
                )
                response['Content-Disposition'] = f'inline; filename="{report.pdf_file.name.split("/")[-1]}"'
                return response
            except Exception as e:
                logger.error(f"Error abriendo pdf_file: {str(e)}")
                # Continuar al siguiente método de fallback
        
        # Fallback: pdf_path (legacy)
        if report.pdf_path:
            if not os.path.exists(report.pdf_path):
                return Response(
                    {'error': 'El archivo PDF no se encuentra en el servidor'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Abrir y servir el archivo
            file_handle = open(report.pdf_path, 'rb')
            response = FileResponse(
                file_handle,
                content_type='application/pdf',
                as_attachment=False
            )
            response['Content-Disposition'] = f'inline; filename="{os.path.basename(report.pdf_path)}"'
            return response
        
        # No hay PDF disponible
        return Response(
            {'error': 'Este reporte no tiene un PDF generado'},
            status=status.HTTP_404_NOT_FOUND
        )
        
    except Exception as e:
        logger.error(f"Error descargando reporte de visita: {str(e)}")
        return Response(
            {'error': f'Error descargando archivo: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ==================== INFORMES DE LABORATORIO ====================

class LabReportListCreateView(generics.ListCreateAPIView):
    """
    Lista y crea informes de laboratorio
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SmartSearchFilter, OrderingFilter]
    search_fields = ['report_number', 'client', 'applicant', 'related_incident__code']
    ordering_fields = ['request_date', 'created_at', 'report_number']
    ordering = ['-request_date']
    
    def get_queryset(self):
        queryset = LabReport.objects.select_related(
            'related_incident', 'related_visit_report', 'created_by'
        ).order_by('-created_at')
        
        # Filtrar por incidencia relacionada
        incident_id = self.request.query_params.get('incident_id')
        if incident_id:
            queryset = queryset.filter(related_incident_id=incident_id)
        
        # Filtrar por estado
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        # Búsqueda general (100% funcional)
        search_query = self.request.query_params.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(report_number__icontains=search_query) |
                Q(related_incident__code__icontains=search_query) |
                Q(related_incident__cliente__icontains=search_query) |
                Q(sample_id__icontains=search_query) |
                Q(technician__icontains=search_query)
            )
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return LabReportCreateSerializer
        return LabReportSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class LabReportRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Obtiene, actualiza o elimina un informe de laboratorio específico
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return LabReport.objects.select_related(
            'related_incident', 'related_visit_report', 'created_by'
        ).all()
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return LabReportCreateSerializer
        return LabReportSerializer

# ==================== INFORMES PARA PROVEEDORES ====================

class SupplierReportListCreateView(generics.ListCreateAPIView):
    """
    Lista y crea informes para proveedores
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SmartSearchFilter, OrderingFilter]
    search_fields = ['report_number', 'supplier_name', 'subject', 'related_incident__code', 'related_incident__provider']
    ordering_fields = ['report_date', 'created_at', 'report_number']
    ordering = ['-report_date']
    
    def get_queryset(self):
        queryset = SupplierReport.objects.select_related(
            'related_incident', 'related_lab_report', 'created_by'
        ).order_by('-created_at')
        
        # Filtrar por incidencia relacionada
        incident_id = self.request.query_params.get('incident_id')
        if incident_id:
            queryset = queryset.filter(related_incident_id=incident_id)
        
        # Filtrar por estado
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        return queryset


    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SupplierReportCreateSerializer
        return SupplierReportListSerializer  # Usar serializer con datos expandidos
    
    def create(self, request, *args, **kwargs):
        """Override create to handle debug logging for 500 errors and attachments"""
        logger.info(f"=== Supplier Report Create Request ===")
        
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                logger.error(f"Serializer validation failed: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            self.perform_create(serializer)
            report = serializer.instance
            
            # --- Manejo de imágenes adjuntas ---
            uploaded_images = request.FILES.getlist('images')
            if uploaded_images and report:
                try:
                    from apps.documents.models import DocumentAttachment
                    logger.info(f"Procesando {len(uploaded_images)} imágenes adjuntas para SupplierReport {report.id}")
                    
                    for image in uploaded_images:
                        DocumentAttachment.objects.create(
                            document_type='supplier_report',
                            document_id=report.id,
                            file=image,
                            filename=image.name,
                            file_type=image.content_type,
                            file_size=image.size,
                            uploaded_by=request.user,
                            description="Evidencia Proveedor"
                        )
                    logger.info("Imágenes adjuntas guardadas correctamente")
                except Exception as img_error:
                    logger.error(f"Error guardando imágenes adjuntas: {img_error}", exc_info=True)
                    # No fallar el reporte principal por error de imágenes, pero loguearlo
            
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            
        except Exception as e:
            logger.error(f"Error creating supplier report: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Error interno: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class SupplierReportRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Obtiene, actualiza o elimina un informe para proveedor específico
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return SupplierReport.objects.select_related(
            'related_incident', 'related_lab_report', 'created_by'
        ).all()
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return SupplierReportCreateSerializer
        return SupplierReportSerializer
    
    def update(self, request, *args, **kwargs):
        """Permitir actualizaciones parciales (PATCH) sin requerir todos los campos"""
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upload_supplier_report_document(request):
    """
    Subir documento adjunto para un reporte de proveedor
    """
    try:
        from django.conf import settings
        from apps.incidents.models import Incident
        import os
        
        incident_id = request.data.get('incident_id')
        uploaded_file = request.FILES.get('file')
        
        if not incident_id:
            return Response({'error': 'ID de incidencia requerido'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not uploaded_file:
            return Response({'error': 'Archivo requerido'}, status=status.HTTP_400_BAD_REQUEST)
        
        incident = get_object_or_404(Incident, id=incident_id)
        
        # Verificar si ya existe un reporte de proveedor para esta incidencia
        existing_report = SupplierReport.objects.filter(related_incident=incident).first()
        
        # Determinar ruta de guardado
        shared_path = getattr(settings, 'SHARED_DOCUMENTS_PATH', None) or getattr(settings, 'MEDIA_ROOT', '')
        incident_folder = os.path.join(shared_path, 'supplier_reports', f'incident_{incident.id}')
        os.makedirs(incident_folder, exist_ok=True)
        
        # Guardar archivo
        file_name = uploaded_file.name
        file_path = os.path.join(incident_folder, file_name)
        
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        # Crear o actualizar reporte
        if existing_report:
            existing_report.pdf_path = file_path
            existing_report.save(update_fields=['pdf_path'])
            report = existing_report
        else:
            report = SupplierReport.objects.create(
                related_incident=incident,
                supplier_name=incident.provider or 'Proveedor',
                subject=f'Reporte para Proveedor - {incident.code}',
                problem_description=incident.descripcion or 'Ver documento adjunto',
                pdf_path=file_path,
                created_by=request.user,
                status='sent'
            )
        
        logger.info(f"Documento de proveedor subido: {file_path}")
        
        return Response({
            'success': True,
            'message': 'Documento adjuntado exitosamente',
            'report_id': report.id,
            'report_number': report.report_number,
            'file_path': file_path
        })
        
    except Exception as e:
        logger.error(f"Error subiendo documento de proveedor: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Error al subir documento: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_supplier_report_document(request, pk):
    """
    Generar documento PDF para un reporte de proveedor
    """
    try:
        from django.conf import settings
        from .services.professional_pdf_generator import ProfessionalPDFGenerator
        import os
        
        report = get_object_or_404(SupplierReport, id=pk)
        incident = report.related_incident
        
        # Preparar datos para el PDF
        pdf_data = {
            'report_number': report.report_number,
            'report_date': report.report_date.strftime('%d/%m/%Y') if report.report_date else '',
            'supplier_name': report.supplier_name,
            'supplier_contact': report.supplier_contact,
            'supplier_email': report.supplier_email,
            'subject': report.subject,
            'introduction': report.introduction,
            'problem_description': report.problem_description,
            'technical_analysis': report.technical_analysis,
            'recommendations': report.recommendations,
            'expected_improvements': report.expected_improvements,
            # Datos de incidencia
            'incident_code': incident.code if incident else '',
            'cliente': incident.cliente if incident else '',
            'obra': incident.obra if incident else '',
        }
        
        # Generar PDF
        pdf_generator = ProfessionalPDFGenerator()
        
        shared_path = getattr(settings, 'SHARED_DOCUMENTS_PATH', None) or getattr(settings, 'MEDIA_ROOT', '')
        incident_folder = os.path.join(shared_path, 'supplier_reports', f'incident_{incident.id}' if incident else 'general')
        os.makedirs(incident_folder, exist_ok=True)
        
        pdf_filename = f"{report.report_number}.pdf"
        pdf_path = os.path.join(incident_folder, pdf_filename)
        
        success = pdf_generator.generate_supplier_report(pdf_data, pdf_path)
        
        if success:
            report.pdf_path = pdf_path
            report.save(update_fields=['pdf_path'])
            
            return Response({
                'success': True,
                'message': 'Documento PDF generado exitosamente',
                'report_id': report.id,
                'report_number': report.report_number,
                'pdf_path': pdf_path
            })
        else:
            return Response({
                'success': False,
                'error': 'Error al generar el documento PDF'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except Exception as e:
        logger.error(f"Error generando documento de proveedor: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Error interno del servidor: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_supplier_report(request, pk):
    """
    Descargar el archivo PDF de un reporte de proveedor
    """
    import os
    from django.http import FileResponse
    
    try:
        report = get_object_or_404(SupplierReport, pk=pk)
        
        if not report.pdf_path:
            return Response(
                {'error': 'Este reporte no tiene un PDF generado o adjunto'}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
        if not os.path.exists(report.pdf_path):
            return Response(
                {'error': 'El archivo físico no se encuentra en el servidor'}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
        # Abrir y servir el archivo
        file_handle = open(report.pdf_path, 'rb')
        response = FileResponse(
            file_handle,
            content_type='application/pdf',
            as_attachment=False
        )
        response['Content-Disposition'] = f'inline; filename="{os.path.basename(report.pdf_path)}"'
        return response
        
    except Exception as e:
        logger.error(f"Error descargando reporte de proveedor: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Error interno descargando archivo: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==================== WORKFLOW Y TRAZABILIDAD ====================

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def incident_workflow(request, incident_id):
    """
    Obtiene el workflow completo de un incidente
    """
    try:
        from apps.incidents.models import Incident
        incident = get_object_or_404(Incident, id=incident_id)
        
        visit_reports = VisitReport.objects.filter(related_incident=incident)
        lab_reports = LabReport.objects.filter(related_incident=incident)
        supplier_reports = SupplierReport.objects.filter(related_incident=incident)
        
        workflow_data = {
            'incident': incident,
            'visit_reports': visit_reports,
            'lab_reports': lab_reports,
            'supplier_reports': supplier_reports
        }
        
        serializer = DocumentWorkflowSerializer(workflow_data)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error getting incident workflow: {e}")
        return Response(
            {'error': 'Error al obtener el workflow del incidente'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def available_incidents(request):
    """
    Obtiene las incidencias disponibles para vincular con documentos
    """
    try:
        from apps.incidents.models import Incident
        from apps.incidents.serializers import IncidentListSerializer
        
        # Obtener incidencias abiertas o en proceso
        incidents = Incident.objects.filter(
            Q(status='open') | Q(status='in_progress')
        ).order_by('-created_at')
        
        serializer = IncidentListSerializer(incidents, many=True)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error getting available incidents: {e}")
        return Response(
            {'error': 'Error al obtener las incidencias disponibles'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def document_statistics(request):
    """
    Obtiene estadísticas de documentos
    """
    try:
        # Conteos básicos para Reportes de Visita
        visit_reports = VisitReport.objects.all()
        
        # Conteos específicos requeridos por el frontend
        stats = {
            'visit_reports': {
                'total': visit_reports.count(),
                # Completados: Status closed/completed O incidencia relacionada cerrada
                'completed': visit_reports.filter(
                    Q(status__in=['closed', 'completed']) | 
                    Q(related_incident__estado='cerrado')
                ).distinct().count(),
                # En Laboratorio: Escalados a calidad
                'in_lab': visit_reports.filter(
                    related_incident__escalated_to_quality=True
                ).distinct().count(),
                # Incidencias sin reporte de visita aún (Pendientes)
                'pending_incidents': Incident.objects.exclude(
                    id__in=visit_reports.values_list('related_incident_id', flat=True)
                ).count(),
            },
            'lab_reports': {
                'total': LabReport.objects.count(),
                'draft': LabReport.objects.filter(status='draft').count(),
                'approved': LabReport.objects.filter(status='approved').count(),
                'sent': LabReport.objects.filter(status='sent').count(),
            },
            'supplier_reports': {
                'total': SupplierReport.objects.count(),
                'draft': SupplierReport.objects.filter(status='draft').count(),
                'approved': SupplierReport.objects.filter(status='approved').count(),
                'sent': SupplierReport.objects.filter(status='sent').count(),
            }
        }
        
        return Response(stats)
        
    except Exception as e:
        logger.error(f"Error getting document statistics: {e}")
        return Response(
            {'error': 'Error al obtener estadísticas de documentos'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_supplier_report_email(request, pk):
    """
    Enviar reporte de proveedor por correo (Professional V2)
    Actualiza estado a WAITING_RESPONSE
    """
    try:
        from .models import DocumentStatus
        import os
        
        report = get_object_or_404(SupplierReport, pk=pk)
        
        # 1. Resolver Datos del Correo (para registro)
        to_email = request.data.get('to') or report.supplier_email
        
        # Validar destinatario
        if not to_email:
             return Response(
                {'error': 'No hay destinatario definido para el registro'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Registrar Acción (Sin enviar correo real)
        logger.info(f"Registrando envío manual de reporte proveedor {pk} a {to_email}")
        
        # 3. Actualizar Estado y Metadatos
        report.status = DocumentStatus.WAITING_RESPONSE
        report.sent_date = timezone.now()
        
        # Actualizar datos de contacto solo para referencia
        if to_email != report.supplier_email:
            report.supplier_email = to_email
        
        report.save(update_fields=['status', 'sent_date', 'supplier_email'])
        
        return Response({
            'success': True, 
            'message': 'Estado actualizado a "Esperando Respuesta". El correo debe ser enviado manualmente por el usuario.',
            'logged_to': to_email
        })
            
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        logger.error(f"Error registrando envío de reporte: {e}\n{tb}", exc_info=True)
        return Response(
            {'error': f'Error interno al registrar estado: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
            

