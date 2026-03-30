#!/usr/bin/env python
"""
GENERADOR PDF PROFESIONAL - POLIFUSIÓN S.A.
Diseño limpio, elegante y 100% funcional (Versión 2.0 Modern)
"""

import io
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import HexColor, white, black, Color
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    Image as ReportLabImage, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.utils import ImageReader
from django.conf import settings

logger = logging.getLogger(__name__)

# =============================================================================
# COLORES CORPORATIVOS & ESTILO
# =============================================================================
# Paleta de colores más moderna y sobria
# Paleta de colores Premium 2026/2027
COLOR_PRIMARY = HexColor('#002B5B')      # Azul Marino Profundo (Premium)
COLOR_SECONDARY = HexColor('#475569')    # Slate Gray
COLOR_ACCENT = HexColor('#EF4444')       # Rojo Moderno
COLOR_BG_HEADER = HexColor('#F8FAFC')    # Fondo Limpio
COLOR_BORDER = HexColor('#CBD5E1')       # Borde Suave
COLOR_TEXT_MAIN = HexColor('#0F172A')    # Texto Principal Oscuro
COLOR_TEXT_LIGHT = HexColor('#64748B')   # Texto Secundario

class ProfessionalPDFGenerator:
    """
    Generador de PDFs de Alto Nivel - Diseño Corporativo 2026
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._init_styles()
        self.page_width, self.page_height = A4
        self.margin_x = 1.5 * cm
        self.margin_y = 1.5 * cm
        self.printable_width = self.page_width - (2 * self.margin_x)
        
        # Logo cache
        self.logo_path = self._find_logo()

    def _init_styles(self):
        """Inicializa estilos personalizados más limpios"""
        # Título Principal (Nombre del Reporte)
        self.styles.add(ParagraphStyle(
            name='ModernTitle',
            fontName='Helvetica-Bold',
            fontSize=18,
            textColor=COLOR_PRIMARY,
            alignment=TA_LEFT,
            spaceAfter=5
        ))
        
        # Subtítulo (Número de Orden, Fechas)
        self.styles.add(ParagraphStyle(
            name='ModernSubtitle',
            fontName='Helvetica',
            fontSize=10,
            textColor=COLOR_TEXT_LIGHT,
            alignment=TA_LEFT,
            spaceAfter=15
        ))
        
        # Encabezados de Sección
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            fontName='Helvetica-Bold',
            fontSize=12,
            textColor=white,
            backColor=COLOR_PRIMARY,
            alignment=TA_LEFT,
            leftIndent=5,
            spaceBefore=15,
            spaceAfter=5,
            padding=3,
            borderPadding=5,
            borderRadius=2
        ))
        
        # Etiquetas de Campo (Label)
        self.styles.add(ParagraphStyle(
            name='FieldLabel',
            fontName='Helvetica-Bold',
            fontSize=9,
            textColor=COLOR_SECONDARY,
            alignment=TA_LEFT,
        ))
        
        # Valor de Campo (Value)
        self.styles.add(ParagraphStyle(
            name='FieldValue',
            fontName='Helvetica',
            fontSize=9,
            textColor=COLOR_TEXT_MAIN,
            alignment=TA_LEFT,
            leading=11
        ))
        
        # Texto Normal Justificado
        self.styles.add(ParagraphStyle(
            name='ModernBodyText',
            fontName='Helvetica',
            fontSize=9,
            textColor=COLOR_TEXT_MAIN,
            alignment=TA_JUSTIFY,
            leading=12
        ))

    def _find_logo(self) -> Optional[str]:
        """Busca el logo en rutas estándar (usa BASE_DIR, sin rutas hardcodeadas)"""
        base = getattr(settings, 'BASE_DIR', '')
        candidates = [
            os.path.join(base, 'static', 'Logo Polifusion blanco.png'),
            os.path.join(base, 'static', 'logo_polifusion.png'),
            os.path.join(base, 'apps', 'documents', 'assets', 'logo_polifusion.png'),
        ]
        for path in candidates:
            if os.path.exists(path):
                return path
        return None

    def _draw_header_footer(self, canvas, doc):
        """Dibuja encabezado y pie de página en cada hoja"""
        canvas.saveState()
        
        # --- HEADER ---
        # Draw Dark Blue Background
        header_height = 3.0 * cm
        header_y_start = self.page_height - header_height
        
        # Rectángulo de fondo (ancho completo)
        canvas.setFillColor(COLOR_PRIMARY)
        canvas.rect(0, header_y_start, self.page_width, header_height, fill=1, stroke=0)
        
        # Logo
        if self.logo_path:
            try:
                img = ImageReader(self.logo_path)
                iw, ih = img.getSize()
                aspect = ih / float(iw)
                
                # Definir tamaño objetivo del logo
                logo_target_w = 6.0 * cm
                logo_target_h = 2.0 * cm
                
                # Escalar para encajar (contain)
                logo_w = logo_target_w
                logo_h = logo_w * aspect
                
                if logo_h > logo_target_h:
                    logo_h = logo_target_h
                    logo_w = logo_h / aspect
                    
                # Posicionar centrado verticalmente en el header
                logo_y = header_y_start + (header_height - logo_h) / 2
                logo_x = self.margin_x
                
                canvas.drawImage(self.logo_path, logo_x, logo_y, width=logo_w, height=logo_h, mask='auto')
            except Exception:
                pass

        # Datos Empresa (Derecha) - Ahora en Blanco
        text_y_start = header_y_start + header_height - 1.0*cm
        canvas.setFont("Helvetica-Bold", 10)
        canvas.setFillColor(white)
        canvas.drawRightString(self.page_width - self.margin_x, text_y_start, "POLIFUSIÓN S.A.")
        
        canvas.setFont("Helvetica", 9)
        canvas.drawRightString(self.page_width - self.margin_x, text_y_start - 12, "Cacique Colin 2525, Lampa")
        canvas.drawRightString(self.page_width - self.margin_x, text_y_start - 24, "Región Metropolitana, Chile")
        canvas.drawRightString(self.page_width - self.margin_x, text_y_start - 36, "+56 2 2387 5000 | www.polifusion.cl")


        # --- FOOTER ---
        # Línea separadora Footer
        canvas.line(self.margin_x, self.margin_y, self.page_width - self.margin_x, self.margin_y)
        
        # info pie de pagina
        generation_time = datetime.now().strftime("%d/%m/%Y %H:%M")
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(COLOR_TEXT_LIGHT)
        canvas.drawString(self.margin_x, self.margin_y - 10, f"Generado el: {generation_time}")
        canvas.drawRightString(self.page_width - self.margin_x, self.margin_y - 10, f"Página {doc.page}")
        
        canvas.restoreState()

    def _create_info_block(self, data_dict: Dict) -> Table:
        """Crea un bloque de información (Label: Value) en 2 columnas"""
        raw_data = []
        row = []
        for i, (label, value) in enumerate(data_dict.items()):
            # Limpiar valor
            if value is None: value = '-'
            value_str = str(value)
            
            # Celda Label
            p_label = Paragraph(label, self.styles['FieldLabel'])
            # Celda Value
            p_value = Paragraph(value_str, self.styles['FieldValue'])
            
            row.extend([p_label, p_value])
            
            # Si completamos 2 pares (4 celdas), cerramos fila
            if len(row) == 4:
                raw_data.append(row)
                row = []
        
        # Si quedó algo impar, rellenar
        if row:
            while len(row) < 4:
                row.append('')
            raw_data.append(row)
            
        t = Table(raw_data, colWidths=[3.5*cm, 5*cm, 3.5*cm, 5*cm])
        t.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        return t

    def _create_full_width_table(self, data_list: List[List], col_widths=None) -> Table:
        """Crea una tabla moderna de ancho completo con estilo Zebra"""
        if not col_widths:
            # Auto distribuir
            col_w = self.printable_width / len(data_list[0])
            col_widths = [col_w] * len(data_list[0])
            
        t = Table(data_list, colWidths=col_widths)
        
        # Estilo moderno
        style = [
            # Header row
            ('BACKGROUND', (0,0), (-1,0), COLOR_BG_HEADER),
            ('TEXTCOLOR', (0,0), (-1,0), COLOR_PRIMARY),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('TOPPADDING', (0,0), (-1,0), 8),
            
            # Content separation
            ('GRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,1), (-1,-1), 8),
        ]
        t.setStyle(TableStyle(style))
        return t

    def _create_photo_grid(self, images: List[Dict]):
        """Crea grid inteligente de fotos con layout optimizado según orientación"""
        if not images:
            return Paragraph("No hay evidencia fotográfica disponible.", self.styles['ModernBodyText'])
        
        from reportlab.lib import colors
        from reportlab.lib.styles import ParagraphStyle
        
        # Analizar orientación de imágenes para determinar layout óptimo
        num_images = len(images)
        vertical_count = 0
        horizontal_count = 0
        
        # Analizar aspect ratio de cada imagen
        for img_data in images[:min(4, num_images)]:  # Muestra de primeras 4
            try:
                img_path = self._resolve_image_path(img_data.get('path', ''))
                if img_path and os.path.exists(img_path):
                    img_reader = ImageReader(img_path)
                    iw, ih = img_reader.getSize()
                    if ih > iw:  # Vertical
                        vertical_count += 1
                    else:  # Horizontal
                        horizontal_count += 1
            except:
                pass
        
        # Decidir número de columnas según orientación y cantidad
        if num_images <= 2:
            num_cols = 2  # 2 imágenes: 2 columnas
        elif num_images == 3:
            num_cols = 3  # 3 imágenes: 3 columnas
        elif vertical_count > horizontal_count:
            # Imágenes mayormente verticales: 4 columnas (más estrechas)
            num_cols = 4
        else:
            # Imágenes mayormente horizontales: 2 columnas (más anchas)
            num_cols = 2
        
        # Calcular dimensiones según número de columnas
        spacing = 0.3*cm
        col_width = (self.printable_width - (spacing * (num_cols - 1))) / num_cols
        max_img_height = 5*cm  # Altura máxima optimizada
        
        grid_data = []
        row = []
        
        for img_data in images:
            try:
                img_path = self._resolve_image_path(img_data.get('path', ''))
                if not img_path or not os.path.exists(img_path):
                    continue
                
                # Crear imagen
                img_reader = ImageReader(img_path)
                iw, ih = img_reader.getSize()
                aspect = ih / float(iw)
                
                # Calcular dimensiones manteniendo aspect ratio
                img_w = col_width
                img_h = col_width * aspect
                if img_h > max_img_height:
                    img_h = max_img_height
                    img_w = max_img_height / aspect
                
                rl_img = ReportLabImage(img_path, width=img_w, height=img_h)
                
                # Crear celda con imagen y descripción (con borde sutil)
                desc_text = img_data.get('description', '')
                
                if desc_text:
                    # Con descripción
                    desc_style = ParagraphStyle(
                        'ImgDesc',
                        parent=self.styles['ModernBodyText'],
                        fontSize=7,
                        textColor=colors.HexColor('#666666'),
                        alignment=1,  # Center
                        spaceAfter=0,
                        leading=9
                    )
                    desc = Paragraph(desc_text, desc_style)
                    cell_data = [[rl_img], [Spacer(1, 2)], [desc]]
                else:
                    # Sin descripción
                    cell_data = [[rl_img]]
                
                # Tabla con borde sutil
                cell_table = Table(cell_data, colWidths=[img_w])
                cell_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDDDDD')),  # Borde sutil
                    ('LEFTPADDING', (0, 0), (-1, -1), 3),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ]))
                row.append(cell_table)
                
                # Agregar fila cuando tengamos el número de columnas necesario
                if len(row) == num_cols:
                    grid_data.append(row)
                    row = []
                    
            except Exception as e:
                logger.error(f"Error procesando imagen para PDF: {e}")
                continue
        
        # Agregar fila incompleta si existe, rellenando con celdas vacías
        if row:
            while len(row) < num_cols:
                row.append('')  # Celdas vacías
            grid_data.append(row)
        
        if not grid_data:
            return Paragraph("No hay evidencia fotográfica disponible.", self.styles['ModernBodyText'])
        
        # Crear tabla optimizada
        col_widths = [col_width] * num_cols
        grid = Table(grid_data, colWidths=col_widths)
        grid.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        return grid
    
    def _resolve_image_path(self, img_path):
        """Resuelve la ruta de una imagen buscando en múltiples ubicaciones posibles"""
        if not img_path:
            return None
            
        possible_paths = []
        
        # A. Ruta exacta si ya es absoluta
        if os.path.exists(img_path):
            return img_path
        
        # B. Si empieza con MEDIA_URL
        media_url = getattr(settings, 'MEDIA_URL', '/media/')
        if img_path.startswith(media_url):
            rel_path = img_path.replace(media_url, '', 1).lstrip('/')
            possible_paths.append(os.path.join(settings.MEDIA_ROOT, rel_path.replace('/', os.sep)))
        
        # C. Intento directo en MEDIA_ROOT
        possible_paths.append(os.path.join(settings.MEDIA_ROOT, img_path.lstrip('/').replace('/', os.sep)))
        
        # D. Intento con BASE_DIR
        possible_paths.append(os.path.join(settings.BASE_DIR, img_path.lstrip('/').replace('/', os.sep)))
        
        for p in possible_paths:
            if os.path.exists(p):
                return p
        
        logger.warning(f"Could not find image: {img_path}. Tried: {possible_paths}")
        return None

    def _get_section_images_flow(self, report_id, section):
        """Busca imágenes adjuntas a un reporte para una sección específica"""
        from ..models import DocumentAttachment
        
        images = []
        if not report_id:
            return images
            
        attachments = DocumentAttachment.objects.filter(
            document_type='quality_report',
            document_id=report_id,
            section=section
        )
        
        for att in attachments:
            if att.file:
                images.append({
                    'path': att.file.path,
                    'description': att.description or f"Evidencia {section}"
                })
        return images


    def _get_digital_signature(self, user) -> Optional[ReportLabImage]:
        """Obtiene la firma digital del usuario con aspect ratio optimizado"""
        if not user or not hasattr(user, 'digital_signature') or not user.digital_signature:
            return None
        
        try:
            path = user.digital_signature.path
            if os.path.exists(path):
                # Mantener aspect ratio original
                img_reader = ImageReader(path)
                iw, ih = img_reader.getSize()
                aspect = ih / float(iw)
                
                # Tamaño optimizado
                width = 5*cm
                height = width * aspect
                
                # Limitar altura máxima
                if height > 2.5*cm:
                    height = 2.5*cm
                    width = height / aspect
                
                return ReportLabImage(path, width=width, height=height, hAlign='CENTER')
        except Exception as e:
            logger.warning(f"No se pudo cargar firma digital: {e}")
        return None

    def generate_visit_report_pdf(self, data: Dict, output_path_or_buffer) -> bool:
        """
        Punto de entrada principal. Genera el PDF completo.
        """
        try:
            # Configurar Doc
            doc = SimpleDocTemplate(
                output_path_or_buffer,
                pagesize=A4,
                rightMargin=self.margin_x,
                leftMargin=self.margin_x,
                topMargin=3.5*cm, # Ajustado para nuevo header
                bottomMargin=2.0*cm
            )
            
            elements = []
            
            # 1. Título y referencias
            incident_code = data.get('incident_code', 'N/A')
            visit_date = data.get('visit_date', '')
            if visit_date:
                # Intentar formatear fecha si es str ISO
                try: 
                    if 'T' in visit_date: visit_date = visit_date.split('T')[0]
                except: pass
                
            elements.append(Paragraph(f"REPORTE DE VISITA TÉCNICA", self.styles['ModernTitle']))
            # Mostrar ID de llamada SAP en lugar de número de orden duplicado
            sap_id = data.get('sap_call_id') or 'N/A'
            elements.append(Paragraph(f"N° Reporte: {data.get('report_number', '-')} | ID Orden SAP: {sap_id} | Fecha: {visit_date}", self.styles['ModernSubtitle']))
            
            elements.append(Spacer(1, 10))
            
            # 2. Información General (Proyecto y Cliente)
            elements.append(Paragraph("INFORMACIÓN GENERAL", self.styles['SectionHeader']))
            general_info = {
                "Proyecto:": data.get('project_name'),
                "ID Proyecto:": data.get('project_id'),
                "Cliente:": data.get('client_name'),
                "Código Cliente:": data.get('client_rut'),
                "Dirección:": data.get('address'),
                "Comuna:": data.get('commune'),
                "Ciudad:": data.get('city'),
                "Constructora:": data.get('construction_company'),
                "Contacto:": data.get('contact_observations', '') or 'Sin obs.'
            }
            elements.append(self._create_info_block(general_info))
            
            # 3. Personal en Obra
            elements.append(Paragraph("PERSONAL Y CONTACTO", self.styles['SectionHeader']))
            personnel_info = {
                "Vendedor:": data.get('salesperson'),
                "Técnico:": data.get('technician'),
                "Instalador:": data.get('installer'),
                "Tel. Instalador:": data.get('installer_phone'),
                "Prof. Obra:": data.get('professional_name'),
                "ITO:": data.get('technical_inspector'),
            }
            elements.append(self._create_info_block(personnel_info))
            
            # --- NUEVA UBICACIÓN: MÉTRICAS Y MAQUINARIA (ANTES DE DETALLES TÉCNICOS) ---
            machine_data = data.get('machine_data', {})
            if isinstance(machine_data, str):
                try: machine_data = json.loads(machine_data)
                except: machine_data = {}
            
            sap_meta = machine_data.get('sap_metadata', {})
            if sap_meta:
                elements.append(Paragraph("MÉTRICAS E INFORMACIÓN DE OBRA", self.styles['SectionHeader']))
                def bool_to_str(v): return "SÍ" if v else "NO"
                complementary_info = {
                    "Obra Finalizada:": bool_to_str(sap_meta.get('is_project_finished')),
                    "Material Mezclado:": bool_to_str(sap_meta.get('is_mixed_material')),
                    "Obra Rescatada/Nueva:": bool_to_str(sap_meta.get('is_rescued_project')),
                    "N° Patente Transp.:": sap_meta.get('patent_number', '-'),
                    "Nivel Instalación:": sap_meta.get('installation_level', 'NORMAL'),
                    "Obra Otro Prov.:": sap_meta.get('project_with_other_provider', 'NO'),
                    "Nombre Proveedor:": sap_meta.get('other_provider', '-'),
                }
                elements.append(self._create_info_block(complementary_info))
                

            
            machines = machine_data.get('machines', [])
            if machines:
                elements.append(Paragraph("DESEMPEÑO DE EQUIPOS Y MAQUINARIA", self.styles['SectionHeader']))
                m_table_data = [['#', 'Máquina / Equipo', 'Inicio (Hrs/Km)', 'Corte (Hrs/Km)']]
                for i, m in enumerate(machines):
                    m_table_data.append([str(i+1), m.get('machine', '-'), m.get('start', '-'), m.get('cut', '-')])
                
                m_col_widths = [1*cm, 9*cm, 3.5*cm, 3.5*cm]
                elements.append(self._create_full_width_table(m_table_data, m_col_widths))
                
                if machine_data.get('machine_removal'):
                    elements.append(Spacer(1, 3))
                    elements.append(Paragraph(f"<b>Retiro de Máquina:</b> SÍ (N° Reporte de Retiro: {machine_data.get('report_number', '-')})", self.styles['ModernBodyText']))
            
            # 4. Detalle Técnico (Motivo + Observaciones)
            elements.append(Paragraph("DETALLES TÉCNICOS Y OBSERVACIONES", self.styles['SectionHeader']))
            elements.append(Paragraph("<b>Motivo Visita:</b> Post Venta", self.styles['ModernBodyText']))
            elements.append(Spacer(1, 4))
            
            # Observaciones específicas
            sections = [
                ('Observaciones Generales', data.get('general_observations')),
                ('Muros / Tabiques', data.get('wall_observations')),
                ('Matriz', data.get('matrix_observations')),
                ('Losa', data.get('slab_observations')),
                ('Almacenaje', data.get('storage_observations')),
                ('Pre-Armados', data.get('pre_assembled_observations')),
                ('Exteriores', data.get('exterior_observations')),
            ]
            
            for title, content in sections:
                if content:
                    elements.append(Paragraph(f"<b>{title}:</b>", self.styles['FieldLabel']))
                    elements.append(Paragraph(content, self.styles['ModernBodyText']))
                    elements.append(Spacer(1, 3))
            
            # 5. Materiales Utilizados
            materials = data.get('materials_data', [])
            # Normalizar si viene como string JSON
            if isinstance(materials, str):
                try: materials = json.loads(materials)
                except: materials = []
                
            if materials:
                elements.append(Paragraph("MATERIALES UTILIZADOS", self.styles['SectionHeader']))
                # headers
                table_data = [['Material / Código', 'Cant.', 'Lote', 'Ubicación']]
                for m in materials:
                    # Adaptarse a la estructura real de materials_data
                    name = m.get('material_name') or m.get('name') or '-'
                    qty = m.get('quantity', '-')
                    lot = m.get('batch') or m.get('lote') or '-'
                    loc = m.get('location') or '-'
                    table_data.append([name, qty, lot, loc])
                
                # Ajustar anchos: Grande, Chico, Medio, Medio
                col_widths = [8*cm, 2*cm, 3*cm, 4*cm]
                total_w = sum(col_widths)
                # Rescale to fit printable width
                scale = self.printable_width / total_w
                col_widths = [w * scale for w in col_widths]
                
                elements.append(self._create_full_width_table(table_data, col_widths))
            
            # 8. Evidencia Fotográfica (Removido el PageBreak forzado para ahorrar hojas)
            elements.append(Spacer(1, 10))
            elements.append(Paragraph("EVIDENCIA FOTOGRÁFICA", self.styles['SectionHeader']))
            
            # Recopilar imágenes
            # (Aquí asumiríamos que las imágenes vienen en 'sap_attachments' o similar, 
            # pero el signal pasa el serializer.data completo. 
            # Si hay adjuntos en base de datos, deberíamos buscarlos aparte o pasarlos en 'data'.)
            # Por simplicidad, asumiremos que 'photos' o similar viene en data, o las del SAP attachments
            # SI NO VIENEN: el usuario mencionó "evidencia fotográfica". 
            # Usualmente esto viene de DocumentAttachment o la integración SAP.
            # Vamos a intentar buscar imágenes en carpetas temporales o URLs si vienen en el data.
            # *Para este caso de uso*, si la data viene de Visita, 
            # buscaremos las imágenes importadas de SAP Attachments si están en el modelo.
            
            # Nota: El serializer `VisitReportSerializer` debería incluir `attachments` o `sap_attachments`.
            # Como fallback, si no están, pondremos un mensaje o placeholder.
            
            # INTENT AR RECUPERAR DE DATA (si el serializer las trajo)
            # Si no, esto requeriría un query extra. asumamos que el serializer include 'attachments_info'
            # (Voy a asumir una lista genérica por ahora para estructura).
            
            # *MEJORA*: Si estamos en signal, podemos pasar las fotos explícitamente.
            # Pero para "optimizar", usaremos lo que hay.
            # Escanear 'attachments' en data
            images_to_show = []
            attachments = data.get('attachments', [])
            
            # DEBUGGING: Ver qué está llegando
            logger.info(f"PDF Generator - Total attachments recibidos: {len(attachments)}")
            for idx, att in enumerate(attachments):
                logger.info(f"Attachment {idx}: file={att.get('file')}, filename={att.get('filename')}")
            
            if attachments:
                for att in attachments:
                    # Si es imagen
                    file_path = att.get('file', '')
                    if file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                        # Construir la ruta absoluta
                        # El campo 'file' viene como /documentos/documents/attachments/...
                        # o como documents/attachments/...
                        # MEDIA_ROOT ya apunta a 'shared', así que necesitamos la parte después de /documentos/
                        rel_path = file_path.lstrip('/')
                        if rel_path.startswith('documentos/'):
                            rel_path = rel_path[len('documentos/'):]  # Remover el prefijo 'documentos/'
                        
                        abs_path = os.path.join(settings.MEDIA_ROOT, rel_path)
                        logger.info(f"Procesando imagen: rel_path={rel_path}, abs_path={abs_path}")
                        
                        # Verificar si el archivo existe
                        if os.path.exists(abs_path):
                            images_to_show.append({
                                'path': abs_path, 
                                'description': att.get('description', att.get('filename', ''))
                            })
                            logger.info(f"Imagen agregada: {abs_path}")
                        else:
                            logger.warning(f"Archivo no encontrado: {abs_path}")
            
            logger.info(f"Total de imágenes para mostrar en PDF: {len(images_to_show)}")
            
            # También soportar imágenes SAP importadas (que suelen guardarse como adjuntos también)
            
            if images_to_show:
                elements.append(self._create_photo_grid(images_to_show))
            else:
                elements.append(Paragraph("No se adjuntaron imágenes a este reporte.", self.styles['ModernBodyText']))
                
            elements.append(Spacer(1, 20))
            
            # 7. Firmas (Digitales)
            elements.append(KeepTogether([
                Paragraph("VALIDACIÓN", self.styles['SectionHeader']),
                Spacer(1, 15),
                self._build_signatures_block(data)
            ]))
            
            # Generar
            doc.build(elements, onFirstPage=self._draw_header_footer, onLaterPages=self._draw_header_footer)
            return True
            
        except Exception as e:
            logger.error(f"FATAL ERROR generando PDF moderno: {e}", exc_info=True)
            return False

    
    def _get_digital_signature(self, user):
        """
        Helper para obtener la ruta absoluta de la firma digital del usuario
        """
        try:
            if not user.digital_signature:
                logger.warning(f"Usuario {user.username} no tiene firma digital asignada")
                return None
                
            # Si es un objeto FieldFile (comportamiento normal de Django models)
            if hasattr(user.digital_signature, 'path'):
                file_path = user.digital_signature.path
                if os.path.exists(file_path):
                    logger.info(f"Firma digital encontrada (FieldFile): {file_path}")
                    return file_path
                else:
                    logger.warning(f"Firma digital (FieldFile) apunta a path inexistente: {file_path}")
            
            # Si es string (ej: URL relativa)
            file_path_str = str(user.digital_signature)
            logger.info(f"Resolviendo firma desde string: {file_path_str}")
            
            # Normalizar separadores y quitar prefijos de URL
            clean_path = file_path_str.replace('/', os.sep).replace('\\', os.sep)
            
            # Quitar 'documentos' del inicio si existe, ya que MEDIA_ROOT termina en 'documentos'
            # MEDIA_ROOT = ...\backend\documentos
            # Path esperado = users\signatures\file.jpg
            
            # Si viene como /documentos/users/... o documentos/users/...
            if clean_path.startswith(f"{os.sep}documentos{os.sep}"):
                clean_path = clean_path.replace(f"{os.sep}documentos{os.sep}", "", 1)
            elif clean_path.startswith(f"documentos{os.sep}"):
                clean_path = clean_path.replace(f"documentos{os.sep}", "", 1)
            elif clean_path.startswith("/documentos/"): # Caso unix style en string
                clean_path = clean_path.replace("/documentos/", "", 1)
                
            # Construir ruta completa
            full_path = os.path.join(settings.MEDIA_ROOT, clean_path)
            
            if os.path.exists(full_path):
                logger.info(f"Firma digital encontrada en path construido: {full_path}")
                return full_path
            
            # Intento alternativo: buscar directamente en la carpeta
            if 'users' in file_path_str and 'signatures' in file_path_str:
                filename = os.path.basename(file_path_str)
                alt_path = os.path.join(settings.MEDIA_ROOT, 'users', 'signatures', filename)
                if os.path.exists(alt_path):
                     logger.info(f"Firma digital encontrada en path alternativo: {alt_path}")
                     return alt_path

            logger.warning(f"No se encontró archivo de firma. Path construido: {full_path}")
            return None
            
        except Exception as e:
            logger.warning(f"Error resolviendo path firma digital: {e}")
            return None

    def _build_signatures_block(self, data):
        """Bloque de firmas dinámico según tipo de reporte"""
        
        # Imports al inicio
        from reportlab.lib import colors
        from reportlab.lib.styles import ParagraphStyle

        report_type = data.get('report_type', 'visita')
        tech_sign_img = None
        
        # Definir roles según tipo de reporte
        if 'Calidad' in str(report_type) or report_type in ['interno', 'cliente', 'proveedor']:
            role_1_title = "Analista de Calidad"
            role_2_title = "Revisado Por" if report_type == 'interno' else "Recibido Por"
            signer_name_field = 'created_by' 
        else:
            role_1_title = "Técnico Polifusión"
            role_2_title = "Aceptación Conforme" 
            signer_name_field = 'technician' # o created_by

        
        # Obtener usuario y firma digital
        user_full_name = "Personal Autorizado"
        tech_sign_img = None
        
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # 1. Intentar con technician_id (ID de SAP) - MÁXIMA PRIORIDAD
            technician_id_val = data.get('technician_id')
            user = None
            
            if technician_id_val:
                user = User.objects.filter(pk=technician_id_val).first()
                if user:
                    logger.info(f"Usuario encontrado por technician_id (SAP): {user.username}")
            
            # 2. Si no se encontró, intentar con created_by
            if not user:
                created_by_val = data.get('created_by')
                if isinstance(created_by_val, dict): 
                    created_by_val = created_by_val.get('id')
                
                if created_by_val:
                    user = User.objects.filter(pk=created_by_val).first()
                    if user:
                        logger.info(f"Usuario encontrado por created_by: {user.username}")
            
            # 3. Fallback: Intentar con technician (Nombre string o ID histórico)
            if not user:
                user_id_alt = data.get('technician')
                
                if user_id_alt:
                    # Si es numérico
                    if isinstance(user_id_alt, int) or (isinstance(user_id_alt, str) and user_id_alt.isdigit()):
                        user = User.objects.filter(pk=user_id_alt).first()
                    
                    # Si es nombre string
                    if not user and isinstance(user_id_alt, str):
                        logger.info(f"Buscando usuario por nombre/username: {user_id_alt}")
                        user = User.objects.filter(username__iexact=user_id_alt).first()
                        
                        if not user:
                            parts = user_id_alt.split()
                            if len(parts) >= 2:
                                user = User.objects.filter(
                                    first_name__iexact=parts[0], 
                                    last_name__iexact=" ".join(parts[1:])
                                ).first()
                        
                        if not user and not user_id_alt.isdigit():
                            # Si definitivamente es un nombre pero no hay usuario, lo guardamos para el PDF
                            user_full_name = user_id_alt
            
            if user:
                logger.info(f"Usuario final para firma: {user.username} (ID: {user.id})")
                signature_path = self._get_digital_signature(user)
                
                if signature_path:
                    try:
                        tech_sign_img = ReportLabImage(signature_path, width=4*cm, height=2*cm)
                        tech_sign_img.hAlign = 'CENTER'
                    except Exception as img_error:
                        logger.warning(f"No se pudo crear Image desde firma: {img_error}")
                
                # Nombre del usuario
                user_full_name = getattr(user, 'full_name', f"{user.first_name} {user.last_name}".strip()) or user.username
        except Exception as e:
            logger.warning(f"No se pudo resolver firma usuario: {e}")

        # Crear estilos específicos
        style_name = ParagraphStyle(
            'SignatureName',
            parent=self.styles['ModernBodyText'],
            fontSize=9,
            textColor=colors.HexColor('#333333'),
            alignment=1,
            spaceAfter=2
        )
        style_label = ParagraphStyle(
            'SignatureLabel',
            parent=self.styles['FieldLabel'],
            fontSize=7,
            textColor=colors.HexColor('#666666'),
            alignment=1
        )

        # Celda Técnico
        content_tech = []
        if tech_sign_img:
            content_tech.append(tech_sign_img)
            content_tech.append(Spacer(1, 3))
        else:
            content_tech.append(Spacer(1, 2*cm))  # Espacio para firma manual
            
        content_tech.append(Paragraph(user_full_name, style_name))
        content_tech.append(Spacer(1, 2))
        content_tech.append(Paragraph(role_1_title, style_label))
        
        # Celda Cliente / Receptor
        client_spacer_height = tech_sign_img.drawHeight if tech_sign_img else 2*cm
        # Intentar obtener nombre real del cliente/receptor
        # Para reportes de calidad, usar 'cliente' o 'provider' según el contexto
        client_signature_name = data.get('client_name') or data.get('cliente') or data.get('provider') or "Cliente"

        content_client = [
            Spacer(1, client_spacer_height),
            Spacer(1, 3),
            Paragraph(client_signature_name, style_name),
            Paragraph("", style_label),
            Spacer(1, 2),
            Paragraph(role_2_title, style_label)
        ]
        
        data_table = [[content_tech, content_client]]
        t = Table(data_table, colWidths=[8*cm, 8*cm])
        t.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('LINEABOVE', (0,0), (0,0), 1, colors.HexColor('#333333')),
            ('LINEABOVE', (1,0), (1,0), 1, colors.HexColor('#333333')),
            ('LEFTPADDING', (0,0), (-1,-1), 15),
            ('RIGHTPADDING', (0,0), (-1,-1), 15),
            ('TOPPADDING', (0,0), (-1,-1), 5),
        ]))
        return t

    def generate_quality_report(self, data: Dict, output_path: str) -> bool:
        """
        Genera un Reporte de Calidad de Alta Gama (Cliente o Interno)
        """
        try:
            from reportlab.lib import colors
            
            # Configurar Doc
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=self.margin_x,
                leftMargin=self.margin_x,
                topMargin=3.5*cm, 
                bottomMargin=2.0*cm
            )
            
            elements = []
            
            # 1. TÍTULO Y CABECERA TÉCNICA
            report_type = data.get('report_type', 'Informe de Calidad')
            report_number = data.get('report_number', '-')
            date_str = data.get('date_created', datetime.now().strftime('%d/%m/%Y'))
            
            elements.append(Paragraph(f"INFORME DE CALIDAD - {report_type.upper()}", self.styles['ModernTitle']))
            elements.append(Paragraph(f"N° Reporte: {report_number} | Fecha: {date_str}", self.styles['ModernSubtitle']))
            elements.append(Spacer(1, 10))
            
            # 2. INFORMACIÓN DE LA INCIDENCIA (CONTEXTO)
            elements.append(Paragraph("INFORMACIÓN DE REFERENCIA", self.styles['SectionHeader']))
            
            # Parsear detalles técnicos si vienen en JSON
            tech_dict = {}
            if data.get('technical_details'):
                import json
                try:
                    tech_dict = json.loads(data['technical_details'])
                except:
                    pass

            ref_info = {
                "Incidencia:": data.get('incident_code', '-'),
                "Cliente:": data.get('cliente', '-'),
                "Proyecto/Obra:": data.get('obra', '-'),
                "Proveedor:": data.get('provider', '-'),
                "Producto/SKU:": f"{data.get('sku', '-')} | Cód: {tech_dict.get('item_code', '-')}",
                "Categoría:": data.get('categoria', '-'),
            }
            elements.append(self._create_info_block(ref_info))
            
            # 2.1 TABLA DE ESPECIFICACIONES TÉCNICAS (NUEVO)
            product_data = tech_dict.get('product', {})
            if product_data:
                elements.append(Paragraph("ESPECIFICACIONES DEL PRODUCTO", self.styles['SectionHeader']))
                spec_info = {
                    "Diámetro (mm):": product_data.get('diameter', '-'),
                    "PN (Presión):": product_data.get('pn', '-'),
                    "SDR:": product_data.get('sdr', '-'),
                    "Material:": product_data.get('material', '-'),
                    "Lote Fabr.:": product_data.get('lot', '-'),
                    "Condición:": product_data.get('condition', 'NUEVO')
                }
                elements.append(self._create_info_block(spec_info))
                elements.append(Spacer(1, 5))

            # 2.2 CONDICIONES DE SITIO E INSTALACIÓN (NUEVO)
            site_data = tech_dict.get('site_conditions', {})
            if site_data:
                elements.append(Paragraph("CONDICIONES DE INSTALACIÓN", self.styles['SectionHeader']))
                site_info = {
                    "Método Unión:": site_data.get('method', '-'),
                    "Temp. Amb.:": f"{site_data.get('temperature', '-')} °C",
                    "ID Máquina:": site_data.get('machine_id', '-'),
                    "Normativa:": site_data.get('normative', '-'),
                    "Herramientas:": site_data.get('tools', '-'),
                    "Instalador:": data.get('installer', '-'),
                }
                elements.append(self._create_info_block(site_info))
                elements.append(Spacer(1, 5))
                
                # Imagen de sitio
                site_imgs = self._get_section_images_flow(data.get('report_id'), 'site_conditions')
                if site_imgs:
                    elements.append(self._create_photo_grid(site_imgs))
                    elements.append(Spacer(1, 5))
            
            # 2.3 PROTOCOLO DE PRUEBAS
            test_data = tech_dict.get('test_protocol', {})
            if test_data:
                elements.append(Paragraph("PROTOCOLO DE INSPECCIÓN Y PRUEBAS", self.styles['SectionHeader']))
                
                # ... tabla de pruebas ...
                result = test_data.get('result', 'N/A')
                res_color = '#10B981' if result == 'Aprobado' else '#EF4444' if result == 'Rechazado' else '#64748B'
                
                test_table_data = [
                    [
                        Paragraph("<b>Inspección Visual</b>", self.styles['FieldLabel']),
                        Paragraph("<b>Prueba Presión</b>", self.styles['FieldLabel']),
                        Paragraph("<b>Presión (Bar)</b>", self.styles['FieldLabel']),
                        Paragraph("<b>VEREDICTO</b>", self.styles['FieldLabel']),
                    ],
                    [
                        Paragraph(test_data.get('visual', '-'), self.styles['ModernBodyText']),
                        Paragraph(test_data.get('pressure_test', '-'), self.styles['ModernBodyText']),
                        Paragraph(str(test_data.get('pressure_bar', '-')), self.styles['ModernBodyText']),
                        Paragraph(f"<font color='{res_color}'><b>{result.upper()}</b></font>", self.styles['ModernBodyText']),
                    ]
                ]
                
                t = Table(test_table_data, colWidths=[4.5*cm, 4.5*cm, 3.5*cm, 4.5*cm])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), COLOR_BG_HEADER),
                    ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                elements.append(t)
                elements.append(Spacer(1, 5))
                
                # Imagen de pruebas
                test_imgs = self._get_section_images_flow(data.get('report_id'), 'test_protocol')
                if test_imgs:
                    elements.append(self._create_photo_grid(test_imgs))
                    elements.append(Spacer(1, 5))

            # 2.4 ENSAYOS DE LABORATORIO (NUEVO)
            lab_data = tech_dict.get('lab_tests', {})
            if lab_data:
                elements.append(Paragraph("ENSAYOS DE LABORATORIO / ANÁLISIS DE POLÍMEROS", self.styles['SectionHeader']))
                
                lab_table_data = [
                    [
                        Paragraph("<b>Ensayo / Parámetro</b>", self.styles['FieldLabel']),
                        Paragraph("<b>Resultado</b>", self.styles['FieldLabel']),
                        Paragraph("<b>Ensayo / Parámetro</b>", self.styles['FieldLabel']),
                        Paragraph("<b>Resultado</b>", self.styles['FieldLabel']),
                    ],
                    [
                        Paragraph("Melt Index (g/10 min):", self.styles['ModernBodyText']),
                        Paragraph(str(lab_data.get('melt_index', '-')), self.styles['ModernBodyText']),
                        Paragraph("Densidad (g/cm³):", self.styles['ModernBodyText']),
                        Paragraph(str(lab_data.get('density', '-')), self.styles['ModernBodyText']),
                    ],
                    [
                        Paragraph("TIO (Oxidation Induction Time):", self.styles['ModernBodyText']),
                        Paragraph(str(lab_data.get('tio', '-')), self.styles['ModernBodyText']),
                        Paragraph("DSC (Diff. Scanning Calo.):", self.styles['ModernBodyText']),
                        Paragraph(str(lab_data.get('dsc', '-')), self.styles['ModernBodyText']),
                    ],
                    [
                        Paragraph("Dispersión Negro de Humo:", self.styles['ModernBodyText']),
                        Paragraph(str(lab_data.get('carbon_black_dispersion', '-')), self.styles['ModernBodyText']),
                        Paragraph("% Negro de Humo:", self.styles['ModernBodyText']),
                        Paragraph(str(lab_data.get('carbon_black_percentage', '-')), self.styles['ModernBodyText']),
                    ],
                    [
                        Paragraph("% Cenizas:", self.styles['ModernBodyText']),
                        Paragraph(str(lab_data.get('ash_percentage', '-')), self.styles['ModernBodyText']),
                        Paragraph("% Humedad:", self.styles['ModernBodyText']),
                        Paragraph(str(lab_data.get('moisture_percentage', '-')), self.styles['ModernBodyText']),
                    ]
                ]
                
                t_lab = Table(lab_table_data, colWidths=[6*cm, 3*cm, 6*cm, 3*cm])
                t_lab.setStyle(TableStyle([
                    ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('BACKGROUND', (0,0), (0,-1), COLOR_BG_HEADER),
                    ('BACKGROUND', (2,0), (2,-1), COLOR_BG_HEADER),
                ]))
                elements.append(t_lab)
                elements.append(Spacer(1, 5))
                
                # Imagen de laboratorio
                lab_imgs = self._get_section_images_flow(data.get('report_id'), 'lab_tests')
                if lab_imgs:
                    elements.append(self._create_photo_grid(lab_imgs))
                    elements.append(Spacer(1, 5))
            
            # 3. RESUMEN EJECUTIVO
            if data.get('executive_summary'):
                elements.append(Paragraph("RESUMEN EJECUTIVO", self.styles['SectionHeader']))
                elements.append(Paragraph(data['executive_summary'], self.styles['ModernBodyText']))
                elements.append(Spacer(1, 5))
            
            # 4. DESCRIPCIÓN DEL PROBLEMA
            elements.append(Paragraph("DESCRIPCIÓN DEL PROBLEMA", self.styles['SectionHeader']))
            elements.append(Paragraph(data.get('problem_description', 'No se proporcionó descripción.'), self.styles['ModernBodyText']))
            elements.append(Spacer(1, 5))
            
            # 5. ANÁLISIS DE CAUSA RAÍZ
            elements.append(Paragraph("ANÁLISIS DE CAUSA RAÍZ (ROOT CAUSE)", self.styles['SectionHeader']))
            elements.append(Paragraph(data.get('root_cause_analysis', 'En proceso de análisis.'), self.styles['ModernBodyText']))
            elements.append(Spacer(1, 10))
            
            # 6. ACCIONES Y MEJORAS (Layout en 2 columnas si es necesario, o lista)
            elements.append(Paragraph("ACCIONES CORRECTIVAS Y PREVENTIVAS", self.styles['SectionHeader']))
            
            elements.append(Paragraph("<b>Acciones Correctivas (Inmediatas):</b>", self.styles['FieldLabel']))
            elements.append(Paragraph(data.get('corrective_actions', '-'), self.styles['ModernBodyText']))
            elements.append(Spacer(1, 5))
            
            elements.append(Paragraph("<b>Medidas Preventivas (Largo Plazo):</b>", self.styles['FieldLabel']))
            elements.append(Paragraph(data.get('preventive_measures', '-'), self.styles['ModernBodyText']))
            elements.append(Spacer(1, 10))
            
            # 7. RECOMENDACIONES TÉCNICAS
            if data.get('recommendations'):
                elements.append(Paragraph("RECOMENDACIONES", self.styles['SectionHeader']))
                elements.append(Paragraph(data['recommendations'], self.styles['ModernBodyText']))
                elements.append(Spacer(1, 10))

            # 8. DETALLES TÉCNICOS ADICIONALES (Solo si existen y no fueron procesados arriba)
            # Si el technical_details era un string plano, lo mostramos aquí
            if data.get('technical_details') and not data['technical_details'].strip().startswith('{'):
                elements.append(Paragraph("DETALLES TÉCNICOS ADICIONALES", self.styles['SectionHeader']))
                elements.append(Paragraph(data['technical_details'], self.styles['ModernBodyText']))
                elements.append(Spacer(1, 10))

            # 9. NOTAS INTERNAS (SÓLO SI ES REPORTE INTERNO)
            # Nota: La vista ya filtra si enviar o no internal_notes según el tipo
            if data.get('internal_notes'):
                elements.append(Paragraph("NOTAS INTERNAS (CONFIDENCIAL)", self.styles['SectionHeader']))
                # Usar color de fondo especial para destacar confidencialidad
                note_style = ParagraphStyle(
                    'InternalNote',
                    parent=self.styles['ModernBodyText'],
                    textColor=colors.HexColor('#7F1D1D'), # Rojo oscuro
                    backColor=colors.HexColor('#FEF2F2'), # Fondo rosado muy claro
                    borderPadding=5,
                    leading=11
                )
                elements.append(Paragraph(data['internal_notes'], note_style))
                elements.append(Spacer(1, 10))

            # 10. FIRMAS Y VALIDACIÓN
            elements.append(Spacer(1, 20))
            elements.append(KeepTogether([
                Paragraph("FIRMAS DE RESPONSABILIDAD", self.styles['SectionHeader']),
                Spacer(1, 15),
                self._build_signatures_block(data)
            ]))
            
            # Generar
            doc.build(elements, onFirstPage=self._draw_header_footer, onLaterPages=self._draw_header_footer)
            return True
            
        except Exception as e:
            logger.error(f"Error generando PDF de reporte de calidad: {e}", exc_info=True)
            return False

    def generate_supplier_report(self, data: Dict, output_path: str) -> bool:
        """
        Genera un Reporte para Proveedor (Wrapper de Calidad)
        """
        try:
            # 1. Configurar tipo
            data['report_type'] = 'Reclamo a Proveedor'
            
            # 2. Mapear campos específicos
            if data.get('supplier_name'):
                data['provider'] = data.get('supplier_name')
                
            # 3. Manejar detalles técnicos (JSON vs Texto)
            # En SupplierReport, el JSON estructurado se guarda en technical_analysis
            tech_content = data.get('technical_analysis', '')
            if tech_content and isinstance(tech_content, str) and tech_content.strip().startswith('{'):
                # Es un JSON estructurado, pasarlo como technical_details para que generate_quality_report lo procese
                data['technical_details'] = tech_content
            
            # 4. Reutilizar generador de calidad de alta gama
            return self.generate_quality_report(data, output_path)
            
        except Exception as e:
            logger.error(f"Error generando PDF de reporte proveedor: {e}", exc_info=True)
            return False
