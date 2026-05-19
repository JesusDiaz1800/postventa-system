#!/usr/bin/env python3
"""
Script para crear documentos de ejemplo realistas para probar las funcionalidades
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from apps.incidents.models import Incident
from apps.documents.models import VisitReport, SupplierReport, LabReport
from apps.documents.services.pdf_generator import ProfessionalPDFGenerator
from django.contrib.auth.models import User

def create_sample_documents():
    """Crear documentos de ejemplo realistas"""
    
    print("🚀 Creando documentos de ejemplo realistas...")
    
    # Obtener incidencias existentes
    incidents = Incident.objects.filter(estado='abierto')[:5]
    
    if not incidents.exists():
        print("❌ No hay incidencias abiertas. Creando algunas...")
        # Crear incidencias de ejemplo
        incidents_data = [
            {
                'code': 'INC-2024-001',
                'cliente': 'Empresa Constructora ABC',
                'provider': 'Proveedor XYZ',
                'description': 'Problema con material de construcción',
                'estado': 'abierto',
                'priority': 'alta'
            },
            {
                'code': 'INC-2024-002', 
                'cliente': 'Inmobiliaria DEF',
                'provider': 'Proveedor ABC',
                'description': 'Defecto en acabados',
                'estado': 'abierto',
                'priority': 'media'
            },
            {
                'code': 'INC-2024-003',
                'cliente': 'Constructora GHI',
                'provider': 'Proveedor DEF',
                'description': 'Problema con instalaciones eléctricas',
                'estado': 'abierto',
                'priority': 'alta'
            }
        ]
        
        for data in incidents_data:
            incident, created = Incident.objects.get_or_create(
                code=data['code'],
                defaults=data
            )
            if created:
                print(f"✅ Creada incidencia: {incident.code}")
        
        incidents = Incident.objects.filter(estado='abierto')
    
    # Datos realistas para reportes
    visit_reports_data = [
        {
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
        },
        {
            'order_number': 'ORD-2024-002',
            'project_name': 'Centro Comercial Plaza Norte',
            'client_name': 'Inmobiliaria DEF',
            'address': 'Av. Norte 456, Santiago',
            'salesperson': 'María González',
            'technician': 'Ana Silva',
            'commune': 'Providencia',
            'city': 'Santiago',
            'visit_reason': 'Evaluación de acabados',
            'general_observations': 'Los acabados presentan irregularidades que requieren corrección antes de la entrega.',
            'status': 'draft'
        }
    ]
    
    supplier_reports_data = [
        {
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
        },
        {
            'report_date': datetime.now().strftime('%Y-%m-%d'),
            'supplier_name': 'Proveedor ABC',
            'supplier_contact': 'Laura Fernández',
            'supplier_email': 'laura@proveedorabc.cl',
            'subject': 'Defectos en acabados',
            'introduction': 'Se reportan defectos en los acabados suministrados.',
            'problem_description': 'Los acabados no presentan la calidad esperada.',
            'technical_analysis': 'Inspección visual revela irregularidades en el acabado.',
            'recommendations': 'Se requiere corrección de los acabados defectuosos.',
            'expected_improvements': 'Mejora en la calidad de los acabados.',
            'status': 'draft'
        }
    ]
    
    lab_reports_data = [
        {
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
        },
        {
            'form_number': 'LAB-2024-002',
            'request_date': datetime.now().strftime('%Y-%m-%d'),
            'applicant': 'María González',
            'client': 'Inmobiliaria DEF',
            'description': 'Evaluación de acabados',
            'project_background': 'Proyecto comercial',
            'tests_performed': 'Inspección visual, medición de espesores, prueba de adherencia',
            'comments': 'Se detectaron irregularidades en el acabado',
            'conclusions': 'Los acabados requieren corrección',
            'recommendations': 'Se recomienda rehacer los acabados defectuosos',
            'report_type': 'interno',
            'status': 'draft'
        }
    ]
    
    # Crear reportes de visita
    print("📋 Creando reportes de visita...")
    for i, incident in enumerate(incidents[:2]):
        if i < len(visit_reports_data):
            report_data = visit_reports_data[i]
            report_data['related_incident'] = incident
            
            visit_report, created = VisitReport.objects.get_or_create(
                related_incident=incident,
                defaults=report_data
            )
            
            if created:
                print(f"✅ Creado reporte de visita: {visit_report.order_number}")
                
                # Generar PDF
                try:
                    pdf_generator = ProfessionalPDFGenerator()
                    pdf_path = pdf_generator.generate_visit_report_pdf(visit_report)
                    print(f"📄 PDF generado: {pdf_path}")
                except Exception as e:
                    print(f"❌ Error generando PDF: {e}")
    
    # Crear informes de proveedores
    print("📋 Creando informes de proveedores...")
    for i, incident in enumerate(incidents[:2]):
        if i < len(supplier_reports_data):
            report_data = supplier_reports_data[i]
            report_data['related_incident'] = incident
            
            supplier_report, created = SupplierReport.objects.get_or_create(
                related_incident=incident,
                defaults=report_data
            )
            
            if created:
                print(f"✅ Creado informe de proveedor: {supplier_report.report_number}")
                
                # Generar PDF
                try:
                    pdf_generator = ProfessionalPDFGenerator()
                    pdf_path = pdf_generator.generate_supplier_report_pdf(supplier_report)
                    print(f"📄 PDF generado: {pdf_path}")
                except Exception as e:
                    print(f"❌ Error generando PDF: {e}")
    
    # Crear reportes de laboratorio
    print("📋 Creando reportes de laboratorio...")
    for i, incident in enumerate(incidents[:2]):
        if i < len(lab_reports_data):
            report_data = lab_reports_data[i]
            report_data['related_incident'] = incident
            
            lab_report, created = LabReport.objects.get_or_create(
                related_incident=incident,
                defaults=report_data
            )
            
            if created:
                print(f"✅ Creado reporte de laboratorio: {lab_report.form_number}")
                
                # Generar PDF
                try:
                    pdf_generator = ProfessionalPDFGenerator()
                    pdf_path = pdf_generator.generate_lab_report_pdf(lab_report)
                    print(f"📄 PDF generado: {pdf_path}")
                except Exception as e:
                    print(f"❌ Error generando PDF: {e}")
    
    print("🎉 Documentos de ejemplo creados exitosamente!")
    print(f"📊 Resumen:")
    print(f"   - Incidencias: {Incident.objects.filter(estado='abierto').count()}")
    print(f"   - Reportes de visita: {VisitReport.objects.count()}")
    print(f"   - Informes de proveedores: {SupplierReport.objects.count()}")
    print(f"   - Reportes de laboratorio: {LabReport.objects.count()}")

if __name__ == '__main__':
    create_sample_documents()