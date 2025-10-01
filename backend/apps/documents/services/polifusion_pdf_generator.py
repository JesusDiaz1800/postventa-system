import os
import io
import json
import asyncio
from datetime import datetime
from django.conf import settings
from django.contrib.auth import get_user_model
from playwright.async_api import async_playwright
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class PolifusionPDFGenerator:
    def __init__(self):
        self.company_info = {
            'name': 'POLIFUSIÓN S.A.',
            'address': 'Cacique Colin 2525, Lampa, Región Metropolitana',
            'phone': '(2) 2387 5000',
            'email': 'info@polifusion.cl',
            'website': 'www.polifusion.cl',
            'rut': '76.000.000-1'
        }

    def generate_visit_report_pdf(self, report_data, user_id=None):
        """Generar PDF súper profesional con información completa"""
        try:
            return asyncio.run(self._generate_pdf_async(report_data, user_id))
        except Exception as e:
            logger.error(f"Error generando PDF: {str(e)}")
            raise e

    async def _generate_pdf_async(self, report_data, user_id=None):
        """Generar PDF de forma asíncrona"""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Obtener información del usuario técnico
            technician_info = self._get_technician_info(user_id, report_data)
            
            # Crear HTML súper profesional
            html_content = self._create_professional_html(report_data, technician_info)
            
            # Cargar HTML en la página
            await page.set_content(html_content)
            
            # Generar PDF con opciones profesionales
            pdf_buffer = await page.pdf(
                format='A4',
                margin={
                    'top': '15mm',
                    'bottom': '15mm',
                    'left': '12mm',
                    'right': '12mm'
                },
                print_background=True,
                prefer_css_page_size=True
            )
            
            await browser.close()
            return io.BytesIO(pdf_buffer)

    def _get_technician_info(self, user_id, report_data):
        """Obtener información del técnico que genera el informe"""
        # Por ahora usar información del formulario para evitar problemas async
        technician_name = report_data.get('technician', 'Técnico Responsable')
        return {
            'name': technician_name,
            'title': 'Ing. Analista de Control de Calidad',
            'company': 'Polifusión S.A.'
        }

    def _create_professional_html(self, report_data, technician_info):
        """Crear HTML súper profesional con todos los campos"""
        return f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Visita Técnica - Polifusión S.A.</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        :root {{
            --primary: #126FCC;
            --primary-light: #3B82F6;
            --primary-dark: #1E40AF;
            --secondary: #10B981;
            --warning: #F59E0B;
            --error: #EF4444;
            --muted: #6B7280;
            --border: #E5E7EB;
            --bg-muted: #F8FAFC;
            --text: #1F2937;
            --white: #FFFFFF;
            --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }}
        
        body {{
            font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
            line-height: 1.6;
            color: var(--text);
            background: var(--white);
            font-size: 13px;
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 0;
        }}
        
        /* HEADER CORPORATIVO */
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            padding: 25px 0;
            border-bottom: 4px solid var(--primary);
            margin-bottom: 30px;
            position: relative;
            background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 6px;
            background: linear-gradient(90deg, var(--primary) 0%, var(--primary-light) 50%, var(--secondary) 100%);
        }}
        
        .logo-section {{
            width: 120px;
            display: flex;
            align-items: center;
        }}
        
        .logo {{
            width: 90px;
            height: 70px;
            background: var(--primary);
            color: var(--white);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 10px;
            border-radius: 8px;
            box-shadow: var(--shadow);
            text-align: center;
            line-height: 1.2;
        }}
        
        .title-section {{
            text-align: center;
            flex: 1;
            padding: 0 20px;
        }}
        
        .main-title {{
            font-size: 28px;
            font-weight: 800;
            color: var(--primary);
            text-transform: uppercase;
            margin-bottom: 8px;
            letter-spacing: -0.5px;
        }}
        
        .subtitle {{
            font-size: 16px;
            font-weight: 600;
            color: var(--text);
            margin-bottom: 8px;
        }}
        
        .order-number {{
            font-size: 13px;
            color: var(--muted);
            background: var(--bg-muted);
            padding: 6px 15px;
            border-radius: 25px;
            display: inline-block;
            border: 1px solid var(--border);
        }}
        
        .company-info {{
            text-align: right;
            font-size: 10px;
            color: var(--muted);
            line-height: 1.4;
        }}
        
        .company-name {{
            font-weight: 700;
            color: var(--primary);
            margin-bottom: 4px;
            font-size: 12px;
        }}
        
        /* SECCIONES PROFESIONALES */
        .section {{
            margin-bottom: 30px;
        }}
        
        .section-title {{
            font-size: 16px;
            font-weight: 700;
            color: var(--primary);
            text-transform: uppercase;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 2px solid var(--primary);
            position: relative;
        }}
        
        .section-title::after {{
            content: '';
            position: absolute;
            bottom: -2px;
            left: 0;
            width: 50px;
            height: 2px;
            background: var(--primary-light);
        }}
        
        /* GRID PROFESIONAL */
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 15px;
        }}
        
        .info-card {{
            background: var(--white);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
            transition: all 0.2s ease;
        }}
        
        .info-label {{
            font-weight: 600;
            color: var(--primary);
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 6px;
        }}
        
        .info-value {{
            font-size: 13px;
            color: var(--text);
            font-weight: 500;
            line-height: 1.4;
        }}
        
        /* OBSERVACIONES PROFESIONALES */
        .observations {{
            background: linear-gradient(135deg, var(--bg-muted) 0%, #f1f5f9 100%);
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid var(--primary);
            box-shadow: var(--shadow);
        }}
        
        .observations p {{
            font-size: 13px;
            line-height: 1.6;
            color: var(--text);
            margin-bottom: 10px;
        }}
        
        .observations p:last-child {{
            margin-bottom: 0;
        }}
        
        /* TABLA PROFESIONAL */
        .professional-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: var(--shadow);
        }}
        
        .professional-table th {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
            color: var(--white);
            font-weight: 600;
            padding: 12px;
            text-align: left;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .professional-table td {{
            padding: 12px;
            border-bottom: 1px solid var(--border);
            font-size: 12px;
        }}
        
        .professional-table tr:nth-child(even) {{
            background: var(--bg-muted);
        }}
        
        .professional-table tr:hover {{
            background: #f1f5f9;
        }}
        
        /* FIRMA PROFESIONAL */
        .signature-section {{
            margin-top: 40px;
            text-align: center;
        }}
        
        .signature-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 25px;
            margin: 25px 0;
        }}
        
        .signature-box {{
            height: 80px;
            border: 2px dashed var(--border);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--bg-muted);
            position: relative;
        }}
        
        .signature-box::before {{
            content: '';
            position: absolute;
            top: 8px;
            left: 8px;
            right: 8px;
            bottom: 8px;
            border: 1px solid var(--border);
            border-radius: 4px;
        }}
        
        .signature-label {{
            color: var(--muted);
            font-size: 11px;
            font-weight: 500;
        }}
        
        .signature-info {{
            margin-top: 20px;
        }}
        
        .signature-name {{
            font-weight: 700;
            font-size: 14px;
            margin-bottom: 6px;
            color: var(--text);
        }}
        
        .signature-title {{
            font-size: 12px;
            color: var(--muted);
            margin-bottom: 3px;
        }}
        
        .signature-company {{
            font-size: 12px;
            color: var(--primary);
            font-weight: 600;
        }}
        
        /* FOOTER CORPORATIVO */
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid var(--border);
            text-align: center;
            font-size: 10px;
            color: var(--muted);
            line-height: 1.5;
            background: var(--bg-muted);
            padding: 15px;
            border-radius: 8px;
        }}
        
        .footer-company {{
            font-weight: 700;
            color: var(--primary);
            margin-bottom: 5px;
            font-size: 11px;
        }}
        
        /* RESPONSIVE */
        @media (max-width: 768px) {{
            .header {{
                flex-direction: column;
                text-align: center;
            }}
            
            .info-grid {{
                grid-template-columns: 1fr;
            }}
            
            .signature-grid {{
                grid-template-columns: 1fr;
            }}
        }}
        
        /* PRINT STYLES */
        @media print {{
            body {{
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }}
            
            .container {{
                max-width: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- HEADER CORPORATIVO -->
        <div class="header">
            <div class="logo-section">
                <div class="logo">POLIFUSIÓN<br>S.A.</div>
            </div>
            <div class="title-section">
                <h1 class="main-title">Reporte de Visita Técnica</h1>
                <p class="subtitle">{report_data.get('project_name', 'N/A')}</p>
                <div class="order-number">N° {report_data.get('order_number', 'N/A')}</div>
            </div>
            <div class="company-info">
                <div class="company-name">POLIFUSIÓN S.A.</div>
                <div>Lampa, Región Metropolitana</div>
                <div>Fecha: {datetime.now().strftime('%d/%m/%Y')}</div>
            </div>
        </div>
        
        <!-- INFORMACIÓN DEL PROYECTO -->
        <div class="section">
            <h2 class="section-title">Información del Proyecto</h2>
            <div class="info-grid">
                <div class="info-card">
                    <div class="info-label">Cliente</div>
                    <div class="info-value">{report_data.get('client_name', 'N/A')}</div>
                </div>
                <div class="info-card">
                    <div class="info-label">Proyecto</div>
                    <div class="info-value">{report_data.get('project_name', 'N/A')}</div>
                </div>
                <div class="info-card">
                    <div class="info-label">Dirección</div>
                    <div class="info-value">{report_data.get('address', 'N/A')}</div>
                </div>
                <div class="info-card">
                    <div class="info-label">Comuna</div>
                    <div class="info-value">{report_data.get('commune', 'N/A')}</div>
                </div>
                <div class="info-card">
                    <div class="info-label">Ciudad</div>
                    <div class="info-value">{report_data.get('city', 'N/A')}</div>
                </div>
                <div class="info-card">
                    <div class="info-label">Fecha de Visita</div>
                    <div class="info-value">{report_data.get('visit_date', 'N/A')}</div>
                </div>
            </div>
        </div>
        
        <!-- PERSONAL INVOLUCRADO -->
        <div class="section">
            <h2 class="section-title">Personal Involucrado</h2>
            <div class="info-grid">
                <div class="info-card">
                    <div class="info-label">Vendedor</div>
                    <div class="info-value">{report_data.get('salesperson', 'N/A')}</div>
                </div>
                <div class="info-card">
                    <div class="info-label">Técnico Responsable</div>
                    <div class="info-value">{report_data.get('technician', 'N/A')}</div>
                </div>
            </div>
        </div>
        
        {self._render_observations_section(report_data)}
        {self._render_machine_data_section(report_data)}
        {self._render_technical_observations_section(report_data)}
        {self._render_additional_sections(report_data)}
        
        <!-- FIRMA PROFESIONAL -->
        <div class="signature-section">
            <h2 class="section-title">Firma del Técnico Responsable</h2>
            <div class="signature-grid">
                <div class="signature-box">
                    <div class="signature-label">Firma</div>
                </div>
                <div class="signature-box">
                    <div class="signature-label">Fecha</div>
                </div>
            </div>
            <div class="signature-info">
                <div class="signature-name">{technician_info['name']}</div>
                <div class="signature-title">{technician_info['title']}</div>
                <div class="signature-company">{technician_info['company']}</div>
            </div>
        </div>
        
        <!-- FOOTER CORPORATIVO -->
        <div class="footer">
            <div class="footer-company">POLIFUSIÓN S.A.</div>
            <div>{self.company_info['address']}</div>
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
                <table class="professional-table">
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

    def _render_additional_sections(self, report_data):
        """Renderizar secciones adicionales del formulario"""
        html = ''
        
        # Información del Producto (si existe)
        product_info = {
            "Categoría del Producto": report_data.get('product_category'),
            "Subcategoría": report_data.get('product_subcategory'),
            "SKU": report_data.get('product_sku'),
            "Lote": report_data.get('product_lot'),
            "Proveedor": report_data.get('product_provider'),
        }
        
        filtered_product_info = {k: v for k, v in product_info.items() if v}
        
        if filtered_product_info:
            html += '''
            <div class="section">
                <h2 class="section-title">Información del Producto</h2>
                <div class="info-grid">
            '''
            for key, value in filtered_product_info.items():
                html += f'''
                <div class="info-card">
                    <div class="info-label">{key}</div>
                    <div class="info-value">{str(value)}</div>
                </div>
                '''
            html += '''
                </div>
            </div>
            '''
        
        # Información de la Incidencia (si existe)
        incident_info = {
            "Descripción de la Incidencia": report_data.get('incident_description'),
            "Prioridad": report_data.get('incident_priority'),
            "Responsable": report_data.get('incident_responsible'),
            "Fecha de Detección": report_data.get('incident_detection_date'),
            "Hora de Detección": report_data.get('incident_detection_time'),
        }
        
        filtered_incident_info = {k: v for k, v in incident_info.items() if v}
        
        if filtered_incident_info:
            html += '''
            <div class="section">
                <h2 class="section-title">Información de la Incidencia</h2>
                <div class="info-grid">
            '''
            for key, value in filtered_incident_info.items():
                html += f'''
                <div class="info-card">
                    <div class="info-label">{key}</div>
                    <div class="info-value">{str(value)}</div>
                </div>
                '''
            html += '''
                </div>
            </div>
            '''
        
        return html

    def generate_lab_report_pdf(self, report_data, user_id=None):
        """Generar PDF para reporte de laboratorio"""
        return self.generate_visit_report_pdf(report_data, user_id)

    def generate_supplier_report_pdf(self, report_data, user_id=None):
        """Generar PDF para reporte de proveedor"""
        return self.generate_visit_report_pdf(report_data, user_id)

    def generate_quality_report_pdf(self, report_data, user_id=None):
        """Generar PDF para reporte de calidad"""
        return self.generate_visit_report_pdf(report_data, user_id)
