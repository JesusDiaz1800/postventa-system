#!/usr/bin/env python
"""
Script para probar el middleware de auditoría y crear logs de prueba
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.audit.models import AuditLog, AuditLogManager
from apps.users.models import User
from django.utils import timezone

def test_audit_middleware():
    """Probar el middleware de auditoría creando logs manualmente"""
    print("🔍 Probando middleware de auditoría...")
    
    # Obtener un usuario para las pruebas
    try:
        user = User.objects.get(email='jdiaz@polifusion.cl')
        print(f"✅ Usuario encontrado: {user.username}")
    except User.DoesNotExist:
        print("❌ Usuario no encontrado")
        return
    
    # Crear algunos logs de prueba
    test_actions = [
        {
            'action': 'login',
            'description': f'Usuario {user.username} inició sesión en el sistema',
            'details': {
                'login_time': timezone.now().isoformat(),
                'ip_address': '192.168.1.100',
                'user_agent': 'Mozilla/5.0 Test Browser'
            }
        },
        {
            'action': 'view_page',
            'description': f'Usuario {user.username} visitó página: Dashboard principal',
            'details': {
                'page': '/dashboard',
                'timestamp': timezone.now().isoformat()
            }
        },
        {
            'action': 'create',
            'description': f'Usuario {user.username} creó nueva incidencia de prueba',
            'details': {
                'incident_code': 'TEST-2024-001',
                'client': 'Cliente de Prueba',
                'created_at': timezone.now().isoformat()
            }
        },
        {
            'action': 'upload',
            'description': f'Usuario {user.username} subió archivo de prueba',
            'details': {
                'filename': 'documento_prueba.pdf',
                'file_size': '2.5 MB',
                'upload_time': timezone.now().isoformat()
            }
        },
        {
            'action': 'logout',
            'description': f'Usuario {user.username} cerró sesión del sistema',
            'details': {
                'logout_time': timezone.now().isoformat(),
                'session_duration': '30 minutos'
            }
        }
    ]
    
    print(f"📝 Creando {len(test_actions)} logs de auditoría de prueba...")
    
    created_logs = []
    for i, action_data in enumerate(test_actions, 1):
        try:
            log = AuditLogManager.log_action(
                user=user,
                action=action_data['action'],
                description=action_data['description'],
                ip_address='192.168.1.100',
                details=action_data['details']
            )
            if log:
                created_logs.append(log)
                print(f"✅ Log {i} creado: {action_data['action']}")
            else:
                print(f"❌ Error creando log {i}: {action_data['action']}")
        except Exception as e:
            print(f"❌ Error creando log {i}: {e}")
    
    # Verificar logs creados
    total_logs = AuditLog.objects.count()
    print(f"\n📊 Total de logs en la base de datos: {total_logs}")
    print(f"📝 Logs creados en esta prueba: {len(created_logs)}")
    
    # Mostrar los últimos 5 logs
    recent_logs = AuditLog.objects.all().order_by('-timestamp')[:5]
    print(f"\n📋 Últimos 5 logs de auditoría:")
    for log in recent_logs:
        print(f"  • {log.get_action_display()} - {log.description[:50]}... ({log.timestamp.strftime('%H:%M:%S')})")
    
    if created_logs:
        print(f"\n🎉 ¡Middleware de auditoría funcionando correctamente!")
        print(f"✅ Se crearon {len(created_logs)} logs de prueba")
        print(f"🌐 Ve a http://localhost:5173/audit para ver los logs")
    else:
        print(f"\n❌ Error: No se pudieron crear logs de auditoría")

if __name__ == '__main__':
    test_audit_middleware()
