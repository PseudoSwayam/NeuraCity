# File: modules/userhub/crud.py
from sqlalchemy.orm import Session
from . import models, schemas, security
from sqlalchemy import desc, func
from typing import Optional
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr

class TokenData(BaseModel):
    email: Optional[EmailStr] = None

def get_user_from_token(db: Session, token: str) -> Optional[models.User]:
    """
    Decodes a JWT token and fetches the corresponding user from the database
    using a provided session. THIS FUNCTION DOES NOT USE 'Depends'.
    """

    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        token_data = TokenData(email=email)
    except JWTError:
        return None
        
    user = get_user_by_email(db, email=token_data.email)
    return user

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users_by_role(db: Session, role: models.UserRole) -> list[models.User]:
    """
    Retrieves all users from the database who are assigned a specific role.
    """
    return db.query(models.User).filter(models.User.role == role).all()

def create_user_attendance_log(db: Session, user_id: int, location: str, status: str) -> models.AttendanceLog:
    """Creates a new check-in or check-out log for a user."""
    db_log = models.AttendanceLog(user_id=user_id, location=location, status=status)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_latest_user_status(db: Session, user_id: int) -> Optional[models.AttendanceLog]:
    """Finds the most recent check-in or check-out record for a single user."""
    return db.query(models.AttendanceLog).filter(models.AttendanceLog.user_id == user_id).order_by(desc(models.AttendanceLog.timestamp)).first()

def get_all_users_on_campus(db: Session) -> list[models.User]:
    """
    Returns a list of all users whose most recent status is 'checked_in'.
    This is a more complex query.
    """
    # This subquery finds the most recent log ID for each user.
    latest_logs_subquery = db.query(
        models.AttendanceLog.user_id,
        func.max(models.AttendanceLog.id).label("max_id")
    ).group_by(models.AttendanceLog.user_id).subquery()
    
    # We join this with the main logs and users tables to get the final list.
    checked_in_users = db.query(models.User).join(
        models.AttendanceLog, models.User.id == models.AttendanceLog.user_id
    ).join(
        latest_logs_subquery,
        (models.AttendanceLog.user_id == latest_logs_subquery.c.user_id) &
        (models.AttendanceLog.id == latest_logs_subquery.c.max_id)
    ).filter(models.AttendanceLog.status == "checked_in").all()
    
    return checked_in_users