# File: modules/userhub/routers/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, models, schemas
from ..database import get_db
from ..dependencies import get_current_user, require_role 

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=schemas.User)
def create_user_endpoint(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@router.get("/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_users(db, skip=skip, limit=limit)

@router.get("/me", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(get_current_user)):
    return current_user

@router.get("/by-role/{role}", response_model=List[schemas.User], dependencies=[Depends(require_role(models.UserRole.admin))])
def read_users_by_role(role: models.UserRole, db: Session = Depends(get_db)):
    """
    Get a list of all users assigned to a specific role.
    This is a protected endpoint intended for inter-service communication.
    """
    return crud.get_users_by_role(db, role=role)