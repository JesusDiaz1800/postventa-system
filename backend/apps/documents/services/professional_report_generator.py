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
from reportlab.graphics.shapes import Drawing, Rect, Line
from reportlab.graphics import renderPDF
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class ProfessionalReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.primary_color = colors.HexColor('#126FCC')  # Azul corporativo
        self.secondary_color = colors.HexColor('#3B82F6')  # Azul claro
        self.success_color = colors.HexColor('#10B981')  # Verde
        self.warning_color = colors.HexColor('#F59E0B')  # Amarillo
        self.error_color = colors.HexColor('#EF4444')  # Rojo
        self.muted_color = colors.HexColor('#6B7280')  # Gris
        self.border_color = colors.HexColor('#E5E7EB')  # Gris claro
        self.bg_muted = colors.HexColor('#F8FAFC')  # Fondo gris muy claro
        self.setup_custom_styles()
        self.company_info = {
            'name': 'POLIFUSIÓN S.A.',
            'address': 'Cacique Colin 2525, Lampa, Región Metropolitana',
            'phone': '(2) 2387 5000',
            'email': 'info@polifusion.cl',
            'website': 'www.polifusion.cl',
            'rut': '76.000.000-1'
        }

    def setup_custom_styles(self):
        """Configurar estilos profesionales modernos"""
        # Título principal del reporte
        if 'ReportTitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='ReportTitle',
                parent=self.styles['Heading1'],
                fontSize=28,
                spaceAfter=15,
                alignment=TA_CENTER,
                textColor=self.primary_color,
                fontName='Helvetica-Bold',
                leading=32
            ))
        
        # Subtítulo del producto
        if 'ProductSubtitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='ProductSubtitle',
                parent=self.styles['Heading2'],
                fontSize=18,
                spaceAfter=20,
                alignment=TA_CENTER,
                textColor=colors.black,
                fontName='Helvetica-Bold',
                leading=22
            ))
        
        # Encabezados de sección con línea inferior
        if 'SectionTitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='SectionTitle',
                parent=self.styles['Heading3'],
                fontSize=16,
                spaceAfter=8,
                spaceBefore=20,
                textColor=self.primary_color,
                fontName='Helvetica-Bold',
                alignment=TA_LEFT,
                leading=20
            ))
        
        # Texto del cuerpo
        if 'BodyText' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='BodyText',
                parent=self.styles['Normal'],
                fontSize=11,
                spaceAfter=6,
                alignment=TA_LEFT,
                textColor=colors.black,
                fontName='Helvetica',
                leading=14
            ))
        
        # Texto de tarjetas de estadísticas
        if 'StatCardTitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='StatCardTitle',
                parent=self.styles['Normal'],
                fontSize=9,
                spaceAfter=2,
                textColor=self.muted_color,
                fontName='Helvetica',
                alignment=TA_LEFT
            ))
        
        # Valor de estadísticas
        if 'StatCardValue' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='StatCardValue',
                parent=self.styles['Normal'],
                fontSize=18,
                spaceAfter=4,
                textColor=colors.black,
                fontName='Helvetica-Bold',
                alignment=TA_LEFT
            ))
        
        # Información de la empresa
        if 'CompanyInfo' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CompanyInfo',
                parent=self.styles['Normal'],
                fontSize=9,
                textColor=colors.black,
                alignment=TA_RIGHT,
                fontName='Helvetica'
            ))
        
        # Firma
        if 'Signature' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='Signature',
                parent=self.styles['Normal'],
                fontSize=12,
                textColor=colors.black,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            ))

    def create_header(self, canvas_obj, doc):
        canvas_obj.saveState()
        
        # Logo en la esquina izquierda
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'logo.svg')
        if os.path.exists(logo_path):
            try:
                logo = ImageReader(logo_path)
                logo_width = 1.0 * inch
                logo_height = logo_width * (logo.getSize()[1] / logo.getSize()[0])
                canvas_obj.drawImage(logo, doc.leftMargin, doc.height + doc.topMargin - logo_height - 0.2*inch, 
                                   width=logo_width, height=logo_height, mask='auto')
            except Exception as e:
                logger.error(f"Error loading logo: {e}")
        
        # Información de la empresa en la esquina derecha
        canvas_obj.setFont('Helvetica-Bold', 10)
        canvas_obj.setFillColor(colors.black)
        canvas_obj.drawRightString(doc.width + doc.leftMargin - 10, 
                                 doc.height + doc.topMargin - 20, 
                                 self.company_info['name'])
        
        canvas_obj.setFont('Helvetica', 9)
        canvas_obj.drawRightString(doc.width + doc.leftMargin - 10, 
                                 doc.height + doc.topMargin - 35, 
                                 self.company_info['address'])
        canvas_obj.drawRightString(doc.width + doc.leftMargin - 10, 
                                 doc.height + doc.topMargin - 50, 
                                 f"Fecha de Emisión: {datetime.now().strftime('%d/%m/%Y')}")
        
        # Línea separadora inferior
        canvas_obj.setStrokeColor(self.primary_color)
        canvas_obj.setLineWidth(2)
        canvas_obj.line(doc.leftMargin, doc.height + doc.topMargin - 0.8*inch, 
                       doc.width + doc.leftMargin, doc.height + doc.topMargin - 0.8*inch)
        
        canvas_obj.restoreState()

    def create_footer(self, canvas_obj, doc):
        canvas_obj.saveState()
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(colors.black)
        
        # Línea separadora superior
        canvas_obj.setStrokeColor(self.border_color)
        canvas_obj.setLineWidth(1)
        canvas_obj.line(doc.leftMargin, doc.bottomMargin + 60, 
                       doc.width + doc.leftMargin, doc.bottomMargin + 60)
        
        # Información de la empresa en el pie
        canvas_obj.drawRightString(doc.width + doc.leftMargin - 10, doc.bottomMargin + 40, 
                                 self.company_info['name'])
        canvas_obj.drawRightString(doc.width + doc.leftMargin - 10, doc.bottomMargin + 30, 
                                 self.company_info['address'])
        canvas_obj.drawRightString(doc.width + doc.leftMargin - 10, doc.bottomMargin + 20, 
                                 f"Tel: {self.company_info['phone']} | Email: {self.company_info['email']}")
        canvas_obj.drawRightString(doc.width + doc.leftMargin - 10, doc.bottomMargin + 10, 
                                 f"RUT: {self.company_info['rut']} | Web: {self.company_info['website']}")
        
        canvas_obj.restoreState()

    def create_stat_card(self, title, value, unit, story, card_color=None):
        """Crear una tarjeta de estadística moderna"""
        # Crear tabla para la tarjeta
        card_data = [
            [Paragraph(f"{title}", self.styles['StatCardTitle']), ""],
            [Paragraph(f"{value} <font color='{self.muted_color}'>{unit}</font>", self.styles['StatCardValue']), ""]
        ]
        
        card_table = Table(card_data, colWidths=[2*inch, 0.5*inch])
        
        # Estilos de la tarjeta
        table_style = [
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 12),
            ('RIGHTPADDING', (0,0), (-1,-1), 12),
            ('BACKGROUND', (0,0), (-1,-1), self.bg_muted),
            ('GRID', (0,0), (-1,-1), 0.5, self.border_color),
        ]
        
        if card_color:
            table_style.append(('BACKGROUND', (0,0), (-1,-1), card_color))
        
        card_table.setStyle(TableStyle(table_style))
        story.append(card_table)

    def create_section_title(self, title, story):
        """Crear un título de sección con línea inferior"""
        story.append(Paragraph(title, self.styles['SectionTitle']))
        # Agregar línea inferior
        story.append(Spacer(1, 0.1 * inch))

    def generate_visit_report_pdf(self, report_data):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=3*cm,
            bottomMargin=3*cm
        )
        story = []

        # Título principal
        story.append(Paragraph("REPORTE DE VISITA TÉCNICA", self.styles['ReportTitle']))
        
        # Subtítulo con información del proyecto
        project_name = report_data.get('project_name', 'N/A')
        story.append(Paragraph(project_name, self.styles['ProductSubtitle']))
        story.append(Spacer(1, 0.3 * inch))

        # Información del Proyecto
        self.create_section_title("INFORMACIÓN DEL PROYECTO", story)
        
        project_info = {
            'Cliente': report_data.get('client_name'),
            'Proyecto': report_data.get('project_name'),
            'Dirección': report_data.get('address'),
            'Comuna': report_data.get('commune'),
            'Ciudad': report_data.get('city'),
            'Fecha de Visita': report_data.get('visit_date'),
        }
        
        # Crear tabla de información del proyecto
        project_data = []
        for key, value in project_info.items():
            if value is not None and str(value).strip():
                project_data.append([
                    Paragraph(f"<b>{key}:</b>", self.styles['BodyText']),
                    Paragraph(str(value), self.styles['BodyText'])
                ])
        
        if project_data:
            project_table = Table(project_data, colWidths=[2*inch, 4*inch])
            project_table.setStyle(TableStyle([
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('LEFTPADDING', (0,0), (-1,-1), 8),
                ('RIGHTPADDING', (0,0), (-1,-1), 8),
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
                ('FONTSIZE', (0,0), (-1,-1), 11),
            ]))
            story.append(project_table)
            story.append(Spacer(1, 0.2 * inch))

        # Personal Involucrado
        self.create_section_title("PERSONAL INVOLUCRADO", story)
        
        personnel_info = {
            'Vendedor': report_data.get('salesperson'),
            'Técnico': report_data.get('technician'),
        }
        
        personnel_data = []
        for key, value in personnel_info.items():
            if value is not None and str(value).strip():
                personnel_data.append([
                    Paragraph(f"<b>{key}:</b>", self.styles['BodyText']),
                    Paragraph(str(value), self.styles['BodyText'])
                ])
        
        if personnel_data:
            personnel_table = Table(personnel_data, colWidths=[2*inch, 4*inch])
            personnel_table.setStyle(TableStyle([
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('LEFTPADDING', (0,0), (-1,-1), 8),
                ('RIGHTPADDING', (0,0), (-1,-1), 8),
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
                ('FONTSIZE', (0,0), (-1,-1), 11),
            ]))
            story.append(personnel_table)
            story.append(Spacer(1, 0.2 * inch))

        # Razón de la Visita
        if report_data.get('visit_reason'):
            self.create_section_title("RAZÓN DE LA VISITA", story)
            story.append(Paragraph(str(report_data.get('visit_reason', '')), self.styles['BodyText']))
            story.append(Spacer(1, 0.2 * inch))

        # Observaciones generales
        if report_data.get('general_observations'):
            self.create_section_title("OBSERVACIONES GENERALES", story)
            story.append(Paragraph(str(report_data.get('general_observations', '')), self.styles['BodyText']))
            story.append(Spacer(1, 0.2 * inch))
        
        # Datos de máquinas (si existen)
        machine_data = report_data.get('machine_data', {})
        
        if isinstance(machine_data, str):
            try:
                machine_data = json.loads(machine_data)
            except (json.JSONDecodeError, TypeError):
                machine_data = {}

        if machine_data and machine_data.get('machines'):
            self.create_section_title("DATOS DE MÁQUINAS", story)
            
            machine_headers = ['Máquina', 'Inicio', 'Corte']
            machine_table_data = [machine_headers]
            
            for machine in machine_data['machines']:
                machine_table_data.append([
                    str(machine.get('machine_name', 'N/A')),
                    str(machine.get('start_time', 'N/A')),
                    str(machine.get('cut_time', 'N/A'))
                ])
            
            machine_table = Table(machine_table_data, colWidths=[3*inch, 2*inch, 2*inch])
            machine_table.setStyle(TableStyle([
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('LEFTPADDING', (0,0), (-1,-1), 8),
                ('RIGHTPADDING', (0,0), (-1,-1), 8),
                ('GRID', (0,0), (-1,-1), 0.5, self.border_color),
                ('BACKGROUND', (0,0), (-1,0), self.bg_muted),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
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
            self.create_section_title("OBSERVACIONES TÉCNICAS", story)
            for key, value in filtered_observations.items():
                story.append(Paragraph(f"<b>{key}:</b> {str(value)}", self.styles['BodyText']))
                story.append(Spacer(1, 0.1 * inch))
            story.append(Spacer(1, 0.2 * inch))

        # Sección de firma moderna
        story.append(Spacer(1, 0.5 * inch))
        
        # Línea separadora
        story.append(Spacer(1, 0.2 * inch))
        
        # Área de firma
        signature_data = [
            ['', ''],
            ['', ''],
            ['', ''],
            ['', ''],
        ]
        
        signature_table = Table(signature_data, colWidths=[3*inch, 3*inch])
        signature_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 20),
            ('TOPPADDING', (0,0), (-1,-1), 20),
            ('LEFTPADDING', (0,0), (-1,-1), 20),
            ('RIGHTPADDING', (0,0), (-1,-1), 20),
            ('GRID', (0,0), (-1,-1), 0.5, self.border_color),
            ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ]))
        story.append(signature_table)
        
        # Información del firmante
        story.append(Spacer(1, 0.1 * inch))
        story.append(Paragraph("Maximiliano Miranda Valdés", self.styles['Signature']))
        story.append(Paragraph("Ing. Analista de Control de Calidad", self.styles['BodyText']))
        story.append(Paragraph("Polifusión S.A.", self.styles['BodyText']))
        
        # Construir PDF
        doc.build(story, onFirstPage=self.create_header, onLaterPages=self.create_header)
        
        buffer.seek(0)
        return buffer

    def generate_lab_report_pdf(self, report_data):
        """Generar PDF profesional para reporte de laboratorio"""
        return self.generate_visit_report_pdf(report_data)

    def generate_supplier_report_pdf(self, report_data):
        """Generar PDF profesional para reporte de proveedor"""
        return self.generate_visit_report_pdf(report_data)

    def generate_quality_report_pdf(self, report_data):
        """Generar PDF profesional para reporte de calidad"""
        return self.generate_visit_report_pdf(report_data)
