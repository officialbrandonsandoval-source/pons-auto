"""Unit tests for inventory management."""

import pytest
from datetime import datetime, timezone
from pons.inventory import InventoryService, InventoryVehicle


@pytest.fixture
def inventory_service() -> InventoryService:
    """Create an inventory service instance."""
    return InventoryService()


@pytest.fixture
def sample_vehicle() -> InventoryVehicle:
    """Create a sample vehicle."""
    return InventoryVehicle(
        id=1,
        vin="1HGCM82633A123456",
        stock_number="A12345",
        year=2023,
        make="Honda",
        model="Accord",
        trim="EX",
        status="available",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


@pytest.mark.asyncio
async def test_add_vehicle(inventory_service: InventoryService, sample_vehicle: InventoryVehicle) -> None:
    """Test adding a vehicle to inventory."""
    result = await inventory_service.add_vehicle(sample_vehicle)
    
    assert result.vin == sample_vehicle.vin
    assert result.make == "Honda"


@pytest.mark.asyncio
async def test_get_vehicle(inventory_service: InventoryService, sample_vehicle: InventoryVehicle) -> None:
    """Test retrieving a vehicle by VIN."""
    await inventory_service.add_vehicle(sample_vehicle)
    
    vehicle = await inventory_service.get_vehicle(sample_vehicle.vin)
    
    assert vehicle is not None
    assert vehicle.vin == sample_vehicle.vin


@pytest.mark.asyncio
async def test_get_nonexistent_vehicle(inventory_service: InventoryService) -> None:
    """Test retrieving a non-existent vehicle."""
    vehicle = await inventory_service.get_vehicle("NONEXISTENT")
    
    assert vehicle is None


@pytest.mark.asyncio
async def test_remove_vehicle(inventory_service: InventoryService, sample_vehicle: InventoryVehicle) -> None:
    """Test removing a vehicle from inventory."""
    await inventory_service.add_vehicle(sample_vehicle)
    
    success = await inventory_service.remove_vehicle(sample_vehicle.vin)
    
    assert success is True
    
    vehicle = await inventory_service.get_vehicle(sample_vehicle.vin)
    assert vehicle is None
