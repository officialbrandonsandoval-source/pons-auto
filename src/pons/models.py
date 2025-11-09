"""Common database models and utilities."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from pons.config import settings

Base = declarative_base()

# Use SQLite for development if PostgreSQL not configured
try:
    engine = create_engine(settings.DATABASE_URL)
except:
    # Fallback to SQLite for local development
    engine = create_engine("sqlite:///./shiftly.db")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Vehicle(Base):
    """Vehicle inventory model."""
    
    __tablename__ = "vehicles"
    
    id = Column(Integer, primary_key=True, index=True)
    vin = Column(String(17), unique=True, index=True, nullable=False)
    stock_number = Column(String(50), unique=True, index=True)
    
    # Vehicle details
    year = Column(Integer)
    make = Column(String(100))
    model = Column(String(100))
    trim = Column(String(100))
    body_type = Column(String(50))
    
    # Pricing
    price = Column(Integer)
    msrp = Column(Integer)
    
    # Specifications
    mileage = Column(Integer)
    exterior_color = Column(String(50))
    interior_color = Column(String(50))
    transmission = Column(String(50))
    fuel_type = Column(String(50))
    drivetrain = Column(String(50))
    
    # Metadata
    source_feed = Column(String(100))
    raw_data = Column(JSON)
    normalized_data = Column(JSON)
    
    # Publishing status
    publishing_status = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
