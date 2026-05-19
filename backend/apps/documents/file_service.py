"""
File Service for managing documents in shared network folder
"""

import os
import mimetypes
import shutil
from typing import Dict, List, Optional, Tuple
from django.conf import settings
from django.http import FileResponse, Http404
from django.core.files.storage import default_storage
import logging

logger = logging.getLogger(__name__)

class DocumentFileService:
    """Service for managing document files in shared network folder"""
    
    def __init__(self):
        self.shared_folder = getattr(settings, 'SHARED_DOCUMENTS_PATH', 'Y:\\CONTROL DE CALIDAD\\postventa')
        self.documents_path = os.path.join(self.shared_folder, 'documents')
        self.templates_path = os.path.join(self.shared_folder, 'templates')
        self.images_path = os.path.join(self.shared_folder, 'images')
        
        # Ensure directories exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure all required directories exist"""
        directories = [
            self.shared_folder,
            self.documents_path,
            self.templates_path,
            self.images_path
        ]
        
        for directory in directories:
            try:
                os.makedirs(directory, exist_ok=True)
                logger.info(f"Directory ensured: {directory}")
            except Exception as e:
                logger.error(f"Error creating directory {directory}: {e}")
    
    def get_document_files(self) -> List[Dict]:
        """Get list of all document files in shared folder, organized by incidents"""
        try:
            if not os.path.exists(self.documents_path):
                return []
            
            files = []
            
            # First, get files from incident-specific folders
            for item in os.listdir(self.documents_path):
                item_path = os.path.join(self.documents_path, item)
                if os.path.isdir(item_path) and item.startswith('INC_'):
                    # This is an incident folder
                    incident_code = item.replace('INC_', '')
                    for file_item in os.listdir(item_path):
                        file_path = os.path.join(item_path, file_item)
                        if os.path.isfile(file_path):
                            file_info = self._get_file_info(file_path, incident_code)
                            if file_info:
                                files.append(file_info)
            
            # Then, get files from the general documents folder
            for filename in os.listdir(self.documents_path):
                file_path = os.path.join(self.documents_path, filename)
                if os.path.isfile(file_path):
                    file_info = self._get_file_info(file_path)
                    if file_info:
                        files.append(file_info)
            
            # Sort files by modification time (newest first)
            files.sort(key=lambda x: x['modified'], reverse=True)
            return files
            
        except Exception as e:
            logger.error(f"Error getting document files: {e}")
            return []
    
    def _get_file_info(self, file_path: str, incident_code: str = None) -> Optional[Dict]:
        """Get file information"""
        try:
            if not os.path.isfile(file_path):
                return None
                
            stat = os.stat(file_path)
            filename = os.path.basename(file_path)
            
            # Get file type
            mime_type, _ = mimetypes.guess_type(file_path)
            file_type = mime_type.split('/')[0] if mime_type else 'unknown'
            
            file_info = {
                'filename': filename,
                'file_path': file_path,
                'size': stat.st_size,
                'created': stat.st_ctime,
                'modified': stat.st_mtime,
                'modified_at': stat.st_mtime,  # Add for compatibility
                'file_type': file_type,
                'mime_type': mime_type,
                'extension': os.path.splitext(filename)[1].lower(),  # Add extension field
                'incident_code': incident_code,  # Add incident code if provided
                'folder_path': os.path.dirname(file_path),
                'relative_path': os.path.relpath(file_path, self.documents_path),
                'can_view': True  # Add for compatibility
            }
            
            return file_info
            
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {e}")
            return None
    
    def get_document_by_filename(self, filename: str) -> Optional[Dict]:
        """Get specific document file info"""
        try:
            file_path = os.path.join(self.documents_path, filename)
            if not os.path.exists(file_path):
                return None
            
            stat = os.stat(file_path)
            return {
                'filename': filename,
                'file_path': file_path,
                'size': stat.st_size,
                'created_at': stat.st_ctime,
                'modified_at': stat.st_mtime,
                'extension': os.path.splitext(filename)[1].lower(),
                'mime_type': mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
            }
        except Exception as e:
            logger.error(f"Error getting document {filename}: {e}")
            return None
    
    def serve_document(self, filename: str) -> FileResponse:
        """Serve document file for download/viewing"""
        try:
            file_path = os.path.join(self.documents_path, filename)
            if not os.path.exists(file_path):
                raise Http404("Document not found")
            
            # Get MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = 'application/octet-stream'
            
            # Determine if it should be displayed inline or downloaded
            if mime_type in ['application/pdf', 'image/jpeg', 'image/png', 'image/gif', 'text/plain']:
                response = FileResponse(
                    open(file_path, 'rb'),
                    content_type=mime_type,
                    as_attachment=False
                )
            else:
                response = FileResponse(
                    open(file_path, 'rb'),
                    content_type=mime_type,
                    as_attachment=True,
                    filename=filename
                )
            
            response['Content-Length'] = os.path.getsize(file_path)
            return response
            
        except Exception as e:
            logger.error(f"Error serving document {filename}: {e}")
            raise Http404("Error serving document")
    
    def delete_document(self, filename: str) -> bool:
        """Delete document file"""
        try:
            file_path = os.path.join(self.documents_path, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Document deleted: {filename}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting document {filename}: {e}")
            return False
    
    def get_document_preview(self, filename: str) -> Optional[str]:
        """Get document preview (for text files)"""
        try:
            file_path = os.path.join(self.documents_path, filename)
            if not os.path.exists(file_path):
                return None
            
            # Only preview text-based files
            text_extensions = ['.txt', '.md', '.log', '.csv']
            if os.path.splitext(filename)[1].lower() in text_extensions:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(1000)  # First 1000 characters
                    return content
            return None
        except Exception as e:
            logger.error(f"Error getting preview for {filename}: {e}")
            return None
    
    def get_documents_by_type(self, file_type: str = None) -> List[Dict]:
        """Get documents filtered by type"""
        files = self.get_document_files()
        
        if not file_type:
            return files
        
        # Filter by file extension
        type_extensions = {
            'pdf': ['.pdf'],
            'word': ['.docx', '.doc'],
            'excel': ['.xlsx', '.xls'],
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'],
            'text': ['.txt', '.md', '.log', '.csv']
        }
        
        extensions = type_extensions.get(file_type.lower(), [])
        if extensions:
            return [f for f in files if f['extension'] in extensions]
        
        return files
    
    def get_folder_stats(self) -> Dict:
        """Get folder statistics"""
        try:
            files = self.get_document_files()
            
            total_files = len(files)
            total_size = sum(f['size'] for f in files)
            
            # Count by type
            type_counts = {}
            for file in files:
                ext = file['extension']
                type_counts[ext] = type_counts.get(ext, 0) + 1
            
            return {
                'total_files': total_files,
                'total_size': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'type_counts': type_counts,
                'folder_path': self.documents_path,
                'folder_exists': os.path.exists(self.documents_path)
            }
        except Exception as e:
            logger.error(f"Error getting folder stats: {e}")
            return {
                'total_files': 0,
                'total_size': 0,
                'total_size_mb': 0,
                'type_counts': {},
                'folder_path': self.documents_path,
                'folder_exists': False,
                'error': str(e)
            }
