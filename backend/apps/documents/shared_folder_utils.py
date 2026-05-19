#!/usr/bin/env python
"""
Utilidades para manejo de la carpeta compartida
"""

import os
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def delete_from_shared_folder(document_type, incident_id, filename=None, title=None):
    """
    Eliminar un documento de la carpeta compartida
    
    Args:
        document_type: Tipo de documento (visit-report, lab-report, etc.)
        incident_id: ID de la incidencia
        filename: Nombre específico del archivo (opcional)
        title: Título del documento para búsqueda por similitud (opcional)
    
    Returns:
        list: Lista de archivos eliminados
    """
    deleted_files = []
    
    try:
        shared_base = getattr(settings, 'SHARED_DOCUMENTS_PATH', None)
        if not shared_base:
            logger.warning("Carpeta compartida no configurada")
            return deleted_files
        
        # Normalizar tipo de documento
        doc_type = document_type.replace('_', '-')
        
        # Posibles ubicaciones en la carpeta compartida
        possible_paths = [
            os.path.join(shared_base, 'documents', doc_type, f'incident_{incident_id}'),
            os.path.join(shared_base, f'{doc_type}s', f'incident_{incident_id}'),
            os.path.join(shared_base, doc_type, f'incident_{incident_id}'),
            # Para reportes de laboratorio separados
            os.path.join(shared_base, 'documents', f'{doc_type}-cliente', f'incident_{incident_id}'),
            os.path.join(shared_base, 'documents', f'{doc_type}-interno', f'incident_{incident_id}'),
        ]
        
        for folder_path in possible_paths:
            if os.path.exists(folder_path):
                logger.info(f"Buscando archivos en: {folder_path}")
                
                if filename:
                    # Eliminar archivo específico
                    file_path = os.path.join(folder_path, filename)
                    if os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                            deleted_files.append(filename)
                            logger.info(f"Archivo eliminado: {file_path}")
                        except Exception as e:
                            logger.error(f"Error eliminando archivo {file_path}: {e}")
                else:
                    # Buscar archivos por título o nombre similar
                    if title:
                        for file in os.listdir(folder_path):
                            if (title.lower() in file.lower() or 
                                file.lower() in title.lower()):
                                file_path = os.path.join(folder_path, file)
                                try:
                                    os.remove(file_path)
                                    deleted_files.append(file)
                                    logger.info(f"Archivo eliminado por título: {file_path}")
                                except Exception as e:
                                    logger.error(f"Error eliminando archivo {file_path}: {e}")
                    else:
                        # Eliminar todos los archivos del directorio
                        for file in os.listdir(folder_path):
                            file_path = os.path.join(folder_path, file)
                            if os.path.isfile(file_path):
                                try:
                                    os.remove(file_path)
                                    deleted_files.append(file)
                                    logger.info(f"Archivo eliminado: {file_path}")
                                except Exception as e:
                                    logger.error(f"Error eliminando archivo {file_path}: {e}")
        
        return deleted_files
        
    except Exception as e:
        logger.error(f"Error eliminando de carpeta compartida: {e}")
        return deleted_files

def list_shared_documents(document_type, incident_id):
    """
    Listar documentos en la carpeta compartida para una incidencia
    
    Args:
        document_type: Tipo de documento
        incident_id: ID de la incidencia
    
    Returns:
        list: Lista de archivos encontrados
    """
    files_found = []
    
    try:
        shared_base = getattr(settings, 'SHARED_DOCUMENTS_PATH', None)
        if not shared_base:
            return files_found
        
        doc_type = document_type.replace('_', '-')
        
        # Posibles ubicaciones
        possible_paths = [
            os.path.join(shared_base, 'documents', doc_type, f'incident_{incident_id}'),
            os.path.join(shared_base, f'{doc_type}s', f'incident_{incident_id}'),
            os.path.join(shared_base, doc_type, f'incident_{incident_id}'),
            os.path.join(shared_base, 'documents', f'{doc_type}-cliente', f'incident_{incident_id}'),
            os.path.join(shared_base, 'documents', f'{doc_type}-interno', f'incident_{incident_id}'),
        ]
        
        for folder_path in possible_paths:
            if os.path.exists(folder_path):
                for file in os.listdir(folder_path):
                    if os.path.isfile(os.path.join(folder_path, file)):
                        files_found.append({
                            'filename': file,
                            'path': os.path.join(folder_path, file),
                            'folder': folder_path
                        })
        
        return files_found
        
    except Exception as e:
        logger.error(f"Error listando documentos compartidos: {e}")
        return files_found
