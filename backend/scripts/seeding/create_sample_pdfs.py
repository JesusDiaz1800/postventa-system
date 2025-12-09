#!/usr/bin/env python3
"""
Script para crear PDFs de ejemplo para los reportes
"""
import os
import sys
import django
from pathlib import Path
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

def create_sample_pdf(filename, title, content, report_type):
    """Crear un PDF de ejemplo"""
    
    # Crear directorio si no existe
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Crear documento PDF
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.darkblue
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        alignment=TA_JUSTIFY
    )
    
    # Contenido del PDF
    story = []
    
    # Logo/Header
    story.append(Paragraph("POLIFUSION", title_style))
    story.append(Paragraph("Sistema de Postventa", styles['Heading3']))
    story.append(Spacer(1, 20))
    
    # Título del reporte
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 20))
    
    # Información del reporte
    story.append(Paragraph(f"<b>Tipo de Reporte:</b> {report_type}", normal_style))
    story.append(Paragraph(f"<b>Fecha de Generación:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", normal_style))
    story.append(Spacer(1, 20))
    
    # Contenido específico
    for section_title, section_content in content.items():
        story.append(Paragraph(section_title, heading_style))
        story.append(Paragraph(section_content, normal_style))
        story.append(Spacer(1, 12))
    
    # Footer
    story.append(Spacer(1, 30))
    story.append(Paragraph("Este documento fue generado automáticamente por el Sistema de Postventa Polifusion", 
                          ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER)))
    
    # Construir PDF
    doc.build(story)
    print(f"PDF creado: {filename}")

def create_all_sample_pdfs():
    """Crear todos los PDFs de ejemplo"""
    
    # PDF de Reporte de Visita
    visit_content = {
        "<b>Resumen de la Visita:</b>": 
            "Se realizó una inspección técnica completa en el proyecto Residencial Los Pinos para evaluar las fisuras detectadas en las tuberías PVC de 110mm.",
        
        "<b>Hallazgos Principales:</b>": 
            "Se identificaron fisuras longitudinales en 12 unidades del lote LOTE-2025-001. Las fisuras tienen una profundidad promedio de 2-3mm y se extienden entre 20-30cm desde las uniones.",
        
        "<b>Análisis Técnico:</b>": 
            "Las fisuras parecen estar relacionadas con tensiones térmicas durante la instalación. Se observó que las tuberías fueron instaladas en condiciones de alta temperatura sin considerar la expansión térmica adecuada.",
        
        "<b>Recomendaciones:</b>": 
            "1. Reemplazar todas las unidades afectadas del lote. 2. Implementar protocolo de instalación con consideración de expansión térmica. 3. Capacitar al personal de instalación en mejores prácticas.",
        
        "<b>Próximos Pasos:</b>": 
            "Envío de muestras a laboratorio para análisis químico y mecánico. Programación de reemplazo de unidades afectadas."
    }
    
    create_sample_pdf(
        "media/visit_reports/VR-2025-001.pdf",
        "REPORTE DE VISITA TÉCNICA",
        visit_content,
        "Reporte de Visita"
    )
    
    # PDF de Informe de Laboratorio
    lab_content = {
        "<b>Descripción de la Muestra:</b>": 
            "Muestras de tubería PVC 110mm con fisuras longitudinales del lote LOTE-2025-001.",
        
        "<b>Métodos de Prueba:</b>": 
            "ASTM D638 (Propiedades de tracción), ASTM D256 (Resistencia al impacto), Análisis químico por espectroscopía infrarroja.",
        
        "<b>Resultados de las Pruebas:</b>": 
            "Resistencia a la tracción: 45.2 MPa (vs. 52.0 MPa especificado). Resistencia al impacto: 8.5 J/m (vs. 12.0 J/m especificado). Análisis químico: Presencia de impurezas en el material base.",
        
        "<b>Conclusiones:</b>": 
            "Las fisuras se deben a una combinación de tensiones térmicas y presencia de impurezas en el material que reducen la resistencia mecánica. El material no cumple con las especificaciones técnicas.",
        
        "<b>Recomendaciones:</b>": 
            "1. Rechazar el lote completo LOTE-2025-001. 2. Solicitar certificado de calidad del proveedor. 3. Implementar control de calidad más estricto en recepción."
    }
    
    create_sample_pdf(
        "media/lab_reports/LR-2025-001.pdf",
        "INFORME DE LABORATORIO",
        lab_content,
        "Informe de Laboratorio"
    )
    
    # PDF de Informe para Proveedor
    supplier_content = {
        "<b>Descripción del Problema:</b>": 
            "Fisuras longitudinales en tuberías PVC 110mm del lote LOTE-2025-001. Análisis de laboratorio confirma que el material no cumple con especificaciones técnicas.",
        
        "<b>Análisis Técnico:</b>": 
            "Las pruebas de laboratorio revelan resistencia a la tracción de 45.2 MPa vs. 52.0 MPa especificado, y presencia de impurezas en el material base que afectan la integridad estructural.",
        
        "<b>Evaluación del Impacto:</b>": 
            "150 unidades afectadas, costo estimado de reemplazo: $2,500 USD. Retraso en proyecto de 5 días. Riesgo de falla estructural en sistema de drenaje.",
        
        "<b>Acciones Solicitadas:</b>": 
            "1. Reemplazo inmediato de todas las unidades del lote LOTE-2025-001. 2. Certificado de calidad del nuevo lote. 3. Compensación por costos adicionales de instalación.",
        
        "<b>Plazo de Respuesta:</b>": 
            "Se solicita respuesta dentro de 7 días hábiles para coordinar el reemplazo de las unidades afectadas."
    }
    
    create_sample_pdf(
        "media/supplier_reports/SR-2025-001.pdf",
        "INFORME PARA PROVEEDOR",
        supplier_content,
        "Informe para Proveedor"
    )
    
    print("=== TODOS LOS PDFs DE EJEMPLO CREADOS ===")
    print("Los archivos están disponibles en:")
    print("- media/visit_reports/VR-2025-001.pdf")
    print("- media/lab_reports/LR-2025-001.pdf")
    print("- media/supplier_reports/SR-2025-001.pdf")

if __name__ == '__main__':
    create_all_sample_pdfs()
