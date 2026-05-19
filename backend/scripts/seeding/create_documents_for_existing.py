#!/usr/bin/env python
"""
Script para crear documentos e imágenes para incidencias existentes
"""
import os
import sys
import django
from datetime import datetime, date, time, timedelta
import random

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

from apps.incidents.models import Incident, IncidentImage
from apps.users.models import User
from apps.documents.models import VisitReport, LabReport, SupplierReport, QualityReport

def create_documents_for_existing_incidents():
    """Crear documentos para incidencias existentes"""
    print("🔧 Creando documentos para incidencias existentes...")
    
    try:
        # Obtener incidencias existentes
        incidents = Incident.objects.filter(estado='abierto')[:3]
        
        if not incidents:
            print("❌ No hay incidencias abiertas para crear documentos")
            return False
        
        created_documents = []
        
        for i, incident in enumerate(incidents):
            print(f"📋 Procesando incidencia: {incident.code}")
            
            # Crear reporte de visita
            try:
                visit_report = VisitReport.objects.create(
                    related_incident=incident,
                    visit_date=date.today() - timedelta(days=random.randint(1, 3)),
                    order_number=f'OV-2025{str(i+1).zfill(3)}',
                    project_name=incident.obra,
                    client_name=incident.cliente,
                    address=incident.direccion_cliente or 'Dirección no especificada',
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
                
            except Exception as e:
                print(f"❌ Error creando reporte de visita: {str(e)}")
            
            # Crear reporte de calidad (cliente)
            try:
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
                
            except Exception as e:
                print(f"❌ Error creando reporte de calidad (cliente): {str(e)}")
            
            # Crear reporte de calidad (interno)
            try:
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
                
            except Exception as e:
                print(f"❌ Error creando reporte de calidad (interno): {str(e)}")
        
        print(f"\n📊 Total de documentos creados: {len(created_documents)}")
        return created_documents
        
    except Exception as e:
        print(f"❌ Error creando documentos: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def create_images_for_existing_incidents():
    """Crear imágenes para incidencias existentes"""
    print("\n🔧 Creando imágenes para incidencias existentes...")
    
    try:
        incidents = Incident.objects.filter(estado='abierto')[:3]
        
        if not incidents:
            print("❌ No hay incidencias abiertas para crear imágenes")
            return False
        
        created_images = []
        
        for incident in incidents:
            print(f"📋 Procesando incidencia: {incident.code}")
            
            # Crear 2-3 imágenes por incidencia
            for i in range(random.randint(2, 3)):
                try:
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
                    
                except Exception as e:
                    print(f"❌ Error creando imagen {i+1}: {str(e)}")
        
        print(f"\n📊 Total de imágenes creadas: {len(created_images)}")
        return created_images
        
    except Exception as e:
        print(f"❌ Error creando imágenes: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def update_incident_counts():
    """Actualizar contadores de imágenes y documentos en las incidencias"""
    print("\n🔧 Actualizando contadores de incidencias...")
    
    try:
        incidents = Incident.objects.all()
        
        for incident in incidents:
            # Contar imágenes
            images_count = incident.images.count()
            
            # Contar documentos
            documents_count = (
                incident.documents_visit_reports.count() +
                incident.quality_reports.count() +
                incident.lab_reports.count() +
                incident.supplier_reports.count()
            )
            
            # Actualizar la incidencia (si los campos existen)
            if hasattr(incident, 'images_count'):
                incident.images_count = images_count
            if hasattr(incident, 'documents_count'):
                incident.documents_count = documents_count
            
            incident.save()
            
            print(f"✅ {incident.code}: {images_count} imágenes, {documents_count} documentos")
        
        return True
        
    except Exception as e:
        print(f"❌ Error actualizando contadores: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando creación de documentos e imágenes...")
    
    # Crear documentos
    documents = create_documents_for_existing_incidents()
    
    # Crear imágenes
    images = create_images_for_existing_incidents()
    
    # Actualizar contadores
    update_incident_counts()
    
    print("\n📊 RESUMEN FINAL:")
    print(f"✅ Documentos creados: {len(documents) if documents else 0}")
    print(f"✅ Imágenes creadas: {len(images) if images else 0}")
    
    print("\n🎉 ¡Datos de prueba completados!")
    print("Ahora puedes probar todas las funcionalidades:")
    print("- Ver incidencias con contadores actualizados")
    print("- Ver detalles con imágenes y documentos")
    print("- Crear reportes desde las páginas correspondientes")
    print("- Probar reabrir incidencias cerradas")
    print("- Probar eliminar incidencias")
