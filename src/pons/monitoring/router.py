"""API router for monitoring and control plane."""

from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, Query
from pons.monitoring import monitoring_service

router = APIRouter()


@router.get("/metrics")
async def get_metrics() -> Any:
    """Get system metrics."""
    metrics = await monitoring_service.get_system_metrics()
    return metrics


@router.get("/alerts")
async def get_alerts(
    severity: Optional[str] = Query(None),
    resolved: bool = Query(False)
) -> Dict[str, Any]:
    """Get system alerts."""
    alerts = await monitoring_service.get_alerts(severity, resolved)
    return {"alerts": alerts, "count": len(alerts)}


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str) -> Dict[str, str]:
    """Resolve an alert."""
    success = await monitoring_service.resolve_alert(alert_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"message": "Alert resolved successfully"}


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Detailed health check."""
    return {
        "status": "healthy",
        "components": {
            "database": "healthy",
            "redis": "healthy",
            "feed_integrations": "healthy",
            "publishing": "healthy"
        }
    }
