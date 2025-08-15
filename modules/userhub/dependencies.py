# File: modules/userhub/dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import get_db
from .security import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Decodes the JWT token and returns the corresponding user from the database."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None: raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


# --- THIS IS THE DEFINITIVE FIX: A HIERARCHICAL ROLE CHECKER ---

# 1. Define the hierarchy. Lower numbers are less privileged.
ROLE_HIERARCHY = {
    models.UserRole.student: 1,
    models.UserRole.staff: 2,
    models.UserRole.security: 3,
    models.UserRole.admin: 4,
    models.UserRole.superadmin: 5,
}

def require_role(minimum_required_role: models.UserRole):
    """
    A FastAPI dependency that checks if the current user's role meets
    or exceeds the minimum required role level.
    """

    def role_checker(current_user: models.User = Depends(get_current_user)):
        # Get the numeric level for the current user and the required role.
        user_level = ROLE_HIERARCHY.get(current_user.role, 0)
        required_level = ROLE_HIERARCHY.get(minimum_required_role, 99) # Default to a high number

        # If the user's level is less than what's required, deny access.
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Insufficient permissions. This action requires at least the "
                    f"'{minimum_required_role.value}' role."
                )
            )
        # If the check passes, return the user object for use in the endpoint.
        return current_user
        
    return role_checker

# --- END FIX ---