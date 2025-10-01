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
    Analyze an image using AI providers
    """
    from .models import AIAnalysis, AIProvider
    from apps.incidents.models import IncidentImage
    from .providers import orchestrator
    
    try:
        # Get the image
        image = IncidentImage.objects.get(id=image_id)
        
        # Read image data
        # TODO: Implement file reading from storage (MinIO or filesystem)
        # For now, we'll simulate the analysis
        
        # Simulate image data (in real implementation, read from storage)
        image_data = b"fake_image_data"
        image_type = "image/jpeg"
        
        # Analyze using orchestrator
        result = orchestrator.analyze_image(image_data, image_type)
        
        if result.get('success'):
            # Update image with analysis results
            image.caption_ai = result['data'].get('description', '')
            image.analysis_json = result['data']
            image.ai_provider_used = result.get('provider', 'unknown')
            image.ai_confidence = 0.8  # Default confidence
            
            # Extract possible causes
            possible_causes = result['data'].get('possible_causes', [])
            if possible_causes:
                image.analysis_json['possible_causes'] = possible_causes
            
            image.save()
            
            # Log the analysis
            AIAnalysis.objects.create(
                analysis_type='image_analysis',
                input_data={'image_id': image_id, 'image_type': image_type},
                output_data=result['data'],
                confidence_score=image.ai_confidence,
                tokens_used=result.get('tokens_used', 0),
                processing_time=result.get('processing_time', 0)
            )
            
            logger.info(f"Image analysis completed for image {image_id}")
            return {'status': 'success', 'image_id': image_id}
        
        else:
            # Log the error
            AIAnalysis.objects.create(
                analysis_type='image_analysis',
                input_data={'image_id': image_id, 'image_type': image_type},
                output_data={},
                error_message=result.get('error', 'Unknown error'),
                processing_time=result.get('processing_time', 0)
            )
            
            logger.error(f"Image analysis failed for image {image_id}: {result.get('error')}")
            return {'status': 'error', 'error': result.get('error')}
    
    except IncidentImage.DoesNotExist:
        logger.error(f"Image {image_id} not found")
        return {'status': 'error', 'error': 'Image not found'}
    
    except Exception as e:
        logger.error(f"Unexpected error in image analysis: {str(e)}")
        return {'status': 'error', 'error': str(e)}


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
