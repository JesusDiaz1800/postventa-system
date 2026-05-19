#!/usr/bin/env python
"""
Script para configurar endpoints de escalamiento a proveedores desde reportes internos de calidad
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.incidents.models import Incident
from apps.audit.models import AuditLogManager

def setup_supplier_escalation():
    """Configurar sistema de escalamiento a proveedores"""
    print("🔧 Configurando escalamiento a proveedores desde reportes internos de calidad...")
    
    # Crear algunas incidencias de prueba que estén listas para escalamiento
    incidents_data = [
        {
            'code': 'INC-2024-001',
            'cliente': 'Constructora ABC',
            'provider': 'Proveedor XYZ',
            'categoria': 'Calidad',
            'subcategoria': 'Defecto de Material',
            'description': 'Material defectuoso detectado en reporte interno de calidad',
            'status': 'escalated',
            'priority': 'high',
            'escalation_date': '2024-01-15',
            'from_quality_report': True
        },
        {
            'code': 'INC-2024-002', 
            'cliente': 'Empresa DEF',
            'provider': 'Suministros GHI',
            'categoria': 'Calidad',
            'subcategoria': 'No Conformidad',
            'description': 'No conformidad detectada en inspección de calidad',
            'status': 'escalated',
            'priority': 'medium',
            'escalation_date': '2024-01-16',
            'from_quality_report': True
        },
        {
            'code': 'INC-2024-003',
            'cliente': 'Proyecto JKL',
            'provider': 'Materiales MNO',
            'categoria': 'Calidad',
            'subcategoria': 'Especificación',
            'description': 'Producto no cumple especificaciones técnicas',
            'status': 'escalated',
            'priority': 'high',
            'escalation_date': '2024-01-17',
            'from_quality_report': True
        }
    ]
    
    created_count = 0
    for incident_data in incidents_data:
        incident, created = Incident.objects.get_or_create(
            code=incident_data['code'],
            defaults={
                'cliente': incident_data['cliente'],
                'provider': incident_data['provider'],
                'categoria': incident_data['categoria'],
                'subcategoria': incident_data['subcategoria'],
                'description': incident_data['description'],
                'status': incident_data['status'],
                'priority': incident_data['priority'],
                'escalation_date': incident_data['escalation_date'],
                'from_quality_report': incident_data['from_quality_report']
            }
        )
        
        if created:
            created_count += 1
            print(f"✅ Creada incidencia: {incident.code}")
            
            # Registrar en auditoría
            AuditLogManager.log_action(
                user=None,  # Sistema
                action='create',
                resource_type='incident',
                resource_id=str(incident.id),
                description=f'Incidencia {incident.code} creada para escalamiento a proveedor',
                metadata={
                    'from_quality_report': True,
                    'ready_for_supplier': True,
                    'escalation_reason': 'Reporte interno de calidad'
                }
            )
        else:
            print(f"ℹ️ Incidencia ya existe: {incident.code}")
    
    print(f"🎉 Configuración completada: {created_count} incidencias listas para escalamiento")
    print("\n📋 Características implementadas:")
    print("  ✅ Endpoint para obtener incidencias escaladas desde calidad interna")
    print("  ✅ Filtros para incidencias listas para proveedor")
    print("  ✅ Sistema de auditoría para escalamientos")
    print("  ✅ Incidencias de prueba configuradas")

if __name__ == '__main__':
    try:
        setup_supplier_escalation()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
