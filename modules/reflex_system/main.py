# File: modules/reflex_system/main.py

from fastapi import FastAPI, APIRouter
from contextlib import asynccontextmanager
import asyncio
from . import action_handlers
from .models import LocationPayload, AnnouncementPayload, NotificationPayload
from .utils.logger import logger

from .health_monitor import monitor_system_health

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages the startup and shutdown of background tasks."""
    print("[ReflexSystem] Application starting up...")
    
    # Start the HealthMonitor as a background task.
    app.state.health_monitor_task = asyncio.create_task(monitor_system_health())
    
    yield
    
    # Gracefully shut down the background task when the server stops.
    print("[ReflexSystem] Application shutting down...")
    if hasattr(app.state, 'health_monitor_task') and app.state.health_monitor_task:
        app.state.health_monitor_task.cancel()
        try:
            await app.state.health_monitor_task
        except asyncio.CancelledError:
            logger.info("[ReflexSystem] Health monitor task successfully cancelled.")


app = FastAPI(
    title="NeuraCity ReflexSystem",
    description="Handles real-world action triggers initiated by AI agents.",
    version="1.0.0",
    lifespan=lifespan  # Wire the lifespan manager into the app
)

router = APIRouter(prefix="/api")

@router.post("/actions/call_security", status_code=200)
async def call_security(payload: LocationPayload):
    """Dispatches security and robustly handles the optional source_module."""
    logger.info(f"Received API request to dispatch security to: {payload.location}")
    payload_dict = payload.model_dump()
    source_module = payload_dict.get("source_module")
    return await action_handlers.handle_security_call(payload.location, source_module)

@router.post("/actions/send_announcement", status_code=200)
async def send_announcement(payload: AnnouncementPayload):
    """Broadcasts a message and robustly handles the optional source_module."""
    logger.info(f"Received API request to send announcement: {payload.message}")
    payload_dict = payload.model_dump()
    source_module = payload_dict.get("source_module")
    return await action_handlers.handle_announcement(payload.message, source_module)

@router.post("/actions/notify_admin", status_code=200)
async def notify_admin(payload: NotificationPayload):
    """Sends a message and robustly handles the optional source_module."""
    logger.info(f"Received API request to notify '{payload.department}' admin.")
    payload_dict = payload.model_dump()
    source_module = payload_dict.get("source_module")
    return await action_handlers.handle_admin_notification(payload.department, payload.message, source_module)

@app.get("/", summary="Health Check")
def read_root():
    """Provides a simple health check for the system."""
    return {"status": "ReflexSystem API is operational."}

app.include_router(router)