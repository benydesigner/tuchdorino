from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Vehicle(Base):
    __tablename__ = 'vehicles'

    id = Column(Integer, primary_key=True, index=True)
    make = Column(String, index=True, nullable=False)
    model = Column(String, index=True, nullable=False)
    year = Column(Integer, nullable=False)
    license_plate = Column(String, unique=True, index=True, nullable=False)
    odometer_reading = Column(Integer, nullable=False)
    vin = Column(String, unique=True, index=True, nullable=True)
    owner_id = Column(Integer, ForeignKey('users.id'))

    owner = relationship('User')
