#!/usr/bin/env python
"""
Script para migrar a modelo de auditoría simplificado y crear datos de prueba en español
"""
import os
import sys
import django
from datetime import datetime, timedelta
import random

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.users.models import User
from apps.audit.models import AuditLog, AuditLogManager

def migrate_to_simple_audit():
    """Migrar a modelo de auditoría simplificado y crear datos de prueba"""
    print("🔧 Migrando a modelo de auditoría simplificado...")
    
    # Obtener usuario admin
    try:
        admin_user = User.objects.get(email="jdiaz@polifusion.cl")
    except User.DoesNotExist:
        print("❌ Usuario admin no encontrado. Ejecuta primero init_data_fix.py")
        return
    
    # Limpiar logs existentes si los hay
    AuditLog.objects.all().delete()
    print("🧹 Logs de auditoría anteriores eliminados")
    
    # Crear logs de prueba en español
    audit_actions = [
        {
            'action': 'login',
            'description': 'Usuario inició sesión en el sistema',
            'details': {'browser': 'Chrome', 'os': 'Windows 10'}
        },
        {
            'action': 'crear',
            'description': 'Creó nueva incidencia INC-2024-001 para cliente Constructora ABC',
            'details': {'incident_id': '1', 'client': 'Constructora ABC'}
        },
        {
            'action': 'actualizar',
            'description': 'Actualizó estado de incidencia INC-2024-001 a "En Proceso"',
            'details': {'incident_id': '1', 'old_status': 'Nueva', 'new_status': 'En Proceso'}
        },
        {
            'action': 'subir',
            'description': 'Subió archivo "reporte_calidad.pdf" para incidencia INC-2024-001',
            'details': {'filename': 'reporte_calidad.pdf', 'size': '2.5 MB'}
        },
        {
            'action': 'escalar',
            'description': 'Escaló incidencia INC-2024-001 a departamento de calidad',
            'details': {'incident_id': '1', 'department': 'Calidad', 'reason': 'Defecto crítico detectado'}
        },
        {
            'action': 'ver',
            'description': 'Consultó reporte de calidad interno para incidencia INC-2024-001',
            'details': {'report_type': 'Calidad Interna', 'incident_id': '1'}
        },
        {
            'action': 'descargar',
            'description': 'Descargó documento "carta_proveedor.docx"',
            'details': {'filename': 'carta_proveedor.docx', 'recipient': 'Proveedor XYZ'}
        },
        {
            'action': 'aprobar',
            'description': 'Aprobó reporte de calidad para cliente Constructora ABC',
            'details': {'report_id': 'QC-2024-001', 'approver': 'Supervisor Calidad'}
        },
        {
            'action': 'cerrar',
            'description': 'Cerró incidencia INC-2024-001 como resuelta',
            'details': {'incident_id': '1', 'resolution': 'Problema solucionado por proveedor'}
        },
        {
            'action': 'exportar',
            'description': 'Exportó reporte de incidencias del mes de enero',
            'details': {'period': 'Enero 2024', 'format': 'PDF', 'records': 45}
        },
        {
            'action': 'buscar',
            'description': 'Realizó búsqueda de incidencias por cliente "Constructora ABC"',
            'details': {'search_term': 'Constructora ABC', 'results': 12}
        },
        {
            'action': 'filtrar',
            'description': 'Aplicó filtros: Estado="Cerrado", Fecha="Últimos 30 días"',
            'details': {'filters': {'status': 'Cerrado', 'date_range': '30_days'}, 'results': 8}
        },
        {
            'action': 'eliminar',
            'description': 'Eliminó imagen adjunta "foto_defecto.jpg" de incidencia INC-2024-002',
            'details': {'filename': 'foto_defecto.jpg', 'incident_id': '2', 'reason': 'Imagen duplicada'}
        },
        {
            'action': 'rechazar',
            'description': 'Rechazó propuesta de solución de proveedor para incidencia INC-2024-003',
            'details': {'incident_id': '3', 'reason': 'Solución no cumple especificaciones', 'provider': 'Suministros GHI'}
        },
        {
            'action': 'logout',
            'description': 'Usuario cerró sesión del sistema',
            'details': {'session_duration': '2h 45m'}
        }
    ]
    
    # Crear logs de auditoría con fechas distribuidas en los últimos 7 días
    created_count = 0
    for i in range(100):  # Crear 100 logs de prueba
        action_data = random.choice(audit_actions)
        
        # Crear variaciones en las descripciones
        if action_data['action'] == 'crear':
            clients = ['Constructora ABC', 'Empresa DEF', 'Proyecto JKL', 'Obra MNO', 'Cliente PQR']
            incidents = ['INC-2024-001', 'INC-2024-002', 'INC-2024-003', 'INC-2024-004', 'INC-2024-005']
            description = f"Creó nueva incidencia {random.choice(incidents)} para cliente {random.choice(clients)}"
        elif action_data['action'] == 'actualizar':
            statuses = ['Nueva', 'En Proceso', 'En Revisión', 'Pendiente', 'Escalada']
            description = f"Actualizó estado de incidencia INC-2024-00{random.randint(1,5)} de '{random.choice(statuses)}' a '{random.choice(statuses)}'"
        elif action_data['action'] == 'subir':
            files = ['reporte_calidad.pdf', 'foto_defecto.jpg', 'especificaciones.docx', 'certificado.pdf', 'carta_proveedor.docx']
            description = f"Subió archivo '{random.choice(files)}' para incidencia INC-2024-00{random.randint(1,5)}"
        else:
            description = action_data['description']
        
        # Crear log con fecha aleatoria en los últimos 7 días
        hours_ago = random.randint(0, 168)  # Últimos 7 días
        timestamp = datetime.now() - timedelta(hours=hours_ago)
        
        # Crear el registro
        audit_log = AuditLog.objects.create(
            user=admin_user if random.choice([True, False]) else None,
            action=action_data['action'],
            description=description,
            ip_address=f"192.168.1.{random.randint(100, 254)}",
            details=action_data['details'],
            timestamp=timestamp
        )
        
        # Actualizar el timestamp manualmente
        audit_log.timestamp = timestamp
        audit_log.save()
        
        created_count += 1
        
        if created_count % 20 == 0:
            print(f"✅ Creados {created_count}/100 logs de auditoría")
    
    print(f"🎉 Migración completada: {created_count} logs de auditoría creados")
    print("\n📋 Características del nuevo sistema:")
    print("  ✅ Modelo simplificado sin campos innecesarios")
    print("  ✅ Todas las acciones en español")
    print("  ✅ Descripciones claras y profesionales")
    print("  ✅ Iconos y colores para cada tipo de acción")
    print("  ✅ Filtros y búsqueda optimizados")
    print("  ✅ Paginación para mejor rendimiento")
    print("  ✅ Exportación de datos en JSON")

if __name__ == '__main__':
    try:
        migrate_to_simple_audit()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
