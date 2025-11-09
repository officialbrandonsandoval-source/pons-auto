"""Production configuration and environment setup."""

import os
from typing import Any, Dict


class ProductionConfig:
    """Production environment configuration."""
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://shiftly:shiftly@postgres:5432/shiftly")
    DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", "20"))
    DATABASE_MAX_OVERFLOW = int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))
    
    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
    REDIS_MAX_CONNECTIONS = int(os.getenv("REDIS_MAX_CONNECTIONS", "50"))
    
    # API
    API_WORKERS = int(os.getenv("API_WORKERS", "4"))
    API_TIMEOUT = int(os.getenv("API_TIMEOUT", "60"))
    
    # Security
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    API_KEY_REQUIRED = os.getenv("API_KEY_REQUIRED", "true").lower() == "true"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = os.getenv("LOG_FORMAT", "json")
    
    # Celery
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)
    CELERY_WORKERS = int(os.getenv("CELERY_WORKERS", "4"))
    
    # Monitoring
    PROMETHEUS_ENABLED = os.getenv("PROMETHEUS_ENABLED", "true").lower() == "true"
    SENTRY_DSN = os.getenv("SENTRY_DSN", "")
    
    @classmethod
    def get_all(cls) -> Dict[str, Any]:
        """Get all configuration values."""
        return {
            key: value for key, value in cls.__dict__.items()
            if not key.startswith('_') and not callable(value)
        }


class DevelopmentConfig:
    """Development environment configuration."""
    
    DATABASE_URL = "sqlite:///./shiftly_dev.db"
    REDIS_URL = "redis://localhost:6379/0"
    API_WORKERS = 1
    LOG_LEVEL = "DEBUG"
    API_KEY_REQUIRED = False
    RATE_LIMIT_PER_MINUTE = 1000


# Select configuration based on environment
ENV = os.getenv("ENVIRONMENT", "development")
config = ProductionConfig if ENV == "production" else DevelopmentConfig
