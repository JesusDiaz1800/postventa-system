from django.core.management.base import BaseCommand
from apps.incidents.models import Incident
from apps.documents.models import VisitReport, SupplierReport, LabReport
from datetime import datetime

class Command(BaseCommand):
    help = 'Crear datos de ejemplo para probar las funcionalidades'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Creando documentos de ejemplo realistas...')
        
        # Crear incidencias
        incident1, created = Incident.objects.get_or_create(
            code='INC-2024-001',
            defaults={
                'cliente': 'Empresa Constructora ABC',
                'provider': 'Proveedor XYZ',
                'description': 'Problema con material de construcción',
                'estado': 'abierto',
                'priority': 'alta'
            }
        )
        
        if created:
            self.stdout.write(f'✅ Creada incidencia: {incident1.code}')
        
        incident2, created = Incident.objects.get_or_create(
            code='INC-2024-002',
            defaults={
                'cliente': 'Inmobiliaria DEF',
                'provider': 'Proveedor ABC',
                'description': 'Defecto en acabados',
                'estado': 'abierto',
                'priority': 'media'
            }
        )
        
        if created:
            self.stdout.write(f'✅ Creada incidencia: {incident2.code}')
        
        # Crear reporte de visita
        visit_report, created = VisitReport.objects.get_or_create(
            related_incident=incident1,
            defaults={
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
        )
        
        if created:
            self.stdout.write(f'✅ Creado reporte de visita: {visit_report.order_number}')
        
        # Crear informe de proveedor
        supplier_report, created = SupplierReport.objects.get_or_create(
            related_incident=incident1,
            defaults={
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
        )
        
        if created:
            self.stdout.write(f'✅ Creado informe de proveedor: {supplier_report.report_number}')
        
        # Crear reporte de laboratorio
        lab_report, created = LabReport.objects.get_or_create(
            related_incident=incident1,
            defaults={
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
        )
        
        if created:
            self.stdout.write(f'✅ Creado reporte de laboratorio: {lab_report.form_number}')
        
        self.stdout.write('🎉 Documentos de ejemplo creados exitosamente!')
        self.stdout.write(f'📊 Resumen:')
        self.stdout.write(f'   - Incidencias: {Incident.objects.filter(estado="abierto").count()}')
        self.stdout.write(f'   - Reportes de visita: {VisitReport.objects.count()}')
        self.stdout.write(f'   - Informes de proveedores: {SupplierReport.objects.count()}')
        self.stdout.write(f'   - Reportes de laboratorio: {LabReport.objects.count()}')
