"""Seed data for development and testing."""

from datetime import datetime, timezone
from pons.models import Vehicle, SessionLocal


def create_seed_data():
    """Create sample vehicle data for testing."""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing = db.query(Vehicle).first()
        if existing:
            print("Seed data already exists, skipping...")
            return
        
        vehicles = [
            Vehicle(
                vin="1HGCM82633A123456",
                stock_number="A12345",
                year=2023,
                make="Honda",
                model="Accord",
                trim="EX",
                body_type="Sedan",
                price=28500,
                msrp=32000,
                mileage=15000,
                exterior_color="White",
                interior_color="Black",
                transmission="Automatic",
                fuel_type="Gasoline",
                drivetrain="FWD",
                source_feed="sample_feed",
                raw_data={},
                normalized_data={},
                publishing_status={},
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            ),
            Vehicle(
                vin="5YFBURHE5HP123789",
                stock_number="B67890",
                year=2022,
                make="Toyota",
                model="Camry",
                trim="LE",
                body_type="Sedan",
                price=25900,
                msrp=28000,
                mileage=22000,
                exterior_color="Silver",
                interior_color="Gray",
                transmission="Automatic",
                fuel_type="Gasoline",
                drivetrain="FWD",
                source_feed="sample_feed",
                raw_data={},
                normalized_data={},
                publishing_status={},
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            ),
            Vehicle(
                vin="1C4RJFAG1FC123456",
                stock_number="C11111",
                year=2024,
                make="Jeep",
                model="Grand Cherokee",
                trim="Laredo",
                body_type="SUV",
                price=42500,
                msrp=45000,
                mileage=5000,
                exterior_color="Black",
                interior_color="Tan",
                transmission="Automatic",
                fuel_type="Gasoline",
                drivetrain="4WD",
                source_feed="sample_feed",
                raw_data={},
                normalized_data={},
                publishing_status={},
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            ),
        ]
        
        db.add_all(vehicles)
        db.commit()
        print(f"✓ Created {len(vehicles)} sample vehicles")
        
    except Exception as e:
        print(f"Error creating seed data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_seed_data()
    print("✓ Seed data creation complete!")
