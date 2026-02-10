from apps.documents.models import DocumentAttachment
from collections import defaultdict

print("\\n=== LIMPIANDO DUPLICADOS ===\\n")

attachments = DocumentAttachment.objects.filter(
    document_type='supplier_response', 
    document_id=20147
).order_by('filename', 'uploaded_at')

files = defaultdict(list)
for att in attachments:
    files[ att.filename].append(att)

deleted = 0
for filename, atts in files.items():
    if len(atts) > 1:
        print(f"Archivo: {filename} - {len(atts)} copias")
        keep = atts[0]
        print(f"  Manteniendo ID {keep.id} ({keep.uploaded_at})")
        for att in atts[1:]:
            print(f"  Eliminando ID {att.id} ({att.uploaded_at})")
            att.delete()
            deleted += 1

print(f"\\nEliminados: {deleted}")
print(f"Restantes: {DocumentAttachment.objects.filter(document_type='supplier_response', document_id=20147).count()}")
