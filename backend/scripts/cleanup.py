from apps.documents.models import DocumentAttachment
from collections import defaultdict

print("\n" + "=" * 70)
print("LIMPIEZA DE ADJUNTOS DUPLICADOS - INCIDENCIA 20147")
print("=" * 70 + "\n")

# Buscar todos los adjuntos supplier_response para incident 20147
attachments = DocumentAttachment.objects.filter(
    document_type='supplier_response',
    document_id=20147
).order_by('filename', 'uploaded_at')

print(f"Total adjuntos: {attachments.count()}\n")

if attachments.count() == 0:
    print("✅ No hay adjuntos")
else:
    # Agrupar por archivo
    files_dict = defaultdict(list)
    for att in attachments:
        files_dict[att.filename].append(att)
    
    # Mostrar y eliminar duplicados
    for filename, atts in files_dict.items():
        print(f"📄 {filename}: {len(atts)} copia(s)")
        for att in atts:
            print(f"   ID: {att.id} | {att.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if len(atts) > 1:
            keep = atts[0]
            to_delete = atts[1:]
            print(f"   ✅ Manteniendo ID {keep.id}")
            for att in to_delete:
                print(f"   🗑️  BORRANDO ID {att.id}")
                att.delete()
    
    remaining = DocumentAttachment.objects.filter(document_type='supplier_response', document_id=20147).count()
    print(f"\n✅ Adjuntos finales: {remaining}")
