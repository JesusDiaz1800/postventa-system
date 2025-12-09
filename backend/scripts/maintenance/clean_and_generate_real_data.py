#!/usr/bin/env python
"""
Script para limpiar la base de datos y generar datos reales con PDFs
"""

import os
import sys
import django
import shutil
from datetime import datetime, timedelta
import random

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

print("📧 Modo desarrollo: Los emails se mostrarán en la consola")
print("✅ Django configurado correctamente")

from django.db import transaction
from apps.incidents.models import Incident, IncidentImage
from apps.documents.models import VisitReport, SupplierReport, LabReport, QualityReport
from apps.users.models import User
from apps.documents.services.ultimate_professional_pdf_generator import UltimateProfessionalPDFGenerator
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def clean_database():
    """
    Limpiar toda la base de datos de incidencias y documentos
    """
    print("🧹 Limpiando base de datos...")
    
    with transaction.atomic():
        # Eliminar todos los documentos
        VisitReport.objects.all().delete()
        SupplierReport.objects.all().delete()
        LabReport.objects.all().delete()
        QualityReport.objects.all().delete()
        print("✅ Documentos eliminados")
        
        # Eliminar imágenes de incidencias
        IncidentImage.objects.all().delete()
        print("✅ Imágenes eliminadas")
        
        # Eliminar incidencias
        Incident.objects.all().delete()
        print("✅ Incidencias eliminadas")
        
        # Limpiar carpeta de documentos compartidos
        shared_path = getattr(settings, 'SHARED_DOCUMENTS_PATH', None)
        if shared_path and os.path.exists(shared_path):
            for folder in ['visit_reports', 'supplier_reports', 'lab_reports', 'quality_reports']:
                folder_path = os.path.join(shared_path, folder)
                if os.path.exists(folder_path):
                    shutil.rmtree(folder_path)
                    print(f"✅ Carpeta {folder} limpiada")
    
    print("🎉 Base de datos limpiada completamente")

def create_real_incidents():
    """
    Crear incidencias reales con datos auténticos
    """
    print("📋 Creando incidencias reales...")
    
    # Datos reales de clientes y proyectos
    clients_data = [
        {
            'cliente': 'Constructora San José S.A.',
            'obra': 'Edificio Residencial Las Flores',
            'address': 'Av. Las Flores 1234, Las Condes',
            'commune': 'Las Condes',
            'city': 'Santiago',
            'provider': 'Polietileno Chile S.A.',
            'categoria': 'Tubería de Polietileno',
            'subcategoria': 'PE-100',
            'sku': 'PE-100-25',
            'lote': 'LOTE-2025-001',
            'prioridad': 'Alta',
            'responsable': 'Carlos Rodríguez',
            'descripcion': 'Falla en soldadura de tubería principal de 25mm. Se observa fisura en la unión soldada que puede comprometer la integridad del sistema de agua potable.'
        },
        {
            'cliente': 'Inmobiliaria Los Robles Ltda.',
            'obra': 'Condominio Residencial Los Robles',
            'address': 'Camino Los Robles 5678, La Reina',
            'commune': 'La Reina',
            'city': 'Santiago',
            'provider': 'Tubos del Sur S.A.',
            'categoria': 'Tubería de Polietileno',
            'subcategoria': 'PE-80',
            'sku': 'PE-80-20',
            'lote': 'LOTE-2025-002',
            'prioridad': 'Media',
            'responsable': 'María González',
            'descripcion': 'Defecto en espesor de pared de tubería de 20mm. Medición con calibre indica espesor inferior al especificado en norma.'
        },
        {
            'cliente': 'Constructora del Pacífico S.A.',
            'obra': 'Proyecto Habitacional Costa Azul',
            'address': 'Av. Costanera 9876, Viña del Mar',
            'commune': 'Viña del Mar',
            'city': 'Viña del Mar',
            'provider': 'Polietileno Nacional S.A.',
            'categoria': 'Tubería de Polietileno',
            'subcategoria': 'PE-100',
            'sku': 'PE-100-32',
            'lote': 'LOTE-2025-003',
            'prioridad': 'Crítica',
            'responsable': 'Juan Pérez',
            'descripcion': 'Falla crítica en tubería de 32mm. Presencia de burbujas de aire en el material que compromete la resistencia mecánica.'
        },
        {
            'cliente': 'Inmobiliaria Central S.A.',
            'obra': 'Torre Residencial Central',
            'address': 'Av. Providencia 3456, Providencia',
            'commune': 'Providencia',
            'city': 'Santiago',
            'provider': 'Tubos Premium S.A.',
            'categoria': 'Tubería de Polietileno',
            'subcategoria': 'PE-80',
            'sku': 'PE-80-25',
            'lote': 'LOTE-2025-004',
            'prioridad': 'Alta',
            'responsable': 'Ana Martínez',
            'descripcion': 'Problema de coloración irregular en tubería. Presencia de manchas oscuras que pueden indicar contaminación del material.'
        },
        {
            'cliente': 'Constructora del Norte S.A.',
            'obra': 'Complejo Habitacional Norte Verde',
            'address': 'Av. Norte 7890, Quilicura',
            'commune': 'Quilicura',
            'city': 'Santiago',
            'provider': 'Polietileno del Norte S.A.',
            'categoria': 'Tubería de Polietileno',
            'subcategoria': 'PE-100',
            'sku': 'PE-100-40',
            'lote': 'LOTE-2025-005',
            'prioridad': 'Media',
            'responsable': 'Luis Fernández',
            'descripcion': 'Defecto en acabado superficial de tubería de 40mm. Presencia de rayas longitudinales que pueden afectar el flujo.'
        }
    ]
    
    # Estados posibles
    estados = ['abierto', 'laboratorio', 'cerrado']
    
    incidents = []
    
    for i, client_data in enumerate(clients_data):
        # Generar fechas realistas
        fecha_deteccion = datetime.now() - timedelta(days=random.randint(1, 30))
        hora_deteccion = f"{random.randint(8, 17):02d}:{random.randint(0, 59):02d}"
        
        # Crear incidencia
        incident = Incident.objects.create(
            code=f"INC-2025-{i+1:04d}",
            cliente=client_data['cliente'],
            obra=client_data['obra'],
            direccion_cliente=client_data['address'],
            provider=client_data['provider'],
            categoria='tuberia_hdpe',  # Usar una categoría válida
            subcategoria=client_data['subcategoria'],
            sku=client_data['sku'],
            lote=client_data['lote'],
            prioridad=client_data['prioridad'].lower(),
            responsable='patricio_morales',  # Usar responsable válido
            descripcion=client_data['descripcion'],
            fecha_deteccion=fecha_deteccion.date(),
            hora_deteccion=hora_deteccion,
            estado=random.choice(estados)
        )
        
        incidents.append(incident)
        print(f"✅ Incidencia creada: {incident.code} - {incident.cliente}")
    
    return incidents

def create_real_documents(incidents):
    """
    Crear documentos reales con PDFs generados
    """
    print("📄 Creando documentos reales...")
    
    # Obtener usuario admin
    try:
        admin_user = User.objects.get(username='admin')
    except User.DoesNotExist:
        admin_user = User.objects.first()
    
    pdf_generator = UltimateProfessionalPDFGenerator()
    
    # Crear reportes de visita para algunas incidencias
    for i, incident in enumerate(incidents[:3]):  # Solo las primeras 3
        print(f"📋 Creando reporte de visita para {incident.code}...")
        
        # Datos del reporte
        report_data = {
            'order_number': f"OV-20250926-{i+1:03d}",
            'client_name': incident.cliente,
            'project_name': incident.obra,
            'address': incident.direccion_cliente,
            'commune': 'Las Condes',  # Valor por defecto
            'city': 'Santiago',  # Valor por defecto
            'visit_date': (datetime.now() - timedelta(days=random.randint(1, 7))).strftime('%d/%m/%Y'),
            'salesperson': 'Juan Pérez',
            'technician': 'Carlos Rodríguez',
            'product_category': incident.categoria,
            'product_subcategory': incident.subcategoria,
            'product_sku': incident.sku,
            'product_lot': incident.lote,
            'product_provider': incident.provider,
            'visit_reason': 'Inspección de calidad de materiales entregados',
            'general_observations': f'Se realizó una inspección exhaustiva de los materiales entregados para el proyecto {incident.obra}. Se verificó la calidad de las tuberías y se confirmó que cumplen con los estándares requeridos según norma NCh 2205.',
            'wall_observations': 'Las paredes presentan buen estado general, sin fisuras visibles. Se verificó la adherencia del material.',
            'matrix_observations': f'La matriz de {incident.subcategoria} muestra uniformidad en el espesor. Medición con calibre digital confirma espesor nominal.',
            'slab_observations': 'La losa presenta buen acabado superficial. No se observan defectos de superficie.',
            'storage_observations': 'Los materiales están almacenados correctamente en ambiente controlado. Temperatura y humedad dentro de rangos normales.',
            'pre_assembled_observations': 'Los elementos pre-ensamblados están en buen estado. Verificación de soldaduras sin defectos.',
            'exterior_observations': 'El exterior del edificio presenta buen acabado. No se observan problemas de estanqueidad.',
            'machine_data': {
                'machines': [
                    {
                        'machine_name': 'Extrusora Principal',
                        'start_time': '08:00',
                        'cut_time': '16:30'
                    },
                    {
                        'machine_name': 'Extrusora Secundaria',
                        'start_time': '09:15',
                        'cut_time': '17:00'
                    }
                ]
            }
        }
        
        # Crear reporte en base de datos
        visit_report = VisitReport.objects.create(
            report_number=f"RV-2025-{i+1:04d}",
            order_number=report_data['order_number'],
            related_incident=incident,
            project_name=report_data['project_name'],
            client_name=report_data['client_name'],
            address=report_data['address'],
            visit_date=datetime.now().date(),
            salesperson=report_data['salesperson'],
            technician=report_data['technician'],
            visit_reason=report_data['visit_reason'],
            general_observations=report_data['general_observations'],
            wall_observations=report_data['wall_observations'],
            matrix_observations=report_data['matrix_observations'],
            slab_observations=report_data['slab_observations'],
            storage_observations=report_data['storage_observations'],
            pre_assembled_observations=report_data['pre_assembled_observations'],
            exterior_observations=report_data['exterior_observations'],
            machine_data=report_data['machine_data'],
            status='draft',
            created_by=admin_user
        )
        
        # Generar PDF
        try:
            pdf_buffer = pdf_generator.generate_visit_report_pdf(report_data)
            
            # Guardar PDF en carpeta compartida
            shared_path = getattr(settings, 'SHARED_DOCUMENTS_PATH', None)
            if shared_path:
                incident_folder = os.path.join(shared_path, 'visit_reports', f'incident_{incident.id}')
                os.makedirs(incident_folder, exist_ok=True)
                
                pdf_path = os.path.join(incident_folder, f"{report_data['order_number']}.pdf")
                with open(pdf_path, 'wb') as f:
                    f.write(pdf_buffer.getvalue())
                
                print(f"✅ PDF generado: {pdf_path}")
            else:
                print("⚠️ SHARED_DOCUMENTS_PATH no configurada")
                
        except Exception as e:
            print(f"❌ Error generando PDF: {str(e)}")
        
        print(f"✅ Reporte de visita creado: {visit_report.report_number}")
    
    # Crear reporte de laboratorio para una incidencia
    if len(incidents) > 3:
        incident = incidents[3]
        print(f"🧪 Creando reporte de laboratorio para {incident.code}...")
        
        lab_report = LabReport.objects.create(
            report_number=f"RL-2025-0001",
            related_incident=incident,
            client=incident.cliente,
            description=incident.descripcion,
            project_background=f"Análisis de material para el proyecto {incident.obra}",
            tests_performed={
                'ensayos': [
                    {'nombre': 'Análisis químico', 'resultado': 'Aprobado'},
                    {'nombre': 'Prueba de resistencia', 'resultado': 'Aprobado'},
                    {'nombre': 'Verificación de espesor', 'resultado': 'Aprobado'}
                ]
            },
            comments='Análisis químico completo realizado. Todos los parámetros dentro de rangos normales.',
            conclusions='El material cumple con las especificaciones técnicas requeridas.',
            recommendations='Continuar con el uso del material. No se requieren acciones correctivas.',
            technical_expert_name='Dr. Ana Química',
            status='draft',
            created_by=admin_user
        )
        
        print(f"✅ Reporte de laboratorio creado: {lab_report.report_number}")
    
    # Crear reporte de proveedor para una incidencia
    if len(incidents) > 4:
        incident = incidents[4]
        print(f"🏭 Creando reporte de proveedor para {incident.code}...")
        
        supplier_report = SupplierReport.objects.create(
            report_number=f"RP-2025-0001",
            related_incident=incident,
            supplier_name=incident.provider,
            supplier_contact='Ing. Roberto Proveedor',
            supplier_email='roberto@proveedor.cl',
            subject=f'Informe de calidad - {incident.code}',
            introduction=f'Presentamos el informe de calidad correspondiente a la incidencia {incident.code} del proyecto {incident.obra}.',
            problem_description=incident.descripcion,
            technical_analysis='Análisis técnico detallado realizado por nuestro equipo de calidad.',
            recommendations='Reconocemos el defecto y ofrecemos reemplazo completo del material.',
            expected_improvements='Implementación de nuevo proceso de control de calidad.',
            status='draft',
            created_by=admin_user
        )
        
        print(f"✅ Reporte de proveedor creado: {supplier_report.report_number}")

def create_real_images(incidents):
    """
    Crear imágenes reales para las incidencias
    """
    print("📸 Creando imágenes reales...")
    
    # Crear imágenes de prueba para algunas incidencias
    for i, incident in enumerate(incidents[:2]):  # Solo las primeras 2
        for j in range(random.randint(1, 3)):  # 1-3 imágenes por incidencia
            image_name = f"imagen_{incident.code}_{j+1}.jpg"
            description = f"Imagen {j+1} de la incidencia {incident.code} - {['Vista general del defecto', 'Detalle de la falla', 'Medición con calibre'][j % 3]}"
            
            # Crear registro de imagen (sin archivo real por ahora)
            image_record = IncidentImage.objects.create(
                incident=incident,
                filename=image_name,
                path=f"/media/incident_images/{image_name}",
                file_size=1024000,  # 1MB simulado
                mime_type="image/jpeg",
                caption_ai=description,
                analysis_json={
                    'description': description,
                    'confidence': 0.85,
                    'suggested_causes': ['Defecto de fabricación', 'Manejo inadecuado']
                },
                ai_provider_used='openai',
                ai_confidence=0.85
            )
            
            print(f"✅ Imagen creada: {image_name} - {description}")

def main():
    """
    Función principal
    """
    print("🚀 Iniciando limpieza y generación de datos reales...")
    
    try:
        # Limpiar base de datos
        clean_database()
        
        # Crear incidencias reales
        incidents = create_real_incidents()
        
        # Crear documentos reales
        create_real_documents(incidents)
        
        # Crear imágenes reales
        create_real_images(incidents)
        
        print("\n🎉 ¡Datos reales generados exitosamente!")
        print(f"📊 Resumen:")
        print(f"   - Incidencias: {len(incidents)}")
        print(f"   - Reportes de visita: {VisitReport.objects.count()}")
        print(f"   - Reportes de laboratorio: {LabReport.objects.count()}")
        print(f"   - Reportes de proveedor: {SupplierReport.objects.count()}")
        print(f"   - Imágenes: {IncidentImage.objects.count()}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
