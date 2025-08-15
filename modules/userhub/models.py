# File: modules/userhub/models.py
from sqlalchemy import Column, Integer, String, Enum as SAEnum, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
import enum

class UserRole(enum.Enum):
    student = "student"
    staff = "staff"
    security = "security"
    admin = "admin"
    superadmin = "superadmin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    hashed_password = Column(String, nullable=False)
    role = Column(SAEnum(UserRole), default=UserRole.student)
    is_active = Column(Boolean, default=True)

# ... We can add relationships to incidents, attendance, etc. here later