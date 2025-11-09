"""Monitoring & Control Plane - System monitoring and alerting."""

from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime
from prometheus_client import Counter, Gauge, Histogram


# Prometheus metrics
feed_ingestions = Counter(
    'shiftly_feed_ingestions_total',
    'Total number of feed ingestions',
    ['source', 'status']
)

vehicles_normalized = Counter(
    'shiftly_vehicles_normalized_total',
    'Total number of vehicles normalized',
    ['source']
)

publish_jobs = Counter(
    'shiftly_publish_jobs_total',
    'Total number of publishing jobs',
    ['status']
)

active_vehicles = Gauge(
    'shiftly_active_vehicles',
    'Number of active vehicles in inventory'
)

api_requests = Counter(
    'shiftly_api_requests_total',
    'Total API requests',
    ['endpoint', 'method', 'status']
)

request_duration = Histogram(
    'shiftly_request_duration_seconds',
    'Request duration in seconds',
    ['endpoint']
)


class SystemMetrics(BaseModel):
    """System metrics snapshot."""
    timestamp: datetime
    total_vehicles: int
    active_publishing_jobs: int
    feed_sources: int
    api_requests_per_minute: float


class Alert(BaseModel):
    """System alert."""
    id: str
    severity: str  # info, warning, error, critical
    message: str
    source: str
    created_at: datetime
    resolved: bool = False


class MonitoringService:
    """Service for monitoring system health and performance."""
    
    def __init__(self):
        self.alerts: List[Alert] = []
    
    async def get_system_metrics(self) -> SystemMetrics:
        """Get current system metrics."""
        return SystemMetrics(
            timestamp=datetime.utcnow(),
            total_vehicles=0,  # Would query from database
            active_publishing_jobs=0,
            feed_sources=0,
            api_requests_per_minute=0.0
        )
    
    async def create_alert(
        self,
        severity: str,
        message: str,
        source: str
    ) -> Alert:
        """Create a new alert."""
        alert = Alert(
            id=f"alert-{datetime.utcnow().timestamp()}",
            severity=severity,
            message=message,
            source=source,
            created_at=datetime.utcnow()
        )
        self.alerts.append(alert)
        return alert
    
    async def get_alerts(
        self,
        severity: Optional[str] = None,
        resolved: bool = False
    ) -> List[Alert]:
        """Get system alerts."""
        alerts = self.alerts
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        alerts = [a for a in alerts if a.resolved == resolved]
        
        return alerts
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Mark an alert as resolved."""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                return True
        return False


# Singleton instance
monitoring_service = MonitoringService()
