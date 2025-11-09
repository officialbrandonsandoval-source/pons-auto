"""Application configuration using Pydantic settings."""

from typing import Any, Dict, List
from pydantic_settings import BaseSettings
import yaml


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "PONS Auto"
    DEBUG: bool = False
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # Database
    DATABASE_URL: str = "postgresql://shiftly:shiftly@localhost:5432/shiftly"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # API Keys (loaded from config/tokens.yaml)
    API_KEYS: Dict[str, Any] = {}
    
    # Rate Limits (loaded from config/limits.yaml)
    RATE_LIMITS: Dict[str, Any] = {}
    
    # Alert Configuration (loaded from config/alerts.yaml)
    ALERTS: Dict[str, Any] = {}
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from .env


def load_config_file(filepath: str) -> Dict[str, Any]:
    """Load YAML configuration file."""
    try:
        with open(filepath, 'r') as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {}


# Initialize settings
settings = Settings()

# Load additional configuration from YAML files
try:
    settings.API_KEYS = load_config_file("config/tokens.yaml")
    settings.RATE_LIMITS = load_config_file("config/limits.yaml")
    settings.ALERTS = load_config_file("config/alerts.yaml")
except Exception as e:
    print(f"Warning: Could not load config files: {e}")
