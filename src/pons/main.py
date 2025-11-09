"""Main FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from pons.config import settings
from pons.feed_integrations.router import router as feed_router
from pons.normalization.router import router as normalization_router
from pons.inventory.router import router as inventory_router
from pons.publishing.router import router as publishing_router
from pons.monitoring.router import router as monitoring_router
from pons.ai.router import router as ai_router
from pons.auth.router import router as auth_router
from pons.billing.router import router as billing_router

app = FastAPI(
    title="PONS Auto",
    description="Safe Infrastructure for Multi-Channel Vehicle Publishing",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Include routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(billing_router, prefix="/api/v1/billing", tags=["Billing"])
app.include_router(feed_router, prefix="/api/v1/feeds", tags=["Feed Integrations"])
app.include_router(normalization_router, prefix="/api/v1/normalization", tags=["Normalization"])
app.include_router(inventory_router, prefix="/api/v1/inventory", tags=["Inventory"])
app.include_router(publishing_router, prefix="/api/v1/publishing", tags=["Publishing"])
app.include_router(monitoring_router, prefix="/api/v1/monitoring", tags=["Monitoring"])
app.include_router(ai_router, prefix="/api/v1/ai", tags=["AI Services"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "PONS Auto",
        "version": "0.1.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
