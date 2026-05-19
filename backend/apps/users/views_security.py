import os
from django.conf import settings
from django.http import FileResponse, Http404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

@api_view(['GET'])
@permission_classes([AllowAny])
def download_ca_cert(request):
    """
    Sirve el certificado Root CA para que los usuarios puedan instalarlo y confiar en el sistema.
    Esto es necesario para habilitar la instalación PWA y eliminar advertencias de seguridad.
    """
    # El certificado se encuentra en frontend/ssl/poly-ca-cert.pem
    # Usamos BASE_DIR (que apunta a /backend/) para subir un nivel y entrar a frontend
    ca_path = os.path.join(settings.BASE_DIR.parent, 'frontend', 'ssl', 'poly-ca-cert.pem')
    
    if not os.path.exists(ca_path):
        # Intentar ruta alternativa si está en producción o empaquetado
        ca_path = os.path.join(settings.BASE_DIR, 'static', 'poly-ca-cert.pem')
        
    if os.path.exists(ca_path):
        try:
            response = FileResponse(open(ca_path, 'rb'), content_type='application/x-x509-ca-cert')
            response['Content-Disposition'] = 'attachment; filename="Polifusion-CA.crt"'
            return response
        except Exception as e:
            raise Http404(f"Error al abrir el certificado: {str(e)}")
    
    raise Http404(f"Certificado Root CA no encontrado. Buscado en: {ca_path}")
