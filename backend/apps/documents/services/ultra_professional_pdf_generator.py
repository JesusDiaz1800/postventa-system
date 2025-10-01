#!/usr/bin/env python
"""
GENERADOR DE PDF ULTRA PROFESIONAL - POLIFUSIÓN S.A.
Sistema de generación de PDFs con diseño corporativo moderno
"""

import io
import os
import base64
import tempfile
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import Color, HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    Image, PageBreak, Frame, PageTemplate, BaseDocTemplate
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect, Line, Circle
from reportlab.graphics import renderPDF
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# COLORES CORPORATIVOS POLIFUSIÓN
PRIMARY_COLOR = HexColor('#1C3664')      # Azul corporativo principal
SECONDARY_COLOR = HexColor('#126FCC')    # Azul secundario
ACCENT_COLOR = HexColor('#10B981')       # Verde éxito
WARNING_COLOR = HexColor('#F59E0B')      # Amarillo advertencia  
DANGER_COLOR = HexColor('#EF4444')       # Rojo peligro
LIGHT_GRAY = HexColor('#F8FAFC')         # Gris claro
MEDIUM_GRAY = HexColor('#E2E8F0')        # Gris medio
DARK_GRAY = HexColor('#64748B')          # Gris oscuro
TEXT_COLOR = HexColor('#1E293B')         # Color de texto principal
WHITE = HexColor('#FFFFFF')              # Blanco

class UltraProfessionalPDFGenerator:
    """
    Generador de PDFs ultra profesional con diseño corporativo moderno
    """
    
    def __init__(self):
        self.company_info = {
            'name': 'Polifusión S.A.',
            'address': 'Lampa, Región Metropolitana',
            'full_address': 'Cacique Colin 2525, Lampa, Región Metropolitana',
            'phone': '(2) 2387 5000',
            'email': 'info@polifusion.cl',
            'website': 'www.polifusion.cl',
            'rut': '96.511.730-0'
        }
        self.logo_path = os.path.join(settings.BASE_DIR, 'static', 'logo_polifusion.svg')
        self.styles = self.create_professional_styles()
    
    def create_professional_styles(self):
        """
        Crear estilos profesionales para el PDF
        """
        styles = getSampleStyleSheet()
        
        # Título principal
        styles.add(ParagraphStyle(
            name='MainTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=PRIMARY_COLOR,
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=32
        ))
        
        # Subtítulo
        styles.add(ParagraphStyle(
            name='SubTitle',
            parent=styles['Heading2'],
            fontSize=18,
            textColor=SECONDARY_COLOR,
            spaceAfter=15,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=22
        ))
        
        # Título de sección
        styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=styles['Heading3'],
            fontSize=16,
            textColor=PRIMARY_COLOR,
            spaceAfter=10,
            spaceBefore=20,
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderColor=PRIMARY_COLOR,
            borderPadding=5,
            leading=20
        ))
        
        # Texto normal mejorado
        styles.add(ParagraphStyle(
            name='NormalText',
            parent=styles['Normal'],
            fontSize=11,
            textColor=TEXT_COLOR,
            spaceAfter=6,
            fontName='Helvetica',
            leading=14
        ))
        
        # Texto destacado
        styles.add(ParagraphStyle(
            name='HighlightText',
            parent=styles['Normal'],
            fontSize=12,
            textColor=PRIMARY_COLOR,
            spaceAfter=8,
            fontName='Helvetica-Bold',
            leading=15
        ))
        
        # Texto pequeño
        styles.add(ParagraphStyle(
            name='SmallText',
            parent=styles['Normal'],
            fontSize=9,
            textColor=DARK_GRAY,
            spaceAfter=4,
            fontName='Helvetica',
            leading=12
        ))
        
        # Estilo para campos de información
        styles.add(ParagraphStyle(
            name='FieldLabel',
            parent=styles['Normal'],
            fontSize=10,
            textColor=DARK_GRAY,
            fontName='Helvetica-Bold',
            spaceAfter=2,
            leading=12
        ))
        
        styles.add(ParagraphStyle(
            name='FieldValue',
            parent=styles['Normal'],
            fontSize=11,
            textColor=TEXT_COLOR,
            fontName='Helvetica',
            spaceAfter=8,
            leading=13
        ))
        
        return styles
    
    def create_professional_header(self, canvas, doc):
        """
        Crear header profesional con degradado y logo
        """
        # Fondo degradado para el header
        canvas.saveState()
        canvas.setFillColor(LIGHT_GRAY)
        canvas.rect(0, A4[1] - 120, A4[0], 120, fill=1, stroke=0)
        
        # Línea superior azul
        canvas.setFillColor(PRIMARY_COLOR)
        canvas.rect(0, A4[1] - 8, A4[0], 8, fill=1, stroke=0)
        
        # Logo de la empresa (rectángulo corporativo si no hay logo)
        try:
            # Si tenemos el logo SVG, intentamos cargarlo
            if os.path.exists(self.logo_path):
                # Para SVG necesitaríamos convertir a PNG primero
                # Por ahora creamos un logo corporativo
                self.create_corporate_logo(canvas, 50, A4[1] - 100)
            else:
                self.create_corporate_logo(canvas, 50, A4[1] - 100)
        except Exception as e:
            logger.warning(f"Error cargando logo: {e}")
            self.create_corporate_logo(canvas, 50, A4[1] - 100)
        
        # Título principal
        canvas.setFillColor(PRIMARY_COLOR)
        canvas.setFont("Helvetica-Bold", 24)
        canvas.drawCentredString(A4[0]/2, A4[1] - 70, "CERTIFICADO DE CALIDAD")
        
        # Subtítulo
        canvas.setFillColor(SECONDARY_COLOR)
        canvas.setFont("Helvetica-Bold", 16)
        canvas.drawCentredString(A4[0]/2, A4[1] - 90, "SISTEMA DE GESTIÓN DE INCIDENCIAS")
        
        # Información de la empresa (lado derecho)
        canvas.setFillColor(DARK_GRAY)
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawRightString(A4[0] - 50, A4[1] - 50, self.company_info['name'])
        canvas.setFont("Helvetica", 9)
        canvas.drawRightString(A4[0] - 50, A4[1] - 65, self.company_info['full_address'])
        canvas.drawRightString(A4[0] - 50, A4[1] - 80, f"Tel: {self.company_info['phone']}")
        canvas.drawRightString(A4[0] - 50, A4[1] - 95, f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        # Línea decorativa inferior
        canvas.setStrokeColor(PRIMARY_COLOR)
        canvas.setLineWidth(3)
        canvas.line(50, A4[1] - 110, A4[0] - 50, A4[1] - 110)
        
        canvas.restoreState()
    
    def create_corporate_logo(self, canvas, x, y):
        """
        Crear logo corporativo cuando no tenemos el SVG
        """
        # Fondo del logo con bordes redondeados
        canvas.saveState()
        canvas.setFillColor(PRIMARY_COLOR)
        canvas.roundRect(x, y, 80, 60, 8, fill=1, stroke=0)
        
        # Sombra del logo
        canvas.setFillColor(HexColor('#00000030'))
        canvas.roundRect(x + 2, y - 2, 80, 60, 8, fill=1, stroke=0)
        
        # Texto del logo
        canvas.setFillColor(WHITE)
        canvas.setFont("Helvetica-Bold", 14)
        canvas.drawCentredString(x + 40, y + 35, "POLIFUSIÓN")
        canvas.setFont("Helvetica", 10)
        canvas.drawCentredString(x + 40, y + 20, "S.A.")
        
        canvas.restoreState()
    
    def create_statistics_cards(self, data, canvas, y_position):
        """
        Crear tarjetas de estadísticas modernas con sombras
        """
        card_width = 120
        card_height = 80
        spacing = 20
        start_x = 50
        
        cards = [
            {
                "title": "Promedio", 
                "value": f"{data.get('promedio', 0):.3f}", 
                "color": ACCENT_COLOR, 
                "icon": "📊"
            },
            {
                "title": "Máximo", 
                "value": f"{data.get('max', 0):.3f}", 
                "color": WARNING_COLOR, 
                "icon": "📈"
            },
            {
                "title": "Mínimo", 
                "value": f"{data.get('min', 0):.3f}", 
                "color": DANGER_COLOR, 
                "icon": "📉"
            },
            {
                "title": "Desv. Est.", 
                "value": f"{data.get('desvEst', 0):.3f}", 
                "color": SECONDARY_COLOR, 
                "icon": "📋"
            }
        ]
        
        for i, card in enumerate(cards):
            x = start_x + i * (card_width + spacing)
            
            # Sombra de la tarjeta
            canvas.saveState()
            canvas.setFillColor(HexColor('#00000020'))
            canvas.roundRect(x + 3, y_position - 3, card_width, card_height, 8, fill=1, stroke=0)
            
            # Fondo de la tarjeta
            canvas.setFillColor(WHITE)
            canvas.setStrokeColor(MEDIUM_GRAY)
            canvas.setLineWidth(1)
            canvas.roundRect(x, y_position, card_width, card_height, 8, fill=1, stroke=1)
            
            # Banda superior con color
            canvas.setFillColor(card['color'])
            canvas.roundRect(x, y_position + card_height - 15, card_width, 15, 8, fill=1, stroke=0)
            
            # Icono
            canvas.setFillColor(card['color'])
            canvas.setFont("Helvetica-Bold", 16)
            canvas.drawString(x + 10, y_position + card_height - 30, card['icon'])
            
            # Título
            canvas.setFillColor(DARK_GRAY)
            canvas.setFont("Helvetica-Bold", 9)
            canvas.drawString(x + 10, y_position + card_height - 45, card['title'])
            
            # Valor
            canvas.setFillColor(PRIMARY_COLOR)
            canvas.setFont("Helvetica-Bold", 18)
            canvas.drawString(x + 10, y_position + 15, card['value'])
            
            canvas.restoreState()
    
    def create_professional_table(self, data, headers=None):
        """
        Crear tabla profesional con filas alternadas y encabezados destacados
        """
        if not headers:
            headers = ['Fecha', 'Orden', 'Cliente', 'Proyecto', 'Estado', 'Responsable']
        
        # Preparar datos de la tabla
        table_data = [headers]
        
        for item in data:
            row = [
                item.get('visit_date', 'N/A'),
                item.get('order_number', 'N/A'),
                item.get('client_name', 'N/A'),
                item.get('project_name', 'N/A'),
                item.get('status', 'N/A'),
                item.get('technician', 'N/A')
            ]
            table_data.append(row)
        
        # Crear tabla con anchos optimizados
        col_widths = [80, 70, 90, 120, 60, 80]
        table = Table(table_data, colWidths=col_widths)
        
        # Aplicar estilo profesional a la tabla
        table.setStyle(TableStyle([
            # Encabezados
            ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_COLOR),
            ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            
            # Filas de datos
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
            
            # Filas alternadas
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
            
            # Bordes
            ('GRID', (0, 0), (-1, -1), 1, MEDIUM_GRAY),
            ('LINEBELOW', (0, 0), (-1, 0), 2, PRIMARY_COLOR),
            
            # Padding
            ('PADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        return table
    
    def create_digital_signature(self, canvas, y_position, technician_name="Técnico Responsable"):
        """
        Crear firma digital profesional con marco y línea de firma
        """
        # Fondo de la firma con sombra
        canvas.saveState()
        
        # Sombra
        canvas.setFillColor(HexColor('#00000020'))
        canvas.roundRect(52, y_position - 2, 200, 80, 8, fill=1, stroke=0)
        
        # Fondo principal
        canvas.setFillColor(LIGHT_GRAY)
        canvas.setStrokeColor(MEDIUM_GRAY)
        canvas.setLineWidth(1)
        canvas.roundRect(50, y_position, 200, 80, 8, fill=1, stroke=1)
        
        # Icono de firma
        canvas.setFillColor(PRIMARY_COLOR)
        canvas.setFont("Helvetica-Bold", 24)
        canvas.drawString(70, y_position + 45, "✍")
        
        # Texto "Firma Digital Válida"
        canvas.setFillColor(PRIMARY_COLOR)
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawString(70, y_position + 25, "Firma Digital Válida")
        
        # Línea de firma
        canvas.setStrokeColor(PRIMARY_COLOR)
        canvas.setLineWidth(2)
        canvas.line(70, y_position + 15, 220, y_position + 15)
        
        # Información del firmante
        canvas.setFillColor(TEXT_COLOR)
        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawString(70, y_position + 5, technician_name)
        
        canvas.setFillColor(DARK_GRAY)
        canvas.setFont("Helvetica", 9)
        canvas.drawString(70, y_position - 10, "Ing. Analista de Control de Calidad")
        canvas.drawString(70, y_position - 22, "Polifusión S.A.")
        
        # Fecha y hora de la firma
        canvas.setFont("Helvetica", 8)
        canvas.drawString(70, y_position - 35, f"Firmado el: {datetime.now().strftime('%d/%m/%Y a las %H:%M')}")
        
        canvas.restoreState()
    
    def create_footer(self, canvas, doc):
        """
        Crear footer profesional con información de la empresa
        """
        canvas.saveState()
        
        # Línea superior del footer
        canvas.setStrokeColor(MEDIUM_GRAY)
        canvas.setLineWidth(1)
        canvas.line(50, 50, A4[0] - 50, 50)
        
        # Información de la empresa
        canvas.setFillColor(DARK_GRAY)
        canvas.setFont("Helvetica", 8)
        
        # Lado izquierdo
        canvas.drawString(50, 35, f"{self.company_info['name']} - {self.company_info['rut']}")
        canvas.drawString(50, 25, f"{self.company_info['full_address']}")
        canvas.drawString(50, 15, f"Tel: {self.company_info['phone']} | Email: {self.company_info['email']}")
        
        # Lado derecho - número de página
        canvas.drawRightString(A4[0] - 50, 35, f"Página {doc.page}")
        canvas.drawRightString(A4[0] - 50, 25, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        canvas.drawRightString(A4[0] - 50, 15, "Sistema de Gestión de Incidencias")
        
        canvas.restoreState()
    
    def generate_visit_report_pdf(self, report_data, user_id=None):
        """
        Generar PDF profesional para reporte de visita
        """
        try:
            # Crear buffer de memoria para el PDF
            buffer = io.BytesIO()
            
            # Crear documento con márgenes profesionales
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=50,
                leftMargin=50,
                topMargin=130,  # Espacio para el header
                bottomMargin=80  # Espacio para el footer
            )
            
            # Crear story (contenido del documento)
            story = []
            
            # Espaciado inicial
            story.append(Spacer(1, 20))
            
            # Título del documento
            story.append(Paragraph(
                "REPORTE DE VISITA TÉCNICA", 
                self.styles['MainTitle']
            ))
            
            story.append(Paragraph(
                f"N° {report_data.get('order_number', 'N/A')} - {datetime.now().strftime('%d de %B de %Y')}", 
                self.styles['SubTitle']
            ))
            
            story.append(Spacer(1, 30))
            
            # Sección: Información del Proyecto
            story.append(Paragraph("INFORMACIÓN DEL PROYECTO", self.styles['SectionTitle']))
            
            project_info = [
                f"<b>Cliente:</b> {report_data.get('client_name', 'N/A')}",
                f"<b>Proyecto:</b> {report_data.get('project_name', 'N/A')}",
                f"<b>Dirección:</b> {report_data.get('address', 'N/A')}",
                f"<b>Comuna:</b> {report_data.get('commune', 'N/A')}",
                f"<b>Ciudad:</b> {report_data.get('city', 'N/A')}",
                f"<b>Fecha de Visita:</b> {report_data.get('visit_date', 'N/A')}"
            ]
            
            for info in project_info:
                story.append(Paragraph(info, self.styles['NormalText']))
            
                story.append(Spacer(1, 20))
            
            # Sección: Personal Involucrado
            story.append(Paragraph("PERSONAL INVOLUCRADO", self.styles['SectionTitle']))
            
            personal_info = [
                f"<b>Vendedor:</b> {report_data.get('salesperson', 'N/A')}",
                f"<b>Técnico Responsable:</b> {report_data.get('technician', 'N/A')}"
            ]
            
            for info in personal_info:
                story.append(Paragraph(info, self.styles['NormalText']))
            
            story.append(Spacer(1, 20))
            
            # Sección: Información del Producto
            if any(report_data.get(field) for field in ['product_category', 'product_subcategory', 'product_sku']):
                story.append(Paragraph("INFORMACIÓN DEL PRODUCTO", self.styles['SectionTitle']))
                
                product_info = [
                    f"<b>Categoría:</b> {report_data.get('product_category', 'N/A')}",
                    f"<b>Subcategoría:</b> {report_data.get('product_subcategory', 'N/A')}",
                    f"<b>SKU:</b> {report_data.get('product_sku', 'N/A')}",
                    f"<b>Lote:</b> {report_data.get('product_lot', 'N/A')}",
                    f"<b>Proveedor:</b> {report_data.get('product_provider', 'N/A')}"
                ]
                
                for info in product_info:
                    story.append(Paragraph(info, self.styles['NormalText']))
                
                story.append(Spacer(1, 20))
            
            # Sección: Razón de la Visita
            if report_data.get('visit_reason'):
                story.append(Paragraph("RAZÓN DE LA VISITA", self.styles['SectionTitle']))
                story.append(Paragraph(
                    str(report_data.get('visit_reason', 'No especificada')), 
                    self.styles['NormalText']
                ))
            story.append(Spacer(1, 20))
            
            # Sección: Observaciones Generales
            if report_data.get('general_observations'):
                story.append(Paragraph("OBSERVACIONES GENERALES", self.styles['SectionTitle']))
                story.append(Paragraph(
                    str(report_data.get('general_observations', 'Sin observaciones')), 
                    self.styles['NormalText']
                ))
            story.append(Spacer(1, 20))
            
            # Datos de máquinas
            machine_data = report_data.get('machine_data', {})
            if isinstance(machine_data, str):
                try:
                    import json
                    machine_data = json.loads(machine_data)
                except (json.JSONDecodeError, TypeError):
                    machine_data = {}
            
            if machine_data and machine_data.get('machines'):
                story.append(Paragraph("DATOS DE MÁQUINAS", self.styles['SectionTitle']))
                
                machine_headers = ['Máquina', 'Inicio', 'Corte']
                machine_table_data = [machine_headers]
                
                for machine in machine_data['machines']:
                    row = [
                        machine.get('machine_name', 'N/A'),
                        machine.get('start_time', 'N/A'),
                        machine.get('cut_time', 'N/A')
                    ]
                    machine_table_data.append(row)
                
                machine_table = Table(machine_table_data, colWidths=[150, 100, 100])
                machine_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_COLOR),
                    ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
                    ('GRID', (0, 0), (-1, -1), 1, MEDIUM_GRAY),
                    ('PADDING', (0, 0), (-1, -1), 8),
                ]))
                
                story.append(machine_table)
                story.append(Spacer(1, 20))
            
            # Observaciones técnicas
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
                story.append(Paragraph("OBSERVACIONES TÉCNICAS", self.styles['SectionTitle']))
                
                for key, value in filtered_observations.items():
                    story.append(Paragraph(f"<b>{key}:</b>", self.styles['FieldLabel']))
                    story.append(Paragraph(str(value), self.styles['FieldValue']))
                
                story.append(Spacer(1, 20))
            
            # Espacio para firma
            story.append(Spacer(1, 40))
            story.append(Paragraph("FIRMA DEL TÉCNICO RESPONSABLE", self.styles['SectionTitle']))
            story.append(Spacer(1, 60))
            
            # Función para header y footer personalizado
            def add_header_footer(canvas, doc):
                self.create_professional_header(canvas, doc)
                self.create_footer(canvas, doc)
                
                # Agregar firma digital en posición fija
                technician_name = report_data.get('technician', 'Técnico Responsable')
                self.create_digital_signature(canvas, 150, technician_name)
            
            # Construir el PDF
            doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
            
            buffer.seek(0)
            return buffer
            
        except Exception as e:
            logger.error(f"Error generando PDF de visita: {str(e)}", exc_info=True)
            raise e
    
    def generate_lab_report_pdf(self, report_data, user_id=None):
        """
        Generar PDF profesional para reporte de laboratorio
        """
        return self.generate_visit_report_pdf(report_data, user_id)
    
    def generate_supplier_report_pdf(self, report_data, user_id=None):
        """
        Generar PDF profesional para reporte de proveedor
        """
        return self.generate_visit_report_pdf(report_data, user_id)
    
    def generate_quality_report_pdf(self, report_data, user_id=None):
        """
        Generar PDF profesional para reporte de calidad
        """
        return self.generate_visit_report_pdf(report_data, user_id)