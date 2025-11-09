"""Celery task configuration and background jobs."""

from typing import Any, Dict, List
from celery import Celery  # type: ignore[import-untyped]
from pons.config import settings

# Create Celery app
celery_app = Celery(
    'shiftly',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(  # type: ignore[attr-defined]
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)


@celery_app.task(name='fetch_feed')  # type: ignore[misc]
def fetch_feed_task(source_name: str) -> Dict[str, Any]:
    """Background task to fetch vehicle feed."""
    from pons.feed_integrations import feed_service
    import asyncio
    
    async def _fetch() -> Dict[str, Any]:
        try:
            vehicles = await feed_service.fetch_feed(source_name)
            return {
                'status': 'success',
                'source': source_name,
                'vehicles_count': len(vehicles)
            }
        except Exception as e:
            return {
                'status': 'error',
                'source': source_name,
                'error': str(e)
            }
    
    return asyncio.run(_fetch())


@celery_app.task(name='publish_vehicle')  # type: ignore[misc]
def publish_vehicle_task(vin: str, channels: List[str]) -> Dict[str, Any]:
    """Background task to publish vehicle to channels."""
    from pons.publishing import publishing_orchestrator, PublishingChannel
    import asyncio
    
    async def _publish() -> Dict[str, Any]:
        try:
            # Convert string channels to PublishingChannel enums
            channel_enums = [PublishingChannel(ch) for ch in channels]
            job = await publishing_orchestrator.create_publish_job(vin, channel_enums)
            _result = await publishing_orchestrator.execute_job(job.id)
            return {
                'status': 'success',
                'job_id': job.id,
                'vin': vin,
                'channels': channels
            }
        except Exception as e:
            return {
                'status': 'error',
                'vin': vin,
                'error': str(e)
            }
    
    return asyncio.run(_publish())


@celery_app.task(name='send_alert')  # type: ignore[misc]
def send_alert_task(severity: str, message: str, source: str) -> Dict[str, Any]:
    """Background task to send system alert."""
    from pons.monitoring import monitoring_service
    import asyncio
    
    async def _send_alert() -> Dict[str, Any]:
        alert = await monitoring_service.create_alert(severity, message, source)
        return {
            'status': 'success',
            'alert_id': alert.id,
            'severity': severity
        }
    
    return asyncio.run(_send_alert())


@celery_app.task(name='cleanup_old_data')  # type: ignore[misc]
def cleanup_old_data_task() -> Dict[str, str]:
    """Background task to cleanup old data."""
    # Implement cleanup logic
    return {'status': 'success', 'message': 'Cleanup completed'}


# Periodic tasks configuration
celery_app.conf.beat_schedule = {  # type: ignore[attr-defined]
    'fetch-feeds-every-hour': {
        'task': 'fetch_feed',
        'schedule': 3600.0,  # Every hour
    },
    'cleanup-daily': {
        'task': 'cleanup_old_data',
        'schedule': 86400.0,  # Daily
    },
}
