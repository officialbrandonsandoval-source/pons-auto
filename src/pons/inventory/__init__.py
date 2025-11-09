"""Inventory Management - Cloud-based vehicle inventory system."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from pons.models import Vehicle as VehicleModel, SessionLocal


class InventoryVehicle(BaseModel):
    """Vehicle in inventory."""
    id: int
    vin: str
    stock_number: Optional[str] = None
    
    # Vehicle details
    year: int
    make: str
    model: str
    trim: Optional[str] = None
    
    # Status
    status: str = "available"  # available, pending, sold, archived
    publishing_channels: List[str] = []
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class InventoryService:
    """Service for managing vehicle inventory with database persistence."""
    
    def __init__(self):
        pass
    
    def _get_db(self) -> Session:
        """Get database session."""
        return SessionLocal()
    
    async def add_vehicle(self, vehicle: InventoryVehicle) -> InventoryVehicle:
        """Add vehicle to inventory."""
        db = self._get_db()
        try:
            db_vehicle = VehicleModel(
                vin=vehicle.vin,
                stock_number=vehicle.stock_number,
                year=vehicle.year,
                make=vehicle.make,
                model=vehicle.model,
                trim=vehicle.trim,
                publishing_channels=vehicle.publishing_channels,
                created_at=vehicle.created_at,
                updated_at=vehicle.updated_at
            )
            db.add(db_vehicle)
            db.commit()
            db.refresh(db_vehicle)
            # Use from_attributes to convert SQLAlchemy model to Pydantic
            return InventoryVehicle.model_validate(db_vehicle)
        finally:
            db.close()
    
    async def get_vehicle(self, vin: str) -> Optional[InventoryVehicle]:
        """Get vehicle by VIN."""
        db = self._get_db()
        try:
            db_vehicle = db.query(VehicleModel).filter(VehicleModel.vin == vin).first()
            if not db_vehicle:
                return None
            
            # Use from_attributes to convert SQLAlchemy model to Pydantic
            return InventoryVehicle.model_validate(db_vehicle)
        finally:
            db.close()
    
    async def update_vehicle(self, vin: str, updates: Dict[str, Any]) -> Optional[InventoryVehicle]:
        """Update vehicle in inventory."""
        db = self._get_db()
        try:
            db_vehicle = db.query(VehicleModel).filter(VehicleModel.vin == vin).first()
            if not db_vehicle:
                return None
            
            for key, value in updates.items():
                if hasattr(db_vehicle, key):
                    setattr(db_vehicle, key, value)
            
            db_vehicle.updated_at = datetime.now(timezone.utc)  # type: ignore[assignment]
            db.commit()
            db.refresh(db_vehicle)
            
            return await self.get_vehicle(vin)
        finally:
            db.close()
    
    async def remove_vehicle(self, vin: str) -> bool:
        """Remove vehicle from inventory."""
        db = self._get_db()
        try:
            db_vehicle = db.query(VehicleModel).filter(VehicleModel.vin == vin).first()
            if not db_vehicle:
                return False
            
            db.delete(db_vehicle)
            db.commit()
            return True
        finally:
            db.close()
    
    async def list_vehicles(
        self,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[InventoryVehicle]:
        """List vehicles in inventory."""
        db = self._get_db()
        try:
            query = db.query(VehicleModel)
            query = query.limit(limit).offset(offset)
            db_vehicles = query.all()
            
            # Use from_attributes to convert SQLAlchemy models to Pydantic
            return [InventoryVehicle.model_validate(v) for v in db_vehicles]
        finally:
            db.close()
    
    async def search_vehicles(self, query: Dict[str, Any]) -> List[InventoryVehicle]:
        """Search vehicles by criteria."""
        db = self._get_db()
        try:
            db_query = db.query(VehicleModel)
            
            if "make" in query:
                db_query = db_query.filter(VehicleModel.make.ilike(f"%{query['make']}%"))
            if "model" in query:
                db_query = db_query.filter(VehicleModel.model.ilike(f"%{query['model']}%"))
            if "year" in query:
                db_query = db_query.filter(VehicleModel.year == int(query["year"]))
            
            db_vehicles = db_query.all()
            
            # Use from_attributes to convert SQLAlchemy models to Pydantic
            return [InventoryVehicle.model_validate(v) for v in db_vehicles]
        finally:
            db.close()


# Singleton instance
inventory_service = InventoryService()
