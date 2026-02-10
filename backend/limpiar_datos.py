import os
import django
import sys

# Configurar entorno Django
backend_path = os.path.join(os.getcwd(), 'backend')
if os.path.exists(backend_path):
    os.chdir(backend_path)
    sys.path.append(backend_path)
else:
    # Si ya estamos en backend o similar (ejecución directa)
    sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.incidents.models import Incident
from apps.documents.models import VisitReport, QualityReport, SupplierReport
from apps.notifications.models import Notification
from apps.audit.models import AuditLog

def limpiar_datos():
    print("INICIANDO LIMPIEZA DE DATOS DE PRUEBA...")
    print("----------------------------------------")

    # 1. Eliminar Notificaciones (Suelen estar ligadas a objetos)
    count_notif, _ = Notification.objects.all().delete()
    print(f"Eliminadas {count_notif} notificaciones.")

    # 2. Eliminar Reportes (Documentos)
    count_visit, _ = VisitReport.objects.all().delete()
    print(f"Eliminados {count_visit} reportes de visita.")

    count_qual, _ = QualityReport.objects.all().delete()
    print(f"Eliminados {count_qual} reportes de calidad.")

    count_supp, _ = SupplierReport.objects.all().delete()
    print(f"Eliminados {count_supp} reportes de proveedor.")

    # 3. Eliminar Incidencias (Cascada principal)
    count_inc, _ = Incident.objects.all().delete()
    print(f"Eliminadas {count_inc} incidencias.")

    # 4. Eliminar Auditoría (Opcional, pero recomendado para prod limpio)
    count_audit, _ = AuditLog.objects.all().delete()
    print(f"Eliminados {count_audit} registros de auditoría.")

    print("----------------------------------------")
    print("¡LIMPIEZA COMPLETADA! El sistema está listo para carga real.")

if __name__ == '__main__':
    try:
        limpiar_datos()
    except Exception as e:
        print(f"Error durante la limpieza: {e}")
