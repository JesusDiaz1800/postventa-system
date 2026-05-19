"""
Servicio para gestión de archivos adjuntos de documentos
"""
import os
import uuid
from datetime import datetime
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import logging
from apps.core.thread_local import get_current_country


logger = logging.getLogger(__name__)

class DocumentAttachmentService:
    """Servicio para gestionar archivos adjuntos de documentos"""
    
    def __init__(self):
        # Usar la variable configurada en settings.py (SHARED_DOCUMENTS_PATH)
        # Fallback a una carpeta 'shared' dentro del directorio del proyecto si no está definida
        from django.conf import settings
        self.shared_path = getattr(settings, 'SHARED_DOCUMENTS_PATH', os.path.join(settings.BASE_DIR, 'shared'))
        self.attachments_folder = os.path.join(self.shared_path, 'attachments')
        # Ya no llamamos a ensure_directories() aquí para evitar crashes en el import
    
    def ensure_directories(self, country=None):
        """Crear directorios necesarios si no existen de forma segura"""
        try:
            if not country:
                country = get_current_country()
                
            directories = [
                self.attachments_folder,
                os.path.join(self.attachments_folder, country),
                os.path.join(self.attachments_folder, country, 'visit_reports'),
                os.path.join(self.attachments_folder, country, 'lab_reports'),
                os.path.join(self.attachments_folder, country, 'supplier_reports'),
            ]
            
            for directory in directories:
                if not os.path.exists(directory):
                    try:
                        os.makedirs(directory, exist_ok=True)
                    except PermissionError:
                        logger.warning(f"No hay permisos para crear el directorio: {directory}")
        except Exception as e:
            logger.error(f"Error crítico en ensure_directories: {e}")
    
    def save_attachment(self, file, document_type, document_id, description=""):
        """
        Guardar archivo adjunto en la carpeta compartida
        
        Args:
            file: Archivo subido
            document_type: Tipo de documento (visit_report, lab_report, supplier_report)
            document_id: ID del documento
            description: Descripción del archivo
        
        Returns:
            dict: Información del archivo guardado
        """
        try:
            # Generar nombre único para el archivo
            file_extension = os.path.splitext(file.name)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Determinar carpeta de destino
            type_folder = {
                'visit_report': 'visit_reports',
                'lab_report': 'lab_reports',
                'supplier_report': 'supplier_reports'
            }.get(document_type, 'general')
            
            # Crear ruta completa
            country = get_current_country()
            self.ensure_directories(country)
            
            folder_path = os.path.join(self.attachments_folder, country, type_folder, str(document_id))
            os.makedirs(folder_path, exist_ok=True)

            
            file_path = os.path.join(folder_path, unique_filename)
            
            # Guardar archivo
            with open(file_path, 'wb') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            
            # Información del archivo
            file_info = {
                'filename': file.name,
                'stored_filename': unique_filename,
                'file_path': file_path,
                'file_size': file.size,
                'file_type': file.content_type,
                'description': description,
                'document_type': document_type,
                'document_id': document_id,
                'uploaded_at': datetime.now().isoformat()
            }
            
            logger.info(f"Archivo adjunto guardado: {file_path}")
            return file_info
            
        except Exception as e:
            logger.error(f"Error guardando archivo adjunto: {e}")
            raise
    
    def get_attachment_path(self, document_type, document_id, filename):
        """Obtener ruta de un archivo adjunto con fallback regional"""
        type_folder = {
            'visit_report': 'visit_reports',
            'lab_report': 'lab_reports',
            'supplier_report': 'supplier_reports'
        }.get(document_type, 'general')
        
        country = get_current_country()
        
        # Intentar ruta regionalizada
        regional_path = os.path.join(self.attachments_folder, country, type_folder, str(document_id), filename)
        if os.path.exists(regional_path):
            return regional_path
            
        # Fallback a ruta legacy
        return os.path.join(self.attachments_folder, type_folder, str(document_id), filename)

    def resolve_file_path(self, stored_path, country=None, sub_folder=None, incident_id=None):
        """
        Resuelve la ruta física de un archivo priorizando la ruta almacenada y 
        aplicando fallbacks regionales y de infraestructura.
        
        Args:
            stored_path: Ruta guardada en la BD.
            country: Código de país (opcional, usa thread_local por defecto).
            sub_folder: Subcarpeta específica (ej: 'visit_reports').
            incident_id: ID de la incidencia relacionada para reconstrucción.
        """
        if not stored_path:
            return None
            
        # 1. Intentar ruta exacta tal cual está en BD
        if os.path.exists(stored_path):
            return stored_path
            
        # 2. Intentar reconstrucción basada en el nombre del archivo
        filename = os.path.basename(stored_path)
        if not country:
            country = get_current_country()
            
        # Posibles bases de búsqueda
        search_bases = []
        shared_path = getattr(settings, 'SHARED_DOCUMENTS_PATH', None)
        media_root = getattr(settings, 'MEDIA_ROOT', '')
        
        if shared_path:
            search_bases.append(shared_path)
        if media_root:
            search_bases.append(media_root)
            
        # Si tenemos sub_folder e incident_id, podemos ser muy específicos
        for base in search_bases:
            if sub_folder and incident_id:
                # Intento A: base/country/sub_folder/incident_{id}/filename
                path_a = os.path.join(base, country, sub_folder, f'incident_{incident_id}', filename)
                if os.path.exists(path_a): return path_a
                
                # Intento B: base/sub_folder/incident_{id}/filename (legacy no country)
                path_b = os.path.join(base, sub_folder, f'incident_{incident_id}', filename)
                if os.path.exists(path_b): return path_b

            # Intento C: Búsqueda genérica en la base actual
            # (Útil para adjuntos de laboratorios o proveedores que no siguen el patrón incident_{id})
            # Pero normalmente sí lo siguen. 
            
        return None

    
    def list_attachments(self, document_type, document_id):
        """Listar archivos adjuntos de un documento"""
        try:
            type_folder = {
                'visit_report': 'visit_reports',
                'lab_report': 'lab_reports',
                'supplier_report': 'supplier_reports'
            }.get(document_type, 'general')
            
            # Intentar primero ruta regionalizada
            country = get_current_country()
            folder_path = os.path.join(self.attachments_folder, country, type_folder, str(document_id))
            
            # Si no existe, intentar ruta legacy
            if not os.path.exists(folder_path):
                folder_path = os.path.join(self.attachments_folder, type_folder, str(document_id))

            
            if not os.path.exists(folder_path):

                return []
            
            attachments = []
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path):
                    stat = os.stat(file_path)
                    attachments.append({
                        'filename': filename,
                        'file_size': stat.st_size,
                        'uploaded_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'file_path': file_path
                    })
            
            return attachments
            
        except Exception as e:
            logger.error(f"Error listando archivos adjuntos: {e}")
            return []
    
    def delete_attachment(self, document_type, document_id, filename):
        """Eliminar archivo adjunto"""
        try:
            file_path = self.get_attachment_path(document_type, document_id, filename)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Archivo adjunto eliminado: {file_path}")
                return True
            else:
                logger.warning(f"Archivo adjunto no encontrado: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error eliminando archivo adjunto: {e}")
            return False
    
    def get_attachment_info(self, document_type, document_id, filename):
        """Obtener información de un archivo adjunto"""
        try:
            file_path = self.get_attachment_path(document_type, document_id, filename)
            
            if not os.path.exists(file_path):
                return None
            
            stat = os.stat(file_path)
            return {
                'filename': filename,
                'file_size': stat.st_size,
                'uploaded_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'file_path': file_path,
                'exists': True
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo información de archivo adjunto: {e}")
            return None

# Instancia global del servicio
attachment_service = DocumentAttachmentService()
