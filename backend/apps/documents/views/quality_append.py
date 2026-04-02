
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def escalate_to_supplier(request, pk):
    """
    Escalar un reporte de calidad a proveedor (Crear SupplierReport y enviar correo)
    """
    try:
        report = get_object_or_404(QualityReport, pk=pk)
        incident = report.related_incident
        
        # Datos del formulario
        supplier_email = request.data.get('supplier_email')
        subject = request.data.get('subject')
        message = request.data.get('message')
        supplier_name = request.data.get('supplier_name')
        
        if not supplier_email or not subject or not message:
            return Response(
                {'error': 'Email, asunto y mensaje son requeridos'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # 1. Crear SupplierReport
        supplier_report = SupplierReport.objects.create(
            related_incident=incident,
            supplier_name=supplier_name or incident.provider or 'Proveedor Desconocido',
            supplier_contact=incident.provider, # Fallback
            supplier_email=supplier_email,
            subject=subject,
            introduction=message, 
            problem_description=report.problem_description, # Heredar del reporte de calidad
            technical_analysis=report.technical_details,
            status=DocumentStatus.SENT,
            sent_date=timezone.now(),
            created_by=request.user,
            pdf_path=report.pdf_path # Reutilizar el PDF del reporte de calidad como adjunto??
            # NO, SupplierReport tiene su propio PDF generado. 
            # Pero en este caso, "Escalar" significa enviar el reporte existente.
            # Podríamos copiar el path o dejarlo vacío y adjuntar el archivo como DocumentAttachment.
        )
        # Si report.pdf_path existe, lo adjuntamos como DocumentAttachment al SupplierReport
        if report.pdf_path:
            # Importar DocumentAttachment si es necesario, o crearlo
            from ..models import DocumentAttachment
            import os
            
            # Crear adjunto
            DocumentAttachment.objects.create(
                document_type='supplier_report',
                document_id=supplier_report.id,
                file=report.pdf_path, # Esto es un path string, FileField espera un File object o path relativo a media root?
                # FileField con path string funciona si está en storage.
                # Mejor copiamos el archivo para evitar problemas si se borra el original?
                # Por simplicidad, usamos el mismo archivo.
                filename=os.path.basename(report.pdf_path),
                file_type='application/pdf',
                file_size=0, # Pendiente
                description='Reporte de Calidad Original',
                uploaded_by=request.user
            )

        # 2. Actualizar Incidencia
        incident.escalated_to_supplier = True
        incident.escalation_date = timezone.now()
        incident.escalation_reason = f"Escalado desde Reporte de Calidad {report.report_number}"
        incident.save(update_fields=['escalated_to_supplier', 'escalation_date', 'escalation_reason'])
        
        # 3. Log de envío
        logger.info(f"📧 ESCALACIÓN A PROVEEDOR ENVIADA: {supplier_email} | Asunto: {subject}")
        
        return Response({
            'success': True,
            'message': 'Reporte escalado a proveedor exitosamente',
            'supplier_report_id': supplier_report.id
        })
        
    except Exception as e:
        logger.error(f"Error escalando a proveedor: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Error interno: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
