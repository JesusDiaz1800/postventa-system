import os
import io
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, Frame, PageTemplate
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class ModernPDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.primary_color = colors.HexColor('#126FCC')  # Azul corporativo
        self.secondary_color = colors.HexColor('#3B82F6')  # Azul claro
        self.text_color = colors.HexColor('#1F2937')  # Gris oscuro
        self.accent_color = colors.HexColor('#F59E0B')  # Naranja
        self.success_color = colors.HexColor('#10B981')  # Verde
        self.warning_color = colors.HexColor('#F59E0B')  # Amarillo
        self.error_color = colors.HexColor('#EF4444')  # Rojo
        self.setup_custom_styles()
        self.company_info = {
            'name': 'POLIFUSIÓN S.A.',
            'address': 'Cacique Colin 2525, Lampa, Región Metropolitana',
            'phone': '(2) 2387 5000',
            'email': 'info@polifusion.cl',
            'website': 'www.polifusion.cl',
            'rut': '76.000.000-1'
        }
        self.logo_path = os.path.join(settings.BASE_DIR, 'static', 'logo.svg')
        if not os.path.exists(self.logo_path):
            logger.warning(f"Logo not found at {self.logo_path}")
            self.logo_path = None

    def setup_custom_styles(self):
        """Configurar estilos personalizados para el PDF moderno"""
        # Estilo para el título principal
        if 'ModernTitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='ModernTitle',
                parent=self.styles['Heading1'],
                fontSize=28,
                spaceAfter=20,
                alignment=TA_CENTER,
                textColor=self.primary_color,
                fontName='Helvetica-Bold',
                leading=32
            ))
        
        # Estilo para subtítulos
        if 'ModernSubtitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='ModernSubtitle',
                parent=self.styles['Heading2'],
                fontSize=18,
                spaceAfter=15,
                spaceBefore=25,
                textColor=self.primary_color,
                fontName='Helvetica-Bold',
                alignment=TA_LEFT,
                borderWidth=1,
                borderColor=self.primary_color,
                borderPadding=8,
                backColor=colors.HexColor('#F8FAFC')
            ))
        
        # Estilo para encabezados de sección
        if 'SectionHeader' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='SectionHeader',
                parent=self.styles['Heading3'],
                fontSize=14,
                spaceAfter=8,
                spaceBefore=20,
                textColor=self.primary_color,
                fontName='Helvetica-Bold',
                alignment=TA_LEFT
            ))
        
        # Estilo para texto del cuerpo
        if 'ModernBodyText' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='ModernBodyText',
                parent=self.styles['Normal'],
                fontSize=11,
                spaceAfter=6,
                alignment=TA_JUSTIFY,
                textColor=self.text_color,
                fontName='Helvetica',
                leading=14
            ))
        
        # Estilo para etiquetas de campo
        if 'FieldLabel' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='FieldLabel',
                parent=self.styles['Normal'],
                fontSize=10,
                spaceAfter=2,
                textColor=self.primary_color,
                fontName='Helvetica-Bold',
                alignment=TA_LEFT
            ))
        
        # Estilo para valores de campo
        if 'FieldValue' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='FieldValue',
                parent=self.styles['Normal'],
                fontSize=11,
                spaceAfter=6,
                textColor=self.text_color,
                fontName='Helvetica',
                alignment=TA_LEFT
            ))
        
        # Estilo para información de la empresa
        if 'CompanyInfo' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CompanyInfo',
                parent=self.styles['Normal'],
                fontSize=9,
                textColor=colors.grey,
                alignment=TA_RIGHT,
                fontName='Helvetica'
            ))
        
        # Estilo para firma
        if 'Signature' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='Signature',
                parent=self.styles['Normal'],
                fontSize=10,
                textColor=self.text_color,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            ))

    def create_header(self, canvas_obj, doc):
        canvas_obj.saveState()
        
        # Fondo del encabezado
        canvas_obj.setFillColor(colors.HexColor('#F8FAFC'))
        canvas_obj.rect(doc.leftMargin, doc.height + doc.topMargin - 1.5*inch, 
                      doc.width, 1.5*inch, fill=1, stroke=0)
        
        # Logo
        if self.logo_path:
            try:
                logo = ImageReader(self.logo_path)
                logo_width = 1.0 * inch
                logo_height = logo_width * (logo.getSize()[1] / logo.getSize()[0])
                canvas_obj.drawImage(logo, doc.leftMargin + 0.2*inch, 
                                   doc.height + doc.topMargin - logo_height - 0.1*inch, 
                                   width=logo_width, height=logo_height, mask='auto')
            except Exception as e:
                logger.error(f"Error loading or drawing logo: {e}")
        
        # Información de la empresa (lado derecho)
        canvas_obj.setFillColor(self.primary_color)
        canvas_obj.setFont('Helvetica-Bold', 12)
        canvas_obj.drawRightString(doc.width + doc.leftMargin - 0.2*inch, 
                                 doc.height + doc.topMargin - 0.3*inch, 
                                 self.company_info['name'])
        
        canvas_obj.setFillColor(self.text_color)
        canvas_obj.setFont('Helvetica', 9)
        canvas_obj.drawRightString(doc.width + doc.leftMargin - 0.2*inch, 
                                 doc.height + doc.topMargin - 0.5*inch, 
                                 self.company_info['address'])
        canvas_obj.drawRightString(doc.width + doc.leftMargin - 0.2*inch, 
                                 doc.height + doc.topMargin - 0.7*inch, 
                                 f"Tel: {self.company_info['phone']} | Email: {self.company_info['email']}")
        canvas_obj.drawRightString(doc.width + doc.leftMargin - 0.2*inch, 
                                 doc.height + doc.topMargin - 0.9*inch, 
                                 f"RUT: {self.company_info['rut']} | Web: {self.company_info['website']}")
        
        # Línea separadora
        canvas_obj.setStrokeColor(self.primary_color)
        canvas_obj.setLineWidth(2)
        canvas_obj.line(doc.leftMargin, doc.height + doc.topMargin - 1.1*inch, 
                       doc.width + doc.leftMargin, doc.height + doc.topMargin - 1.1*inch)
        
        canvas_obj.restoreState()

    def create_footer(self, canvas_obj, doc):
        canvas_obj.saveState()
        canvas_obj.setFont('Helvetica', 9)
        canvas_obj.setFillColor(colors.grey)
        
        # Línea superior
        canvas_obj.setStrokeColor(self.primary_color)
        canvas_obj.setLineWidth(1)
        canvas_obj.line(doc.leftMargin, doc.bottomMargin + 0.8*inch, 
                       doc.width + doc.leftMargin, doc.bottomMargin + 0.8*inch)
        
        # Fecha de generación
        date_str = datetime.now().strftime('%d/%m/%Y %H:%M')
        canvas_obj.drawString(doc.leftMargin, doc.bottomMargin + 0.6*inch, 
                            f"Generado el: {date_str}")
        
        # Número de página
        page_number_text = f"Página {doc.page}"
        canvas_obj.drawRightString(doc.width + doc.leftMargin, doc.bottomMargin + 0.6*inch, 
                                 page_number_text)
        
        # Información de contacto en el pie de página
        canvas_obj.drawCentredString(doc.width / 2.0 + doc.leftMargin, doc.bottomMargin + 0.4*inch, 
                                   f"{self.company_info['name']} - {self.company_info['address']}")
        
        canvas_obj.restoreState()

    def create_info_card(self, title, data_dict, story):
        """Crear una tarjeta de información con estilo moderno"""
        story.append(Paragraph(title, self.styles['SectionHeader']))
        
        # Crear tabla con datos
        table_data = []
        for key, value in data_dict.items():
            if value is not None and str(value).strip():
                table_data.append([
                    Paragraph(f"<b>{key}:</b>", self.styles['FieldLabel']),
                    Paragraph(str(value), self.styles['FieldValue'])
                ])
        
        if table_data:
            info_table = Table(table_data, colWidths=[2.5*inch, 4.5*inch])
            info_table.setStyle(TableStyle([
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                ('TOPPADDING', (0,0), (-1,-1), 4),
                ('LEFTPADDING', (0,0), (-1,-1), 8),
                ('RIGHTPADDING', (0,0), (-1,-1), 8),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F8FAFC')),
                ('TEXTCOLOR', (0,0), (-1,0), self.primary_color),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 10),
            ]))
            story.append(info_table)
            story.append(Spacer(1, 0.2 * inch))

    def generate_visit_report_pdf(self, report_data):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=3*cm,
            bottomMargin=2.5*cm
        )
        story = []

        # Título principal
        order_number = report_data.get('order_number', 'N/A')
        story.append(Paragraph(f"REPORTE DE VISITA TÉCNICA", self.styles['ModernTitle']))
        story.append(Paragraph(f"N° {order_number}", self.styles['ModernSubtitle']))
        story.append(Spacer(1, 0.3 * inch))

        # Información del Proyecto
        project_info = {
            'Cliente': report_data.get('client_name'),
            'Proyecto': report_data.get('project_name'),
            'Dirección': report_data.get('address'),
            'Comuna': report_data.get('commune'),
            'Ciudad': report_data.get('city'),
            'Fecha de Visita': report_data.get('visit_date'),
        }
        self.create_info_card("INFORMACIÓN DEL PROYECTO", project_info, story)

        # Personal Involucrado
        personnel_info = {
            'Vendedor': report_data.get('salesperson'),
            'Técnico': report_data.get('technician'),
        }
        self.create_info_card("PERSONAL INVOLUCRADO", personnel_info, story)

        # Razón de la Visita
        if report_data.get('visit_reason'):
            story.append(Paragraph("RAZÓN DE LA VISITA", self.styles['SectionHeader']))
            story.append(Paragraph(str(report_data.get('visit_reason', '')), self.styles['ModernBodyText']))
            story.append(Spacer(1, 0.2 * inch))

        # Observaciones generales
        if report_data.get('general_observations'):
            story.append(Paragraph("OBSERVACIONES GENERALES", self.styles['SectionHeader']))
            story.append(Paragraph(str(report_data.get('general_observations', '')), self.styles['ModernBodyText']))
            story.append(Spacer(1, 0.2 * inch))
        
        # Datos de máquinas (si existen)
        machine_data = report_data.get('machine_data', {})
        
        # Si machine_data es un string, intentar parsearlo como JSON
        if isinstance(machine_data, str):
            try:
                machine_data = json.loads(machine_data)
            except (json.JSONDecodeError, TypeError):
                machine_data = {}

        if machine_data and machine_data.get('machines'):
            story.append(Paragraph("DATOS DE MÁQUINAS", self.styles['SectionHeader']))
            story.append(Spacer(1, 0.1 * inch))
            
            machine_headers = [
                Paragraph("<b>Máquina</b>", self.styles['FieldLabel']),
                Paragraph("<b>Inicio</b>", self.styles['FieldLabel']),
                Paragraph("<b>Corte</b>", self.styles['FieldLabel'])
            ]
            machine_table_data = [machine_headers]
            
            for machine in machine_data['machines']:
                machine_table_data.append([
                    Paragraph(str(machine.get('machine_name', 'N/A')), self.styles['ModernBodyText']),
                    Paragraph(str(machine.get('start_time', 'N/A')), self.styles['ModernBodyText']),
                    Paragraph(str(machine.get('cut_time', 'N/A')), self.styles['ModernBodyText'])
                ])
            
            machine_table = Table(machine_table_data, colWidths=[3*inch, 2*inch, 2*inch])
            machine_table.setStyle(TableStyle([
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('LEFTPADDING', (0,0), (-1,-1), 8),
                ('RIGHTPADDING', (0,0), (-1,-1), 8),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
                ('BACKGROUND', (0,0), (-1,0), self.primary_color),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 10),
            ]))
            story.append(machine_table)
            story.append(Spacer(1, 0.2 * inch))

        # Observaciones Técnicas
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
            story.append(Paragraph("OBSERVACIONES TÉCNICAS", self.styles['SectionHeader']))
            for key, value in filtered_observations.items():
                story.append(Paragraph(f"<b>{key}:</b>", self.styles['FieldLabel']))
                story.append(Paragraph(str(value), self.styles['ModernBodyText']))
                story.append(Spacer(1, 0.1 * inch))
            story.append(Spacer(1, 0.2 * inch))

        # Firma y fecha
        story.append(Spacer(1, 0.5 * inch))
        story.append(Paragraph("FIRMA DEL TÉCNICO", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.3 * inch))
        
        # Línea para firma
        story.append(Paragraph("_" * 50, self.styles['ModernBodyText']))
        story.append(Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", self.styles['ModernBodyText']))
        story.append(Spacer(1, 0.2 * inch))
        
        # Información del firmante
        story.append(Paragraph("Jesus Enrique Diaz Rios", self.styles['Signature']))
        story.append(Paragraph("Ing. Analista de Control de Calidad", self.styles['ModernBodyText']))
        story.append(Paragraph("Polifusión S.A.", self.styles['ModernBodyText']))
        
        # Construir PDF
        doc.build(story, onFirstPage=self.create_header, onLaterPages=self.create_header)
        
        buffer.seek(0)
        return buffer

    def generate_lab_report_pdf(self, report_data):
        """Generar PDF moderno para reporte de laboratorio"""
        return self.generate_visit_report_pdf(report_data)

    def generate_supplier_report_pdf(self, report_data):
        """Generar PDF moderno para reporte de proveedor"""
        return self.generate_visit_report_pdf(report_data)

    def generate_quality_report_pdf(self, report_data):
        """Generar PDF moderno para reporte de calidad"""
        return self.generate_visit_report_pdf(report_data)
