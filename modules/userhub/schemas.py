# File: modules/userhub/schemas.py

from pydantic import BaseModel, EmailStr
from typing import Optional
from .models import UserRole
import datetime

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

class AttendanceLogBase(BaseModel):
    user_id: int
    location: str

class AttendanceCheckIn(AttendanceLogBase):
    pass # Status will be set by the endpoint

class AttendanceLog(AttendanceLogBase):
    id: int
    timestamp: datetime.datetime
    status: str

    class Config:
        from_attributes = True