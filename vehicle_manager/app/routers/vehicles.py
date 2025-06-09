from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import schemas, crud
from app.models import Vehicle as VehicleModel
from app.models import User as UserModel # Explicit import for clarity
from app.core.database import get_db
from app.core.auth_utils import get_current_active_user

router = APIRouter(
    prefix='/vehicles',
    tags=['vehicles']
)

@router.post('/', response_model=schemas.Vehicle)
def create_new_vehicle(
    vehicle: schemas.VehicleCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    return crud.create_vehicle(db=db, vehicle=vehicle, owner_id=current_user.id)

@router.get('/', response_model=List[schemas.Vehicle])
def read_all_vehicles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    vehicles = crud.get_vehicles_by_owner(db, owner_id=current_user.id, skip=skip, limit=limit)
    return vehicles

@router.get('/{vehicle_id}', response_model=schemas.Vehicle)
def read_single_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    db_vehicle = crud.get_vehicle(db, vehicle_id=vehicle_id)
    if db_vehicle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Vehicle not found')
    if db_vehicle.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this vehicle")
    return db_vehicle

@router.put('/{vehicle_id}', response_model=schemas.Vehicle)
def update_existing_vehicle(
    vehicle_id: int,
    vehicle: schemas.VehicleUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    db_vehicle = crud.get_vehicle(db, vehicle_id=vehicle_id)
    if db_vehicle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Vehicle not found')
    if db_vehicle.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this vehicle")
    updated_vehicle = crud.update_vehicle(db=db, vehicle_id=vehicle_id, vehicle_update=vehicle)
    return updated_vehicle

@router.delete('/{vehicle_id}', response_model=schemas.Vehicle)
def delete_existing_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    db_vehicle = crud.get_vehicle(db, vehicle_id=vehicle_id)
    if db_vehicle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Vehicle not found')
    if db_vehicle.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this vehicle")
    deleted_vehicle = crud.delete_vehicle(db=db, vehicle_id=vehicle_id)
    # crud.delete_vehicle returns the db_vehicle object it found and deleted.
    # If deletion failed somehow after check, it might not be None, but it won't be in DB.
    # The original return db_vehicle is fine as it returns the object that was deleted.
    return db_vehicle
