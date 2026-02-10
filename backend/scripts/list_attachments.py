from apps.documents.models import DocumentAttachment

atts = DocumentAttachment.objects.filter(document_type='supplier_response', document_id=20147).order_by('filename', 'uploaded_at')
print(f"\n=== Total: {atts.count()} adjuntos ===\n")
for att in atts:
    print(f"ID: {att.id:3d} | {att.filename:45s} | {att.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')}")
