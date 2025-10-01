"""
Servicio profesional de generación de PDFs con logo de empresa
"""
import os
import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from django.conf import settings
from django.core.files.storage import default_storage
import logging

logger = logging.getLogger(__name__)

class ProfessionalPDFGenerator:
    """Generador de PDFs profesionales con logo de empresa"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        self.logo_path = self.get_logo_path()
    
    def get_logo_path(self):
        """Obtiene la ruta del logo de la empresa"""
        logo_paths = [
            os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.png'),
            os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.jpg'),
            os.path.join(settings.BASE_DIR, 'static', 'images', 'polifusion_logo.png'),
            os.path.join(settings.BASE_DIR, 'static', 'images', 'polifusion_logo.jpg'),
        ]
        
        for path in logo_paths:
            if os.path.exists(path):
                return path
        
        # Si no encuentra logo, crear uno temporal
        return self.create_temp_logo()
    
    def create_temp_logo(self):
        """Crea un logo temporal si no existe uno"""
        try:
            from reportlab.graphics.shapes import Drawing, Rect, String
            from reportlab.graphics import renderPDF
            
            # Crear directorio si no existe
            logo_dir = os.path.join(settings.BASE_DIR, 'static', 'images')
            os.makedirs(logo_dir, exist_ok=True)
            
            # Crear logo temporal
            logo_path = os.path.join(logo_dir, 'temp_logo.png')
            
            # Crear un logo simple con texto
            d = Drawing(200, 60)
            d.add(Rect(0, 0, 200, 60, fillColor=colors.blue, strokeColor=colors.blue))
            d.add(String(100, 30, "POLIFUSION", textAnchor="middle", fontSize=16, fillColor=colors.white))
            
            # Guardar como imagen
            renderPDF.drawToFile(d, logo_path)
            return logo_path
            
        except Exception as e:
            logger.warning(f"No se pudo crear logo temporal: {e}")
            return None
    
    def setup_custom_styles(self):
        """Configura estilos personalizados para los documentos"""
        # Estilo para el título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1e40af'),  # Azul
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para subtítulos
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#7c3aed'),  # Púrpura
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para encabezados de sección
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceAfter=8,
            spaceBefore=16,
            textColor=colors.HexColor('#059669'),  # Verde
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=colors.HexColor('#059669'),
            borderPadding=8,
            backColor=colors.HexColor('#f0fdf4')
        ))
        
        # Estilo para texto normal
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
        
        # Estilo para información de contacto
        self.styles.add(ParagraphStyle(
            name='ContactInfo',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=4,
            alignment=TA_LEFT,
            fontName='Helvetica'
        ))
    
    def create_header(self, story, title, subtitle=None):
        """Crea el encabezado del documento con logo"""
        # Logo de la empresa
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                logo = Image(self.logo_path, width=2*inch, height=0.8*inch)
                logo.hAlign = 'CENTER'
                story.append(logo)
                story.append(Spacer(1, 0.2*inch))
            except Exception as e:
                logger.warning(f"Error al cargar logo: {e}")
        
        # Título del documento
        story.append(Paragraph(title, self.styles['CustomTitle']))
        
        # Subtítulo si se proporciona
        if subtitle:
            story.append(Paragraph(subtitle, self.styles['CustomSubtitle']))
        
        story.append(Spacer(1, 0.3*inch))
    
    def create_footer_info(self, story, incident_data=None):
        """Crea información del pie de página"""
        # Información de la empresa
        company_info = [
            ["<b>POLIFUSION S.A.</b>", f"<b>Fecha de Generación:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}"],
            ["Sistema de Postventa", f"<b>Usuario:</b> {incident_data.get('created_by', 'Sistema') if incident_data else 'Sistema'}"],
            ["Control de Calidad", f"<b>Documento:</b> {incident_data.get('document_type', 'Reporte') if incident_data else 'Reporte'}"]
        ]
        
        table = Table(company_info, colWidths=[3*inch, 3*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#374151')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.2*inch))
    
    def create_incident_info_table(self, story, incident_data):
        """Crea tabla con información de la incidencia"""
        if not incident_data:
            return
        
        # Datos de la incidencia
        incident_info = [
            ["<b>INFORMACIÓN DE LA INCIDENCIA</b>", ""],
            ["<b>Código:</b>", incident_data.get('code', 'N/A')],
            ["<b>Cliente:</b>", incident_data.get('cliente', 'N/A')],
            ["<b>Obra:</b>", incident_data.get('obra', 'N/A')],
            ["<b>Proveedor:</b>", incident_data.get('provider', 'N/A')],
            ["<b>Categoría:</b>", incident_data.get('categoria', 'N/A')],
            ["<b>Subcategoría:</b>", incident_data.get('subcategoria', 'N/A')],
            ["<b>Prioridad:</b>", incident_data.get('prioridad', 'N/A')],
            ["<b>Estado:</b>", incident_data.get('estado', 'N/A')],
            ["<b>Fecha de Detección:</b>", incident_data.get('fecha_deteccion', 'N/A')],
            ["<b>Hora de Detección:</b>", incident_data.get('hora_deteccion', 'N/A')],
        ]
        
        # Agregar campos adicionales si existen
        if incident_data.get('sku'):
            incident_info.append(["<b>SKU:</b>", incident_data.get('sku')])
        if incident_data.get('lote'):
            incident_info.append(["<b>Lote:</b>", incident_data.get('lote')])
        if incident_data.get('factura_num'):
            incident_info.append(["<b>N° Factura:</b>", incident_data.get('factura_num')])
        if incident_data.get('pedido_num'):
            incident_info.append(["<b>N° Pedido:</b>", incident_data.get('pedido_num')])
        
        table = Table(incident_info, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.3*inch))
    
    def create_content_section(self, story, title, content):
        """Crea una sección de contenido"""
        if not content:
            return
        
        # Título de la sección
        story.append(Paragraph(title, self.styles['SectionHeader']))
        
        # Contenido
        if isinstance(content, list):
            for item in content:
                story.append(Paragraph(f"• {item}", self.styles['CustomNormal']))
        else:
            story.append(Paragraph(content, self.styles['CustomNormal']))
        
        story.append(Spacer(1, 0.2*inch))
    
    def generate_visit_report_pdf(self, report_data, incident_data=None):
        """Genera PDF para reporte de visita"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                              rightMargin=72, leftMargin=72, 
                              topMargin=72, bottomMargin=18)
        
        story = []
        
        # Encabezado
        self.create_header(story, "REPORTE DE VISITA TÉCNICA", "Sistema de Postventa - Polifusion")
        
        # Información de la empresa
        self.create_footer_info(story, incident_data)
        
        # Información de la incidencia si existe
        if incident_data:
            self.create_incident_info_table(story, incident_data)
        
        # Información del reporte
        report_info = [
            ["<b>INFORMACIÓN DEL REPORTE</b>", ""],
            ["<b>Número de Reporte:</b>", report_data.get('report_number', 'N/A')],
            ["<b>Proyecto:</b>", report_data.get('project_name', 'N/A')],
            ["<b>Ubicación:</b>", report_data.get('location', 'N/A')],
            ["<b>Fecha de Visita:</b>", report_data.get('visit_date', 'N/A')],
            ["<b>Técnico Responsable:</b>", report_data.get('technician_name', 'N/A')],
            ["<b>Cliente:</b>", report_data.get('client_name', 'N/A')],
            ["<b>Contacto Cliente:</b>", report_data.get('client_contact', 'N/A')],
        ]
        
        table = Table(report_info, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c3aed')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#faf5ff')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e9d5ff')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.3*inch))
        
        # Secciones de contenido
        self.create_content_section(story, "OBJETIVO DE LA VISITA", report_data.get('objective', ''))
        self.create_content_section(story, "OBSERVACIONES TÉCNICAS", report_data.get('observations', ''))
        self.create_content_section(story, "ACCIONES REALIZADAS", report_data.get('actions_taken', ''))
        self.create_content_section(story, "RECOMENDACIONES", report_data.get('recommendations', ''))
        self.create_content_section(story, "CONCLUSIONES", report_data.get('conclusions', ''))
        
        # Construir PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_lab_report_pdf(self, report_data, incident_data=None):
        """Genera PDF para informe de laboratorio"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                              rightMargin=72, leftMargin=72, 
                              topMargin=72, bottomMargin=18)
        
        story = []
        
        # Encabezado
        self.create_header(story, "INFORME DE LABORATORIO", "Análisis Técnico - Polifusion")
        
        # Información de la empresa
        self.create_footer_info(story, incident_data)
        
        # Información de la incidencia si existe
        if incident_data:
            self.create_incident_info_table(story, incident_data)
        
        # Información del informe
        report_info = [
            ["<b>INFORMACIÓN DEL INFORME</b>", ""],
            ["<b>Número de Informe:</b>", report_data.get('report_number', 'N/A')],
            ["<b>Muestra:</b>", report_data.get('sample_id', 'N/A')],
            ["<b>Tipo de Análisis:</b>", report_data.get('analysis_type', 'N/A')],
            ["<b>Fecha de Recepción:</b>", report_data.get('received_date', 'N/A')],
            ["<b>Fecha de Análisis:</b>", report_data.get('analysis_date', 'N/A')],
            ["<b>Analista:</b>", report_data.get('analyst_name', 'N/A')],
            ["<b>Método Utilizado:</b>", report_data.get('method_used', 'N/A')],
        ]
        
        table = Table(report_info, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0fdf4')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bbf7d0')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.3*inch))
        
        # Secciones de contenido
        self.create_content_section(story, "RESUMEN EJECUTIVO", report_data.get('executive_summary', ''))
        self.create_content_section(story, "METODOLOGÍA", report_data.get('methodology', ''))
        self.create_content_section(story, "RESULTADOS", report_data.get('results', ''))
        self.create_content_section(story, "ANÁLISIS", report_data.get('analysis', ''))
        self.create_content_section(story, "CONCLUSIONES", report_data.get('conclusions', ''))
        self.create_content_section(story, "RECOMENDACIONES", report_data.get('recommendations', ''))
        
        # Construir PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_supplier_report_pdf(self, report_data, incident_data=None):
        """Genera PDF para informe de proveedor"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                              rightMargin=72, leftMargin=72, 
                              topMargin=72, bottomMargin=18)
        
        story = []
        
        # Encabezado
        self.create_header(story, "INFORME PARA PROVEEDOR", "Comunicación Técnica - Polifusion")
        
        # Información de la empresa
        self.create_footer_info(story, incident_data)
        
        # Información de la incidencia si existe
        if incident_data:
            self.create_incident_info_table(story, incident_data)
        
        # Información del informe
        report_info = [
            ["<b>INFORMACIÓN DEL INFORME</b>", ""],
            ["<b>Número de Informe:</b>", report_data.get('report_number', 'N/A')],
            ["<b>Proveedor:</b>", report_data.get('supplier_name', 'N/A')],
            ["<b>Contacto:</b>", report_data.get('supplier_contact', 'N/A')],
            ["<b>Producto:</b>", report_data.get('product_name', 'N/A')],
            ["<b>Lote:</b>", report_data.get('batch_number', 'N/A')],
            ["<b>Fecha de Emisión:</b>", report_data.get('issue_date', 'N/A')],
            ["<b>Responsable:</b>", report_data.get('responsible_person', 'N/A')],
        ]
        
        table = Table(report_info, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fef2f2')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#fecaca')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.3*inch))
        
        # Secciones de contenido
        self.create_content_section(story, "DESCRIPCIÓN DEL PROBLEMA", report_data.get('problem_description', ''))
        self.create_content_section(story, "ANÁLISIS REALIZADO", report_data.get('analysis_performed', ''))
        self.create_content_section(story, "HALLAZGOS", report_data.get('findings', ''))
        self.create_content_section(story, "ACCIONES REQUERIDAS", report_data.get('required_actions', ''))
        self.create_content_section(story, "PLAZOS", report_data.get('deadlines', ''))
        self.create_content_section(story, "CONTACTO", report_data.get('contact_info', ''))
        
        # Construir PDF
        doc.build(story)
        buffer.seek(0)
        return buffer

# Instancia global del generador
pdf_generator = ProfessionalPDFGenerator()
