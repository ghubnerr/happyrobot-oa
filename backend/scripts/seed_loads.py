"""
Script to seed the database with sample load data.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal, init_db
from app.models import Load
from datetime import datetime, timedelta

# Sample loads data
SAMPLE_LOADS = [
    {
        "load_id": "LOAD-001",
        "origin": "Los Angeles, CA",
        "destination": "New York, NY",
        "pickup_datetime": datetime.now() + timedelta(days=2),
        "delivery_datetime": datetime.now() + timedelta(days=5),
        "equipment_type": "Dry Van",
        "loadboard_rate": 3500.00,
        "notes": "Standard dry van load, no special requirements",
        "weight": 45000,
        "commodity_type": "General Freight",
        "num_of_pieces": 24,
        "miles": 2789,
        "dimensions": "53' x 102\" x 110\"",
    },
    {
        "load_id": "LOAD-002",
        "origin": "Chicago, IL",
        "destination": "Atlanta, GA",
        "pickup_datetime": datetime.now() + timedelta(days=1),
        "delivery_datetime": datetime.now() + timedelta(days=3),
        "equipment_type": "Refrigerated",
        "loadboard_rate": 2800.00,
        "notes": "Temperature controlled, must maintain 38-42°F",
        "weight": 42000,
        "commodity_type": "Food Products",
        "num_of_pieces": 18,
        "miles": 715,
        "dimensions": "53' x 102\" x 110\"",
    },
    {
        "load_id": "LOAD-003",
        "origin": "Dallas, TX",
        "destination": "Denver, CO",
        "pickup_datetime": datetime.now() + timedelta(days=3),
        "delivery_datetime": datetime.now() + timedelta(days=5),
        "equipment_type": "Flatbed",
        "loadboard_rate": 2200.00,
        "notes": "Oversized load, requires tarping",
        "weight": 38000,
        "commodity_type": "Construction Materials",
        "num_of_pieces": 6,
        "miles": 925,
        "dimensions": "48' x 96\" x 12'",
    },
    {
        "load_id": "LOAD-004",
        "origin": "Miami, FL",
        "destination": "Boston, MA",
        "pickup_datetime": datetime.now() + timedelta(days=4),
        "delivery_datetime": datetime.now() + timedelta(days=7),
        "equipment_type": "Dry Van",
        "loadboard_rate": 3200.00,
        "notes": "Expedited delivery required",
        "weight": 40000,
        "commodity_type": "Electronics",
        "num_of_pieces": 32,
        "miles": 1534,
        "dimensions": "53' x 102\" x 110\"",
    },
    {
        "load_id": "LOAD-005",
        "origin": "Seattle, WA",
        "destination": "Portland, OR",
        "pickup_datetime": datetime.now() + timedelta(days=1),
        "delivery_datetime": datetime.now() + timedelta(days=2),
        "equipment_type": "Dry Van",
        "loadboard_rate": 1200.00,
        "notes": "Short haul, local delivery",
        "weight": 35000,
        "commodity_type": "Retail Goods",
        "num_of_pieces": 45,
        "miles": 173,
        "dimensions": "53' x 102\" x 110\"",
    },
]


def seed_loads():
    """Seed the database with sample loads."""
    init_db()
    db = SessionLocal()
    
    try:
        # Clear existing loads (optional - comment out if you want to keep existing)
        # db.query(Load).delete()
        
        for load_data in SAMPLE_LOADS:
            # Check if load already exists
            existing = db.query(Load).filter(Load.load_id == load_data["load_id"]).first()
            if existing:
                print(f"Load {load_data['load_id']} already exists, skipping...")
                continue
            
            load = Load(**load_data)
            db.add(load)
            print(f"Added load: {load_data['load_id']} - {load_data['origin']} to {load_data['destination']}")
        
        db.commit()
        print(f"\nSuccessfully seeded {len(SAMPLE_LOADS)} loads!")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding loads: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_loads()

