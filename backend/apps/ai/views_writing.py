"""
API Views for AI Writing Assistant
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import logging

from .services.writing_assistant import writing_assistant

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def improve_text(request):
    """
    Improve text to make it more professional.
    
    POST /api/ai/writing/improve/
    Body: {"text": "texto a mejorar"}
    """
    text = request.data.get('text', '')
    
    if not text or len(text.strip()) < 10:
        return Response(
            {'error': 'Por favor proporcione un texto de al menos 10 caracteres'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        result = writing_assistant.improve_text(text)
        return Response(result)
    except Exception as e:
        logger.error(f"Error improving text: {e}")
        return Response(
            {'error': 'Error al procesar el texto'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def fix_errors(request):
    """
    Fix grammar, spelling and punctuation errors.
    
    POST /api/ai/writing/fix/
    Body: {"text": "texto con errores"}
    """
    text = request.data.get('text', '')
    
    if not text or len(text.strip()) < 5:
        return Response(
            {'error': 'Por favor proporcione un texto'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        result = writing_assistant.fix_errors(text)
        return Response(result)
    except Exception as e:
        logger.error(f"Error fixing text: {e}")
        return Response(
            {'error': 'Error al corregir el texto'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_report(request):
    """
    Generate technical report content.
    
    POST /api/ai/writing/generate-report/
    Body: {"client_name": "...", "project_name": "...", "visit_reason": "...", "observations": "..."}
    """
    context = {
        'client_name': request.data.get('client_name', ''),
        'project_name': request.data.get('project_name', ''),
        'visit_reason': request.data.get('visit_reason', ''),
        'observations': request.data.get('observations', ''),
    }
    
    try:
        result = writing_assistant.generate_technical_report(context)
        return Response(result)
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return Response(
            {'error': 'Error al generar el reporte'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def suggest_terms(request):
    """
    Suggest correct technical terms.
    
    POST /api/ai/writing/suggest-terms/
    Body: {"text": "texto a analizar"}
    """
    text = request.data.get('text', '')
    
    if not text:
        return Response(
            {'error': 'Por favor proporcione un texto'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        result = writing_assistant.suggest_technical_terms(text)
        return Response(result)
    except Exception as e:
        logger.error(f"Error suggesting terms: {e}")
        return Response(
            {'error': 'Error al analizar el texto'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def expand_term(request):
    """
    Expand and explain a technical term.
    
    POST /api/ai/writing/expand-term/
    Body: {"term": "HDPE"}
    """
    term = request.data.get('term', '')
    
    if not term:
        return Response(
            {'error': 'Por favor proporcione un término'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        result = writing_assistant.expand_abbreviation(term)
        return Response(result)
    except Exception as e:
        logger.error(f"Error expanding term: {e}")
        return Response(
            {'error': 'Error al expandir el término'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_closure(request):
    """
    Generate an analytical closure conclusion based on stage documents.
    
    POST /api/ai/writing/analyze-closure/
    Body: {"incident_id": 123, "stage": "laboratorio"}
    """
    incident_id = request.data.get('incident_id')
    stage = request.data.get('stage', 'general')  # laboratorio, proveedor, visita, general
    
    if not incident_id:
        return Response(
            {'error': 'incident_id es requerido'},
            status=status.HTTP_400_BAD_REQUEST
        )
        
    try:
        from apps.incidents.models import Incident
        from apps.documents.models import VisitReport, LabReport, SupplierReport, QualityReport
        
        # 1. Fetch Incident
        try:
            incident = Incident.objects.get(pk=incident_id)
        except Incident.DoesNotExist:
             return Response({'error': 'Incidencia no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        context = {
            'client_name': incident.cliente,
            'project_name': incident.obra,
            'problem': incident.descripcion,
            'stage': stage
        }
        
        evidence_text = []
        
        # 2. Gather Evidence based on Stage
        if stage == 'reporte_visita':
            reports = VisitReport.objects.filter(related_incident=incident)
            for r in reports:
                evidence_text.append(f"REPORTE VISITA {r.report_number}: {r.general_observations}")
                
        elif stage == 'laboratorio' or stage == 'calidad':
            # Check Lab Reports
            lab_reports = LabReport.objects.filter(related_incident=incident)
            for r in lab_reports:
                evidence_text.append(f"INFORME LAB {r.report_number}: Conclusiones: {r.conclusions}. Recomendaciones: {r.recommendations}")
            
            # Check Quality Reports (Internal)
            q_reports = QualityReport.objects.filter(related_incident=incident, report_type='interno')
            for r in q_reports:
                evidence_text.append(f"REPORTE CALIDAD {r.report_number}: Causa Raíz: {r.root_cause_analysis}. Acciones: {r.corrective_actions}")
                
        elif stage == 'proveedor':
            sup_reports = SupplierReport.objects.filter(related_incident=incident)
            for r in sup_reports:
                evidence_text.append(f"INFORME PROVEEDOR {r.report_number}: Análisis: {r.technical_analysis}")

        # Fallback if no specific docs found
        if not evidence_text:
            evidence_text.append("No se encontraron documentos específicos para esta etapa. Basar análisis en la descripción del problema y estado general.")

        context['evidence'] = "\n".join(evidence_text)
        
        # 3. Call AI
        result = writing_assistant.generate_closure_analysis(context)
        return Response(result)
        
    except Exception as e:
        logger.error(f"Error analyzing closure: {e}")
        return Response(
            {'error': f'Error al generar análisis: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_text(request):
    """
    Generic text generation for analysis, reasons, etc.
    """
    prompt = request.data.get('prompt', '')
    context = request.data.get('context', {})
    prompt_type = request.data.get('prompt_type', 'general')
    
    if not prompt and not context:
        return Response(
            {'error': 'Se requiere un prompt o contexto'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Use existing service to generate text
        result = writing_assistant.generate_custom_text(prompt, context, prompt_type)
        return Response(result)
    except Exception as e:
        logger.error(f"Error generating generic text: {e}")
        return Response(
            {'error': 'Error al generar texto con IA'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
