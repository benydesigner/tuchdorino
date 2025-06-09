from sqlalchemy.orm import Session
from app.models import Vehicle as VehicleModel # Renaming to avoid conflict
from app.schemas import VehicleCreate, VehicleUpdate

def get_vehicle(db: Session, vehicle_id: int):
    return db.query(VehicleModel).filter(VehicleModel.id == vehicle_id).first()

def get_vehicles_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100):
    return db.query(VehicleModel).filter(VehicleModel.owner_id == owner_id).offset(skip).limit(limit).all()

def get_all_vehicles(db: Session, skip: int = 0, limit: int = 100): # Temporary, until auth
    return db.query(VehicleModel).offset(skip).limit(limit).all()

def create_vehicle(db: Session, vehicle: VehicleCreate, owner_id: int): # Added owner_id
    db_vehicle = VehicleModel(**vehicle.model_dump(), owner_id=owner_id) # Use model_dump() for Pydantic v2
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle

def update_vehicle(db: Session, vehicle_id: int, vehicle_update: VehicleUpdate):
    db_vehicle = get_vehicle(db, vehicle_id)
    if db_vehicle:
        update_data = vehicle_update.model_dump(exclude_unset=True) # Get only provided fields
        for key, value in update_data.items():
            setattr(db_vehicle, key, value)
        db.commit()
        db.refresh(db_vehicle)
    return db_vehicle

def delete_vehicle(db: Session, vehicle_id: int):
    db_vehicle = get_vehicle(db, vehicle_id)
    if db_vehicle:
        db.delete(db_vehicle)
        db.commit()
    return db_vehicle
