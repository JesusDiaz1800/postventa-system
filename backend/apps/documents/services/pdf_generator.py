import os
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from django.conf import settings
import logging
from .professional_pdf_generator import ProfessionalPDFGenerator

logger = logging.getLogger(__name__)

class ProfessionalPDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        self.company_info = {
            'name': 'POLIFUSIÓN S.A.',
            'address': 'Cacique Colin 2525, Lampa, Región Metropolitana',
            'phone': '(2) 2387 5000',
            'email': 'info@polifusion.cl',
            'website': 'www.polifusion.cl'
        }
    
    def setup_custom_styles(self):
        """Configurar estilos personalizados para el PDF"""
        # Verificar si los estilos ya existen antes de agregarlos
        if 'CompanyTitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CompanyTitle',
                parent=self.styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#1e40af'),
                fontName='Helvetica-Bold'
            ))
        
        if 'SectionTitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='SectionTitle',
                parent=self.styles['Heading2'],
                fontSize=16,
                spaceAfter=12,
                spaceBefore=20,
                textColor=colors.HexColor('#1e40af'),
                fontName='Helvetica-Bold',
                borderWidth=1,
                borderColor=colors.HexColor('#1e40af'),
                borderPadding=8,
                backColor=colors.HexColor('#f8fafc')
            ))
        
        if 'CustomBodyText' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CustomBodyText',
                parent=self.styles['Normal'],
                fontSize=11,
                spaceAfter=6,
                alignment=TA_JUSTIFY,
                fontName='Helvetica'
            ))
        
        if 'CompanyInfo' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CompanyInfo',
                parent=self.styles['Normal'],
                fontSize=10,
                spaceAfter=4,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#6b7280'),
                fontName='Helvetica'
            ))
        
        if 'TableHeader' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='TableHeader',
                parent=self.styles['Normal'],
                fontSize=10,
                alignment=TA_CENTER,
                textColor=colors.white,
                fontName='Helvetica-Bold'
            ))
        
        if 'TableData' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='TableData',
                parent=self.styles['Normal'],
                fontSize=9,
                alignment=TA_LEFT,
                fontName='Helvetica'
            ))

    def create_header(self, canvas, doc):
        """Crear encabezado profesional con logo y datos de empresa"""
        canvas.saveState()
        
        # Fondo del encabezado
        canvas.setFillColor(colors.HexColor('#1e40af'))
        canvas.rect(0, A4[1] - 120, A4[0], 120, fill=1, stroke=0)
        
        # Logo de POLIFUSIÓN
        canvas.setFillColor(colors.white)
        canvas.setFont('Helvetica-Bold', 24)
        canvas.drawString(50, A4[1] - 50, 'POLIFUSIÓN')
        
        # Información de la empresa
        canvas.setFont('Helvetica-Bold', 16)
        canvas.drawString(50, A4[1] - 75, self.company_info['name'])
        
        canvas.setFont('Helvetica', 10)
        canvas.drawString(50, A4[1] - 90, self.company_info['address'])
        canvas.drawString(50, A4[1] - 103, f"Tel: {self.company_info['phone']}")
        
        # Línea separadora
        canvas.setStrokeColor(colors.white)
        canvas.setLineWidth(2)
        canvas.line(50, A4[1] - 110, A4[0] - 50, A4[1] - 110)
        
        canvas.restoreState()

    def create_footer(self, canvas, doc):
        """Crear pie de página profesional"""
        canvas.saveState()
        
        # Fondo del pie
        canvas.setFillColor(colors.HexColor('#f8fafc'))
        canvas.rect(0, 0, A4[0], 40, fill=1, stroke=0)
        
        # Línea superior
        canvas.setStrokeColor(colors.HexColor('#1e40af'))
        canvas.setLineWidth(1)
        canvas.line(50, 40, A4[0] - 50, 40)
        
        # Información del pie
        canvas.setFillColor(colors.HexColor('#6b7280'))
        canvas.setFont('Helvetica', 8)
        canvas.drawString(50, 25, f"Página {doc.page}")
        canvas.drawString(A4[0] - 150, 25, f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        canvas.restoreState()

    def create_professional_table(self, data, headers, col_widths=None):
        """Crear tabla profesional con estilo corporativo"""
        if not col_widths:
            col_widths = [A4[0] / len(headers)] * len(headers)
        
        # Crear datos de la tabla
        table_data = [headers] + data
        
        # Crear tabla
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        # Estilo de la tabla
        table_style = TableStyle([
            # Encabezados
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Datos
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            
            # Filas alternadas
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')])
        ])
        
        table.setStyle(table_style)
        return table

    def generate_visit_report_pdf(self, report_data):
        """Generar PDF profesional para reporte de visita"""
        buffer = io.BytesIO()
        
        # Crear documento con encabezado y pie personalizados
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=150,
            bottomMargin=60
        )
        
        # Crear encabezado y pie
        def header_callback(canvas, doc):
            self.create_header(canvas, doc)
        
        def footer_callback(canvas, doc):
            self.create_footer(canvas, doc)
        
        # Contenido del documento
        story = []
        
        # Título del reporte
        story.append(Paragraph("REPORTE DE VISITA TÉCNICA", self.styles['CompanyTitle']))
        story.append(Spacer(1, 20))
        
        # Información del reporte
        report_info = [
            ['Número de Reporte:', report_data.get('report_number', 'N/A')],
            ['Número de Orden:', report_data.get('order_number', 'N/A')],
            ['Fecha de Visita:', report_data.get('visit_date', 'N/A')],
            ['Técnico:', report_data.get('technician', 'N/A')],
            ['Cliente:', report_data.get('client_name', 'N/A')],
            ['Proyecto:', report_data.get('project_name', 'N/A')]
        ]
        
        story.append(self.create_professional_table(
            [[row[1]] for row in report_info],
            ['Información del Reporte'],
            [A4[0] - 100]
        ))
        story.append(Spacer(1, 20))
        
        # Información del proyecto
        story.append(Paragraph("INFORMACIÓN DEL PROYECTO", self.styles['SectionTitle']))
        story.append(Spacer(1, 10))
        
        project_info = [
            ['Cliente:', report_data.get('client_name', 'N/A')],
            ['Dirección:', report_data.get('address', 'N/A')],
            ['Comuna:', report_data.get('commune', 'N/A')],
            ['Ciudad:', report_data.get('city', 'N/A')],
            ['Empresa Constructora:', report_data.get('construction_company', 'N/A')]
        ]
        
        story.append(self.create_professional_table(
            [[row[1]] for row in project_info],
            ['Detalles del Proyecto'],
            [A4[0] - 100]
        ))
        story.append(Spacer(1, 20))
        
        # Personal involucrado
        story.append(Paragraph("PERSONAL INVOLUCRADO", self.styles['SectionTitle']))
        story.append(Spacer(1, 10))
        
        personnel_data = [
            ['Vendedor:', report_data.get('salesperson', 'N/A')],
            ['Técnico:', report_data.get('technician', 'N/A')],
            ['Instalador:', report_data.get('installer', 'N/A')],
            ['Teléfono Instalador:', report_data.get('installer_phone', 'N/A')]
        ]
        
        story.append(self.create_professional_table(
            [[row[1]] for row in personnel_data],
            ['Personal'],
            [A4[0] - 100]
        ))
        story.append(Spacer(1, 20))
        
        # Información del producto
        story.append(Paragraph("INFORMACIÓN DEL PRODUCTO", self.styles['SectionTitle']))
        story.append(Spacer(1, 10))
        
        product_data = [
            ['Categoría:', report_data.get('product_category', 'N/A')],
            ['Subcategoría:', report_data.get('product_subcategory', 'N/A')],
            ['SKU:', report_data.get('product_sku', 'N/A')],
            ['Lote:', report_data.get('product_lot', 'N/A')],
            ['Proveedor:', report_data.get('product_provider', 'N/A')]
        ]
        
        story.append(self.create_professional_table(
            [[row[1]] for row in product_data],
            ['Detalles del Producto'],
            [A4[0] - 100]
        ))
        story.append(Spacer(1, 20))
        
        # Motivo de la visita
        story.append(Paragraph("MOTIVO DE LA VISITA", self.styles['SectionTitle']))
        story.append(Spacer(1, 10))
        story.append(Paragraph(f"<b>Motivo:</b> {report_data.get('visit_reason', 'N/A')}", self.styles['CustomBodyText']))
        story.append(Spacer(1, 20))
        
        # Datos de máquinas (si existen)
        machine_data = report_data.get('machine_data', {})
        
        # Si machine_data es un string, intentar parsearlo como JSON
        if isinstance(machine_data, str):
            try:
                import json
                machine_data = json.loads(machine_data)
            except (json.JSONDecodeError, TypeError):
                machine_data = {}
        
        if machine_data and machine_data.get('machines'):
            story.append(Paragraph("DATOS DE MÁQUINAS", self.styles['SectionTitle']))
            story.append(Spacer(1, 10))
            
            machine_headers = ['Máquina', 'Inicio', 'Corte']
            machine_table_data = []
            
            for machine in machine_data.get('machines', []):
                machine_table_data.append([
                    machine.get('machine', ''),
                    machine.get('start', ''),
                    machine.get('cut', '')
                ])
            
            story.append(self.create_professional_table(
                machine_table_data,
                machine_headers,
                [2*inch, 1.5*inch, 1.5*inch]
            ))
            story.append(Spacer(1, 20))
        
        # Observaciones
        story.append(Paragraph("OBSERVACIONES", self.styles['SectionTitle']))
        story.append(Spacer(1, 10))
        story.append(Paragraph(f"<b>Descripción de la Incidencia:</b><br/>{report_data.get('incident_description', 'N/A')}", self.styles['CustomBodyText']))
        story.append(Spacer(1, 20))
        
        # Firma
        story.append(Paragraph("FIRMA DEL TÉCNICO", self.styles['SectionTitle']))
        story.append(Spacer(1, 30))
        story.append(Paragraph("_________________________", self.styles['CustomBodyText']))
        story.append(Paragraph(f"<b>{report_data.get('technician', 'N/A')}</b>", self.styles['CustomBodyText']))
        story.append(Paragraph("Técnico", self.styles['CustomBodyText']))
        
        # Construir PDF
        doc.build(story, onFirstPage=header_callback, onLaterPages=header_callback)
        
        buffer.seek(0)
        return buffer

    def generate_lab_report_pdf(self, report_data):
        """Generar PDF profesional para reporte de laboratorio"""
        # Por ahora, usar el mismo formato que el reporte de calidad
        return self.generate_quality_report_pdf(report_data)

    def generate_supplier_report_pdf(self, report_data):
        """Generar PDF profesional para reporte de proveedor"""
        # Por ahora, usar el mismo formato que el reporte de calidad
        return self.generate_quality_report_pdf(report_data)

    def generate_quality_report_pdf(self, report_data):
        """Generar PDF profesional para reporte de calidad"""
        buffer = io.BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=150,
            bottomMargin=60
        )
        
        def header_callback(canvas, doc):
            self.create_header(canvas, doc)
        
        def footer_callback(canvas, doc):
            self.create_footer(canvas, doc)
        
        story = []
        
        # Título del reporte
        story.append(Paragraph("REPORTE DE CALIDAD", self.styles['CompanyTitle']))
        story.append(Spacer(1, 20))
        
        # Información del reporte
        report_info = [
            ['Número de Reporte:', report_data.get('report_number', 'N/A')],
            ['Fecha de Reporte:', report_data.get('report_date', 'N/A')],
            ['Fecha de Inspección:', report_data.get('inspection_date', 'N/A')],
            ['Ubicación:', report_data.get('inspection_location', 'N/A')],
            ['Responsable:', report_data.get('follow_up_responsible', 'N/A')]
        ]
        
        story.append(self.create_professional_table(
            [[row[1]] for row in report_info],
            ['Información del Reporte'],
            [A4[0] - 100]
        ))
        story.append(Spacer(1, 20))
        
        # Información del producto
        story.append(Paragraph("INFORMACIÓN DEL PRODUCTO", self.styles['SectionTitle']))
        story.append(Spacer(1, 10))
        
        product_data = [
            ['SKU:', report_data.get('product_sku', 'N/A')],
            ['Lote:', report_data.get('product_lot', 'N/A')],
            ['Categoría:', report_data.get('product_category', 'N/A')],
            ['Subcategoría:', report_data.get('product_subcategory', 'N/A')],
            ['Descripción:', report_data.get('product_description', 'N/A')],
            ['Proveedor:', report_data.get('supplier_name', 'N/A')]
        ]
        
        story.append(self.create_professional_table(
            [[row[1]] for row in product_data],
            ['Detalles del Producto'],
            [A4[0] - 100]
        ))
        story.append(Spacer(1, 20))
        
        # Alcance de la inspección
        story.append(Paragraph("ALCANCE DE LA INSPECCIÓN", self.styles['SectionTitle']))
        story.append(Spacer(1, 10))
        story.append(Paragraph(f"<b>Alcance:</b> {report_data.get('inspection_scope', 'N/A')}", self.styles['CustomBodyText']))
        story.append(Paragraph(f"<b>Criterios:</b> {report_data.get('inspection_criteria', 'N/A')}", self.styles['CustomBodyText']))
        story.append(Paragraph(f"<b>Método de Muestreo:</b> {report_data.get('sampling_method', 'N/A')}", self.styles['CustomBodyText']))
        story.append(Paragraph(f"<b>Tamaño de Muestra:</b> {report_data.get('sample_size', 'N/A')}", self.styles['CustomBodyText']))
        story.append(Spacer(1, 20))
        
        # Resultados de las pruebas
        story.append(Paragraph("RESULTADOS DE LAS PRUEBAS", self.styles['SectionTitle']))
        story.append(Spacer(1, 10))
        
        test_results = [
            ['Inspección Visual:', report_data.get('visual_inspection', 'N/A')],
            ['Análisis Dimensional:', report_data.get('dimensional_analysis', 'N/A')],
            ['Pruebas Mecánicas:', report_data.get('mechanical_tests', 'N/A')],
            ['Análisis Químico:', report_data.get('chemical_analysis', 'N/A')],
            ['Otras Pruebas:', report_data.get('other_tests', 'N/A')]
        ]
        
        story.append(self.create_professional_table(
            [[row[1]] for row in test_results],
            ['Tipo de Prueba', 'Resultado'],
            [2*inch, 4*inch]
        ))
        story.append(Spacer(1, 20))
        
        # Conclusiones y recomendaciones
        story.append(Paragraph("CONCLUSIONES Y RECOMENDACIONES", self.styles['SectionTitle']))
        story.append(Spacer(1, 10))
        story.append(Paragraph(f"<b>Conclusiones:</b><br/>{report_data.get('conclusions', 'N/A')}", self.styles['CustomBodyText']))
        story.append(Spacer(1, 10))
        story.append(Paragraph(f"<b>Recomendaciones:</b><br/>{report_data.get('recommendations', 'N/A')}", self.styles['CustomBodyText']))
        story.append(Spacer(1, 20))
        
        # Firma
        story.append(Paragraph("FIRMA DEL RESPONSABLE", self.styles['SectionTitle']))
        story.append(Spacer(1, 30))
        story.append(Paragraph("_________________________", self.styles['CustomBodyText']))
        story.append(Paragraph(f"<b>{report_data.get('follow_up_responsible', 'N/A')}</b>", self.styles['CustomBodyText']))
        story.append(Paragraph("Responsable de Calidad", self.styles['CustomBodyText']))
        
        doc.build(story, onFirstPage=header_callback, onLaterPages=header_callback)
        
        buffer.seek(0)
        return buffer

    def generate_lab_report_pdf(self, report_data):
        """Generar PDF profesional para reporte de laboratorio"""
        # Por ahora, usar el mismo formato que el reporte de calidad
        return self.generate_quality_report_pdf(report_data)

    def generate_supplier_report_pdf(self, report_data):
        """Generar PDF profesional para reporte de proveedor"""
        # Por ahora, usar el mismo formato que el reporte de calidad
        return self.generate_quality_report_pdf(report_data)
