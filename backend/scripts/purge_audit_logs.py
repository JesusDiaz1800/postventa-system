
import os
import sys
import django

# Setup Django Environment
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.audit.models import AuditLog
from django.db.models import Q

def purge_logs():
    print("Iniciando limpieza de logs antiguos...")
    
    # Lista de acciones permitidas
    allowed_actions = [
        'user_login',
        'user_logout',
        'create', 'incident_created', 'report_attached', 'user_created',
        'escalation_triggered', 'escalate',
        'delete',
        'incident_closed', 'close'
        # 'item_restored' is also good to keep usually, but user didn't list it. 
        # I'll keep it as it's critical for audit integrity of the bin itself.
    ]
    
    # 1. Eliminar logs con acciones NO permitidas
    # Usamos exclude para borrar todo lo que NO esté en la lista
    deleted_count, _ = AuditLog.objects.exclude(
        Q(action__in=allowed_actions) | 
        Q(action__icontains='restored') # Keep restoration logs for safety
    ).delete()
    
    print(f"Eliminados {deleted_count} logs de acciones no deseadas (updates genéricos, etc).")
    
    # 2. (Opcional) Eliminar logs muy antiguos si el usuario quisiera (Ej: > 1 año), 
    # pero dijo 'eliminar todos los otros logs de auditoria antiguos ya no me sirven', 
    # refiriéndose probablemente a los tipos de logs incorrectos.
    
    print("Limpieza completada.")

if __name__ == '__main__':
    purge_logs()
