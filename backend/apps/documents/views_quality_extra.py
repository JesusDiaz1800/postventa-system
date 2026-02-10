
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def escalate_to_supplier(request, pk):
    """
    Escalar un reporte de calidad a proveedor (Solo cambia estado, NO crea reporte automático)
    """
    try:
        report = get_object_or_404(QualityReport, pk=pk)
        incident = report.related_incident
        
        # 1. Actualizar Reporte de Calidad
        report.status = 'escalated'
        report.save()
        
        # 2. Actualizar Incidencia
        incident.escalated_to_supplier = True
        incident.escalation_date = timezone.now()
        incident.escalation_reason = f"Escalado desde Reporte de Calidad {report.report_number}"
        incident.save(update_fields=['escalated_to_supplier', 'escalation_date', 'escalation_reason'])
        
        return Response({
            'success': True,
            'message': 'Reporte escalado a proveedor exitosamente (Estado actualizado)',
            'report_id': report.id
        })
        
    except Exception as e:
        logger.error(f"Error escalando a proveedor: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Error interno: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
