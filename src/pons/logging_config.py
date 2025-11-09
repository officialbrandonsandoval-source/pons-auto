"""Logging configuration for Shiftly Auto."""

import logging
import sys
from typing import Any, Dict, List, Optional
from pythonjsonlogger import jsonlogger  # type: ignore[import-untyped]


def setup_logging(level: str = "INFO"):
    """Set up application logging."""
    
    # Create logger
    logger = logging.getLogger("shiftly")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Console handler with JSON formatting
    console_handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(  # type: ignore[attr-defined]
        '%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler for errors
    error_handler = logging.FileHandler('logs/error.log')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    return logger


# Create global logger
logger = setup_logging()


def log_api_request(endpoint: str, method: str, status_code: int, duration: float):
    """Log API request."""
    logger.info(
        "API Request",
        extra={
            'endpoint': endpoint,
            'method': method,
            'status_code': status_code,
            'duration_ms': round(duration * 1000, 2)
        }
    )


def log_feed_ingestion(source: str, vehicle_count: int, success: bool):
    """Log feed ingestion."""
    logger.info(
        "Feed Ingestion",
        extra={
            'source': source,
            'vehicle_count': vehicle_count,
            'success': success
        }
    )


def log_publishing_job(job_id: str, vin: str, channels: List[str], status: str):
    """Log publishing job."""
    logger.info(
        "Publishing Job",
        extra={
            'job_id': job_id,
            'vin': vin,
            'channels': channels,
            'status': status
        }
    )


def log_error(error: Exception, context: Optional[Dict[str, Any]] = None):
    """Log error with context."""
    logger.error(
        "Error occurred",
        extra={
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context or {}
        },
        exc_info=True
    )
