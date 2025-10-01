"""
File Views for managing real documents in shared network folder
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse, Http404
from .file_service import DocumentFileService
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_real_documents(request):
    """List all real documents in shared folder"""
    try:
        file_service = DocumentFileService()
        files = file_service.get_document_files()
        
        # Add additional info for each file
        for file_info in files:
            file_info['preview'] = file_service.get_document_preview(file_info['filename'])
            file_info['can_preview'] = file_info['extension'] in ['.txt', '.md', '.log', '.csv']
            file_info['can_view'] = file_info['extension'] in ['.pdf', '.jpg', '.jpeg', '.png', '.gif']
        
        return Response({
            'success': True,
            'files': files,
            'total_files': len(files)
        })
        
    except Exception as e:
        logger.error(f"Error listing real documents: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_document_info(request, filename):
    """Get specific document information"""
    try:
        file_service = DocumentFileService()
        file_info = file_service.get_document_by_filename(filename)
        
        if not file_info:
            return Response({
                'success': False,
                'error': 'Document not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Add preview if available
        file_info['preview'] = file_service.get_document_preview(filename)
        file_info['can_preview'] = file_info['extension'] in ['.txt', '.md', '.log', '.csv']
        file_info['can_view'] = file_info['extension'] in ['.pdf', '.jpg', '.jpeg', '.png', '.gif']
        
        return Response({
            'success': True,
            'file': file_info
        })
        
    except Exception as e:
        logger.error(f"Error getting document info for {filename}: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def serve_real_document(request, filename):
    """Serve real document file for download/viewing"""
    try:
        file_service = DocumentFileService()
        return file_service.serve_document(filename)
        
    except Http404:
        return Response({
            'success': False,
            'error': 'Document not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error serving document {filename}: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def serve_real_document_public(request, filename):
    """Serve real document file for download/viewing (public access)"""
    try:
        file_service = DocumentFileService()
        return file_service.serve_document(filename)
        
    except Http404:
        return Response({
            'success': False,
            'error': 'Document not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error serving document {filename}: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_real_document(request, filename):
    """Delete real document file"""
    try:
        file_service = DocumentFileService()
        success = file_service.delete_document(filename)
        
        if success:
            return Response({
                'success': True,
                'message': f'Document {filename} deleted successfully'
            })
        else:
            return Response({
                'success': False,
                'error': 'Document not found or could not be deleted'
            }, status=status.HTTP_404_NOT_FOUND)
            
    except Exception as e:
        logger.error(f"Error deleting document {filename}: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_documents_by_type(request):
    """Get documents filtered by type"""
    try:
        file_type = request.GET.get('type', '')
        file_service = DocumentFileService()
        files = file_service.get_documents_by_type(file_type)
        
        # Add additional info for each file
        for file_info in files:
            file_info['preview'] = file_service.get_document_preview(file_info['filename'])
            file_info['can_preview'] = file_info['extension'] in ['.txt', '.md', '.log', '.csv']
            file_info['can_view'] = file_info['extension'] in ['.pdf', '.jpg', '.jpeg', '.png', '.gif']
        
        return Response({
            'success': True,
            'files': files,
            'total_files': len(files),
            'filter_type': file_type
        })
        
    except Exception as e:
        logger.error(f"Error getting documents by type {file_type}: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_folder_stats(request):
    """Get folder statistics"""
    try:
        file_service = DocumentFileService()
        stats = file_service.get_folder_stats()
        
        return Response({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting folder stats: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_documents(request):
    """Search documents by filename"""
    try:
        query = request.GET.get('q', '').lower()
        if not query:
            return Response({
                'success': False,
                'error': 'Search query is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        file_service = DocumentFileService()
        all_files = file_service.get_document_files()
        
        # Filter files by filename
        matching_files = [
            f for f in all_files 
            if query in f['filename'].lower()
        ]
        
        # Add additional info for each file
        for file_info in matching_files:
            file_info['preview'] = file_service.get_document_preview(file_info['filename'])
            file_info['can_preview'] = file_info['extension'] in ['.txt', '.md', '.log', '.csv']
            file_info['can_view'] = file_info['extension'] in ['.pdf', '.jpg', '.jpeg', '.png', '.gif']
        
        return Response({
            'success': True,
            'files': matching_files,
            'total_files': len(matching_files),
            'query': query
        })
        
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
