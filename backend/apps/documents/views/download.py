"""
Views for downloading and viewing documents
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions, status
from django.shortcuts import get_object_or_404
from django.http import FileResponse
import os
import mimetypes

from ..models import Document


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_document(request, document_id, file_type='docx'):
    """Download a document file (DOCX or PDF)"""
    try:
        document = get_object_or_404(Document, id=document_id)
        
        # Check permissions
        user = request.user
        if user.role == 'provider':
            # Providers can only download documents related to their incidents
            if not document.incident or document.incident.provider != user:
                return Response({
                    'error': 'No tienes permisos para descargar este documento'
                }, status=status.HTTP_403_FORBIDDEN)
        
        # Determine file path based on file type
        if file_type.lower() == 'pdf' and document.pdf_path:
            file_path = document.pdf_path
            filename = document.title.replace(' ', '_') + '.pdf'
        elif file_type.lower() == 'docx' and document.docx_path:
            file_path = document.docx_path
            filename = document.title.replace(' ', '_') + '.docx'
        else:
            return Response({
                'error': f'Archivo {file_type.upper()} no disponible para este documento'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if file exists
        if not os.path.exists(file_path):
            return Response({
                'error': 'El archivo no existe en el servidor'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get MIME type
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = 'application/octet-stream'
        
        # Create file response
        response = FileResponse(
            open(file_path, 'rb'),
            content_type=mime_type,
            as_attachment=True,
            filename=filename
        )
        
        # Add headers for better browser handling
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = os.path.getsize(file_path)
        
        return response
        
    except Exception as e:
        return Response({
            'error': f'Error al descargar el documento: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def view_document(request, document_id, file_type='pdf'):
    """View a document in browser (PDF) or download (DOCX)"""
    try:
        document = get_object_or_404(Document, id=document_id)
        
        # Check permissions
        user = request.user
        if user.role == 'provider':
            # Providers can only view documents related to their incidents
            if not document.incident or document.incident.provider != user:
                return Response({
                    'error': 'No tienes permisos para ver este documento'
                }, status=status.HTTP_403_FORBIDDEN)
        
        # For PDF files, try to display in browser
        if file_type.lower() == 'pdf' and document.pdf_path:
            file_path = document.pdf_path
            filename = document.title.replace(' ', '_') + '.pdf'
            
            if not os.path.exists(file_path):
                return Response({
                    'error': 'El archivo PDF no existe en el servidor'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Create file response for inline viewing
            response = FileResponse(
                open(file_path, 'rb'),
                content_type='application/pdf',
                as_attachment=False,
                filename=filename
            )
            
            # Add headers for inline viewing
            response['Content-Disposition'] = f'inline; filename="{filename}"'
            response['Content-Length'] = os.path.getsize(file_path)
            
            return response
        
        # For DOCX files, force download
        elif file_type.lower() == 'docx' and document.docx_path:
            return download_document(request, document_id, 'docx')
        
        else:
            return Response({
                'error': f'Archivo {file_type.upper()} no disponible para este documento'
            }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        return Response({
            'error': f'Error al abrir el documento: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def edit_document(request, document_id):
    """Edit document metadata"""
    try:
        document = get_object_or_404(Document, id=document_id)
        
        # Check if user has permission to edit this document
        if not request.user.is_staff and document.incident and document.incident.user != request.user:
            return Response({'error': 'No tienes permisos para editar este documento'}, status=status.HTTP_403_FORBIDDEN)
        
        # Update document fields
        if 'title' in request.data:
            document.title = request.data['title']
        if 'description' in request.data:
            document.description = request.data['description']
        
        document.save()
        
        return Response({
            'message': 'Documento actualizado exitosamente',
            'document': {
                'id': document.id,
                'title': document.title,
                'description': document.description,
                'created_at': document.created_at,
                'updated_at': document.updated_at
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': f'Error al editar el documento: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_document(request, document_id):
    """Delete a document and its files"""
    try:
        document = get_object_or_404(Document, id=document_id)
        
        # Check if user has permission to delete this document
        if not request.user.is_staff and document.incident and document.incident.user != request.user:
            return Response({'error': 'No tienes permisos para eliminar este documento'}, status=status.HTTP_403_FORBIDDEN)
        
        # Delete files if they exist (both local and shared)
        files_deleted = []
        
        # Delete local files
        if document.docx_path and os.path.exists(document.docx_path):
            try:
                os.remove(document.docx_path)
                files_deleted.append('DOCX')
            except Exception as e:
                logger.warning(f"Could not delete DOCX file {document.docx_path}: {e}")
        
        if document.pdf_path and os.path.exists(document.pdf_path):
            try:
                os.remove(document.pdf_path)
                files_deleted.append('PDF')
            except Exception as e:
                logger.warning(f"Could not delete PDF file {document.pdf_path}: {e}")
        
        # Delete from shared folder if it exists
        try:
            from ..shared_folder_utils import delete_from_shared_folder
            
            if document.incident:
                incident_id = document.incident.id
                document_type = document.document_type
                
                # Eliminar de carpeta compartida
                shared_deleted = delete_from_shared_folder(
                    document_type=document_type,
                    incident_id=incident_id,
                    title=document.title
                )
                
                # Agregar archivos eliminados de carpeta compartida
                for file in shared_deleted:
                    files_deleted.append(f'SHARED: {file}')
                    
        except Exception as e:
            logger.warning(f"Error deleting from shared folder: {e}")
        
        # Delete document record
        document_title = document.title
        document.delete()
        
        return Response({
            'message': f'Documento "{document_title}" eliminado exitosamente',
            'files_deleted': files_deleted
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': f'Error al eliminar el documento: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def document_info(request, document_id):
    """Get document information including file paths and availability"""
    try:
        document = get_object_or_404(Document, id=document_id)
        
        # Check permissions
        user = request.user
        if user.role == 'provider':
            # Providers can only see documents related to their incidents
            if not document.incident or document.incident.provider != user:
                return Response({
                    'error': 'No tienes permisos para ver este documento'
                }, status=status.HTTP_403_FORBIDDEN)
        
        # Check file availability
        docx_exists = os.path.exists(document.docx_path) if document.docx_path else False
        pdf_exists = os.path.exists(document.pdf_path) if document.pdf_path else False
        
        # Get file sizes
        docx_size = os.path.getsize(document.docx_path) if docx_exists else 0
        pdf_size = os.path.getsize(document.pdf_path) if pdf_exists else 0
        
        return Response({
            'id': document.id,
            'title': document.title,
            'document_type': document.document_type,
            'created_at': document.created_at,
            'created_by': document.created_by.username if document.created_by else None,
            'incident_id': document.incident.id if document.incident else None,
            'incident_title': document.incident.title if document.incident else None,
            'files': {
                'docx': {
                    'available': docx_exists,
                    'path': document.docx_path,
                    'size': docx_size,
                    'size_mb': round(docx_size / (1024 * 1024), 2) if docx_size > 0 else 0
                },
                'pdf': {
                    'available': pdf_exists,
                    'path': document.pdf_path,
                    'size': pdf_size,
                    'size_mb': round(pdf_size / (1024 * 1024), 2) if pdf_size > 0 else 0
                }
            },
            'notes': document.notes,
            'placeholders_data': document.placeholders_data
        })
        
    except Exception as e:
        return Response({
            'error': f'Error al obtener información del documento: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
