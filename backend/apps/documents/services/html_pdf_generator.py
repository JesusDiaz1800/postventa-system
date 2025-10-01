import os
import io
import json
from datetime import datetime
from django.conf import settings
from django.template.loader import render_to_string
from django.http import HttpResponse
import subprocess
import tempfile
import logging

logger = logging.getLogger(__name__)

class HTMLPDFGenerator:
    def __init__(self):
        self.company_info = {
            'name': 'POLIFUSIÓN S.A.',
            'address': 'Cacique Colin 2525, Lampa, Región Metropolitana',
            'phone': '(2) 2387 5000',
            'email': 'info@polifusion.cl',
            'website': 'www.polifusion.cl',
            'rut': '76.000.000-1'
        }

    def generate_visit_report_pdf(self, report_data):
        """Generar PDF usando HTML/CSS moderno"""
        try:
            # Crear HTML con diseño moderno
            html_content = self._create_modern_html(report_data)
            
            # Guardar HTML temporal
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as temp_html:
                temp_html.write(html_content)
                temp_html_path = temp_html.name
            
            # Generar PDF con wkhtmltopdf
            pdf_path = temp_html_path.replace('.html', '.pdf')
            
            # Comando wkhtmltopdf con opciones modernas
            cmd = [
                'wkhtmltopdf',
                '--page-size', 'A4',
                '--margin-top', '20mm',
                '--margin-bottom', '20mm',
                '--margin-left', '15mm',
                '--margin-right', '15mm',
                '--encoding', 'UTF-8',
                '--print-media-type',
                '--disable-smart-shrinking',
                '--enable-local-file-access',
                temp_html_path,
                pdf_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Leer PDF generado
                with open(pdf_path, 'rb') as pdf_file:
                    pdf_content = pdf_file.read()
                
                # Limpiar archivos temporales
                os.unlink(temp_html_path)
                os.unlink(pdf_path)
                
                return io.BytesIO(pdf_content)
            else:
                logger.error(f"Error generando PDF: {result.stderr}")
                raise Exception(f"Error generando PDF: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Error en HTMLPDFGenerator: {str(e)}")
            raise e

    def _create_modern_html(self, report_data):
        """Crear HTML moderno con CSS profesional"""
        return f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Visita Técnica</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #1f2937;
            background: #ffffff;
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            padding-bottom: 20px;
            border-bottom: 3px solid #126FCC;
            margin-bottom: 30px;
        }}
        
        .logo-section {{
            width: 100px;
        }}
        
        .title-section {{
            text-align: center;
            flex: 1;
        }}
        
        .main-title {{
            font-size: 28px;
            font-weight: bold;
            color: #126FCC;
            text-transform: uppercase;
            margin-bottom: 10px;
        }}
        
        .subtitle {{
            font-size: 18px;
            font-weight: 600;
            color: #374151;
        }}
        
        .company-info {{
            text-align: right;
            font-size: 10px;
            color: #6b7280;
        }}
        
        .company-name {{
            font-weight: bold;
            color: #126FCC;
            margin-bottom: 5px;
        }}
        
        .section {{
            margin-bottom: 25px;
        }}
        
        .section-title {{
            font-size: 16px;
            font-weight: bold;
            color: #126FCC;
            text-transform: uppercase;
            margin-bottom: 15px;
            padding-bottom: 5px;
            border-bottom: 2px solid #126FCC;
        }}
        
        .info-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }}
        
        .info-item {{
            display: flex;
            flex-direction: column;
        }}
        
        .info-label {{
            font-weight: bold;
            color: #126FCC;
            font-size: 12px;
            margin-bottom: 5px;
        }}
        
        .info-value {{
            font-size: 14px;
            color: #374151;
            padding: 8px 12px;
            background: #f8fafc;
            border: 1px solid #e5e7eb;
            border-radius: 4px;
        }}
        
        .observations {{
            background: #f8fafc;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #126FCC;
        }}
        
        .machine-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}
        
        .machine-table th,
        .machine-table td {{
            padding: 12px;
            text-align: left;
            border: 1px solid #e5e7eb;
        }}
        
        .machine-table th {{
            background: #126FCC;
            color: white;
            font-weight: bold;
        }}
        
        .machine-table tr:nth-child(even) {{
            background: #f8fafc;
        }}
        
        .signature-section {{
            margin-top: 40px;
            text-align: center;
        }}
        
        .signature-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }}
        
        .signature-box {{
            height: 80px;
            border: 2px dashed #d1d5db;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #f9fafb;
        }}
        
        .signature-info {{
            margin-top: 20px;
        }}
        
        .signature-name {{
            font-weight: bold;
            font-size: 14px;
            margin-bottom: 5px;
        }}
        
        .signature-title {{
            font-size: 12px;
            color: #6b7280;
        }}
        
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
            text-align: right;
            font-size: 10px;
            color: #6b7280;
        }}
        
        @media print {{
            body {{
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo-section">
                <!-- Logo placeholder -->
                <div style="width: 80px; height: 60px; background: #126FCC; color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 12px;">
                    LOGO
                </div>
            </div>
            <div class="title-section">
                <h1 class="main-title">Reporte de Visita Técnica</h1>
                <p class="subtitle">{report_data.get('project_name', 'N/A')}</p>
            </div>
            <div class="company-info">
                <div class="company-name">POLIFUSIÓN S.A.</div>
                <div>Lampa, Región Metropolitana</div>
                <div>Fecha de Emisión: {datetime.now().strftime('%d/%m/%Y')}</div>
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">Información del Proyecto</h2>
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">Cliente</div>
                    <div class="info-value">{report_data.get('client_name', 'N/A')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Proyecto</div>
                    <div class="info-value">{report_data.get('project_name', 'N/A')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Dirección</div>
                    <div class="info-value">{report_data.get('address', 'N/A')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Comuna</div>
                    <div class="info-value">{report_data.get('commune', 'N/A')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Ciudad</div>
                    <div class="info-value">{report_data.get('city', 'N/A')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Fecha de Visita</div>
                    <div class="info-value">{report_data.get('visit_date', 'N/A')}</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">Personal Involucrado</h2>
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">Vendedor</div>
                    <div class="info-value">{report_data.get('salesperson', 'N/A')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Técnico</div>
                    <div class="info-value">{report_data.get('technician', 'N/A')}</div>
                </div>
            </div>
        </div>
        
        {self._render_observations_section(report_data)}
        {self._render_machine_data_section(report_data)}
        {self._render_technical_observations_section(report_data)}
        
        <div class="signature-section">
            <h2 class="section-title">Firma del Técnico</h2>
            <div class="signature-grid">
                <div class="signature-box">
                    <div style="color: #9ca3af; font-size: 12px;">Firma</div>
                </div>
                <div class="signature-box">
                    <div style="color: #9ca3af; font-size: 12px;">Fecha</div>
                </div>
            </div>
            <div class="signature-info">
                <div class="signature-name">Maximiliano Miranda Valdés</div>
                <div class="signature-title">Ing. Analista de Control de Calidad</div>
                <div class="signature-title">Polifusión S.A.</div>
            </div>
        </div>
        
        <div class="footer">
            <div>POLIFUSIÓN S.A. - {self.company_info['address']}</div>
            <div>Tel: {self.company_info['phone']} | Email: {self.company_info['email']}</div>
            <div>RUT: {self.company_info['rut']} | Web: {self.company_info['website']}</div>
        </div>
    </div>
</body>
</html>
        """

    def _render_observations_section(self, report_data):
        """Renderizar sección de observaciones"""
        if report_data.get('visit_reason') or report_data.get('general_observations'):
            html = '<div class="section">'
            if report_data.get('visit_reason'):
                html += f'''
                <h2 class="section-title">Razón de la Visita</h2>
                <div class="observations">
                    <p>{report_data.get('visit_reason', '')}</p>
                </div>
                '''
            if report_data.get('general_observations'):
                html += f'''
                <h2 class="section-title">Observaciones Generales</h2>
                <div class="observations">
                    <p>{report_data.get('general_observations', '')}</p>
                </div>
                '''
            html += '</div>'
            return html
        return ''

    def _render_machine_data_section(self, report_data):
        """Renderizar sección de datos de máquinas"""
        machine_data = report_data.get('machine_data', {})
        
        if isinstance(machine_data, str):
            try:
                machine_data = json.loads(machine_data)
            except (json.JSONDecodeError, TypeError):
                machine_data = {}

        if machine_data and machine_data.get('machines'):
            html = '''
            <div class="section">
                <h2 class="section-title">Datos de Máquinas</h2>
                <table class="machine-table">
                    <thead>
                        <tr>
                            <th>Máquina</th>
                            <th>Inicio</th>
                            <th>Corte</th>
                        </tr>
                    </thead>
                    <tbody>
            '''
            for machine in machine_data['machines']:
                html += f'''
                        <tr>
                            <td>{machine.get('machine_name', 'N/A')}</td>
                            <td>{machine.get('start_time', 'N/A')}</td>
                            <td>{machine.get('cut_time', 'N/A')}</td>
                        </tr>
                '''
            html += '''
                    </tbody>
                </table>
            </div>
            '''
            return html
        return ''

    def _render_technical_observations_section(self, report_data):
        """Renderizar sección de observaciones técnicas"""
        technical_observations = {
            "Observaciones de Muro": report_data.get('wall_observations'),
            "Observaciones de Matriz": report_data.get('matrix_observations'),
            "Observaciones de Losa": report_data.get('slab_observations'),
            "Observaciones de Almacenamiento": report_data.get('storage_observations'),
            "Observaciones de Pre-ensamblado": report_data.get('pre_assembled_observations'),
            "Observaciones de Exterior": report_data.get('exterior_observations'),
        }
        
        filtered_observations = {k: v for k, v in technical_observations.items() if v}
        
        if filtered_observations:
            html = '''
            <div class="section">
                <h2 class="section-title">Observaciones Técnicas</h2>
                <div class="observations">
            '''
            for key, value in filtered_observations.items():
                html += f'<p><strong>{key}:</strong> {str(value)}</p>'
            html += '''
                </div>
            </div>
            '''
            return html
        return ''

    def generate_lab_report_pdf(self, report_data):
        """Generar PDF para reporte de laboratorio"""
        return self.generate_visit_report_pdf(report_data)

    def generate_supplier_report_pdf(self, report_data):
        """Generar PDF para reporte de proveedor"""
        return self.generate_visit_report_pdf(report_data)

    def generate_quality_report_pdf(self, report_data):
        """Generar PDF para reporte de calidad"""
        return self.generate_visit_report_pdf(report_data)
