"""
Celery tasks for AI Orchestrator
"""
# from celery import shared_task
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


# @shared_task(bind=True)
def analyze_image_task(self, image_id):
    """
    Analyze an image using AI providers (OBSOLETE for Incidents)
    """
    logger.warning(f"analyze_image_task called for image_id {image_id}, but IncidentImage model is removed.")
    return {'status': 'error', 'error': 'Model removed'}


# @shared_task(bind=True)
def generate_text_task(self, prompt, context=None, analysis_type='text_rewrite'):
    """
    Generate text using AI providers
    """
    from .models import AIAnalysis
    from .providers import orchestrator
    
    try:
        # Generate text using orchestrator
        result = orchestrator.generate_text(prompt, context)
        
        if result.get('success'):
            # Log the analysis
            AIAnalysis.objects.create(
                analysis_type=analysis_type,
                input_data={'prompt': prompt, 'context': context or {}},
                output_data={'text': result['text']},
                tokens_used=result.get('tokens_used', 0),
                processing_time=result.get('processing_time', 0)
            )
            
            logger.info(f"Text generation completed for type {analysis_type}")
            return {
                'status': 'success',
                'text': result['text'],
                'provider': result.get('provider', 'unknown')
            }
        
        else:
            # Log the error
            AIAnalysis.objects.create(
                analysis_type=analysis_type,
                input_data={'prompt': prompt, 'context': context or {}},
                output_data={},
                error_message=result.get('error', 'Unknown error'),
                processing_time=result.get('processing_time', 0)
            )
            
            logger.error(f"Text generation failed for type {analysis_type}: {result.get('error')}")
            return {'status': 'error', 'error': result.get('error')}
    
    except Exception as e:
        logger.error(f"Unexpected error in text generation: {str(e)}")
        return {'status': 'error', 'error': str(e)}


# @shared_task(bind=True)
def reset_quotas_task(self):
    """
    Reset daily quotas for all AI providers
    """
    from .models import AIProvider
    
    try:
        providers = AIProvider.objects.filter(enabled=True)
        reset_count = 0
        
        for provider in providers:
            if provider.last_reset_date < timezone.now().date():
                provider.reset_quota()
                reset_count += 1
        
        logger.info(f"Reset quotas for {reset_count} providers")
        return {'status': 'success', 'reset_count': reset_count}
    
    except Exception as e:
        logger.error(f"Error resetting quotas: {str(e)}")
        return {'status': 'error', 'error': str(e)}
