"""
Motor de workflows para gestión de incidencias
"""
import logging
from typing import Dict, Any, List, Optional, Tuple
from django.db import transaction
from django.utils import timezone
from .models import Workflow, WorkflowState, WorkflowTransition, IncidentWorkflow, WorkflowHistory
from apps.incidents.models import Incident
from apps.users.models import User

logger = logging.getLogger(__name__)


class WorkflowEngine:
    """Motor de workflows para gestión de incidencias"""
    
    def __init__(self):
        self.workflows = {}
        self._load_workflows()
    
    def _load_workflows(self):
        """Cargar workflows desde la base de datos"""
        try:
            workflows = Workflow.objects.filter(is_active=True)
            for workflow in workflows:
                self.workflows[workflow.incident_type] = workflow
            logger.info(f"Cargados {len(self.workflows)} workflows")
        except Exception as e:
            logger.error(f"Error cargando workflows: {e}")
    
    def get_workflow_for_incident(self, incident: Incident) -> Optional[Workflow]:
        """Obtener workflow apropiado para una incidencia"""
        try:
            # Buscar workflow por tipo de incidencia
            workflow = self.workflows.get(incident.categoria)
            if workflow:
                return workflow
            
            # Fallback a workflow por defecto
            default_workflow = Workflow.objects.filter(
                incident_type='defecto_fabricacion',
                is_active=True
            ).first()
            
            return default_workflow
            
        except Exception as e:
            logger.error(f"Error obteniendo workflow para incidencia: {e}")
            return None
    
    def start_workflow(self, incident: Incident, user: User) -> Optional[IncidentWorkflow]:
        """Iniciar workflow para una incidencia"""
        try:
            with transaction.atomic():
                # Obtener workflow apropiado
                workflow = self.get_workflow_for_incident(incident)
                if not workflow:
                    raise ValueError("No se encontró workflow apropiado")
                
                # Obtener estado inicial
                initial_state = WorkflowState.objects.filter(
                    workflow=workflow,
                    is_initial=True
                ).first()
                
                if not initial_state:
                    raise ValueError("No se encontró estado inicial del workflow")
                
                # Crear instancia de workflow
                incident_workflow = IncidentWorkflow.objects.create(
                    incident=incident,
                    workflow=workflow,
                    current_state=initial_state
                )
                
                # Registrar en historial
                WorkflowHistory.objects.create(
                    incident_workflow=incident_workflow,
                    to_state=initial_state,
                    user=user,
                    description=f"Iniciado workflow {workflow.name}",
                    metadata={'workflow_id': workflow.id}
                )
                
                logger.info(f"Workflow iniciado para incidencia {incident.code}")
                return incident_workflow
                
        except Exception as e:
            logger.error(f"Error iniciando workflow: {e}")
            return None
    
    def get_available_transitions(self, incident_workflow: IncidentWorkflow, user: User) -> List[WorkflowTransition]:
        """Obtener transiciones disponibles para el estado actual"""
        try:
            transitions = WorkflowTransition.objects.filter(
                workflow=incident_workflow.workflow,
                from_state=incident_workflow.current_state,
                is_active=True
            )
            
            # Filtrar por rol del usuario
            available_transitions = []
            for transition in transitions:
                if user.role in transition.allowed_roles:
                    # Verificar condiciones
                    if self._check_transition_conditions(transition, incident_workflow):
                        available_transitions.append(transition)
            
            return available_transitions
            
        except Exception as e:
            logger.error(f"Error obteniendo transiciones disponibles: {e}")
            return []
    
    def _check_transition_conditions(self, transition: WorkflowTransition, incident_workflow: IncidentWorkflow) -> bool:
        """Verificar condiciones para una transición"""
        try:
            # Verificar acciones requeridas
            for action in transition.required_actions:
                if not self._is_action_completed(action, incident_workflow):
                    return False
            
            # Verificar condiciones específicas
            for condition in transition.required_conditions:
                if not self._evaluate_condition(condition, incident_workflow):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error verificando condiciones de transición: {e}")
            return False
    
    def _is_action_completed(self, action: str, incident_workflow: IncidentWorkflow) -> bool:
        """Verificar si una acción está completada"""
        try:
            incident = incident_workflow.incident
            
            if action == 'upload_photos':
                return incident.images.exists()
            elif action == 'complete_analysis':
                return bool(incident.ai_analysis)
            elif action == 'generate_document':
                # Verificar si hay documentos en las tablas existentes
                from apps.documents.models import VisitReport, SupplierReport, LabReport, QualityReport
                return (
                    VisitReport.objects.filter(related_incident=incident).exists() or
                    SupplierReport.objects.filter(related_incident=incident).exists() or
                    LabReport.objects.filter(related_incident=incident).exists() or
                    QualityReport.objects.filter(related_incident=incident).exists()
                )
            elif action == 'lab_report':
                return incident.lab_reports.exists()
            elif action == 'approve_solution':
                return incident.estado == 'resuelto'
            elif action == 'notify_client':
                # Verificar si se envió notificación al cliente
                return incident.estado in ['resuelto', 'cerrado']
            elif action == 'notify_provider':
                # Verificar si se envió notificación al proveedor
                return incident.estado in ['resuelto', 'cerrado']
            
            return False
            
        except Exception as e:
            logger.error(f"Error verificando acción completada: {e}")
            return False
    
    def _evaluate_condition(self, condition: Dict[str, Any], incident_workflow: IncidentWorkflow) -> bool:
        """Evaluar condición específica"""
        try:
            condition_type = condition.get('type')
            condition_value = condition.get('value')
            
            if condition_type == 'incident_priority':
                return incident_workflow.incident.prioridad == condition_value
            elif condition_type == 'has_lab_report':
                return incident_workflow.incident.lab_reports.exists()
            elif condition_type == 'has_ai_analysis':
                return bool(incident_workflow.incident.ai_analysis)
            
            return True
            
        except Exception as e:
            logger.error(f"Error evaluando condición: {e}")
            return True
    
    def transition_to_state(self, incident_workflow: IncidentWorkflow, to_state: WorkflowState, user: User, data: Dict[str, Any] = None) -> Tuple[bool, str]:
        """Realizar transición a un nuevo estado"""
        try:
            with transaction.atomic():
                # Verificar si la transición es válida
                transition = WorkflowTransition.objects.filter(
                    workflow=incident_workflow.workflow,
                    from_state=incident_workflow.current_state,
                    to_state=to_state,
                    is_active=True
                ).first()
                
                if not transition:
                    return False, "Transición no válida"
                
                # Verificar rol del usuario
                if user.role not in transition.allowed_roles:
                    return False, f"Rol {user.role} no autorizado para esta transición"
                
                # Verificar condiciones
                if not self._check_transition_conditions(transition, incident_workflow):
                    return False, "Condiciones no cumplidas para la transición"
                
                # Realizar transición
                from_state = incident_workflow.current_state
                incident_workflow.current_state = to_state
                incident_workflow.updated_at = timezone.now()
                incident_workflow.save()
                
                # Registrar en historial
                WorkflowHistory.objects.create(
                    incident_workflow=incident_workflow,
                    from_state=from_state,
                    to_state=to_state,
                    transition=transition,
                    user=user,
                    description=transition.description or f"Transición de {from_state.display_name} a {to_state.display_name}",
                    metadata=data or {}
                )
                
                # Actualizar estado de la incidencia si es necesario
                self._update_incident_state(incident_workflow, to_state)
                
                logger.info(f"Transición exitosa: {incident_workflow.incident.code} - {from_state.display_name} → {to_state.display_name}")
                return True, "Transición exitosa"
                
        except Exception as e:
            logger.error(f"Error realizando transición: {e}")
            return False, f"Error en transición: {str(e)}"
    
    def _update_incident_state(self, incident_workflow: IncidentWorkflow, workflow_state: WorkflowState):
        """Actualizar estado de la incidencia basado en el estado del workflow"""
        try:
            incident = incident_workflow.incident
            
            # Mapear estados del workflow a estados de incidencia
            state_mapping = {
                'nuevo': 'abierto',
                'triage': 'abierto',
                'inspeccion': 'en_proceso',
                'laboratorio': 'en_proceso',
                'propuesta': 'en_proceso',
                'resuelto': 'resuelto',
                'cerrado': 'cerrado'
            }
            
            new_incident_state = state_mapping.get(workflow_state.name, incident.estado)
            if new_incident_state != incident.estado:
                incident.estado = new_incident_state
                incident.save()
                
        except Exception as e:
            logger.error(f"Error actualizando estado de incidencia: {e}")
    
    def get_workflow_progress(self, incident_workflow: IncidentWorkflow) -> Dict[str, Any]:
        """Obtener progreso del workflow"""
        try:
            workflow = incident_workflow.workflow
            current_state = incident_workflow.current_state
            
            # Obtener todos los estados del workflow
            all_states = WorkflowState.objects.filter(workflow=workflow).order_by('order')
            
            # Calcular progreso
            total_states = all_states.count()
            current_order = current_state.order
            progress_percentage = (current_order / total_states) * 100 if total_states > 0 else 0
            
            # Obtener transiciones disponibles
            available_transitions = self.get_available_transitions(incident_workflow, incident_workflow.incident.created_by)
            
            # Obtener historial
            history = WorkflowHistory.objects.filter(incident_workflow=incident_workflow).order_by('-created_at')
            
            return {
                'workflow_name': workflow.name,
                'current_state': {
                    'name': current_state.name,
                    'display_name': current_state.display_name,
                    'description': current_state.description,
                    'order': current_state.order
                },
                'progress_percentage': progress_percentage,
                'total_states': total_states,
                'current_order': current_order,
                'available_transitions': [
                    {
                        'id': t.id,
                        'name': t.name,
                        'display_name': t.display_name,
                        'description': t.description,
                        'to_state': t.to_state.display_name
                    }
                    for t in available_transitions
                ],
                'history': [
                    {
                        'from_state': h.from_state.display_name if h.from_state else 'Inicio',
                        'to_state': h.to_state.display_name,
                        'user': h.user.username,
                        'description': h.description,
                        'timestamp': h.created_at.isoformat()
                    }
                    for h in history
                ]
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo progreso del workflow: {e}")
            return {}
    
    def refresh_workflows(self):
        """Refrescar workflows desde la base de datos"""
        try:
            self.workflows.clear()
            self._load_workflows()
            logger.info("Workflows refrescados")
        except Exception as e:
            logger.error(f"Error refrescando workflows: {e}")


# Instancia global del motor de workflows
workflow_engine = WorkflowEngine()