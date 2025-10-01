"""
Script para probar el generador PDF con carpeta compartida
"""

import os
import sys
import django
from datetime import datetime

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from apps.documents.services.professional_pdf_generator import ProfessionalPDFGenerator
from apps.incidents.models import Incident

def probar_generador_con_carpeta_compartida():
    """
    Probar el generador PDF con carpeta compartida
    """
    print("🧪 PROBANDO GENERADOR CON CARPETA COMPARTIDA")
    print("=" * 60)
    
    try:
        # Crear instancia del generador
        generator = ProfessionalPDFGenerator()
        print("✅ Generador profesional creado exitosamente")
        print(f"📁 Carpeta compartida configurada: {generator.shared_folder}")
        
        # Verificar que la carpeta compartida existe
        if not os.path.exists(generator.shared_folder):
            print(f"❌ La carpeta compartida no existe: {generator.shared_folder}")
            print("💡 Verificar la configuración de SHARED_FOLDER_PATH en settings")
            return False
        
        print("✅ Carpeta compartida existe")
        
        # Obtener una incidencia de prueba
        incident = Incident.objects.filter(estado='abierto').first()
        if not incident:
            print("❌ No se encontraron incidencias abiertas para probar")
            return False
        
        print(f"📋 Usando incidencia: {incident.code} - {incident.cliente}")
        
        # Datos de prueba para reporte de visita
        report_data = {
            'order_number': f'RV-{datetime.now().strftime("%Y%m%d")}-001',
            'visit_date': datetime.now().strftime('%Y-%m-%d'),
            'client_name': incident.cliente,
            'project_name': incident.obra,
            'address': incident.direccion_cliente,
            'technician': 'Juan Pérez',
            'salesperson': 'María González',
            'visit_reason': f'Visita técnica para {incident.descripcion}',
            'general_observations': f'Se realizó inspección técnica del problema reportado: {incident.descripcion}. Se tomaron muestras y se documentaron las condiciones encontradas.',
            'incident': {
                'id': incident.id,
                'code': incident.code,
                'descripcion': incident.descripcion,
                'prioridad': incident.prioridad,
                'estado': incident.estado,
                'provider': incident.provider,
                'sku': incident.sku,
                'lote': incident.lote
            }
        }
        
        # Generar PDF de reporte de visita
        local_output = f'backend/documents/output/reporte_visita_compartido_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        os.makedirs(os.path.dirname(local_output), exist_ok=True)
        
        print(f"📄 Generando PDF profesional: {local_output}")
        success = generator.generate_visit_report_pdf(report_data, local_output)
        
        if success:
            print("✅ PDF profesional generado exitosamente")
            print(f"📁 Archivo local guardado en: {local_output}")
            
            # Verificar que el archivo local existe
            if os.path.exists(local_output):
                file_size = os.path.getsize(local_output)
                print(f"📊 Tamaño del archivo local: {file_size:,} bytes")
                
                # Verificar que también se guardó en la carpeta compartida
                shared_folder = generator.shared_folder
                incident_folder = os.path.join(shared_folder, 'documents', 'visit-reports', f'incident_{incident.id}')
                filename = os.path.basename(local_output)
                shared_path = os.path.join(incident_folder, filename)
                
                if os.path.exists(shared_path):
                    shared_size = os.path.getsize(shared_path)
                    print(f"✅ PDF guardado en carpeta compartida: {shared_path}")
                    print(f"📊 Tamaño del archivo compartido: {shared_size:,} bytes")
                    print("🎉 ¡Generador con carpeta compartida funcionando correctamente!")
                    return True
                else:
                    print(f"❌ El archivo no se guardó en la carpeta compartida: {shared_path}")
                    return False
            else:
                print("❌ El archivo local no se creó correctamente")
                return False
        else:
            print("❌ Error generando PDF profesional")
            return False
            
    except Exception as e:
        print(f"❌ Error en la prueba: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def mostrar_instrucciones_carpeta_compartida():
    """
    Mostrar instrucciones para usar el generador con carpeta compartida
    """
    print("\n🌐 INSTRUCCIONES PARA CARPETA COMPARTIDA")
    print("=" * 60)
    
    print("""
1. 🚀 INICIAR SERVIDOR DJANGO:
   ===========================
   python manage.py runserver 0.0.0.0:8000

2. 🌐 INICIAR FRONTEND:
   ====================
   cd frontend
   npm start

3. 📱 USAR DESDE LA APLICACIÓN:
   ===========================
   
   a) Ir a la página de "Reportes de Visita"
   b) Hacer clic en "Crear Reporte"
   c) Seleccionar una incidencia
   d) Completar el formulario
   e) El PDF se generará automáticamente
   f) Se guardará en la carpeta compartida de red
   g) Hacer clic en "Ver reporte" para abrir el PDF

4. 📁 UBICACIÓN DE ARCHIVOS:
   =========================
   
   Los documentos se guardan en:
   • Carpeta local: backend/documents/output/
   • Carpeta compartida: Y:\\CONTROL DE CALIDAD\\postventa\\documents\\
   
   Estructura en carpeta compartida:
   documents/
   ├── visit-reports/
   │   └── incident_XX/
   │       └── RV-YYYYMMDD-001.pdf
   ├── lab-reports/
   │   └── incident_XX/
   │       └── LR-YYYYMMDD-001.pdf
   └── supplier-reports/
       └── incident_XX/
           └── SR-YYYYMMDD-001.pdf

5. 🔧 CONFIGURACIÓN:
   =================
   
   La carpeta compartida se configura en:
   • settings.py: SHARED_FOLDER_PATH
   • Valor por defecto: 'Y:\\CONTROL DE CALIDAD\\postventa'
   
   Para cambiar la ubicación, modificar en settings.py:
   SHARED_FOLDER_PATH = '\\\\servidor\\carpeta\\postventa'
""")

def main():
    """
    Función principal
    """
    print("🧪 PROBADOR DEL GENERADOR CON CARPETA COMPARTIDA")
    print("=" * 80)
    print("Probando el generador con guardado en carpeta compartida de red")
    print("=" * 80)
    
    # Probar generador
    exito = probar_generador_con_carpeta_compartida()
    
    if exito:
        mostrar_instrucciones_carpeta_compartida()
        
        print("\n🎯 CONCLUSIÓN")
        print("=" * 30)
        print("✅ Generador con carpeta compartida funcionando")
        print("✅ PDFs se guardan en carpeta local Y compartida")
        print("✅ Estructura de carpetas organizada por incidente")
        print("✅ Acceso desde red de la empresa")
        print("🚀 ¡Listo para usar desde la aplicación!")
    else:
        print("\n❌ ERROR")
        print("=" * 30)
        print("❌ El generador con carpeta compartida tiene problemas")
        print("💡 Revisar la configuración de SHARED_FOLDER_PATH")

if __name__ == "__main__":
    main()
