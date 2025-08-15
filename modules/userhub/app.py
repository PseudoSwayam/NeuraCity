# File: modules/userhub/app.py
from fastapi import FastAPI
from .database import Base, engine
from .routers import auth, users, attendance

# This will create the database tables if they don't exist, but Alembic is preferred.
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NeuraCity UserHub",
    description="The central identity, authentication, and user data service for the NeuraCity platform.",
    version="1.0.0"
)

# Include the routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(attendance.router)

@app.get("/")
def read_root():
    return {"message": "UserHub is running"}