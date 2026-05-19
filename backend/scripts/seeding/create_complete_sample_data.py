#!/usr/bin/env python3
"""
Script para crear datos de ejemplo completos con incidencias y reportes
"""
import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

from django.contrib.auth import get_user_model
from apps.incidents.models import Incident
from apps.documents.models import VisitReport, LabReport, SupplierReport
from django.utils import timezone
from datetime import datetime, timedelta
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

User = get_user_model()

def create_complete_sample_data():
    """Crear datos de ejemplo completos"""
    
    # Obtener o crear usuario admin
    admin_user, created = User.objects.get_or_create(
        username='jdiaz',
        defaults={
            'email': 'jdiaz@polifusion.com',
            'first_name': 'Jesús',
            'last_name': 'Díaz',
            'role': 'admin',
            'is_active': True,
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        logger.info("Usuario admin creado")
    else:
        logger.info("Usuario admin ya existe")

    # Crear incidencia de ejemplo
    incident_data = {
        'code': 'INC-2025-001',
        'cliente': 'Empresa Constructora ABC',
        'provider': 'Polifusion',
        'obra': 'Proyecto Residencial Los Pinos',
        'sku': 'TUB-PVC-110-6M',
        'lote': 'LOTE-2025-001',
        'fecha_reporte': timezone.now() - timedelta(days=5),
        'fecha_deteccion': (timezone.now() - timedelta(days=5)).date(),
        'hora_deteccion': (timezone.now() - timedelta(days=5)).time(),
        'descripcion': 'Fisuras longitudinales en tuberías PVC de 110mm, diámetro 6 metros. Las fisuras aparecen principalmente en las uniones y se extienden aproximadamente 20-30cm a lo largo de la tubería.',
        'acciones_inmediatas': 'Revisión técnica completa y reemplazo de unidades afectadas',
        'prioridad': 'alta',
        'estado': 'abierto',
        'created_by': admin_user,
        'assigned_to': admin_user
    }
    
    incident, created = Incident.objects.get_or_create(
        code=incident_data['code'],
        defaults=incident_data
    )
    
    if created:
        logger.info(f"Incidencia creada: {incident.code}")
    else:
        logger.info(f"Incidencia ya existe: {incident.code}")

    # Crear reporte de visita
    visit_report_data = {
        'related_incident': incident,
        'report_number': 'VR-2025-001',
        'order_number': 'ORD-2025-001',
        'visit_date': timezone.now() - timedelta(days=3),
        'project_name': 'Proyecto Residencial Los Pinos',
        'client_name': 'Empresa Constructora ABC',
        'address': 'Av. Principal 123, Los Pinos',
        'salesperson': 'María González',
        'technician': 'Carlos Mendoza',
        'commune': 'Las Condes',
        'city': 'Santiago',
        'visit_reason': 'Inspección de fisuras en tuberías',
        'general_observations': 'Se realizó inspección visual completa de las tuberías afectadas. Se identificaron fisuras longitudinales en 12 unidades del lote LOTE-2025-001.',
        'pdf_path': 'visit_reports/VR-2025-001.pdf',
        'created_by': admin_user
    }
    
    visit_report, created = VisitReport.objects.get_or_create(
        related_incident=incident,
        report_number=visit_report_data['report_number'],
        defaults=visit_report_data
    )
    
    if created:
        logger.info(f"Reporte de visita creado: {visit_report.report_number}")
    else:
        logger.info(f"Reporte de visita ya existe: {visit_report.report_number}")

    # Crear informe de laboratorio
    lab_report_data = {
        'related_incident': incident,
        'related_visit_report': visit_report,
        'report_number': 'LR-2025-001',
        'request_date': timezone.now() - timedelta(days=2),
        'applicant': 'POLIFUSION',
        'client': 'Empresa Constructora ABC',
        'description': 'Fisuras longitudinales en tuberías PVC 110mm del lote LOTE-2025-001',
        'pdf_path': 'lab_reports/LR-2025-001.pdf',
        'created_by': admin_user
    }
    
    lab_report, created = LabReport.objects.get_or_create(
        related_incident=incident,
        report_number=lab_report_data['report_number'],
        defaults=lab_report_data
    )
    
    if created:
        logger.info(f"Informe de laboratorio creado: {lab_report.report_number}")
    else:
        logger.info(f"Informe de laboratorio ya existe: {lab_report.report_number}")

    # Crear informe para proveedor
    supplier_report_data = {
        'related_incident': incident,
        'related_lab_report': lab_report,
        'report_number': 'SR-2025-001',
        'supplier_name': 'Tubos y Accesorios del Norte S.A.',
        'supplier_contact': 'Ing. Roberto Silva',
        'supplier_email': 'r.silva@tubosnorte.com',
        'report_date': timezone.now() - timedelta(days=1),
        'subject': 'Fisuras en tuberías PVC - Lote LOTE-2025-001',
        'introduction': 'Mediante el presente informe, comunicamos los resultados del análisis técnico realizado a las tuberías PVC afectadas.',
        'problem_description': 'Fisuras longitudinales en tuberías PVC 110mm del lote LOTE-2025-001. Análisis de laboratorio confirma que el material no cumple con especificaciones técnicas.',
        'technical_analysis': 'Las pruebas de laboratorio revelan resistencia a la tracción de 45.2 MPa vs. 52.0 MPa especificado.',
        'recommendations': 'Reemplazo inmediato de todas las unidades del lote LOTE-2025-001.',
        'pdf_path': 'supplier_reports/SR-2025-001.pdf',
        'created_by': admin_user
    }
    
    supplier_report, created = SupplierReport.objects.get_or_create(
        related_incident=incident,
        report_number=supplier_report_data['report_number'],
        defaults=supplier_report_data
    )
    
    if created:
        logger.info(f"Informe para proveedor creado: {supplier_report.report_number}")
    else:
        logger.info(f"Informe para proveedor ya existe: {supplier_report.report_number}")

    # Crear carpetas para PDFs si no existen
    pdf_dirs = [
        'media/visit_reports',
        'media/lab_reports', 
        'media/supplier_reports',
        'media/shared_documents'
    ]
    
    for pdf_dir in pdf_dirs:
        os.makedirs(pdf_dir, exist_ok=True)
        logger.info(f"Directorio creado/verificado: {pdf_dir}")

    logger.info("=== DATOS DE EJEMPLO COMPLETOS CREADOS ===")
    logger.info(f"Incidencia: {incident.code}")
    logger.info(f"Reporte de Visita: {visit_report.report_number}")
    logger.info(f"Informe de Laboratorio: {lab_report.report_number}")
    logger.info(f"Informe para Proveedor: {supplier_report.report_number}")
    logger.info("Todos los reportes tienen rutas de PDF configuradas")

if __name__ == '__main__':
    create_complete_sample_data()
