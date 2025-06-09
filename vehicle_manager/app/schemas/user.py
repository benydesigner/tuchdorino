from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase): # Schema for reading/returning user data
    id: int
    is_active: bool

    class Config:
        from_attributes = True
