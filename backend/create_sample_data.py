#!/usr/bin/env python3
"""
Script para crear datos de muestra con PDFs reales
"""
import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

from apps.incidents.models import Incident
from apps.documents.models import VisitReport, LabReport, SupplierReport
from apps.users.models import User
from django.utils import timezone
import shutil
from pathlib import Path

def create_sample_data():
    """Crear datos de muestra con PDFs reales"""
    
    print("🧹 Limpiando datos existentes...")
    
    # Eliminar reportes existentes
    VisitReport.objects.all().delete()
    LabReport.objects.all().delete()
    SupplierReport.objects.all().delete()
    
    # Eliminar incidencias existentes
    Incident.objects.all().delete()
    
    print("✅ Datos limpiados")
    
    # Obtener usuario admin
    try:
        admin_user = User.objects.filter(role='admin').first()
        if not admin_user:
            admin_user = User.objects.create_user(
                username='admin',
                email='admin@polifusion.cl',
                password='admin123',
                first_name='Admin',
                last_name='User',
                role='admin'
            )
    except Exception as e:
        print(f"❌ Error creando usuario admin: {e}")
        return
    
    print("📋 Creando incidencias de muestra...")
    
    # Crear incidencias de muestra
    incidents_data = [
        {
            'code': 'INC-2025-0001',
            'provider': 'Polifusion S.A.',
            'obra': 'Edificio Residencial Las Flores',
            'cliente': 'Constructora ABC S.A.',
            'sku': 'TUB-001',
            'lote': 'L2025001',
            'fecha_deteccion': timezone.now().date(),
            'hora_deteccion': timezone.now().time(),
            'descripcion': 'Fuga en tubería principal de agua potable en el sótano del edificio',
            'categoria': 'tuberia',
            'subcategoria': 'fuga',
            'prioridad': 'alta',
            'estado': 'abierto',
            'created_by': admin_user
        },
        {
            'code': 'INC-2025-0002',
            'provider': 'Tuberías del Norte S.A.',
            'obra': 'Proyecto Industrial Sur',
            'cliente': 'Empresa XYZ',
            'sku': 'ACC-002',
            'lote': 'L2025002',
            'fecha_deteccion': timezone.now().date(),
            'hora_deteccion': timezone.now().time(),
            'descripcion': 'Falla en accesorio de conexión',
            'categoria': 'accesorio_plastico',
            'subcategoria': 'conexion',
            'prioridad': 'media',
            'estado': 'abierto',
            'created_by': admin_user
        },
        {
            'code': 'INC-2025-0003',
            'provider': 'Materiales del Sur',
            'obra': 'Centro Comercial Plaza Norte',
            'cliente': 'Desarrolladora Norte',
            'sku': 'LLV-003',
            'lote': 'L2025003',
            'fecha_deteccion': timezone.now().date(),
            'hora_deteccion': timezone.now().time(),
            'descripcion': 'Defecto en llave de paso principal',
            'categoria': 'llave',
            'subcategoria': 'defecto',
            'prioridad': 'baja',
            'estado': 'abierto',
            'created_by': admin_user
        }
    ]
    
    incidents = []
    for data in incidents_data:
        incident = Incident.objects.create(**data)
        incidents.append(incident)
        print(f"✅ Creada incidencia: {incident.code}")
    
    print("📄 Creando reportes de muestra...")
    
    # Crear reportes de visita
    visit_reports_data = [
        {
            'report_number': 'VR-2025-0001',
            'visit_date': timezone.now().date(),
            'client_name': 'Constructora ABC S.A.',
            'project_name': 'Edificio Residencial Las Flores',
            'technician': 'Juan Pérez',
            'visit_reason': 'Inspección de fuga',
            'general_observations': 'Se detectó fuga en tubería principal. Se requiere reemplazo inmediato.',
            'related_incident': incidents[0],
            'status': 'completed'
        }
    ]
    
    for data in visit_reports_data:
        report = VisitReport.objects.create(**data)
        print(f"✅ Creado reporte de visita: {report.report_number}")
    
    # Crear reportes de laboratorio
    lab_reports_data = [
        {
            'report_number': 'LR-2025-0001',
            'form_number': 'FORM-001',
            'request_date': timezone.now().date(),
            'applicant': 'Juan Pérez',
            'client': 'Constructora ABC S.A.',
            'description': 'Análisis de calidad de tubería',
            'project_background': 'Verificación de calidad post-instalación',
            'tests_performed': {
                'presion': '15 bar',
                'temperatura': '20°C',
                'duracion': '24 horas'
            },
            'comments': 'Tubería cumple con especificaciones técnicas',
            'conclusions': 'Producto apto para uso',
            'recommendations': 'Mantenimiento preventivo cada 6 meses',
            'status': 'completed',
            'related_incident': incidents[0]
        },
        {
            'report_number': 'LR-2025-0002',
            'form_number': 'FORM-002',
            'request_date': timezone.now().date(),
            'applicant': 'María González',
            'client': 'Empresa XYZ',
            'description': 'Análisis interno de accesorio',
            'project_background': 'Control de calidad interno',
            'tests_performed': {
                'resistencia': 'Excelente',
                'durabilidad': 'Aprobada',
                'certificacion': 'ISO 9001'
            },
            'comments': 'Accesorio presenta defecto de fabricación',
            'conclusions': 'Producto no cumple estándares',
            'recommendations': 'Rechazar lote completo',
            'status': 'completed',
            'related_incident': incidents[1]
        }
    ]
    
    for data in lab_reports_data:
        report = LabReport.objects.create(**data)
        print(f"✅ Creado reporte de laboratorio: {report.report_number}")
    
    # Crear reportes de proveedores
    supplier_reports_data = [
        {
            'report_number': 'SP-2025-0001',
            'supplier_name': 'Tuberías del Norte S.A.',
            'supplier_contact': 'Juan Pérez',
            'supplier_email': 'juan.perez@tuberiasnorte.cl',
            'subject': 'Evaluación de proveedor por falla en producto',
            'introduction': 'Se ha identificado una falla en el producto suministrado.',
            'problem_description': 'El accesorio presenta defectos de fabricación que afectan su funcionalidad.',
            'technical_analysis': 'Análisis técnico revela fallas en el proceso de fabricación.',
            'recommendations': 'Se requiere mejora en control de calidad y revisión de procesos.',
            'expected_improvements': 'Implementar controles de calidad más estrictos.',
            'status': 'sent',
            'related_incident': incidents[1]
        }
    ]
    
    for data in supplier_reports_data:
        report = SupplierReport.objects.create(**data)
        print(f"✅ Creado reporte de proveedor: {report.report_number}")
    
    print("📁 Creando estructura de carpetas y PDFs de muestra...")
    
    # Crear estructura de carpetas
    base_path = Path("Y:/CONTROL DE CALIDAD/postventa")
    
    folders = [
        'visit_report/incident_1',
        'visit_report/incident_2', 
        'visit_report/incident_3',
        'lab_report/incident_1',
        'lab_report/incident_2',
        'lab_report/incident_3',
        'supplier_report/incident_1',
        'supplier_report/incident_2',
        'supplier_report/incident_3'
    ]
    
    for folder in folders:
        folder_path = base_path / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Creada carpeta: {folder_path}")
    
    print("📄 Creando PDFs de muestra...")
    
    # Crear PDFs de muestra (archivos de texto como placeholder)
    sample_pdfs = [
        'visit_report/incident_1/VR-2025-0001_Reporte_Visita.pdf',
        'lab_report/incident_1/LR-2025-0001_Informe_Cliente.pdf',
        'lab_report/incident_2/LR-2025-0002_Informe_Interno.pdf',
        'supplier_report/incident_2/SP-2025-0001_Evaluacion_Proveedor.pdf'
    ]
    
    for pdf_path in sample_pdfs:
        full_path = base_path / pdf_path
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(f"PDF de muestra: {pdf_path}\n")
            f.write("Este es un archivo PDF de ejemplo para demostración.\n")
            f.write("En un entorno real, aquí estaría el contenido del reporte.\n")
        print(f"✅ Creado PDF: {full_path}")
    
    print("\n🎉 ¡Datos de muestra creados exitosamente!")
    print("📊 Resumen:")
    print(f"   - Incidencias: {Incident.objects.count()}")
    print(f"   - Reportes de visita: {VisitReport.objects.count()}")
    print(f"   - Reportes de laboratorio: {LabReport.objects.count()}")
    print(f"   - Reportes de proveedores: {SupplierReport.objects.count()}")
    print(f"   - PDFs de muestra: {len(sample_pdfs)}")

if __name__ == '__main__':
    create_sample_data()
