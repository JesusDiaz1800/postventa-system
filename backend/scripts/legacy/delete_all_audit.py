#!/usr/bin/env python
"""
Script para borrar TODOS los registros de auditoría y configurar el sistema limpio
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.audit.models import AuditLog

def delete_all_audit():
    """Borrar TODOS los registros de auditoría"""
    print("🗑️ BORRANDO TODOS LOS REGISTROS DE AUDITORÍA...")
    
    # Contar registros antes
    count_before = AuditLog.objects.count()
    print(f"📊 Registros encontrados: {count_before}")
    
    if count_before > 0:
        # Eliminar TODOS los logs
        AuditLog.objects.all().delete()
        print("✅ TODOS los registros eliminados exitosamente")
    else:
        print("ℹ️ No había registros para eliminar")
    
    # Verificar que se eliminaron
    count_after = AuditLog.objects.count()
    print(f"📊 Registros restantes: {count_after}")
    
    if count_after == 0:
        print("🎉 BASE DE DATOS DE AUDITORÍA LIMPIA")
        print("\n📋 El sistema ahora registrará SOLO:")
        print("  🔑 Login y Logout")
        print("  👁️ Páginas visitadas")
        print("  ➕ Crear incidencias")
        print("  🗑️ Eliminar incidencias")
        print("  📤 Subir archivos")
        print("  📥 Descargar archivos")
        print("  📎 Adjuntar documentos")
        print("  ⬆️ Escalar incidencias")
        print("  ✅ Cerrar incidencias")
        print("\n❌ NO registrará consultas, búsquedas ni archivos estáticos")
    else:
        print("❌ Error: Aún quedan registros")

if __name__ == '__main__':
    try:
        delete_all_audit()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
