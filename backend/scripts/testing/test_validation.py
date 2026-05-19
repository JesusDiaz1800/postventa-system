#!/usr/bin/env python
"""
Test de validación de documentos
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

print("📧 Modo desarrollo: Los emails se mostrarán en la consola")
print("✅ Django configurado correctamente")

try:
    from apps.documents.services.document_validation import DocumentValidationService
    from apps.incidents.models import Incident
    from apps.documents.models import VisitReport
    
    print("✅ Importaciones exitosas")
    
    # Verificar incidencias existentes
    incidents = Incident.objects.all()[:5]
    print(f"📊 Incidencias encontradas: {len(incidents)}")
    
    for incident in incidents:
        print(f"  - Incidencia {incident.id}: {incident.code} - Estado: {incident.estado}")
        
        # Verificar reportes de visita existentes
        visit_reports = VisitReport.objects.filter(related_incident=incident)
        print(f"    Reportes de visita: {visit_reports.count()}")
        
        # Probar validación
        can_create, message = DocumentValidationService.can_create_visit_report(incident.id)
        print(f"    Puede crear reporte: {can_create} - {message}")
        
        # Obtener estado completo
        status = DocumentValidationService.get_incident_documents_status(incident.id)
        if status:
            print(f"    Estado documentos: {status}")
        
        print()
    
    print("✅ Test de validación completado")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
