#!/usr/bin/env python
"""
Script para crear datos realistas de incidencias y documentos
"""
import os
import sys
import django
from datetime import datetime, date, time, timedelta
import random

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

from apps.incidents.models import Incident
from apps.users.models import User
from apps.documents.models import VisitReport, LabReport, SupplierReport, QualityReport

def create_realistic_incidents():
    """Crear incidencias realistas con datos completos"""
    print("🔧 Creando incidencias realistas...")
    
    try:
        # Obtener usuario admin
        user = User.objects.first()
        if not user:
            print("❌ No hay usuarios en el sistema")
            return False
        
        # Datos realistas para incidencias
        incidents_data = [
            {
                'code': 'INC-2025-0001',
                'provider': 'Polifusión S.A.',
                'obra': 'Edificio Residencial Las Flores',
                'cliente': 'Constructora ABC S.A.',
                'cliente_rut': '12.345.678-9',
                'direccion_cliente': 'Av. Las Flores 1234, Las Condes, Santiago',
                'sku': 'TUB-BETA-25',
                'lote': 'L2025001',
                'factura_num': 'FAC-001-2025',
                'pedido_num': 'PED-001-2025',
                'fecha_reporte': datetime.now() - timedelta(days=5),
                'fecha_deteccion': date.today() - timedelta(days=5),
                'hora_deteccion': time(14, 30),
                'descripcion': 'Fuga en tubería principal de agua potable en el sótano del edificio. Se observa humedad constante y goteo en la unión de la tubería de 25mm con el fitting de conexión.',
                'acciones_inmediatas': 'Se cerró la válvula principal y se aisló la zona afectada. Se colocaron contenedores para recoger el agua.',
                'categoria': 'tuberia_beta',
                'subcategoria': 'fuga',
                'prioridad': 'alta',
                'estado': 'abierto',
                'responsable': 'patricio_morales',
                'acciones_posteriores': 'Coordinar con el equipo técnico para el reemplazo de la tubería afectada.'
            },
            {
                'code': 'INC-2025-0002',
                'provider': 'Tuberías del Norte S.A.',
                'obra': 'Proyecto Industrial Sur',
                'cliente': 'Empresa XYZ',
                'cliente_rut': '98.765.432-1',
                'direccion_cliente': 'Zona Industrial Sur, Ruta 5 Sur Km 45, San Bernardo',
                'sku': 'FITTING-PPR-32',
                'lote': 'L2025002',
                'factura_num': 'FAC-002-2025',
                'pedido_num': 'PED-002-2025',
                'fecha_reporte': datetime.now() - timedelta(days=3),
                'fecha_deteccion': date.today() - timedelta(days=3),
                'hora_deteccion': time(9, 15),
                'descripcion': 'Falla en accesorio de conexión PPR de 32mm. El fitting presenta una fisura longitudinal que compromete la estanqueidad de la unión.',
                'acciones_inmediatas': 'Se desmontó el fitting defectuoso y se instaló uno de reemplazo temporal.',
                'categoria': 'fitting_ppr',
                'subcategoria': 'fisura',
                'prioridad': 'media',
                'estado': 'abierto',
                'responsable': 'marco_montenegro',
                'acciones_posteriores': 'Solicitar análisis del fitting defectuoso al laboratorio de calidad.'
            },
            {
                'code': 'INC-2025-0003',
                'provider': 'Materiales del Sur',
                'obra': 'Centro Comercial Plaza Norte',
                'cliente': 'Desarrolladora Norte',
                'cliente_rut': '11.222.333-4',
                'direccion_cliente': 'Av. Américo Vespucio 1500, Huechuraba, Santiago',
                'sku': 'LLAVE-PASO-20',
                'lote': 'L2025003',
                'factura_num': 'FAC-003-2025',
                'pedido_num': 'PED-003-2025',
                'fecha_reporte': datetime.now() - timedelta(days=2),
                'fecha_deteccion': date.today() - timedelta(days=2),
                'hora_deteccion': time(16, 45),
                'descripcion': 'Defecto en llave de paso principal de 20mm. La llave no cierra completamente, permitiendo un goteo constante.',
                'acciones_inmediatas': 'Se instaló una llave de paso de emergencia para controlar el flujo.',
                'categoria': 'llave',
                'subcategoria': 'defecto',
                'prioridad': 'baja',
                'estado': 'abierto',
                'responsable': 'patricio_morales',
                'acciones_posteriores': 'Programar reemplazo de la llave defectuosa en el próximo mantenimiento.'
            },
            {
                'code': 'INC-2025-0004',
                'provider': 'Proveedor Internacional',
                'obra': 'Complejo Habitacional Los Robles',
                'cliente': 'Inmobiliaria Los Robles',
                'cliente_rut': '22.333.444-5',
                'direccion_cliente': 'Calle Los Robles 567, Providencia, Santiago',
                'sku': 'TUB-HDPE-40',
                'lote': 'L2025004',
                'factura_num': 'FAC-004-2025',
                'pedido_num': 'PED-004-2025',
                'fecha_reporte': datetime.now() - timedelta(days=1),
                'fecha_deteccion': date.today() - timedelta(days=1),
                'hora_deteccion': time(11, 20),
                'descripcion': 'Tubería HDPE de 40mm presenta deformación en un tramo de 2 metros. La deformación afecta el flujo y puede comprometer la presión del sistema.',
                'acciones_inmediatas': 'Se marcó el tramo afectado y se redujo la presión del sistema para evitar mayores daños.',
                'categoria': 'tuberia_hdpe',
                'subcategoria': 'deformacion',
                'prioridad': 'media',
                'estado': 'abierto',
                'responsable': 'marco_montenegro',
                'acciones_posteriores': 'Coordinar con el proveedor para el análisis de la causa de la deformación.'
            },
            {
                'code': 'INC-2025-0005',
                'provider': 'Accesorios del Pacífico',
                'obra': 'Hospital Regional Norte',
                'cliente': 'Servicio de Salud Metropolitano',
                'cliente_rut': '33.444.555-6',
                'direccion_cliente': 'Av. Independencia 1234, Independencia, Santiago',
                'sku': 'FLANGE-ACERO-50',
                'lote': 'L2025005',
                'factura_num': 'FAC-005-2025',
                'pedido_num': 'PED-005-2025',
                'fecha_reporte': datetime.now() - timedelta(hours=6),
                'fecha_deteccion': date.today(),
                'hora_deteccion': time(8, 30),
                'descripcion': 'Flange de acero de 50mm presenta corrosión en la superficie de contacto. La corrosión puede comprometer la estanqueidad de la unión.',
                'acciones_inmediatas': 'Se aplicó tratamiento anticorrosivo temporal y se programó inspección detallada.',
                'categoria': 'flange',
                'subcategoria': 'corrosion',
                'prioridad': 'alta',
                'estado': 'abierto',
                'responsable': 'patricio_morales',
                'acciones_posteriores': 'Solicitar análisis químico del material para determinar la causa de la corrosión.'
            }
        ]
        
        created_incidents = []
        
        for incident_data in incidents_data:
            # Verificar si la incidencia ya existe
            if Incident.objects.filter(code=incident_data['code']).exists():
                print(f"⚠️ Incidencia {incident_data['code']} ya existe, saltando...")
                continue
            
            incident = Incident.objects.create(
                created_by=user,
                **incident_data
            )
            
            created_incidents.append(incident)
            print(f"✅ Incidencia creada: {incident.code} - {incident.cliente}")
        
        print(f"\n📊 Total de incidencias creadas: {len(created_incidents)}")
        return created_incidents
        
    except Exception as e:
        print(f"❌ Error creando incidencias: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def create_test_documents():
    """Crear documentos de prueba para las incidencias"""
    print("\n🔧 Creando documentos de prueba...")
    
    try:
        # Obtener incidencias
        incidents = Incident.objects.filter(estado='abierto')[:3]
        
        if not incidents:
            print("❌ No hay incidencias abiertas para crear documentos")
            return False
        
        created_documents = []
        
        for i, incident in enumerate(incidents):
            # Crear reporte de visita
            visit_report = VisitReport.objects.create(
                related_incident=incident,
                visit_date=date.today() - timedelta(days=random.randint(1, 3)),
                order_number=f'OV-2025{str(i+1).zfill(3)}',
                project_name=incident.obra,
                client_name=incident.cliente,
                address=incident.direccion_cliente,
                commune='Santiago',
                city='Santiago',
                visit_reason='01-Visita Técnica',
                salesperson='Juan Pérez',
                technician='Pedro Gómez',
                installer='Luis Rodríguez',
                installer_phone='+56912345678',
                construction_company=incident.cliente,
                machine_data={
                    'machines': [
                        {'machine': 'Máquina A', 'start': '08:00', 'cut': '09:00'},
                        {'machine': 'Máquina B', 'start': '09:30', 'cut': '10:30'},
                    ]
                },
                general_observations=f'Se realizó una inspección detallada de la incidencia {incident.code}. Se identificaron los puntos críticos y se documentaron las condiciones actuales.'
            )
            
            created_documents.append(visit_report)
            print(f"✅ Reporte de visita creado: {visit_report.order_number}")
            
            # Crear reporte de calidad (cliente)
            quality_report_client = QualityReport.objects.create(
                related_incident=incident,
                report_type='cliente',
                report_number=f'QR-CLI-2025{str(i+1).zfill(3)}',
                report_date=date.today() - timedelta(days=random.randint(1, 2)),
                product_category=incident.categoria,
                product_subcategory=incident.subcategoria,
                product_sku=incident.sku,
                product_lot=incident.lote,
                product_description=f'Análisis de calidad para {incident.sku} del lote {incident.lote}',
                supplier_name=incident.provider,
                inspection_date=date.today() - timedelta(days=random.randint(1, 2)),
                inspection_location='Planta de Producción',
                inspection_scope=f'Análisis de calidad según normativas aplicables para {incident.categoria}',
                inspection_criteria='ISO 15874, ASTM F2389',
                sampling_method='Muestreo aleatorio simple',
                sample_size='20 unidades',
                sample_condition='Muestras en perfecto estado, embalaje original',
                test_parameters='Dimensiones, resistencia a la presión, resistencia al impacto',
                visual_inspection='No se observaron defectos superficiales',
                dimensional_analysis='Todas las dimensiones dentro de las tolerancias especificadas',
                mechanical_tests='Resistencia a la presión: 10 bar (cumple)',
                chemical_analysis='Composición confirmada según especificaciones',
                other_tests='Prueba de elongación: 300% (cumple)',
                test_results='Todos los resultados cumplen con las especificaciones técnicas',
                non_conformities='Ninguna no conformidad detectada',
                corrective_actions='N/A',
                preventive_actions='N/A',
                conclusions=f'El lote {incident.lote} cumple con los estándares de calidad requeridos',
                recommendations='Continuar con el monitoreo de calidad en la producción',
                follow_up_responsible='Equipo de Control de Calidad'
            )
            
            created_documents.append(quality_report_client)
            print(f"✅ Reporte de calidad (cliente) creado: {quality_report_client.report_number}")
            
            # Crear reporte de calidad (interno)
            quality_report_internal = QualityReport.objects.create(
                related_incident=incident,
                report_type='interno',
                report_number=f'QR-INT-2025{str(i+1).zfill(3)}',
                report_date=date.today() - timedelta(days=random.randint(1, 2)),
                product_category=incident.categoria,
                product_subcategory=incident.subcategoria,
                product_sku=incident.sku,
                product_lot=incident.lote,
                product_description=f'Análisis interno de calidad para {incident.sku} del lote {incident.lote}',
                supplier_name=incident.provider,
                inspection_date=date.today() - timedelta(days=random.randint(1, 2)),
                inspection_location='Laboratorio Interno',
                inspection_scope=f'Análisis interno detallado para {incident.categoria}',
                inspection_criteria='Normativas internas de calidad',
                sampling_method='Muestreo dirigido',
                sample_size='10 unidades',
                sample_condition='Muestras seleccionadas para análisis detallado',
                test_parameters='Análisis completo de propiedades físicas y químicas',
                visual_inspection='Inspección detallada sin defectos aparentes',
                dimensional_analysis='Mediciones precisas dentro de tolerancias',
                mechanical_tests='Pruebas de resistencia completas',
                chemical_analysis='Análisis químico detallado',
                other_tests='Pruebas adicionales de durabilidad',
                test_results='Resultados satisfactorios en todas las pruebas',
                non_conformities='Ninguna no conformidad en análisis interno',
                corrective_actions='N/A',
                preventive_actions='Implementar controles adicionales',
                conclusions=f'Análisis interno confirma calidad del lote {incident.lote}',
                recommendations='Mantener estándares de calidad actuales',
                follow_up_responsible='Equipo de Calidad Interno'
            )
            
            created_documents.append(quality_report_internal)
            print(f"✅ Reporte de calidad (interno) creado: {quality_report_internal.report_number}")
        
        print(f"\n📊 Total de documentos creados: {len(created_documents)}")
        return created_documents
        
    except Exception as e:
        print(f"❌ Error creando documentos: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def create_test_images():
    """Crear imágenes de prueba para las incidencias"""
    print("\n🔧 Creando imágenes de prueba...")
    
    try:
        from apps.incidents.models import IncidentImage
        
        incidents = Incident.objects.filter(estado='abierto')[:3]
        
        if not incidents:
            print("❌ No hay incidencias abiertas para crear imágenes")
            return False
        
        created_images = []
        
        for incident in incidents:
            # Crear 2-3 imágenes por incidencia
            for i in range(random.randint(2, 3)):
                image = IncidentImage.objects.create(
                    incident=incident,
                    filename=f'imagen_{incident.code}_{i+1}.jpg',
                    path=f'/media/incident_images/{incident.id}/imagen_{i+1}.jpg',
                    file_size=random.randint(500000, 2000000),  # 500KB - 2MB
                    mime_type='image/jpeg',
                    uploaded_by=incident.created_by
                )
                
                created_images.append(image)
                print(f"✅ Imagen creada: {image.filename}")
        
        print(f"\n📊 Total de imágenes creadas: {len(created_images)}")
        return created_images
        
    except Exception as e:
        print(f"❌ Error creando imágenes: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    print("🚀 Iniciando creación de datos realistas...")
    
    # Crear incidencias
    incidents = create_realistic_incidents()
    
    if incidents:
        # Crear documentos
        documents = create_test_documents()
        
        # Crear imágenes
        images = create_test_images()
        
        print("\n📊 RESUMEN FINAL:")
        print(f"✅ Incidencias creadas: {len(incidents)}")
        print(f"✅ Documentos creados: {len(documents) if documents else 0}")
        print(f"✅ Imágenes creadas: {len(images) if images else 0}")
        
        print("\n🎉 ¡Datos de prueba creados exitosamente!")
        print("Ahora puedes probar todas las funcionalidades del sistema:")
        print("- Ver incidencias en la tabla")
        print("- Ver detalles de incidencias")
        print("- Editar incidencias")
        print("- Crear reportes de visita")
        print("- Crear reportes de calidad")
        print("- Reabrir incidencias cerradas")
        print("- Eliminar incidencias")
    else:
        print("❌ No se pudieron crear las incidencias")
