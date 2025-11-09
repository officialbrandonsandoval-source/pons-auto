"""Webhook system for real-time notifications."""

import hmac
import hashlib
import httpx
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from pydantic import BaseModel, HttpUrl
from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean
from pons.models import Base, SessionLocal


class WebhookSubscription(Base):
    """Webhook subscription model."""
    __tablename__ = "webhook_subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    event_type = Column(String, nullable=False)  # vehicle.created, vehicle.updated, etc.
    secret = Column(String, nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    webhook_metadata = Column(JSON, default={})


class WebhookEvent(BaseModel):
    """Webhook event data."""
    event_type: str
    timestamp: datetime
    data: Dict[str, Any]
    signature: Optional[str] = None


class WebhookService:
    """Manage webhook subscriptions and delivery."""
    
    def __init__(self):
        self.timeout = 10.0
    
    async def subscribe(
        self,
        url: str,
        event_type: str,
        secret: Optional[str] = None
    ) -> WebhookSubscription:
        """Create a new webhook subscription."""
        db = SessionLocal()
        
        try:
            subscription = WebhookSubscription(
                url=url,
                event_type=event_type,
                secret=secret or self._generate_secret()
            )
            
            db.add(subscription)
            db.commit()
            db.refresh(subscription)
            
            return subscription
        finally:
            db.close()
    
    async def unsubscribe(self, subscription_id: int) -> bool:
        """Remove a webhook subscription."""
        db = SessionLocal()
        
        try:
            subscription = db.query(WebhookSubscription).filter(
                WebhookSubscription.id == subscription_id
            ).first()
            
            if subscription:
                db.delete(subscription)
                db.commit()
                return True
            
            return False
        finally:
            db.close()
    
    async def trigger_event(self, event_type: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Trigger a webhook event to all subscribers."""
        db = SessionLocal()
        results = []
        
        try:
            # Get all active subscriptions for this event type
            subscriptions = db.query(WebhookSubscription).filter(
                WebhookSubscription.event_type == event_type,
                WebhookSubscription.active == True
            ).all()
            
            # Create event payload
            event = WebhookEvent(
                event_type=event_type,
                timestamp=datetime.now(timezone.utc),
                data=data
            )
            
            # Send to each subscriber
            for sub in subscriptions:
                result = await self._send_webhook(sub, event)
                results.append({
                    "subscription_id": sub.id,
                    "url": sub.url,
                    **result
                })
            
            return results
        finally:
            db.close()
    
    async def _send_webhook(
        self,
        subscription: WebhookSubscription,
        event: WebhookEvent
    ) -> Dict[str, Any]:
        """Send webhook to a single subscriber."""
        # Generate signature
        payload = event.model_dump()
        signature = self._generate_signature(
            json.dumps(payload, default=str),
            str(subscription.secret)
        )
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    str(subscription.url),
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "X-Webhook-Signature": signature,
                        "X-Event-Type": event.event_type
                    },
                    timeout=self.timeout
                )
                
                return {
                    "success": response.status_code < 400,
                    "status_code": response.status_code,
                    "delivered_at": datetime.now(timezone.utc).isoformat()
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "delivered_at": datetime.now(timezone.utc).isoformat()
            }
    
    def _generate_signature(self, payload: str, secret: str) -> str:
        """Generate HMAC signature for webhook payload."""
        return hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _generate_secret(self) -> str:
        """Generate a random webhook secret."""
        import secrets
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def verify_signature(payload: str, signature: str, secret: str) -> bool:
        """Verify webhook signature."""
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)


# Webhook event types
WEBHOOK_EVENTS = {
    "vehicle.created": "New vehicle added to inventory",
    "vehicle.updated": "Vehicle information updated",
    "vehicle.deleted": "Vehicle removed from inventory",
    "vehicle.published": "Vehicle published to a channel",
    "vehicle.unpublished": "Vehicle removed from a channel",
    "feed.imported": "Feed successfully imported",
    "feed.failed": "Feed import failed",
}


# Service instance
webhook_service = WebhookService()
