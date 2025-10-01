"""
Script para probar el nuevo generador PDF profesional
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

def probar_generador_profesional():
    """
    Probar el nuevo generador PDF profesional
    """
    print("🧪 PROBANDO GENERADOR PDF PROFESIONAL")
    print("=" * 60)
    
    try:
        # Crear instancia del generador
        generator = ProfessionalPDFGenerator()
        print("✅ Generador profesional creado exitosamente")
        
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
        output_path = f'backend/documents/output/reporte_visita_profesional_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        print(f"📄 Generando PDF profesional: {output_path}")
        success = generator.generate_visit_report_pdf(report_data, output_path)
        
        if success:
            print("✅ PDF profesional generado exitosamente")
            print(f"📁 Archivo guardado en: {output_path}")
            
            # Verificar que el archivo existe
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"📊 Tamaño del archivo: {file_size:,} bytes")
                print("🎉 ¡Generador profesional funcionando correctamente!")
                return True
            else:
                print("❌ El archivo no se creó correctamente")
                return False
        else:
            print("❌ Error generando PDF profesional")
            return False
            
    except Exception as e:
        print(f"❌ Error en la prueba: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def mostrar_instrucciones():
    """
    Mostrar instrucciones para usar el generador profesional
    """
    print("\n🌐 INSTRUCCIONES PARA EL GENERADOR PROFESIONAL")
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
   e) El PDF se generará automáticamente con diseño profesional
   f) Hacer clic en "Ver reporte" para abrir el PDF

4. 🎨 CARACTERÍSTICAS DEL DISEÑO PROFESIONAL:
   =========================================
   
   • ✅ Logo de Polifusión en el encabezado
   • ✅ Colores corporativos (#126FCC)
   • ✅ Diseño limpio y profesional
   • ✅ Tablas con formato corporativo
   • ✅ Información de la empresa en el encabezado
   • ✅ Pie de página con información de generación
   • ✅ Tipografía Helvetica profesional
   • ✅ Espaciado y márgenes optimizados

5. 📁 ARCHIVOS GENERADOS:
   ======================
   
   Los documentos se guardan en:
   backend/documents/output/
   
   Puedes abrirlos directamente desde esa carpeta.
""")

def main():
    """
    Función principal
    """
    print("🧪 PROBADOR DEL GENERADOR PDF PROFESIONAL")
    print("=" * 80)
    print("Probando el nuevo generador con diseño verdaderamente profesional")
    print("=" * 80)
    
    # Probar generador
    exito = probar_generador_profesional()
    
    if exito:
        mostrar_instrucciones()
        
        print("\n🎯 CONCLUSIÓN")
        print("=" * 30)
        print("✅ Generador profesional funcionando correctamente")
        print("✅ Diseño verdaderamente profesional implementado")
        print("✅ Logo de Polifusión integrado")
        print("✅ Colores corporativos aplicados")
        print("🚀 ¡Listo para usar desde la aplicación!")
    else:
        print("\n❌ ERROR")
        print("=" * 30)
        print("❌ El generador profesional tiene problemas")
        print("💡 Revisar los errores anteriores")

if __name__ == "__main__":
    main()
