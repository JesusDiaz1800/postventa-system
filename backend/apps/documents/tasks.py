"""
Celery tasks for document generation and conversion
"""
# from celery import shared_task
from django.utils import timezone
from django.conf import settings
import logging
import os
import subprocess
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


# @shared_task(bind=True)
def generate_document_task(self, document_id):
    """
    Generate document from template using docxtpl
    """
    from .models import Document, DocumentTemplate
    from docxtpl import DocxTemplate
    import json
    
    try:
        document = Document.objects.get(id=document_id)
        template = document.template
        
        if not template:
            raise ValueError("No template specified for document")
        
        # Get template file path
        template_path = os.path.join(settings.MEDIA_ROOT, template.docx_template_path)
        
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template file not found: {template_path}")
        
        # Load template
        doc = DocxTemplate(template_path)
        
        # Prepare context data
        context = document.placeholders_data.copy()
        
        # Add incident data if available
        if document.incident:
            incident = document.incident
            context.update({
                'INC_CODE': incident.code,
                'FECHA_DETECCION': incident.fecha_deteccion.strftime('%d/%m/%Y'),
                'HORA_DETECCION': incident.hora_deteccion.strftime('%H:%M'),
                'PROVEEDOR': incident.provider,
                'OBRA': incident.obra,
                'CLIENTE': incident.cliente,
                'CLIENTE_RUT': incident.cliente_rut,
                'DIRECCION': incident.direccion_cliente,
                'NUM_PEDIDO': incident.pedido_num,
                'NUM_FACTURA': incident.factura_num,
                'NC_NUMBER': incident.nc_number,
                'NP_NUMBER': incident.np_number,
                'SKU': incident.sku,
                'LOTE': incident.lote,
                'DESCRIPCION': incident.descripcion,
                'ACCIONES_INMEDIATAS': incident.acciones_inmediatas,
                'CATEGORIA': incident.get_categoria_display(),
                'SUBCATEGORIA': incident.subcategoria,
                'PRIORIDAD': incident.get_prioridad_display(),
                'ESTADO': incident.get_estado_display(),
            })
        
        # Add current date and time
        context.update({
            'FECHA_ACTUAL': timezone.now().strftime('%d/%m/%Y'),
            'HORA_ACTUAL': timezone.now().strftime('%H:%M'),
        })
        
        # Render document
        doc.render(context)
        
        # Save document
        output_dir = os.path.join(settings.MEDIA_ROOT, 'documents', str(document.id))
        os.makedirs(output_dir, exist_ok=True)
        
        output_filename = f"{document.title.replace(' ', '_')}_v{document.version}.docx"
        output_path = os.path.join(output_dir, output_filename)
        
        doc.save(output_path)
        
        # Update document record
        document.docx_path = f"documents/{document.id}/{output_filename}"
        document.save()
        
        logger.info(f"Document generated successfully: {output_path}")
        return {'status': 'success', 'document_id': document_id, 'docx_path': document.docx_path}
        
    except Document.DoesNotExist:
        logger.error(f"Document {document_id} not found")
        return {'status': 'error', 'error': 'Document not found'}
    
    except Exception as e:
        logger.error(f"Error generating document {document_id}: {str(e)}")
        return {'status': 'error', 'error': str(e)}


# @shared_task(bind=True)
def convert_document_task(self, conversion_id):
    """
    Convert document from DOCX to PDF using LibreOffice
    """
    from .models import DocumentConversion, Document
    import time
    
    try:
        conversion = DocumentConversion.objects.get(id=conversion_id)
        document = conversion.document
        
        # Update status to processing
        conversion.status = 'processing'
        conversion.save()
        
        start_time = time.time()
        
        # Get source file path
        source_path = os.path.join(settings.MEDIA_ROOT, conversion.source_path)
        
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source file not found: {source_path}")
        
        # Create output directory
        output_dir = os.path.dirname(os.path.join(settings.MEDIA_ROOT, conversion.target_path))
        os.makedirs(output_dir, exist_ok=True)
        
        # Convert using LibreOffice
        output_path = os.path.join(settings.MEDIA_ROOT, conversion.target_path)
        
        cmd = [
            'libreoffice',
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', output_dir,
            source_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            # Update conversion record
            conversion.status = 'completed'
            conversion.processing_time = time.time() - start_time
            conversion.completed_at = timezone.now()
            conversion.save()
            
            # Update document record
            document.pdf_path = conversion.target_path
            document.save()
            
            logger.info(f"Document converted successfully: {output_path}")
            return {'status': 'success', 'conversion_id': conversion_id, 'pdf_path': conversion.target_path}
        
        else:
            # Conversion failed
            conversion.status = 'failed'
            conversion.error_message = result.stderr
            conversion.processing_time = time.time() - start_time
            conversion.save()
            
            logger.error(f"Document conversion failed: {result.stderr}")
            return {'status': 'error', 'error': result.stderr}
    
    except DocumentConversion.DoesNotExist:
        logger.error(f"Conversion {conversion_id} not found")
        return {'status': 'error', 'error': 'Conversion not found'}
    
    except subprocess.TimeoutExpired:
        conversion.status = 'failed'
        conversion.error_message = 'Conversion timeout'
        conversion.save()
        
        logger.error(f"Document conversion timeout: {conversion_id}")
        return {'status': 'error', 'error': 'Conversion timeout'}
    
    except Exception as e:
        conversion.status = 'failed'
        conversion.error_message = str(e)
        conversion.save()
        
        logger.error(f"Error converting document {conversion_id}: {str(e)}")
        return {'status': 'error', 'error': str(e)}


# @shared_task(bind=True)
def cleanup_temp_files_task(self):
    """
    Clean up temporary files older than 24 hours
    """
    try:
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
        if not os.path.exists(temp_dir):
            return {'status': 'success', 'message': 'No temp directory found'}
        
        current_time = timezone.now()
        cleaned_count = 0
        
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                file_time = timezone.datetime.fromtimestamp(
                    os.path.getmtime(file_path),
                    tz=timezone.get_current_timezone()
                )
                
                # Delete files older than 24 hours
                if (current_time - file_time).total_seconds() > 86400:
                    try:
                        os.remove(file_path)
                        cleaned_count += 1
                    except OSError:
                        pass
        
        logger.info(f"Cleaned up {cleaned_count} temporary files")
        return {'status': 'success', 'cleaned_count': cleaned_count}
    
    except Exception as e:
        logger.error(f"Error cleaning up temp files: {str(e)}")
        return {'status': 'error', 'error': str(e)}
