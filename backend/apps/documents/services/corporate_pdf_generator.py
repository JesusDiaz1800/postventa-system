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

class CorporatePDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.primary_color = colors.HexColor('#126FCC')  # Azul corporativo
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
        """Configurar estilos corporativos"""
        # Título principal
        if 'CorporateTitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CorporateTitle',
                parent=self.styles['Heading1'],
                fontSize=24,
                spaceAfter=20,
                alignment=TA_CENTER,
                textColor=self.primary_color,
                fontName='Helvetica-Bold'
            ))
        
        # Subtítulo con fondo azul
        if 'CorporateSubtitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CorporateSubtitle',
                parent=self.styles['Heading2'],
                fontSize=16,
                spaceAfter=15,
                spaceBefore=10,
                textColor=colors.white,
                fontName='Helvetica-Bold',
                alignment=TA_CENTER,
                backColor=self.primary_color,
                borderPadding=8
            ))
        
        # Encabezados de sección
        if 'SectionHeader' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='SectionHeader',
                parent=self.styles['Heading3'],
                fontSize=12,
                spaceAfter=8,
                spaceBefore=15,
                textColor=self.primary_color,
                fontName='Helvetica-Bold',
                alignment=TA_LEFT
            ))
        
        # Texto del cuerpo
        if 'BodyText' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='BodyText',
                parent=self.styles['Normal'],
                fontSize=10,
                spaceAfter=6,
                alignment=TA_LEFT,
                textColor=colors.black,
                fontName='Helvetica',
                leading=12
            ))
        
        # Información de la empresa
        if 'CompanyInfo' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CompanyInfo',
                parent=self.styles['Normal'],
                fontSize=8,
                textColor=colors.black,
                alignment=TA_RIGHT,
                fontName='Helvetica'
            ))

    def create_header(self, canvas_obj, doc):
        canvas_obj.saveState()
        
        # Información de la empresa en la esquina superior derecha
        canvas_obj.setFont('Helvetica-Bold', 10)
        canvas_obj.setFillColor(self.primary_color)
        canvas_obj.drawRightString(doc.width + doc.leftMargin - 10, 
                                 doc.height + doc.topMargin - 20, 
                                 self.company_info['name'])
        
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(colors.black)
        canvas_obj.drawRightString(doc.width + doc.leftMargin - 10, 
                                 doc.height + doc.topMargin - 35, 
                                 self.company_info['address'])
        canvas_obj.drawRightString(doc.width + doc.leftMargin - 10, 
                                 doc.height + doc.topMargin - 50, 
                                 f"Tel: {self.company_info['phone']} | Email: {self.company_info['email']}")
        canvas_obj.drawRightString(doc.width + doc.leftMargin - 10, 
                                 doc.height + doc.topMargin - 65, 
                                 f"RUT: {self.company_info['rut']} | Web: {self.company_info['website']}")
        
        canvas_obj.restoreState()

    def create_footer(self, canvas_obj, doc):
        canvas_obj.saveState()
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(colors.black)
        
        # Línea separadora
        canvas_obj.setStrokeColor(colors.black)
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
        story.append(Paragraph("REPORTE DE VISITA TÉCNICA", self.styles['CorporateTitle']))
        
        # Subtítulo con número de orden
        order_number = report_data.get('order_number', 'N/A')
        story.append(Paragraph(f"N° {order_number}", self.styles['CorporateSubtitle']))
        story.append(Spacer(1, 0.3 * inch))

        # Información del Proyecto
        story.append(Paragraph("INFORMACIÓN DEL PROYECTO", self.styles['SectionHeader']))
        project_data = [
            ['Cliente', str(report_data.get('client_name', 'N/A') or 'N/A')],
            ['Proyecto', str(report_data.get('project_name', 'N/A') or 'N/A')],
            ['Dirección', str(report_data.get('address', 'N/A') or 'N/A')],
            ['Comuna', str(report_data.get('commune', 'N/A') or 'N/A')],
            ['Ciudad', str(report_data.get('city', 'N/A') or 'N/A')],
            ['Fecha de Visita', str(report_data.get('visit_date', 'N/A') or 'N/A')],
        ]
        
        project_table = Table(project_data, colWidths=[2*inch, 4*inch])
        project_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
        ]))
        story.append(project_table)
        story.append(Spacer(1, 0.2 * inch))

        # Personal Involucrado
        story.append(Paragraph("PERSONAL INVOLUCRADO", self.styles['SectionHeader']))
        personnel_data = [
            ['Vendedor', str(report_data.get('salesperson', 'N/A') or 'N/A')],
            ['Técnico', str(report_data.get('technician', 'N/A') or 'N/A')],
        ]
        
        personnel_table = Table(personnel_data, colWidths=[2*inch, 4*inch])
        personnel_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
        ]))
        story.append(personnel_table)
        story.append(Spacer(1, 0.2 * inch))

        # Razón de la Visita
        if report_data.get('visit_reason'):
            story.append(Paragraph("RAZÓN DE LA VISITA", self.styles['SectionHeader']))
            story.append(Paragraph(str(report_data.get('visit_reason', '')), self.styles['BodyText']))
            story.append(Spacer(1, 0.2 * inch))

        # Observaciones generales
        if report_data.get('general_observations'):
            story.append(Paragraph("OBSERVACIONES GENERALES", self.styles['SectionHeader']))
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
            story.append(Paragraph("DATOS DE MÁQUINAS", self.styles['SectionHeader']))
            story.append(Spacer(1, 0.1 * inch))
            
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
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                ('TOPPADDING', (0,0), (-1,-1), 4),
                ('LEFTPADDING', (0,0), (-1,-1), 6),
                ('RIGHTPADDING', (0,0), (-1,-1), 6),
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
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
                story.append(Paragraph(f"{key}: {str(value)}", self.styles['BodyText']))
            story.append(Spacer(1, 0.2 * inch))

        # Firma y fecha
        story.append(Spacer(1, 0.3 * inch))
        story.append(Paragraph("FIRMA DEL TÉCNICO", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph("_________________________", self.styles['BodyText']))
        story.append(Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", self.styles['BodyText']))
        story.append(Spacer(1, 0.1 * inch))
        story.append(Paragraph("Jesus Enrique Diaz Rios", self.styles['BodyText']))
        story.append(Paragraph("Ing. Analista de Control de Calidad", self.styles['BodyText']))
        story.append(Paragraph("Polifusión S.A.", self.styles['BodyText']))
        
        # Construir PDF
        doc.build(story, onFirstPage=self.create_header, onLaterPages=self.create_header)
        
        buffer.seek(0)
        return buffer

    def generate_lab_report_pdf(self, report_data):
        """Generar PDF corporativo para reporte de laboratorio"""
        return self.generate_visit_report_pdf(report_data)

    def generate_supplier_report_pdf(self, report_data):
        """Generar PDF corporativo para reporte de proveedor"""
        return self.generate_visit_report_pdf(report_data)

    def generate_quality_report_pdf(self, report_data):
        """Generar PDF corporativo para reporte de calidad"""
        return self.generate_visit_report_pdf(report_data)