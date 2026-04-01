import os
import django
import sys
import uuid
import logging
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

# Setup Django environment
sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.incidents.models import Incident, IncidentAttachment
from apps.core.thread_local import set_current_country

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_closure_attachment():
    print("=== Verificando Lógica de Adjunto en Cierre ===")
    
    # 1. Preparar un incidente de prueba (o usar uno existente)
    incident = Incident.objects.first()
    if not incident:
        print("Error: No se encontró ningún incidente para la prueba.")
        return
    
    print(f"Probando con Incidente: {incident.code} (ID: {incident.id})")
    
    # 2. Simular un archivo subido
    file_content = b"Contenido de prueba para el adjunto de cierre"
    file_name = f"test_closure_{uuid.uuid4().hex[:6]}.txt"
    uploaded_file = SimpleUploadedFile(file_name, file_content, content_type="text/plain")
    
    # 3. Datos para el cierre
    stage = 'calidad' # Estaba en el serializer como opción
    summary = "Cierre de prueba mediante script de verificación."
    
    # 4. Simular la lógica de la vista (procesamiento manual ya que no queremos levantar el servidor completo)
    try:
        set_current_country('cl') # Forzamos Chile para la ruta
        country = 'cl'
        
        # Definir rutas según la nueva lógica en views.py
        safe_filename = f"{uuid.uuid4().hex[:8]}_{file_name}"
        relative_path = f"{country}/documents/attachments/{safe_filename}"
        full_dir_path = os.path.join(settings.SHARED_DOCUMENTS_PATH, country, "documents", "attachments")
        os.makedirs(full_dir_path, exist_ok=True)
        
        full_file_path = os.path.join(full_dir_path, safe_filename)
        
        print(f"Guardando archivo en: {full_file_path}")
        with open(full_file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        # Crear registro de adjunto (IDEM a la vista)
        attachment = IncidentAttachment.objects.create(
            incident=incident,
            file_name=file_name,
            file_path=relative_path,
            file_size=uploaded_file.size,
            file_type='document',
            mime_type='text/plain',
            description=f"Adjunto de cierre verif - Etapa: {stage}",
            uploaded_by=None # En la vista es request.user
        )
        
        print(f"Registro de adjunto creado: ID {attachment.id}")
        print(f"Path en DB: {attachment.file_path}")
        
        # 5. Verificar persistencia física
        if os.path.exists(full_file_path):
            print(f"SUCCESS: El archivo físico existe en el storage.")
        else:
            print(f"FAILED: El archivo físico NO se encontró en el storage.")
            
        # 6. Limpieza (Opcional, pero mejor dejarlo para ver si se creó bien)
        # os.remove(full_file_path)
        # attachment.delete()
        
    except Exception as e:
        print(f"ERROR durante la verificación: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_closure_attachment()
