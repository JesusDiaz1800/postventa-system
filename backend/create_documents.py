#!/usr/bin/env python3
"""
Script para crear documentos de ejemplo usando manage.py
"""

import os
import sys
import django
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from apps.incidents.models import Incident
from apps.documents.models import VisitReport, SupplierReport, LabReport

def create_sample_documents():
    """Crear documentos de ejemplo realistas"""
    
    print("🚀 Creando documentos de ejemplo realistas...")
    
    # Obtener o crear incidencias
    incidents = []
    
    # Crear incidencias si no existen
    incident_data = {
        'code': 'INC-2024-001',
        'cliente': 'Empresa Constructora ABC',
        'provider': 'Proveedor XYZ',
        'description': 'Problema con material de construcción',
        'estado': 'abierto',
        'priority': 'alta'
    }
    
    incident, created = Incident.objects.get_or_create(
        code=incident_data['code'],
        defaults=incident_data
    )
    incidents.append(incident)
    
    if created:
        print(f"✅ Creada incidencia: {incident.code}")
    
    # Crear segunda incidencia
    incident_data2 = {
        'code': 'INC-2024-002',
        'cliente': 'Inmobiliaria DEF',
        'provider': 'Proveedor ABC',
        'description': 'Defecto en acabados',
        'estado': 'abierto',
        'priority': 'media'
    }
    
    incident2, created = Incident.objects.get_or_create(
        code=incident_data2['code'],
        defaults=incident_data2
    )
    incidents.append(incident2)
    
    if created:
        print(f"✅ Creada incidencia: {incident2.code}")
    
    # Crear reporte de visita
    print("📋 Creando reporte de visita...")
    visit_data = {
        'related_incident': incident,
        'order_number': 'ORD-2024-001',
        'project_name': 'Edificio Residencial Las Flores',
        'client_name': 'Empresa Constructora ABC',
        'address': 'Av. Principal 123, Santiago',
        'salesperson': 'Juan Pérez',
        'technician': 'Carlos Rodríguez',
        'commune': 'Las Condes',
        'city': 'Santiago',
        'visit_reason': 'Inspección de materiales defectuosos',
        'general_observations': 'Se encontraron problemas en la calidad del cemento suministrado. Se requiere reemplazo inmediato.',
        'status': 'completed'
    }
    
    visit_report, created = VisitReport.objects.get_or_create(
        related_incident=incident,
        defaults=visit_data
    )
    
    if created:
        print(f"✅ Creado reporte de visita: {visit_report.order_number}")
    
    # Crear informe de proveedor
    print("📋 Creando informe de proveedor...")
    supplier_data = {
        'related_incident': incident,
        'report_date': datetime.now().strftime('%Y-%m-%d'),
        'supplier_name': 'Proveedor XYZ',
        'supplier_contact': 'Roberto Martínez',
        'supplier_email': 'roberto@proveedorxyz.cl',
        'subject': 'Problema con calidad de cemento',
        'introduction': 'Se ha identificado un problema crítico con la calidad del cemento suministrado.',
        'problem_description': 'El cemento no cumple con las especificaciones técnicas acordadas.',
        'technical_analysis': 'Análisis de laboratorio confirma deficiencias en la composición química.',
        'recommendations': 'Se recomienda reemplazo inmediato del material.',
        'expected_improvements': 'Mejora en la calidad y cumplimiento de especificaciones.',
        'status': 'completed'
    }
    
    supplier_report, created = SupplierReport.objects.get_or_create(
        related_incident=incident,
        defaults=supplier_data
    )
    
    if created:
        print(f"✅ Creado informe de proveedor: {supplier_report.report_number}")
    
    # Crear reporte de laboratorio
    print("📋 Creando reporte de laboratorio...")
    lab_data = {
        'related_incident': incident,
        'form_number': 'LAB-2024-001',
        'request_date': datetime.now().strftime('%Y-%m-%d'),
        'applicant': 'Juan Pérez',
        'client': 'Empresa Constructora ABC',
        'description': 'Análisis de calidad de cemento',
        'project_background': 'Proyecto de construcción residencial',
        'tests_performed': 'Análisis químico, resistencia a compresión, tiempo de fraguado',
        'comments': 'Se realizaron pruebas estándar según normativa chilena',
        'conclusions': 'El material no cumple con las especificaciones técnicas',
        'recommendations': 'Se recomienda reemplazo del material',
        'report_type': 'cliente',
        'status': 'completed'
    }
    
    lab_report, created = LabReport.objects.get_or_create(
        related_incident=incident,
        defaults=lab_data
    )
    
    if created:
        print(f"✅ Creado reporte de laboratorio: {lab_report.form_number}")
    
    print("🎉 Documentos de ejemplo creados exitosamente!")
    print(f"📊 Resumen:")
    print(f"   - Incidencias: {Incident.objects.filter(estado='abierto').count()}")
    print(f"   - Reportes de visita: {VisitReport.objects.count()}")
    print(f"   - Informes de proveedores: {SupplierReport.objects.count()}")
    print(f"   - Reportes de laboratorio: {LabReport.objects.count()}")

if __name__ == '__main__':
    create_sample_documents()
