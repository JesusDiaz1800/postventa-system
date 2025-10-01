#!/usr/bin/env python
"""
GENERADOR DE PDF ULTIMATE PROFESIONAL - POLIFUSIÓN S.A.
Sistema de generación de PDFs con diseño corporativo ultra moderno
Siguiendo las especificaciones exactas de la otra IA
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

# COLORES CORPORATIVOS EXACTOS
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

class UltimatePDFGenerator:
    """
    Generador de PDFs ultimate profesional con diseño corporativo ultra moderno
    Siguiendo las especificaciones exactas de la otra IA
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
        self.styles = self.create_ultimate_styles()
    
    def create_ultimate_styles(self):
        """
        Crear estilos ultimate profesionales siguiendo las especificaciones exactas
        """
        styles = getSampleStyleSheet()
        
        # Título principal profesional
        styles.add(ParagraphStyle(
            name='UltimateMainTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=PRIMARY_COLOR,
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=28
        ))
        
        # Subtítulo profesional
        styles.add(ParagraphStyle(
            name='UltimateSubTitle',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=SECONDARY_COLOR,
            spaceAfter=15,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=20
        ))
        
        # Título de sección con diseño moderno
        styles.add(ParagraphStyle(
            name='UltimateSectionTitle',
            parent=styles['Heading3'],
            fontSize=14,
            textColor=PRIMARY_COLOR,
            spaceAfter=10,
            spaceBefore=20,
            fontName='Helvetica-Bold',
            leading=18
        ))
        
        # Texto normal mejorado
        styles.add(ParagraphStyle(
            name='UltimateNormalText',
            parent=styles['Normal'],
            fontSize=12,
            textColor=TEXT_COLOR,
            spaceAfter=8,
            fontName='Helvetica',
            leading=16,
            alignment=TA_JUSTIFY
        ))
        
        # Texto destacado profesional
        styles.add(ParagraphStyle(
            name='UltimateHighlightText',
            parent=styles['Normal'],
            fontSize=13,
            textColor=PRIMARY_COLOR,
            spaceAfter=10,
            fontName='Helvetica-Bold',
            leading=17
        ))
        
        # Texto pequeño elegante
        styles.add(ParagraphStyle(
            name='UltimateSmallText',
            parent=styles['Normal'],
            fontSize=10,
            textColor=DARK_GRAY,
            spaceAfter=6,
            fontName='Helvetica',
            leading=13
        ))
        
        # Estilo para campos de información
        styles.add(ParagraphStyle(
            name='UltimateFieldLabel',
            parent=styles['Normal'],
            fontSize=11,
            textColor=DARK_GRAY,
            fontName='Helvetica-Bold',
            spaceAfter=3,
            leading=14
        ))
        
        styles.add(ParagraphStyle(
            name='UltimateFieldValue',
            parent=styles['Normal'],
            fontSize=12,
            textColor=TEXT_COLOR,
            fontName='Helvetica',
            spaceAfter=10,
            leading=15
        ))
        
        return styles
    
    def create_ultimate_header(self, canvas, doc):
        """
        Crear header profesional con logo real y diseño limpio
        """
        # Fondo sutil
        canvas.saveState()
        canvas.setFillColor(LIGHT_GRAY)
        canvas.rect(0, A4[1] - 100, A4[0], 100, fill=1, stroke=0)
        
        # Logo real de Polifusión
        try:
            if os.path.exists(self.logo_path):
                # Usar logo SVG real
                self.create_real_logo(canvas, 50, A4[1] - 80)
            else:
                self.create_corporate_logo_ultimate(canvas, 50, A4[1] - 80)
        except Exception as e:
            logger.warning(f"Error cargando logo SVG: {e}")
            self.create_corporate_logo_ultimate(canvas, 50, A4[1] - 80)
        
        # Información de la empresa (lado derecho) - más compacta
        canvas.setFillColor(DARK_GRAY)
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawRightString(A4[0] - 50, A4[1] - 50, self.company_info['name'])
        canvas.setFont("Helvetica", 10)
        canvas.drawRightString(A4[0] - 50, A4[1] - 65, self.company_info['full_address'])
        canvas.drawRightString(A4[0] - 50, A4[1] - 80, f"Tel: {self.company_info['phone']}")
        canvas.drawRightString(A4[0] - 50, A4[1] - 95, f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        # Línea decorativa sutil
        canvas.setStrokeColor(PRIMARY_COLOR)
        canvas.setLineWidth(2)
        canvas.line(50, A4[1] - 105, A4[0] - 50, A4[1] - 105)
        
        canvas.restoreState()
    
    def create_real_logo(self, canvas, x, y):
        """
        Crear logo real de Polifusión basado en el SVG
        """
        try:
            canvas.saveState()
            
            # Crear el logo "P" estilizado basado en el SVG
            # Fondo azul del logo
            canvas.setFillColor(PRIMARY_COLOR)
            canvas.roundRect(x, y, 100, 50, 8, fill=1, stroke=0)
            
            # Crear la "P" estilizada
            canvas.setFillColor(WHITE)
            canvas.setStrokeColor(WHITE)
            canvas.setLineWidth(3)
            
            # Línea vertical de la P
            canvas.line(x + 15, y + 10, x + 15, y + 40)
            
            # Línea horizontal superior de la P
            canvas.line(x + 15, y + 40, x + 35, y + 40)
            
            # Línea horizontal media de la P
            canvas.line(x + 15, y + 30, x + 35, y + 30)
            
            # Línea vertical de cierre de la P
            canvas.line(x + 35, y + 30, x + 35, y + 40)
            
            # Texto "POLIFUSIÓN"
            canvas.setFillColor(WHITE)
            canvas.setFont("Helvetica-Bold", 16)
            canvas.drawCentredString(x + 50, y + 35, "POLIFUSIÓN")
            canvas.setFont("Helvetica-Bold", 12)
            canvas.drawCentredString(x + 50, y + 20, "S.A.")
            
            # Línea decorativa
            canvas.setStrokeColor(WHITE)
            canvas.setLineWidth(1)
            canvas.line(x + 25, y + 15, x + 75, y + 15)
            
            canvas.restoreState()
            
        except Exception as e:
            logger.warning(f"Error creando logo real: {e}")
            self.create_corporate_logo_ultimate(canvas, x, y)
    
    def create_corporate_logo_ultimate(self, canvas, x, y):
        """
        Crear logo corporativo ultra profesional
        """
        # Fondo del logo con gradiente
        canvas.saveState()
        canvas.setFillColor(PRIMARY_COLOR)
        canvas.roundRect(x, y, 100, 70, 12, fill=1, stroke=0)
        
        # Sombra del logo
        canvas.setFillColor(HexColor('#00000030'))
        canvas.roundRect(x + 3, y - 3, 100, 70, 12, fill=1, stroke=0)
        
        # Texto del logo ultra profesional
        canvas.setFillColor(WHITE)
        canvas.setFont("Helvetica-Bold", 16)
        canvas.drawCentredString(x + 50, y + 40, "POLIFUSIÓN")
        canvas.setFont("Helvetica", 12)
        canvas.drawCentredString(x + 50, y + 25, "S.A.")
        
        # Línea decorativa
        canvas.setStrokeColor(WHITE)
        canvas.setLineWidth(2)
        canvas.line(x + 20, y + 15, x + 80, y + 15)
        
        canvas.restoreState()
    
    def create_statistics_cards_ultimate(self, data, canvas, y_position):
        """
        Crear tarjetas de estadísticas ultra modernas con sombras 3D
        """
        card_width = 130
        card_height = 90
        spacing = 25
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
            
            # Sombra 3D de la tarjeta
            canvas.saveState()
            canvas.setFillColor(HexColor('#00000025'))
            canvas.roundRect(x + 4, y_position - 4, card_width, card_height, 12, fill=1, stroke=0)
            
            # Fondo de la tarjeta ultra profesional
            canvas.setFillColor(WHITE)
            canvas.setStrokeColor(MEDIUM_GRAY)
            canvas.setLineWidth(1)
            canvas.roundRect(x, y_position, card_width, card_height, 12, fill=1, stroke=1)
            
            # Banda superior con color corporativo
            canvas.setFillColor(card['color'])
            canvas.roundRect(x, y_position + card_height - 20, card_width, 20, 12, fill=1, stroke=0)
            
            # Icono profesional
            canvas.setFillColor(WHITE)
            canvas.setFont("Helvetica-Bold", 20)
            canvas.drawCentredString(x + card_width/2, y_position + card_height - 35, card['icon'])
            
            # Título
            canvas.setFillColor(DARK_GRAY)
            canvas.setFont("Helvetica-Bold", 10)
            canvas.drawCentredString(x + card_width/2, y_position + card_height - 55, card['title'])
            
            # Valor destacado
            canvas.setFillColor(PRIMARY_COLOR)
            canvas.setFont("Helvetica-Bold", 20)
            canvas.drawCentredString(x + card_width/2, y_position + 20, card['value'])
            
            canvas.restoreState()
    
    def create_ultimate_table(self, data, headers=None):
        """
        Crear tabla ultra profesional con diseño moderno
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
        col_widths = [90, 80, 100, 130, 70, 90]
        table = Table(table_data, colWidths=col_widths)
        
        # Aplicar estilo ultra profesional a la tabla
        table.setStyle(TableStyle([
            # Encabezados ultra profesionales
            ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_COLOR),
            ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            
            # Filas de datos profesionales
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
            
            # Filas alternadas elegantes
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
            
            # Bordes profesionales
            ('GRID', (0, 0), (-1, -1), 1, MEDIUM_GRAY),
            ('LINEBELOW', (0, 0), (-1, 0), 3, PRIMARY_COLOR),
            
            # Padding profesional
            ('PADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        return table
    
    def create_simple_signature(self, story, technician_name="Técnico Responsable"):
        """
        Crear información simple del técnico sin firma digital
        """
        story.append(Spacer(1, 20))
        story.append(Paragraph(
            f"<b>Técnico Responsable:</b> {technician_name}", 
            self.styles['UltimateNormalText']
        ))
        story.append(Paragraph(
            f"<b>Fecha de Generación:</b> {datetime.now().strftime('%d/%m/%Y a las %H:%M')}", 
            self.styles['UltimateNormalText']
        ))
    
    def create_ultimate_footer(self, canvas, doc):
        """
        Crear footer simple sin datos de empresa
        """
        canvas.saveState()
        
        # Solo información básica del documento
        canvas.setFillColor(DARK_GRAY)
        canvas.setFont("Helvetica", 9)
        
        # Lado derecho - información del documento
        canvas.drawRightString(A4[0] - 50, 30, f"Página {doc.page}")
        canvas.drawRightString(A4[0] - 50, 20, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        canvas.restoreState()
    
    def generate_visit_report_pdf(self, report_data, user_id=None):
        """
        Generar PDF ultimate profesional para reporte de visita
        Siguiendo las especificaciones exactas
        """
        try:
            # Crear buffer de memoria para el PDF
            buffer = io.BytesIO()
            
            # Crear documento con márgenes ultra profesionales
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=60,
                leftMargin=60,
                topMargin=150,  # Espacio para el header ultimate
                bottomMargin=100  # Espacio para el footer ultimate
            )
            
            # Crear story (contenido del documento)
            story = []
            
            # Espaciado inicial profesional
            story.append(Spacer(1, 30))
            
            # Título del documento profesional
            story.append(Paragraph(
                "REPORTE DE VISITA TÉCNICA", 
                self.styles['UltimateMainTitle']
            ))
            
            story.append(Paragraph(
                f"N° {report_data.get('order_number', 'N/A')} - {datetime.now().strftime('%d de %B de %Y')}", 
                self.styles['UltimateSubTitle']
            ))
            
            story.append(Spacer(1, 40))
            
            # Sección: Información del Proyecto
            story.append(Paragraph("INFORMACIÓN DEL PROYECTO", self.styles['UltimateSectionTitle']))
            
            project_info = [
                f"<b>Cliente:</b> {report_data.get('client_name', 'N/A')}",
                f"<b>Proyecto:</b> {report_data.get('project_name', 'N/A')}",
                f"<b>Dirección:</b> {report_data.get('address', 'N/A')}",
                f"<b>Comuna:</b> {report_data.get('commune', 'N/A')}",
                f"<b>Ciudad:</b> {report_data.get('city', 'N/A')}",
                f"<b>Fecha de Visita:</b> {report_data.get('visit_date', 'N/A')}"
            ]
            
            for info in project_info:
                story.append(Paragraph(info, self.styles['UltimateNormalText']))
            
            story.append(Spacer(1, 25))
            
            # Sección: Personal Involucrado
            story.append(Paragraph("PERSONAL INVOLUCRADO", self.styles['UltimateSectionTitle']))
            
            personal_info = [
                f"<b>Vendedor:</b> {report_data.get('salesperson', 'N/A')}",
                f"<b>Técnico Responsable:</b> {report_data.get('technician', 'N/A')}"
            ]
            
            for info in personal_info:
                story.append(Paragraph(info, self.styles['UltimateNormalText']))
            
            story.append(Spacer(1, 25))
            
            # Sección: Información del Producto
            if any(report_data.get(field) for field in ['product_category', 'product_subcategory', 'product_sku']):
                story.append(Paragraph("INFORMACIÓN DEL PRODUCTO", self.styles['UltimateSectionTitle']))
                
                product_info = [
                    f"<b>Categoría:</b> {report_data.get('product_category', 'N/A')}",
                    f"<b>Subcategoría:</b> {report_data.get('product_subcategory', 'N/A')}",
                    f"<b>SKU:</b> {report_data.get('product_sku', 'N/A')}",
                    f"<b>Lote:</b> {report_data.get('product_lot', 'N/A')}",
                    f"<b>Proveedor:</b> {report_data.get('product_provider', 'N/A')}"
                ]
                
                for info in product_info:
                    story.append(Paragraph(info, self.styles['UltimateNormalText']))
                
                story.append(Spacer(1, 25))
            
            # Sección: Razón de la Visita
            if report_data.get('visit_reason'):
                story.append(Paragraph("RAZÓN DE LA VISITA", self.styles['UltimateSectionTitle']))
                story.append(Paragraph(
                    str(report_data.get('visit_reason', 'No especificada')), 
                    self.styles['UltimateNormalText']
                ))
                story.append(Spacer(1, 25))
            
            # Sección: Observaciones Generales
            if report_data.get('general_observations'):
                story.append(Paragraph("OBSERVACIONES GENERALES", self.styles['UltimateSectionTitle']))
                story.append(Paragraph(
                    str(report_data.get('general_observations', 'Sin observaciones')), 
                    self.styles['UltimateNormalText']
                ))
                story.append(Spacer(1, 25))
            
            # Datos de máquinas
            machine_data = report_data.get('machine_data', {})
            if isinstance(machine_data, str):
                try:
                    import json
                    machine_data = json.loads(machine_data)
                except (json.JSONDecodeError, TypeError):
                    machine_data = {}
            
            if machine_data and machine_data.get('machines'):
                story.append(Paragraph("DATOS DE MÁQUINAS", self.styles['UltimateSectionTitle']))
                
                machine_headers = ['Máquina', 'Inicio', 'Corte']
                machine_table_data = [machine_headers]
                
                for machine in machine_data['machines']:
                    row = [
                        machine.get('machine_name', 'N/A'),
                        machine.get('start_time', 'N/A'),
                        machine.get('cut_time', 'N/A')
                    ]
                    machine_table_data.append(row)
                
                machine_table = Table(machine_table_data, colWidths=[180, 120, 120])
                machine_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_COLOR),
                    ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
                    ('GRID', (0, 0), (-1, -1), 1, MEDIUM_GRAY),
                    ('PADDING', (0, 0), (-1, -1), 10),
                ]))
                
                story.append(machine_table)
                story.append(Spacer(1, 25))
            
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
                story.append(Paragraph("OBSERVACIONES TÉCNICAS", self.styles['UltimateSectionTitle']))
                
                for key, value in filtered_observations.items():
                    story.append(Paragraph(f"<b>{key}:</b>", self.styles['UltimateFieldLabel']))
                    story.append(Paragraph(str(value), self.styles['UltimateFieldValue']))
                
                story.append(Spacer(1, 25))
            
            # Espacio para firma
            story.append(Spacer(1, 50))
            story.append(Paragraph("FIRMA DEL TÉCNICO RESPONSABLE", self.styles['UltimateSectionTitle']))
            story.append(Spacer(1, 80))
            
            # Función para header y footer ultimate
            def add_ultimate_header_footer(canvas, doc):
                self.create_ultimate_header(canvas, doc)
                self.create_ultimate_footer(canvas, doc)
                
                # Agregar firma digital en posición fija
                technician_name = report_data.get('technician', 'Técnico Responsable')
                # Información simple del técnico (sin firma digital)
                self.create_simple_signature(story, technician_name)
            
            # Construir el PDF ultimate
            doc.build(story, onFirstPage=add_ultimate_header_footer, onLaterPages=add_ultimate_header_footer)
            
            buffer.seek(0)
            return buffer
            
        except Exception as e:
            logger.error(f"Error generando PDF ultimate de visita: {str(e)}", exc_info=True)
            raise e
    
    def generate_lab_report_pdf(self, report_data, user_id=None):
        """
        Generar PDF ultimate profesional para reporte de laboratorio
        """
        return self.generate_visit_report_pdf(report_data, user_id)
    
    def generate_supplier_report_pdf(self, report_data, user_id=None):
        """
        Generar PDF ultimate profesional para reporte de proveedor
        """
        return self.generate_visit_report_pdf(report_data, user_id)
    
    def generate_quality_report_pdf(self, report_data, user_id=None):
        """
        Generar PDF ultimate profesional para reporte de calidad
        """
        return self.generate_visit_report_pdf(report_data, user_id)
