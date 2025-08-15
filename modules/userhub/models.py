# File: modules/userhub/models.py
from sqlalchemy import Column, Integer, String, Enum as SAEnum, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base
import enum
import datetime

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
    attendance_logs = relationship("AttendanceLog", back_populates="user")

class AttendanceLog(Base):
    __tablename__ = "attendance_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    status = Column(SAEnum("checked_in", "checked_out", name="attendancestatusenum"), nullable=False)
    location = Column(String, nullable=False) # e.g., "Main Entrance", "Library NFC Reader"
    
    user = relationship("User", back_populates="attendance_logs")