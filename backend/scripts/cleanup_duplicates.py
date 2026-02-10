"""
Script para limpiar adjuntos duplicados de supplier_response para la incidencia 20147
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from apps.documents.models import DocumentAttachment
from collections import defaultdict

print("\n" + "=" * 70)
print("LIMPIEZA DE ADJUNTOS DUPLICADOS - INCIDENCIA 20147")
print("=" * 70 + "\n")

# Buscar todos los adjuntos de tipo supplier_response para incident 20147
attachments = DocumentAttachment.objects.filter(
    document_type='supplier_response',
    document_id=20147
).order_by('filename', 'uploaded_at')

print(f"Total de adjuntos encontrados: {attachments.count()}\n")

if attachments.count() == 0:
    print("✅ No hay adjuntos para limpiar")
    exit(0)

# Agrupar por nombre de archivo
files_dict = defaultdict(list)
for att in attachments:
    files_dict[att.filename].append(att)

# Mostrar duplicados
print("📋 ADJUNTOS ACTUALES:")
print("-" * 70)
duplicates_found = False

for filename, atts in files_dict.items():
    print(f"\n📄 Archivo: {filename}")
    for att in atts:
        print(f"   ID: {att.id} | Subido: {att.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if len(atts) > 1:
        duplicates_found = True
        print(f"   ⚠️  DUPLICADO - {len(atts)} copias encontradas")
        keep = atts[0]  # Mantener el más antiguo
        to_delete = atts[1:]
        print(f"   ✅ Se mantendrá: ID {keep.id}")
        print(f"   ❌ Se eliminarán: {', '.join([f'ID {a.id}' for a in to_delete])}")

print("\n" + "=" * 70)

if not duplicates_found:
    print("✅ No se encontraron duplicados")
else:
    print("\n⚠️  DUPLICADOS ENCONTRADOS")
    print("\n¿Desea eliminar los duplicados? (s/n): ", end='')
    
    # Auto-confirmar para scripting (cambiar a input() si quieres confirmación manual)
    respuesta = 's'  # Cambia a: respuesta = input().strip().lower()
    
    if respuesta == 's':
        deleted_count = 0
        for filename, atts in files_dict.items():
            if len(atts) > 1:
                to_delete = atts[1:]  # Eliminar todos excepto el primero (más antiguo)
                for att in to_delete:
                    print(f"🗑️  Eliminando: ID {att.id} - {att.filename}")
                    att.delete()
                    deleted_count += 1
        
        print(f"\n✅ Se eliminaron {deleted_count} adjuntos duplicados")
        print(f"✅ Adjuntos restantes: {DocumentAttachment.objects.filter(document_type='supplier_response', document_id=20147).count()}")
    else:
        print("❌ Operación cancelada")

print("\n" + "=" * 70)
