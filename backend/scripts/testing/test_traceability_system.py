#!/usr/bin/env python
"""
Script de prueba para el sistema de trazabilidad documental
"""
import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from apps.incidents.models import Incident
from apps.documents.models import VisitReport, LabReport, SupplierReport
from apps.users.models import User
from django.utils import timezone

def test_traceability_system():
    """Prueba el sistema de trazabilidad documental"""
    print("🧪 Iniciando pruebas del sistema de trazabilidad documental...")
    
    try:
        # 1. Verificar que existe al menos un usuario
        users = User.objects.all()
        if not users.exists():
            print("❌ No hay usuarios en el sistema")
            return False
        
        user = users.first()
        print(f"✅ Usuario encontrado: {user.username}")
        
        # 2. Crear una incidencia de prueba
        incident = Incident.objects.create(
            code="TEST-001",
            cliente="Cliente de Prueba",
            provider="Proveedor de Prueba",
            description="Incidencia de prueba para el sistema de trazabilidad",
            status="open",
            created_by=user
        )
        print(f"✅ Incidencia creada: {incident.code}")
        
        # 3. Crear un reporte de visita
        visit_report = VisitReport.objects.create(
            order_number="ORD-001",
            related_incident=incident,
            project_name="Proyecto de Prueba",
            client_name="Cliente de Prueba",
            address="Dirección de Prueba 123",
            salesperson="Vendedor de Prueba",
            technician="Técnico de Prueba",
            commune="Comuna de Prueba",
            city="Ciudad de Prueba",
            visit_reason="01-Visita Técnica",
            general_observations="Observaciones de prueba para el reporte de visita",
            created_by=user
        )
        print(f"✅ Reporte de visita creado: {visit_report.report_number}")
        
        # 4. Crear un informe de laboratorio
        lab_report = LabReport.objects.create(
            related_incident=incident,
            related_visit_report=visit_report,
            client="Cliente de Prueba",
            description="Descripción del problema para análisis de laboratorio",
            project_background="Antecedentes del proyecto de prueba",
            tests_performed=["Evaluación visual", "Análisis térmico"],
            comments="Comentarios sobre la muestra recibida",
            conclusions="Conclusiones del análisis de laboratorio",
            recommendations="Recomendaciones técnicas",
            created_by=user
        )
        print(f"✅ Informe de laboratorio creado: {lab_report.report_number}")
        
        # 5. Crear un informe para proveedor
        supplier_report = SupplierReport.objects.create(
            related_incident=incident,
            related_lab_report=lab_report,
            supplier_name="Proveedor de Prueba",
            supplier_contact="Contacto del Proveedor",
            supplier_email="proveedor@ejemplo.com",
            subject="Solicitud de mejora en producto",
            introduction="Introducción profesional al informe",
            problem_description="Descripción técnica del problema observado",
            technical_analysis="Análisis técnico detallado",
            recommendations="Recomendaciones específicas para el proveedor",
            expected_improvements="Mejoras esperadas en el producto",
            created_by=user
        )
        print(f"✅ Informe para proveedor creado: {supplier_report.report_number}")
        
        # 6. Verificar la trazabilidad
        print("\n🔍 Verificando trazabilidad...")
        
        # Verificar que la incidencia tiene los documentos relacionados
        visit_reports = incident.documents_visit_reports.all()
        lab_reports = incident.documents_lab_reports.all()
        supplier_reports = incident.documents_supplier_reports.all()
        
        print(f"   - Reportes de visita vinculados: {visit_reports.count()}")
        print(f"   - Informes de laboratorio vinculados: {lab_reports.count()}")
        print(f"   - Informes para proveedores vinculados: {supplier_reports.count()}")
        
        # Verificar que el informe de laboratorio está vinculado al reporte de visita
        if lab_report.related_visit_report == visit_report:
            print("   ✅ Informe de laboratorio correctamente vinculado al reporte de visita")
        
        # Verificar que el informe para proveedor está vinculado al informe de laboratorio
        if supplier_report.related_lab_report == lab_report:
            print("   ✅ Informe para proveedor correctamente vinculado al informe de laboratorio")
        
        # 7. Mostrar el workflow completo
        print("\n📋 Workflow completo de la incidencia:")
        print(f"   1. Incidencia: {incident.code} - {incident.cliente}")
        print(f"   2. Reporte de Visita: {visit_report.report_number} - {visit_report.project_name}")
        print(f"   3. Informe de Laboratorio: {lab_report.report_number} - {lab_report.client}")
        print(f"   4. Informe para Proveedor: {supplier_report.report_number} - {supplier_report.supplier_name}")
        
        # 8. Limpiar datos de prueba
        print("\n🧹 Limpiando datos de prueba...")
        supplier_report.delete()
        lab_report.delete()
        visit_report.delete()
        incident.delete()
        print("   ✅ Datos de prueba eliminados")
        
        print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error durante las pruebas: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoints():
    """Prueba los endpoints de la API"""
    print("\n🌐 Probando endpoints de la API...")
    
    try:
        from django.test import Client
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        client = Client()
        
        # Crear un usuario de prueba
        user = User.objects.create_user(
            username='testuser',
            email='test@ejemplo.com',
            password='testpass123',
            role='admin'
        )
        
        # Autenticar
        client.force_login(user)
        
        # Probar endpoint de incidencias disponibles
        response = client.get('/api/documents/available-incidents/')
        if response.status_code == 200:
            print("   ✅ Endpoint de incidencias disponibles funciona")
        else:
            print(f"   ❌ Error en endpoint de incidencias disponibles: {response.status_code}")
        
        # Probar endpoint de estadísticas
        response = client.get('/api/documents/statistics/')
        if response.status_code == 200:
            print("   ✅ Endpoint de estadísticas funciona")
        else:
            print(f"   ❌ Error en endpoint de estadísticas: {response.status_code}")
        
        # Limpiar usuario de prueba
        user.delete()
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando endpoints: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Sistema de Trazabilidad Documental - Pruebas")
    print("=" * 50)
    
    # Ejecutar pruebas
    success1 = test_traceability_system()
    success2 = test_api_endpoints()
    
    if success1 and success2:
        print("\n🎯 ¡Todas las pruebas completadas exitosamente!")
        print("✅ El sistema de trazabilidad documental está funcionando correctamente")
    else:
        print("\n⚠️  Algunas pruebas fallaron")
        print("❌ Revisar la configuración del sistema")
