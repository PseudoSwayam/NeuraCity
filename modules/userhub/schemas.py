# File: modules/userhub/schemas.py

from pydantic import BaseModel, EmailStr
from typing import Optional
from .models import UserRole

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.student

class User(UserBase):
    id: int
    role: UserRole
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[EmailStr] = None