from apps.documents.models import DocumentAttachment
count = DocumentAttachment.objects.filter(document_type='supplier_response', document_id=20147).count()
print(f"Adjuntos actuales: {count}")
if count > 0:
    for att in DocumentAttachment.objects.filter(document_type='supplier_response', document_id=20147):
        print(f"- ID {att.id}: {att.filename}")
