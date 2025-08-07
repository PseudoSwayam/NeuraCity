# File: modules/reflex_system/main.py

from fastapi import FastAPI, APIRouter
from . import action_handlers
from .models import LocationPayload, AnnouncementPayload, NotificationPayload
from .utils.logger import logger

app = FastAPI(
    title="NeuraCity ReflexSystem",
    description="Handles real-world action triggers initiated by AI agents.",
    version="1.0.0"
)

# Using an APIRouter is a best practice for modularity.
# It allows us to version our API easily (e.g., /api/v1).
router = APIRouter(prefix="/api")

@router.post("/actions/call_security", status_code=200)
async def call_security(payload: LocationPayload):
    """Dispatches security and logs a high-priority incident."""
    logger.info(f"Received API request to dispatch security to: {payload.location}")
    return await action_handlers.handle_security_call(payload.location)

@router.post("/actions/send_announcement", status_code=200)
async def send_announcement(payload: AnnouncementPayload):
    """Broadcasts a message across campus systems."""
    logger.info(f"Received API request to send announcement: {payload.message}")
    return await action_handlers.handle_announcement(payload.message)

@router.post("/actions/notify_admin", status_code=200)
async def notify_admin(payload: NotificationPayload):
    """Sends a message to a specific department head or service desk."""
    logger.info(f"Received API request to notify '{payload.department}' admin.")
    return await action_handlers.handle_admin_notification(payload.department, payload.message)


@app.get("/", summary="Health Check")
def read_root():
    """Provides a simple health check for the system."""
    return {"status": "ReflexSystem API is operational."}

# Include the router in the main FastAPI application instance
app.include_router(router)


# This allows running the server directly with 'python3 -m modules.reflex_system.main'
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("modules.reflex_system.main:app", host="0.0.0.0", port=8001, reload=True)
