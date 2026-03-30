import os
import shutil
from django.conf import settings
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import logging
from datetime import datetime

import logging
from datetime import datetime
from apps.ai.rag_service import RAGService
from apps.core.thread_local import get_current_country


logger = logging.getLogger(__name__)

def sync_to_shared_folder(local_path, document_type, incident_id, filename, report_type=None):
    """
    Sincroniza el documento a la carpeta compartida de la empresa
    Para reportes de calidad, separa por tipo (cliente/interno)
    """
    try:
        # Ruta de la carpeta compartida
        shared_base = getattr(settings, 'SHARED_DOCUMENTS_PATH', None)
        if not shared_base:
            logger.warning("SHARED_DOCUMENTS_PATH no configurada")
            return None
        
        # Crear estructura en carpeta compartida
        # Convertir visit-report a visit_reports, lab-report a lab_reports, etc.
        folder_name = document_type.replace('-', '_') + 's'
        country = get_current_country()
        shared_type_folder = os.path.join(shared_base, country, folder_name)

        
        # Para reportes de calidad, crear subcarpetas por tipo
        if document_type == 'quality-report' and report_type:
            if report_type == 'cliente':
                shared_incident_folder = os.path.join(shared_type_folder, 'cliente', f'incident_{incident_id}')
            elif report_type == 'interno':
                shared_incident_folder = os.path.join(shared_type_folder, 'interno', f'incident_{incident_id}')
            else:
                # Fallback si no se especifica tipo
                shared_incident_folder = os.path.join(shared_type_folder, f'incident_{incident_id}')
        else:
            shared_incident_folder = os.path.join(shared_type_folder, f'incident_{incident_id}')
        
        # Crear carpetas si no existen
        os.makedirs(shared_incident_folder, exist_ok=True)
        
        # Ruta completa del archivo en carpeta compartida
        shared_file_path = os.path.join(shared_incident_folder, filename)
        
        # Copiar archivo a carpeta compartida
        shutil.copy2(local_path, shared_file_path)
        
        logger.info(f"Documento sincronizado a carpeta compartida: {shared_file_path}")
        return shared_file_path
        
    except Exception as e:
        logger.error(f"Error al sincronizar a carpeta compartida: {str(e)}")
        return None

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_visit_report(request):
    """
    Sube un reporte de visita específicamente
    """
    # Verificar autenticación
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Autenticación requerida'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    try:
        # Obtener datos del formulario
        incident_id = request.POST.get('incident_id')
        title = request.POST.get('title', 'Reporte de Visita')
        description = request.POST.get('description', '')
        file = request.FILES.get('file')
        
        if not incident_id:
            return Response(
                {'error': 'ID de incidencia requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not file:
            return Response(
                {'error': 'Archivo requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Usar carpeta compartida de red si está configurada, sino MEDIA_ROOT
        shared_base = getattr(settings, 'SHARED_DOCUMENTS_PATH', None)
        if not shared_base:
            # Fallback a MEDIA_ROOT si no hay carpeta compartida configurada
            shared_base = os.path.join(settings.MEDIA_ROOT, 'shared_documents')
        
        # Crear estructura de carpetas
        country = get_current_country()
        type_folder = os.path.join(shared_base, country, 'visit_report')
        incident_folder = os.path.join(type_folder, f'incident_{incident_id}')

        
        # Crear carpetas si no existen
        os.makedirs(incident_folder, exist_ok=True)
        
        # Generar nombre único para el archivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"visit_report_{incident_id}_{timestamp}_{file.name}"
        file_path = os.path.join(incident_folder, filename)
        
        # Guardar archivo
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        # Sincronizar a carpeta compartida
        shared_path = sync_to_shared_folder(file_path, 'visit-report', incident_id, filename)
        
        # Crear registro en la base de datos
        try:
            from apps.incidents.models import Incident
            from apps.documents.models import VisitReport
            
            logger.info(f"=== CREANDO REGISTRO EN BD PARA INCIDENCIA {incident_id} ===")
            
            # Verificar que la incidencia existe
            incident = Incident.objects.get(id=incident_id)
            logger.info(f"Incidencia encontrada: {incident.id} - {incident.code}")
            
            # Generar números únicos
            timestamp_suffix = str(int(datetime.now().timestamp()))[-6:]
            order_number = f"ORD-{datetime.now().year}-{timestamp_suffix}"
            report_number = f"RPT-{datetime.now().year}-{timestamp_suffix}"
            logger.info(f"Número de orden generado: {order_number}")
            logger.info(f"Número de reporte generado: {report_number}")
            
            # Crear el reporte de visita
            logger.info("Creando registro VisitReport...")
            visit_report = VisitReport.objects.create(
                related_incident=incident,
                report_number=report_number,
                order_number=order_number,
                visit_date=datetime.now(),
                project_name=incident.obra or 'Proyecto por definir',
                project_id=incident.pedido_num or '',
                client_name=incident.cliente or 'Cliente por definir',
                client_rut=incident.cliente_rut or '',
                address=incident.direccion_cliente or 'Dirección por definir',
                construction_company=incident.provider or '',
                salesperson='Vendedor por asignar',
                technician='Técnico por asignar',
                installer='',
                installer_phone='',
                commune='Comuna por definir',
                city='Ciudad por definir',
                visit_reason='Inspección técnica',
                machine_data={},
                wall_observations='',
                matrix_observations='',
                slab_observations='',
                storage_observations='',
                pre_assembled_observations='',
                exterior_observations='',
                general_observations='Observaciones pendientes de completar',
                status='draft',
                docx_path=file_path if file.name.endswith('.docx') else '',
                pdf_path=file_path if file.name.endswith('.pdf') else ''
            )
            
            logger.info(f"Reporte de visita creado en BD: {visit_report.id} para incidencia {incident_id}")
            
        except Exception as e:
            logger.error(f"Error al crear reporte de visita en BD: {str(e)}")
            logger.error(f"Tipo de error: {type(e).__name__}")
            logger.error(f"Detalles del error: {str(e)}")
            import traceback
            logger.error(f"Traceback completo: {traceback.format_exc()}")
            # Continuar sin crear el registro si falla
        
        # Registrar en logs
        logger.info(f"Reporte de visita subido: {filename} para incidencia {incident_id}")
        
        # Indexar en RAG
        try:
            if 'visit_report' in locals() and visit_report:
                RAGService.index_report(visit_report, 'visit_report')
        except Exception as e:
            logger.warning(f"Error indexando RAG (no bloqueante): {e}")
        
        return Response({
            'success': True,
            'message': 'Reporte de visita subido exitosamente',
            'filename': filename,
            'local_path': file_path,
            'shared_path': shared_path,
            'incident_id': incident_id,
            'title': title,
            'description': description
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error al subir reporte de visita: {str(e)}")
        return Response(
            {'error': f'Error interno del servidor: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_supplier_report(request):
    """
    Sube un reporte de proveedor específicamente
    """
    # Verificar autenticación
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Autenticación requerida'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    try:
        # Obtener datos del formulario
        incident_id = request.POST.get('incident_id')
        title = request.POST.get('title', 'Reporte de Proveedor')
        description = request.POST.get('description', '')
        file = request.FILES.get('file')
        
        if not incident_id:
            return Response(
                {'error': 'ID de incidencia requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not file:
            return Response(
                {'error': 'Archivo requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Usar carpeta compartida de red si está configurada, sino MEDIA_ROOT
        shared_base = getattr(settings, 'SHARED_DOCUMENTS_PATH', None)
        if not shared_base:
            # Fallback a MEDIA_ROOT si no hay carpeta compartida configurada
            shared_base = os.path.join(settings.MEDIA_ROOT, 'shared_documents')
        
        # Crear estructura de carpetas
        country = get_current_country()
        type_folder = os.path.join(shared_base, country, 'supplier_report')
        incident_folder = os.path.join(type_folder, f'incident_{incident_id}')

        
        # Crear carpetas si no existen
        os.makedirs(incident_folder, exist_ok=True)
        
        # Generar nombre único para el archivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"supplier_report_{incident_id}_{timestamp}_{file.name}"
        file_path = os.path.join(incident_folder, filename)
        
        # Guardar archivo
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        # Sincronizar a carpeta compartida
        shared_path = sync_to_shared_folder(file_path, 'supplier-report', incident_id, filename)
        
        # Crear registro en la base de datos
        try:
            from apps.incidents.models import Incident
            from apps.documents.models import SupplierReport
            
            # Verificar que la incidencia existe
            incident = Incident.objects.get(id=incident_id)
            
            # Generar número de orden único
            order_number = f"SP-{datetime.now().year}-{str(int(datetime.now().timestamp()))[-3:]}"
            
            # Crear el reporte de proveedor
            supplier_report = SupplierReport.objects.create(
                related_incident=incident,
                order_number=order_number,
                report_date=datetime.now().date(),
                supplier_name=incident.provider or 'Proveedor por definir',
                supplier_contact='Contacto por definir',
                supplier_email='',
                supplier_phone='',
                report_type='quality_issue',
                description=incident.descripcion or 'Descripción pendiente',
                corrective_actions='Acciones correctivas pendientes',
                preventive_measures='Medidas preventivas pendientes',
                supplier_response='Respuesta del proveedor pendiente',
                status='draft',
                docx_path=file_path if file.name.endswith('.docx') else '',
                pdf_path=file_path if file.name.endswith('.pdf') else ''
            )
            
            logger.info(f"Reporte de proveedor creado en BD: {supplier_report.id} para incidencia {incident_id}")
            
        except Exception as e:
            logger.error(f"Error al crear reporte de proveedor en BD: {str(e)}")
            # Continuar sin crear el registro si falla
        
        # Registrar en logs
        logger.info(f"Reporte de proveedor subido: {filename} para incidencia {incident_id}")

        # Indexar en RAG
        try:
            if 'supplier_report' in locals() and supplier_report:
                RAGService.index_report(supplier_report, 'supplier_report')
        except Exception as e:
            logger.warning(f"Error indexando RAG (no bloqueante): {e}")
        
        return Response({
            'success': True,
            'message': 'Reporte de proveedor subido exitosamente',
            'filename': filename,
            'local_path': file_path,
            'shared_path': shared_path,
            'incident_id': incident_id,
            'title': title,
            'description': description
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error al subir reporte de proveedor: {str(e)}")
        return Response(
            {'error': f'Error interno del servidor: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_lab_report(request):
    """
    Sube un reporte de laboratorio específicamente
    """
    # Verificar autenticación
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Autenticación requerida'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    try:
        # Obtener datos del formulario
        incident_id = request.POST.get('incident_id')
        title = request.POST.get('title', 'Reporte de Laboratorio')
        description = request.POST.get('description', '')
        file = request.FILES.get('file')
        
        if not incident_id:
            return Response(
                {'error': 'ID de incidencia requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not file:
            return Response(
                {'error': 'Archivo requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Usar carpeta compartida de red si está configurada, sino MEDIA_ROOT
        shared_base = getattr(settings, 'SHARED_DOCUMENTS_PATH', None)
        if not shared_base:
            # Fallback a MEDIA_ROOT si no hay carpeta compartida configurada
            shared_base = os.path.join(settings.MEDIA_ROOT, 'shared_documents')
        
        # Crear estructura de carpetas
        country = get_current_country()
        type_folder = os.path.join(shared_base, country, 'lab_report')
        incident_folder = os.path.join(type_folder, f'incident_{incident_id}')

        
        # Crear carpetas si no existen
        os.makedirs(incident_folder, exist_ok=True)
        
        # Generar nombre único para el archivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"lab_report_{incident_id}_{timestamp}_{file.name}"
        file_path = os.path.join(incident_folder, filename)
        
        # Guardar archivo
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        # Sincronizar a carpeta compartida
        shared_path = sync_to_shared_folder(file_path, 'lab-report', incident_id, filename)
        
        # Crear registro en la base de datos
        try:
            from apps.incidents.models import Incident
            from apps.documents.models import LabReport
            
            # Verificar que la incidencia existe
            incident = Incident.objects.get(id=incident_id)
            
            # Generar número de orden único
            order_number = f"LB-{datetime.now().year}-{str(int(datetime.now().timestamp()))[-3:]}"
            
            # Crear el reporte de laboratorio
            lab_report = LabReport.objects.create(
                related_incident=incident,
                order_number=order_number,
                request_date=datetime.now().date(),
                client=incident.cliente or 'Cliente por definir',
                test_type='quality_test',
                test_parameters={},
                test_results={},
                conclusion='Conclusión pendiente',
                recommendations='Recomendaciones pendientes',
                status='draft',
                docx_path=file_path if file.name.endswith('.docx') else '',
                pdf_path=file_path if file.name.endswith('.pdf') else ''
            )
            
            logger.info(f"Reporte de laboratorio creado en BD: {lab_report.id} para incidencia {incident_id}")
            
        except Exception as e:
            logger.error(f"Error al crear reporte de laboratorio en BD: {str(e)}")
            # Continuar sin crear el registro si falla
        
        # Registrar en logs
        logger.info(f"Reporte de laboratorio subido: {filename} para incidencia {incident_id}")
        
        # Indexar en RAG
        try:
            if 'lab_report' in locals() and lab_report:
                RAGService.index_report(lab_report, 'lab_report')
        except Exception as e:
            logger.warning(f"Error indexando RAG (no bloqueante): {e}")
        
        return Response({
            'success': True,
            'message': 'Reporte de laboratorio subido exitosamente',
            'filename': filename,
            'local_path': file_path,
            'shared_path': shared_path,
            'incident_id': incident_id,
            'title': title,
            'description': description
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error al subir reporte de laboratorio: {str(e)}")
        return Response(
            {'error': f'Error interno del servidor: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_quality_report(request):
    """
    Sube un reporte de calidad específicamente
    """
    # Verificar autenticación
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Autenticación requerida'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    try:
        # Obtener datos del formulario
        incident_id = request.POST.get('incident_id')
        title = request.POST.get('title', 'Reporte de Calidad')
        description = request.POST.get('description', '')
        file = request.FILES.get('file')
        
        if not incident_id:
            return Response(
                {'error': 'ID de incidencia requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not file:
            return Response(
                {'error': 'Archivo requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Usar carpeta compartida de red si está configurada, sino MEDIA_ROOT
        shared_base = getattr(settings, 'SHARED_DOCUMENTS_PATH', None)
        if not shared_base:
            # Fallback a MEDIA_ROOT si no hay carpeta compartida configurada
            shared_base = os.path.join(settings.MEDIA_ROOT, 'shared_documents')
        
        # Crear estructura de carpetas
        country = get_current_country()
        type_folder = os.path.join(shared_base, country, 'quality_report')
        incident_folder = os.path.join(type_folder, f'incident_{incident_id}')

        
        # Crear carpetas si no existen
        os.makedirs(incident_folder, exist_ok=True)
        
        # Generar nombre único para el archivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"quality_report_{incident_id}_{timestamp}_{file.name}"
        file_path = os.path.join(incident_folder, filename)
        
        # Guardar archivo
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        # Sincronizar a carpeta compartida
        shared_path = sync_to_shared_folder(file_path, 'quality-report', incident_id, filename)
        
        # Crear registro en la base de datos
        try:
            from apps.incidents.models import Incident
            from apps.documents.models import QualityReport
            
            logger.info(f"=== CREANDO REGISTRO EN BD PARA INCIDENCIA {incident_id} ===")
            
            # Verificar que la incidencia existe
            incident = Incident.objects.get(id=incident_id)
            logger.info(f"Incidencia encontrada: {incident.id} - {incident.code}")
            
            # Generar números únicos
            timestamp_suffix = str(int(datetime.now().timestamp()))[-6:]
            report_number = f"QC-{datetime.now().year}-{timestamp_suffix}"
            logger.info(f"Número de reporte generado: {report_number}")
            
            # Crear el reporte de calidad
            logger.info("Creando registro QualityReport...")
            quality_report = QualityReport.objects.create(
                related_incident=incident,
                report_number=report_number,
                report_type='cliente',  # Por defecto cliente
                title=title or 'Reporte de Calidad',
                executive_summary='Resumen ejecutivo del reporte de calidad generado automáticamente. Pendiente de revisión y completar detalles específicos.',
                problem_description=incident.descripcion or 'Descripción del problema detectado en la incidencia. Pendiente de análisis detallado.',
                root_cause_analysis='Análisis de causa raíz pendiente de completar. Se requiere investigación adicional para determinar las causas fundamentales del problema.',
                corrective_actions='Acciones correctivas pendientes de implementar. Se requiere definir las medidas específicas a tomar para resolver el problema.',
                preventive_measures='Medidas preventivas pendientes de establecer. Se requiere definir estrategias para evitar la recurrencia del problema.',
                recommendations='Recomendaciones pendientes de formular. Se requiere análisis adicional para proponer mejoras específicas.',
                technical_details='',
                internal_notes='',
                status='draft',
                docx_path=file_path if file.name.endswith('.docx') else '',
                pdf_path=file_path if file.name.endswith('.pdf') else '',
                created_by=request.user
            )
            logger.info(f"Reporte de calidad creado en BD: {quality_report.id} para incidencia {incident_id}")
            
        except Exception as e:
            logger.error(f"Error al crear reporte de calidad en BD: {str(e)}")
            logger.error(f"Tipo de error: {type(e).__name__}")
            logger.error(f"Detalles del error: {str(e)}")
            import traceback
            logger.error(f"Traceback completo: {traceback.format_exc()}")
            # Continuar sin crear el registro si falla
        
        # Registrar en logs
        logger.info(f"Reporte de calidad subido: {filename} para incidencia {incident_id}")
        
        # Indexar en RAG
        try:
            if 'quality_report' in locals() and quality_report:
                RAGService.index_report(quality_report, 'quality_report')
        except Exception as e:
            logger.warning(f"Error indexando RAG (no bloqueante): {e}")
        
        return Response({
            'success': True,
            'message': 'Reporte de calidad subido exitosamente',
            'filename': filename,
            'local_path': file_path,
            'shared_path': shared_path,
            'incident_id': incident_id,
            'title': title,
            'description': description
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error al subir reporte de calidad: {str(e)}")
        return Response(
            {'error': f'Error interno del servidor: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_document(request):
    """
    Sube un documento y lo copia a la carpeta compartida para trazabilidad
    """
    # Verificar autenticación
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Autenticación requerida'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    try:
        # Obtener datos del formulario
        incident_id = request.POST.get('incident_id')
        document_type = request.POST.get('document_type', 'unknown')
        report_type = request.POST.get('report_type')  # Para quality-report
        title = request.POST.get('title', 'Documento sin título')
        description = request.POST.get('description', '')
        file = request.FILES.get('file')
        
        if not incident_id:
            return Response(
                {'error': 'ID de incidencia requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not file:
            return Response(
                {'error': 'Archivo requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear estructura de carpetas locales
        country = get_current_country()
        shared_folder = os.path.join(settings.MEDIA_ROOT, 'shared_documents', country)
        type_folder = os.path.join(shared_folder, document_type)
        incident_folder = os.path.join(type_folder, f'incident_{incident_id}')

        
        # Crear carpetas si no existen
        os.makedirs(incident_folder, exist_ok=True)
        
        # Generar nombre único para el archivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_extension = os.path.splitext(file.name)[1]
        safe_filename = f"{timestamp}_{file.name}"
        file_path = os.path.join(incident_folder, safe_filename)
        
        # Guardar archivo
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        # Sincronizar a carpeta compartida (opcional)
        shared_file_path = None
        try:
            shared_file_path = sync_to_shared_folder(file_path, document_type, incident_id, safe_filename, report_type)
        except Exception as e:
            logger.warning(f"No se pudo sincronizar a carpeta compartida: {e}")
            # Continuar sin sincronización si falla
        
        # Verificar que la incidencia existe (opcional)
        try:
            from apps.incidents.models import Incident
            incident = Incident.objects.get(id=incident_id)
            logger.info(f"Incidencia {incident_id} encontrada: {incident.code}")
        except Incident.DoesNotExist:
            logger.warning(f"Incidencia con ID {incident_id} no encontrada, pero continuando con upload.")
        except Exception as e:
            logger.warning(f"Error verificando incidencia: {e}, pero continuando con upload.")
        
        # Crear registro en base de datos según el tipo de documento
        report_id = None
        if document_type == 'visit-report':
            from apps.documents.models import VisitReport
            report = VisitReport.objects.create(
                related_incident_id=incident_id,
                visit_date=datetime.now().date(),
                client_name='',
                project_name='',
                address='',
                salesperson='',
                technician='',
                commune='',
                city='',
                visit_reason='',
                general_observations='',
                status='draft',
                created_by=request.user,
                pdf_path=shared_file_path
            )
            report_id = report.id
        elif document_type == 'lab-report':
            from apps.documents.models import LabReport
            report = LabReport.objects.create(
                related_incident_id=incident_id,
                form_number='',
                request_date=datetime.now().date(),
                applicant='',
                client='',
                description='',
                project_background='',
                tests_performed={},
                comments='',
                conclusions='',
                recommendations='',
                created_by=request.user,
                pdf_path=shared_file_path
            )
            report_id = report.id
        elif document_type == 'supplier-report':
            from apps.documents.models import SupplierReport
            report = SupplierReport.objects.create(
                related_incident_id=incident_id,
                supplier_name='',
                supplier_contact='',
                supplier_email='',
                subject='',
                introduction='',
                problem_description='',
                technical_analysis='',
                recommendations='',
                expected_improvements='',
                report_date=datetime.now().date(),
                created_by=request.user,
                pdf_path=shared_file_path
            )
            report_id = report.id
        elif document_type == 'quality-report':
            from apps.documents.models import QualityReport
            report = QualityReport.objects.create(
                related_incident_id=incident_id,
                report_type=report_type or 'cliente',  # Default a cliente si no se especifica
                title=title,
                executive_summary='',
                problem_description='',
                root_cause_analysis='',
                corrective_actions='',
                preventive_measures='',
                recommendations='',
                created_by=request.user,
                pdf_path=shared_file_path
            )
            report_id = report.id
        
        logger.info(f"Documento subido exitosamente: {safe_filename} para incidencia {incident_id}")
        
        return Response({
            'success': True,
            'message': 'Documento subido exitosamente',
            'file_path': file_path,
            'shared_file_path': shared_file_path,
            'filename': safe_filename,
            'report_id': report_id
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error al subir documento: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Error interno del servidor: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@require_http_methods(["GET"])
def open_document(request, document_type, incident_id, filename):
    """
    Abre un documento desde la carpeta compartida
    """
    try:
        # Decodificar el nombre del archivo para manejar caracteres especiales
        from urllib.parse import unquote
        decoded_filename = unquote(filename)
        
        # Ruta de la carpeta compartida
        shared_base = getattr(settings, 'SHARED_DOCUMENTS_PATH', None)
        if not shared_base:
            # Usar ruta por defecto si no está configurada
            shared_base = os.path.join(settings.BASE_DIR, 'documents')
            logger.warning(f"SHARED_DOCUMENTS_PATH no configurada, usando ruta por defecto: {shared_base}")
        
        # Verificar que la carpeta existe
        if not os.path.exists(shared_base):
            logger.error(f"Carpeta compartida no existe: {shared_base}")
            raise Http404(f"Carpeta compartida no existe: {shared_base}")
        
        # Construir ruta del archivo (manejar diferentes formatos de nombres)
        # Convertir visit-report a visit_reports, lab-report a lab_reports, etc.
        folder_name = document_type.replace('-', '_') + 's'
        country = get_current_country()
        
        # Intentar primero ruta regionalizada
        regional_path = os.path.join(shared_base, country, folder_name)
        
        # Para quality reports, buscar en ambas subcarpetas (cliente e interno)
        if document_type == 'quality-report':
            shared_file_path = None
            for report_type in ['cliente', 'interno']:
                # Probar ruta regional
                test_path = os.path.join(
                    shared_base, 
                    country,
                    folder_name, 
                    report_type,
                    f'incident_{incident_id}', 
                    decoded_filename
                )
                if os.path.exists(test_path):
                    shared_file_path = test_path
                    break
                
                # Probar ruta legacy
                test_path_legacy = os.path.join(
                    shared_base, 
                    folder_name, 
                    report_type,
                    f'incident_{incident_id}', 
                    decoded_filename
                )
                if os.path.exists(test_path_legacy):
                    shared_file_path = test_path_legacy
                    break

            
            if not shared_file_path:
                # Listar archivos disponibles para debugging
                available_files = []
                for report_type in ['cliente', 'interno']:
                    incident_folder = os.path.join(shared_base, folder_name, report_type, f'incident_{incident_id}')
                    if os.path.exists(incident_folder):
                        available_files.extend(os.listdir(incident_folder))
                
                error_msg = f"Archivo no encontrado en quality reports. Archivos disponibles: {available_files}"
                logger.warning(error_msg)
                raise Http404(error_msg)
        else:
            # Para otros tipos de documentos, usar la estructura normal
            shared_file_path = os.path.join(
                shared_base, 
                folder_name, 
                f'incident_{incident_id}', 
                decoded_filename
            )
            
            # Verificar que el archivo existe
            if not os.path.exists(shared_file_path):
                # Listar archivos disponibles para debugging
                incident_folder = os.path.join(shared_base, folder_name, f'incident_{incident_id}')
                available_files = []
                if os.path.exists(incident_folder):
                    available_files = os.listdir(incident_folder)
                
                # Buscar archivos similares en otras incidencias
                similar_files = []
                try:
                    for other_incident_folder in os.listdir(os.path.join(shared_base, folder_name)):
                        if other_incident_folder.startswith('incident_') and other_incident_folder != f'incident_{incident_id}':
                            other_folder_path = os.path.join(shared_base, folder_name, other_incident_folder)
                            if os.path.exists(other_folder_path):
                                for other_file in os.listdir(other_folder_path):
                                    if decoded_filename.lower() in other_file.lower() or other_file.lower() in decoded_filename.lower():
                                        similar_files.append({
                                            'incident_id': other_incident_folder.replace('incident_', ''),
                                            'filename': other_file,
                                            'path': os.path.join(other_folder_path, other_file)
                                        })
                except Exception as e:
                    logger.warning(f"Error buscando archivos similares: {str(e)}")
                
                error_msg = f"Archivo no encontrado: {decoded_filename}. Archivos disponibles en incident_{incident_id}: {available_files}"
                if similar_files:
                    error_msg += f". Archivos similares encontrados: {similar_files}"
                
                logger.warning(error_msg)
                raise Http404(error_msg)
        
        # Retornar el archivo directamente
        return FileResponse(
            open(shared_file_path, 'rb'),
            as_attachment=False,
            filename=decoded_filename
        )
        
    except Http404:
        raise
    except Exception as e:
        logger.error(f"Error al abrir documento: {str(e)}", exc_info=True)
        raise Http404(f"Error interno del servidor: {str(e)}")

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_shared_documents(request):
    """
    Lista documentos en la carpeta compartida
    """
    try:
        shared_base = getattr(settings, 'SHARED_DOCUMENTS_PATH', None)
        if not shared_base:
            return Response(
                {'error': 'Carpeta compartida no configurada'}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        documents = []
        
        # Recorrer carpetas de tipos de documentos
        for doc_type in os.listdir(shared_base):
            type_path = os.path.join(shared_base, doc_type)
            if os.path.isdir(type_path):
                # Recorrer carpetas de incidencias
                for incident_folder in os.listdir(type_path):
                    incident_path = os.path.join(type_path, incident_folder)
                    if os.path.isdir(incident_path) and incident_folder.startswith('incident_'):
                        incident_id = incident_folder.replace('incident_', '')
                        
                        # Listar archivos en la carpeta de incidencia
                        for filename in os.listdir(incident_path):
                            file_path = os.path.join(incident_path, filename)
                            if os.path.isfile(file_path):
                                documents.append({
                                    'document_type': doc_type,
                                    'incident_id': incident_id,
                                    'filename': filename,
                                    'file_path': file_path,
                                    'size': os.path.getsize(file_path),
                                    'modified': os.path.getmtime(file_path),
                                    'download_url': f'/api/documents/open/{doc_type.replace("_", "-")}/{incident_id}/{filename}'
                                })
        
        return Response({
            'documents': documents,
            'total': len(documents)
        })
        
    except Exception as e:
        logger.error(f"Error al listar documentos compartidos: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Error interno del servidor: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_document_by_name(request, document_type, filename):
    """
    Buscar un documento por nombre en todas las incidencias
    """
    try:
        shared_base = getattr(settings, 'SHARED_DOCUMENTS_PATH', None)
        if not shared_base:
            return Response(
                {'error': 'Carpeta compartida no configurada'}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # Construir ruta del archivo
        folder_name = document_type.replace('-', '_') + 's'
        type_folder = os.path.join(shared_base, folder_name)
        
        if not os.path.exists(type_folder):
            return Response({
                'error': f'Carpeta de tipo no encontrada: {type_folder}',
                'shared_base': shared_base,
                'folder_name': folder_name
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Buscar archivo en todas las incidencias
        found_files = []
        for incident_folder in os.listdir(type_folder):
            if incident_folder.startswith('incident_'):
                incident_path = os.path.join(type_folder, incident_folder)
                if os.path.isdir(incident_path):
                    for file in os.listdir(incident_path):
                        if file == filename or filename.lower() in file.lower():
                            file_path = os.path.join(incident_path, file)
                            if os.path.isfile(file_path):
                                file_stat = os.stat(file_path)
                                found_files.append({
                                    'incident_id': incident_folder.replace('incident_', ''),
                                    'filename': file,
                                    'size': file_stat.st_size,
                                    'size_human': f"{file_stat.st_size / 1024:.1f} KB",
                                    'created_at': datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                                    'modified_at': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                                    'download_url': f'/api/documents/open/{document_type}/{incident_folder.replace("incident_", "")}/{file}'
                                })
        
        return Response({
            'search_filename': filename,
            'document_type': document_type,
            'found_files': found_files,
            'count': len(found_files)
        })
        
    except Exception as e:
        logger.error(f"Error en search_document_by_name: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Error interno del servidor: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def debug_shared_folder(request, document_type, incident_id):
    """
    Endpoint de debugging para verificar qué archivos están disponibles
    """
    try:
        shared_base = getattr(settings, 'SHARED_DOCUMENTS_PATH', None)
        if not shared_base:
            return Response(
                {'error': 'Carpeta compartida no configurada'}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # Construir ruta del archivo
        folder_name = document_type.replace('-', '_') + 's'
        incident_folder = os.path.join(shared_base, folder_name, f'incident_{incident_id}')
        
        # Verificar si la carpeta existe
        if not os.path.exists(incident_folder):
            return Response({
                'error': f'Carpeta no encontrada: {incident_folder}',
                'shared_base': shared_base,
                'folder_name': folder_name,
                'incident_id': incident_id,
                'full_path': incident_folder
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Listar archivos disponibles
        files = []
        for filename in os.listdir(incident_folder):
            file_path = os.path.join(incident_folder, filename)
            if os.path.isfile(file_path):
                file_stat = os.stat(file_path)
                files.append({
                    'filename': filename,
                    'size': file_stat.st_size,
                    'size_human': f"{file_stat.st_size / 1024:.1f} KB",
                    'created_at': datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                    'modified_at': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                    'download_url': f'/api/documents/open/{document_type}/{incident_id}/{filename}'
                })
        
        return Response({
            'incident_folder': incident_folder,
            'files': files,
            'count': len(files),
            'shared_base': shared_base,
            'folder_name': folder_name
        })
        
    except Exception as e:
        logger.error(f"Error en debug_shared_folder: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Error interno del servidor: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_uploaded_documents(request, document_type, incident_id):
    """
    Lista los documentos subidos para una incidencia específica
    """
    try:
        shared_base = getattr(settings, 'SHARED_DOCUMENTS_PATH', None)
        if not shared_base:
            return Response(
                {'error': 'Carpeta compartida no configurada'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        folder_name = document_type.replace('-', '_') + 's'
        
        # Para quality reports, buscar en ambas subcarpetas (cliente e interno)
        if document_type == 'quality-report':
            files = []
            for report_type in ['cliente', 'interno']:
                incident_folder = os.path.join(shared_base, folder_name, report_type, f'incident_{incident_id}')
                if os.path.exists(incident_folder):
                    for filename in os.listdir(incident_folder):
                        file_path = os.path.join(incident_folder, filename)
                        if os.path.isfile(file_path):
                            file_stat = os.stat(file_path)
                            files.append({
                                'filename': filename,
                                'size': file_stat.st_size,
                                'size_human': f"{file_stat.st_size / 1024:.1f} KB",
                                'created_at': datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                                'modified_at': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                                'download_url': f'/api/documents/open/{document_type}/{incident_id}/{filename}',
                                'report_type': report_type
                            })
        else:
            # Para otros tipos de documentos, usar la estructura normal
            incident_folder = os.path.join(shared_base, folder_name, f'incident_{incident_id}')
            
            if not os.path.exists(incident_folder):
                return Response({
                    'documents': [],
                    'folder_path': incident_folder,
                    'message': 'No hay documentos subidos para esta incidencia'
                })
            
            # Listar archivos en la carpeta
            files = []
            for filename in os.listdir(incident_folder):
                file_path = os.path.join(incident_folder, filename)
                if os.path.isfile(file_path):
                    file_stat = os.stat(file_path)
                    files.append({
                        'filename': filename,
                        'size': file_stat.st_size,
                        'size_human': f"{file_stat.st_size / 1024:.1f} KB",
                        'created_at': datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                        'modified_at': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                        'download_url': f'/api/documents/open/{document_type}/{incident_id}/{filename}'
                    })
        
        # Ordenar por fecha de modificación (más recientes primero)
        files.sort(key=lambda x: x['modified_at'], reverse=True)
        
        return Response({
            'documents': files,
            'folder_path': incident_folder,
            'count': len(files)
        })
        
    except Exception as e:
        logger.error(f"Error al listar documentos: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Error interno del servidor: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_uploaded_document(request, document_type, incident_id, filename):
    """
    Elimina un documento subido de la carpeta compartida
    """
    try:
        from .shared_folder_utils import delete_from_shared_folder
        
        # Eliminar archivo específico de la carpeta compartida
        deleted_files = delete_from_shared_folder(
            document_type=document_type,
            incident_id=incident_id,
            filename=filename
        )
        
        if not deleted_files:
            return Response(
                {'error': 'Archivo no encontrado en carpeta compartida'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        logger.info(f"Archivo(s) eliminado(s): {deleted_files}")
        
        return Response({
            'message': 'Archivo eliminado exitosamente',
            'deleted_files': deleted_files
        })
        
    except Exception as e:
        logger.error(f"Error al eliminar documento: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Error interno del servidor: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_all_incident_documents(request, incident_id):
    """
    Elimina todos los documentos de una incidencia de la carpeta compartida
    """
    try:
        from .shared_folder_utils import delete_from_shared_folder
        
        # Tipos de documentos a buscar
        document_types = ['visit-report', 'lab-report', 'supplier-report', 'quality-report']
        all_deleted = []
        
        for doc_type in document_types:
            # Eliminar documentos normales
            deleted_files = delete_from_shared_folder(
                document_type=doc_type,
                incident_id=incident_id
            )
            all_deleted.extend([f"{doc_type}: {file}" for file in deleted_files])
            
            # Eliminar documentos de laboratorio separados
            for lab_type in ['cliente', 'interno']:
                lab_deleted = delete_from_shared_folder(
                    document_type=f"{doc_type}-{lab_type}",
                    incident_id=incident_id
                )
                all_deleted.extend([f"{doc_type}-{lab_type}: {file}" for file in lab_deleted])
        
        if not all_deleted:
            return Response({
                'message': 'No se encontraron documentos para eliminar',
                'deleted_files': []
            })
        
        logger.info(f"Documentos eliminados para incidencia {incident_id}: {all_deleted}")
        
        return Response({
            'message': f'Se eliminaron {len(all_deleted)} documentos de la incidencia',
            'deleted_files': all_deleted
        })
        
    except Exception as e:
        logger.error(f"Error eliminando documentos de incidencia: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Error interno del servidor: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


