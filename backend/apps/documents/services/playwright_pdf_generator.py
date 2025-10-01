import os
import io
import json
import asyncio
from datetime import datetime
from django.conf import settings
from playwright.async_api import async_playwright
import logging

logger = logging.getLogger(__name__)

class PlaywrightPDFGenerator:
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
        """Generar PDF usando Playwright con diseño súper moderno"""
        try:
            # Ejecutar función async
            return asyncio.run(self._generate_pdf_async(report_data))
        except Exception as e:
            logger.error(f"Error generando PDF con Playwright: {str(e)}")
            raise e

    async def _generate_pdf_async(self, report_data):
        """Generar PDF de forma asíncrona"""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Crear HTML moderno
            html_content = self._create_modern_html(report_data)
            
            # Cargar HTML en la página
            await page.set_content(html_content)
            
            # Generar PDF con opciones profesionales
            pdf_buffer = await page.pdf(
                format='A4',
                margin={
                    'top': '20mm',
                    'bottom': '20mm',
                    'left': '15mm',
                    'right': '15mm'
                },
                print_background=True,
                prefer_css_page_size=True
            )
            
            await browser.close()
            return io.BytesIO(pdf_buffer)

    def _create_modern_html(self, report_data):
        """Crear HTML súper moderno con CSS Grid y Flexbox"""
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
        
        :root {{
            --primary: #126FCC;
            --primary-light: #3B82F6;
            --secondary: #10B981;
            --warning: #F59E0B;
            --error: #EF4444;
            --muted: #6B7280;
            --border: #E5E7EB;
            --bg-muted: #F8FAFC;
            --text: #1F2937;
            --white: #FFFFFF;
        }}
        
        body {{
            font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
            line-height: 1.6;
            color: var(--text);
            background: var(--white);
            font-size: 14px;
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 0;
        }}
        
        /* HEADER MODERNO */
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            padding: 30px 0;
            border-bottom: 3px solid var(--primary);
            margin-bottom: 40px;
            position: relative;
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--primary) 0%, var(--primary-light) 100%);
        }}
        
        .logo-section {{
            width: 120px;
            display: flex;
            align-items: center;
        }}
        
        .logo {{
            width: 80px;
            height: 60px;
            background: var(--primary);
            color: var(--white);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 12px;
            border-radius: 8px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}
        
        .title-section {{
            text-align: center;
            flex: 1;
            padding: 0 20px;
        }}
        
        .main-title {{
            font-size: 32px;
            font-weight: 800;
            color: var(--primary);
            text-transform: uppercase;
            margin-bottom: 8px;
            letter-spacing: -0.5px;
        }}
        
        .subtitle {{
            font-size: 18px;
            font-weight: 600;
            color: var(--text);
            margin-bottom: 10px;
        }}
        
        .order-number {{
            font-size: 14px;
            color: var(--muted);
            background: var(--bg-muted);
            padding: 4px 12px;
            border-radius: 20px;
            display: inline-block;
        }}
        
        .company-info {{
            text-align: right;
            font-size: 11px;
            color: var(--muted);
            line-height: 1.4;
        }}
        
        .company-name {{
            font-weight: 700;
            color: var(--primary);
            margin-bottom: 4px;
            font-size: 13px;
        }}
        
        /* SECCIONES MODERNAS */
        .section {{
            margin-bottom: 35px;
        }}
        
        .section-title {{
            font-size: 18px;
            font-weight: 700;
            color: var(--primary);
            text-transform: uppercase;
            margin-bottom: 20px;
            padding-bottom: 8px;
            border-bottom: 2px solid var(--primary);
            position: relative;
        }}
        
        .section-title::after {{
            content: '';
            position: absolute;
            bottom: -2px;
            left: 0;
            width: 40px;
            height: 2px;
            background: var(--primary-light);
        }}
        
        /* GRID MODERNO */
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        
        .info-card {{
            background: var(--white);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
            transition: all 0.2s ease;
        }}
        
        .info-card:hover {{
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            transform: translateY(-1px);
        }}
        
        .info-label {{
            font-weight: 600;
            color: var(--primary);
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }}
        
        .info-value {{
            font-size: 15px;
            color: var(--text);
            font-weight: 500;
            line-height: 1.4;
        }}
        
        /* OBSERVACIONES MODERNAS */
        .observations {{
            background: linear-gradient(135deg, var(--bg-muted) 0%, #f1f5f9 100%);
            padding: 25px;
            border-radius: 12px;
            border-left: 4px solid var(--primary);
            box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.1);
        }}
        
        .observations p {{
            font-size: 14px;
            line-height: 1.6;
            color: var(--text);
        }}
        
        /* TABLA MODERNA */
        .modern-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        }}
        
        .modern-table th {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
            color: var(--white);
            font-weight: 600;
            padding: 15px;
            text-align: left;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .modern-table td {{
            padding: 15px;
            border-bottom: 1px solid var(--border);
            font-size: 14px;
        }}
        
        .modern-table tr:nth-child(even) {{
            background: var(--bg-muted);
        }}
        
        .modern-table tr:hover {{
            background: #f1f5f9;
        }}
        
        /* FIRMA MODERNA */
        .signature-section {{
            margin-top: 50px;
            text-align: center;
        }}
        
        .signature-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin: 30px 0;
        }}
        
        .signature-box {{
            height: 100px;
            border: 2px dashed var(--border);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--bg-muted);
            position: relative;
            transition: all 0.2s ease;
        }}
        
        .signature-box:hover {{
            border-color: var(--primary);
            background: #f1f5f9;
        }}
        
        .signature-box::before {{
            content: '';
            position: absolute;
            top: 10px;
            left: 10px;
            right: 10px;
            bottom: 10px;
            border: 1px solid var(--border);
            border-radius: 8px;
        }}
        
        .signature-label {{
            color: var(--muted);
            font-size: 12px;
            font-weight: 500;
        }}
        
        .signature-info {{
            margin-top: 25px;
        }}
        
        .signature-name {{
            font-weight: 700;
            font-size: 16px;
            margin-bottom: 8px;
            color: var(--text);
        }}
        
        .signature-title {{
            font-size: 13px;
            color: var(--muted);
            margin-bottom: 4px;
        }}
        
        .signature-company {{
            font-size: 13px;
            color: var(--primary);
            font-weight: 600;
        }}
        
        /* FOOTER MODERNO */
        .footer {{
            margin-top: 50px;
            padding-top: 25px;
            border-top: 1px solid var(--border);
            text-align: right;
            font-size: 11px;
            color: var(--muted);
            line-height: 1.5;
        }}
        
        .footer-company {{
            font-weight: 600;
            color: var(--primary);
            margin-bottom: 5px;
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
        <!-- HEADER MODERNO -->
        <div class="header">
            <div class="logo-section">
                <div class="logo">LOGO</div>
            </div>
            <div class="title-section">
                <h1 class="main-title">Reporte de Visita Técnica</h1>
                <p class="subtitle">{report_data.get('project_name', 'N/A')}</p>
                <div class="order-number">N° {report_data.get('order_number', 'N/A')}</div>
            </div>
            <div class="company-info">
                <div class="company-name">POLIFUSIÓN S.A.</div>
                <div>Lampa, Región Metropolitana</div>
                <div>Fecha de Emisión: {datetime.now().strftime('%d/%m/%Y')}</div>
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
                    <div class="info-label">Técnico</div>
                    <div class="info-value">{report_data.get('technician', 'N/A')}</div>
                </div>
            </div>
        </div>
        
        {self._render_observations_section(report_data)}
        {self._render_machine_data_section(report_data)}
        {self._render_technical_observations_section(report_data)}
        
        <!-- FIRMA MODERNA -->
        <div class="signature-section">
            <h2 class="section-title">Firma del Técnico</h2>
            <div class="signature-grid">
                <div class="signature-box">
                    <div class="signature-label">Firma</div>
                </div>
                <div class="signature-box">
                    <div class="signature-label">Fecha</div>
                </div>
            </div>
            <div class="signature-info">
                <div class="signature-name">Maximiliano Miranda Valdés</div>
                <div class="signature-title">Ing. Analista de Control de Calidad</div>
                <div class="signature-company">Polifusión S.A.</div>
            </div>
        </div>
        
        <!-- FOOTER MODERNO -->
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
                <table class="modern-table">
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
