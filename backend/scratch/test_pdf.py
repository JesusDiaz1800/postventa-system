import os
import sys
import django
import io

# Setup Django
sys.path.append('C:\\Users\\jdiaz\\Desktop\\sertec-system\\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from apps.documents.services.professional_pdf_generator import ProfessionalPDFGenerator

def test_pdf():
    generator = ProfessionalPDFGenerator()
    buffer = io.BytesIO()
    data = {
        'report_number': 'TEST-001',
        'visit_date': '2026-04-30',
        'project_name': 'Proyecto Test',
        'client_name': 'Cliente Test',
        'client_rut': '12.345.678-9',
        'address': 'Calle Falsa 123',
        'commune': 'Lampa',
        'city': 'Santiago',
        'technician': 'Juan Perez',
        'installation_level': 'NORMAL',
        'is_project_finished': True,
        'is_mixed_material': False,
        'is_rescued_project': False,
        'machine_data': {
            'machines': [
                {'machine': 'Maquina 1', 'start': '100', 'cut': '150'}
            ]
        },
        'general_observations': 'Esta es una observación de prueba.'
    }
    
    print("Iniciando generación de PDF...")
    try:
        success = generator.generate_visit_report_pdf(data, buffer)
        if success:
            print("✅ PDF generado con éxito en el buffer.")
            with open('test_output.pdf', 'wb') as f:
                f.write(buffer.getvalue())
            print(f"✅ Archivo guardado como {os.path.abspath('test_output.pdf')}")
        else:
            print("❌ El generador devolvió False.")
    except Exception as e:
        import traceback
        print(f"❌ Error fatal: {e}")
        print(traceback.format_exc())

if __name__ == "__main__":
    test_pdf()
