#!/usr/bin/env python
"""
Verificar el estado de las incidencias y sus documentos
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

print("🔍 Verificando estado de incidencias y documentos...")

try:
    from apps.incidents.models import Incident
    from apps.documents.models import VisitReport, LabReport, SupplierReport, QualityReport
    
    # Obtener todas las incidencias
    incidents = Incident.objects.all()
    print(f"📊 Total de incidencias: {incidents.count()}")
    
    for incident in incidents:
        print(f"\n🔍 Incidencia: {incident.code} (ID: {incident.id})")
        print(f"   Cliente: {incident.cliente}")
        print(f"   Estado: {incident.estado}")
        
        # Verificar documentos existentes
        visit_reports = VisitReport.objects.filter(related_incident=incident)
        lab_reports = LabReport.objects.filter(related_incident=incident)
        supplier_reports = SupplierReport.objects.filter(related_incident=incident)
        quality_reports = QualityReport.objects.filter(related_incident=incident)
        
        print(f"   📋 Reportes de visita: {visit_reports.count()}")
        print(f"   🧪 Reportes de laboratorio: {lab_reports.count()}")
        print(f"   🏭 Reportes de proveedor: {supplier_reports.count()}")
        print(f"   📄 Reportes de calidad: {quality_reports.count()}")
        
        # Buscar incidencias sin reportes de visita
        if visit_reports.count() == 0:
            print(f"   ✅ Esta incidencia NO tiene reporte de visita - ID: {incident.id}")
    
    # Buscar incidencias sin ningún documento
    print(f"\n🔍 Incidencias sin reportes de visita:")
    incidents_without_visit = []
    for incident in incidents:
        if VisitReport.objects.filter(related_incident=incident).count() == 0:
            incidents_without_visit.append(incident)
            print(f"   - {incident.code} (ID: {incident.id}) - {incident.cliente}")
    
    if not incidents_without_visit:
        print("   ❌ Todas las incidencias tienen reportes de visita")
    else:
        print(f"   ✅ Encontradas {len(incidents_without_visit)} incidencias sin reportes de visita")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
