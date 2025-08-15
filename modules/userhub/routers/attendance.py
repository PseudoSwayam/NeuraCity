# File: modules/userhub/routers/attendance.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import crud, models, schemas
from ..database import get_db

router = APIRouter(prefix="/attendance", tags=["Attendance"])

@router.post("/check-in", response_model=schemas.AttendanceLog)
def check_in(check_in_data: schemas.AttendanceCheckIn, db: Session = Depends(get_db)):
    """Simulates a user checking in at a specific campus location."""
    user = db.get(models.User, check_in_data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Optional: You could check if they are already checked in.
    # For now, we'll just log the new event.
    return crud.create_user_attendance_log(
        db=db, user_id=user.id, location=check_in_data.location, status="checked_in"
    )

@router.post("/check-out", response_model=schemas.AttendanceLog)
def check_out(check_out_data: schemas.AttendanceCheckIn, db: Session = Depends(get_db)):
    """Simulates a user checking out from a specific campus location."""
    user = db.get(models.User, check_out_data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return crud.create_user_attendance_log(
        db=db, user_id=user.id, location=check_out_data.location, status="checked_out"
    )

@router.get("/on-campus", response_model=List[schemas.User])
def get_users_on_campus(db: Session = Depends(get_db)):
    """Returns a list of all users currently checked in on campus."""
    return crud.get_all_users_on_campus(db=db)