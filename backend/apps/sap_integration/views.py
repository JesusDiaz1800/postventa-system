from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .sap_query_service import SAPQueryService

# Instancia global del servicio
sap_service = SAPQueryService()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_sap_customers(request):
    """
    Buscar clientes en SAP por nombre o código.
    Query params: q (string de búsqueda)
    """
    query = request.query_params.get('q', '')
    
    if len(query) < 3:
        return Response(
            {'error': 'La búsqueda debe tener al menos 3 caracteres'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    customers = sap_service.search_customers(query)
    
    return Response({
        'results': customers,
        'count': len(customers)
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_sales_employees(request):
    """Obtener lista de vendedores de SAP"""
    employees = sap_service.get_sales_employees()
    return Response(employees)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_technicians(request):
    """Obtener lista de técnicos/empleados de SAP"""
    from apps.core.thread_local import get_current_country
    import logging
    logger = logging.getLogger(__name__)
    country = get_current_country()
    
    # Soporta filtrar por rol técnico oficial (?role=technician)
    role = request.query_params.get('role')
    only_technical_role = (role == 'technician')
    
    technicians = sap_service.get_technicians(only_technical_role=only_technical_role)
    
    logger.info(f"[API] get_technicians for {country} (role={role}): Found {len(technicians)} results")
    return Response(technicians)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_customer_details(request, card_code):
    """Obtener detalles completos del cliente incluyendo vendedor, direcciones y proyectos"""
    details = sap_service.get_customer_full_details(card_code)
    
    if not details:
        return Response(
            {'error': 'Cliente no encontrado en SAP'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    return Response(details)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_sap_customer(request, card_code):
    """Obtener detalles completos de un cliente por su código"""
    customer = sap_service.get_customer_by_code(card_code)
    
    if not customer:
        return Response(
            {'error': 'Cliente no encontrado en SAP'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    return Response(customer)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_sap_service_call(request, doc_num):
    """Obtener detalles de una llamada de servicio por su DocNum"""
    call = sap_service.get_service_call(doc_num)
    
    if not call:
        return Response(
            {'error': 'Llamada de servicio no encontrada en SAP'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    call['attachments'] = sap_service.get_attachments(call['call_id'])
    return Response(call)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_sap_attachment(request, atc_entry, line):
    """
    Descargar/Servir archivo adjunto desde ruta de red de SAP.
    Actúa como proxy para evitar problemas de CORS/Seguridad con rutas UNC.
    """
    from django.http import HttpResponse, Http404
    
    content, mime_type, filename = sap_service.get_attachment_file(atc_entry, line)
    
    if content is None:
        return Response(
            {'error': filename or 'Archivo no encontrado'}, 
            status=status.HTTP_404_NOT_FOUND
        )
        
    response = HttpResponse(content, content_type=mime_type)
    # Si es imagen, dejar que el navegador la muestre (inline)
    # Si es otro archivo, forzar descarga o según preferencia
    if not mime_type.startswith('image/'):
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
    else:
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        
    return response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_customer_projects(request, card_code):
    """Obtener lista de obras asociadas a un cliente"""
    projects = sap_service.get_customer_projects(card_code)
    
    return Response({
        'projects': projects,
        'count': len(projects)
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recent_service_calls(request):
    """Obtener llamadas de servicio recientes. Opcional filtrar por cliente."""
    customer_code = request.query_params.get('customer_code')
    limit = int(request.query_params.get('limit', 20))
    
    calls = sap_service.get_recent_service_calls(customer_code, limit)
    
    return Response({
        'results': calls,
        'count': len(calls)
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def debug_sap_connections(request):
    """
    Diagnóstico profundo de las conexiones a bases de datos SAP.
    Intenta conectar a sap_db, sap_db_pe y sap_db_co y reporta fallos.
    """
    from django.db import connections
    from django.db.utils import OperationalError
    import traceback
    
    results = {}
    db_aliases = ['sap_db', 'sap_db_pe', 'sap_db_co']
    
    for alias in db_aliases:
        try:
            conn = connections[alias]
            # Probamos consulta mínima
            with conn.cursor() as cursor:
                cursor.execute("SELECT TOP 1 CardCode FROM OCRD")
                row = cursor.fetchone()
                status_msg = "EXITOSO" if row else "CONEXIÓN OK (Tabla vacía)"
                error_msg = None
        except OperationalError as e:
            status_msg = "FALLIDO (Conexión)"
            error_msg = str(e)
        except Exception as e:
            status_msg = "FALLIDO (SQL/Permisos)"
            error_msg = str(e)
            
        # Extraer info de config (sin contraseña por seguridad, solo el inicio)
        db_config = conn.settings_dict
        results[alias] = {
            'status': status_msg,
            'database': db_config.get('NAME'),
            'user': db_config.get('USER'),
            'host': db_config.get('HOST'),
            'driver': db_config.get('OPTIONS', {}).get('driver'),
            'error_detail': error_msg
        }
        
    return Response(results)
