"""Database initialization script."""

from alembic.config import Config
from pons.models import Base, engine
import os


def init_database():
    """Initialize the database schema."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully")


def create_alembic_config():
    """Create Alembic configuration."""
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", "alembic")
    alembic_cfg.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL", "sqlite:///./shiftly.db"))
    return alembic_cfg


if __name__ == "__main__":
    init_database()
    print("\n✓ Database initialization complete!")
