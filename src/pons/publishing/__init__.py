"""Publishing Orchestrator - Manage multi-channel vehicle publishing."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime, timezone
from enum import Enum


class PublishingChannel(str, Enum):
    """Supported publishing channels."""
    AUTOTRADER = "autotrader"
    CARS_COM = "cars_com"
    FACEBOOK = "facebook"
    CARGURUS = "cargurus"
    DEALER_WEBSITE = "dealer_website"


class PublishingStatus(str, Enum):
    """Publishing status."""
    PENDING = "pending"
    PUBLISHED = "published"
    FAILED = "failed"
    RETRYING = "retrying"


class PublishJob(BaseModel):
    """Publishing job."""
    id: str
    vin: str
    channels: List[PublishingChannel]
    status: PublishingStatus = PublishingStatus.PENDING
    created_at: datetime = datetime.now(timezone.utc)
    completed_at: Optional[datetime] = None
    results: Dict[str, Dict[str, Any]] = {}


class PublishingOrchestrator:
    """Orchestrates vehicle publishing across multiple channels."""
    
    def __init__(self):
        self.jobs: Dict[str, PublishJob] = {}
    
    async def create_publish_job(
        self,
        vin: str,
        channels: List[PublishingChannel]
    ) -> PublishJob:
        """Create a new publishing job."""
        job_id = f"{vin}-{datetime.now(timezone.utc).timestamp()}"
        job = PublishJob(
            id=job_id,
            vin=vin,
            channels=channels
        )
        self.jobs[job_id] = job
        return job
    
    async def execute_job(self, job_id: str) -> PublishJob:
        """Execute a publishing job."""
        job = self.jobs.get(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        # Publish to each channel
        for channel in job.channels:
            try:
                result = await self._publish_to_channel(job.vin, channel)
                job.results[channel] = result
            except Exception as e:
                job.results[channel] = {"error": str(e)}
        
        # Update job status
        failed_channels = [
            ch for ch, res in job.results.items()
            if "error" in res
        ]
        
        if failed_channels:
            job.status = PublishingStatus.FAILED
        else:
            job.status = PublishingStatus.PUBLISHED
        
        job.completed_at = datetime.now(timezone.utc)
        return job
    
    async def _publish_to_channel(
        self,
        vin: str,
        channel: PublishingChannel
    ) -> Dict[str, Any]:
        """Publish vehicle to specific channel."""
        # This would call the appropriate bridge
        return {
            "status": "success",
            "channel": channel,
            "published_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def get_job(self, job_id: str) -> Optional[PublishJob]:
        """Get publishing job by ID."""
        return self.jobs.get(job_id)
    
    async def list_jobs(self, vin: Optional[str] = None) -> List[PublishJob]:
        """List publishing jobs."""
        jobs = list(self.jobs.values())
        if vin:
            jobs = [j for j in jobs if j.vin == vin]
        return jobs


# Singleton instance
publishing_orchestrator = PublishingOrchestrator()
