from pydantic import BaseModel
from typing import Optional

class VehicleBase(BaseModel):
    make: str
    model: str
    year: int
    license_plate: str
    odometer_reading: int
    vin: Optional[str] = None

class VehicleCreate(VehicleBase):
    pass

class VehicleUpdate(VehicleBase):
    # All fields are optional for update
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    license_plate: Optional[str] = None
    odometer_reading: Optional[int] = None
    vin: Optional[str] = None

class Vehicle(VehicleBase): # Schema for reading/returning vehicle data
    id: int
    owner_id: int # Assuming we will link to an owner

    class Config:
        from_attributes = True # Changed from orm_mode = True for Pydantic v2
