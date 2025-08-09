# File: modules/insightcloud/app.py

from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
from . import analytics, realtime
from .healthcheck import health_checker

# --- MODIFICATION: Define handles for BOTH background tasks ---
redis_listener_task = None
health_checker_task = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages the startup and shutdown of background tasks."""
    global redis_listener_task, health_checker_task
    print("[InsightCloud] Application starting up...")
    
    # Start listening for live events from Redis and store the task
    redis_listener_task = await realtime.live_analytics.register_with_reflex()
    
    # Start the new, proactive health checker in the background
    health_checker_task = asyncio.create_task(health_checker.start_background_checker())
    
    # Do an initial data cache refresh from MemoryCore
    await analytics.refresh_data_cache()
    
    yield
    
    # --- On Application Shutdown ---
    # This block now gracefully cancels BOTH background tasks.
    print("[InsightCloud] Application shutting down...")
    
    if redis_listener_task:
        print("[InsightCloud] Cancelling Redis listener task...")
        redis_listener_task.cancel()
        try:
            await redis_listener_task
        except asyncio.CancelledError:
            print("[InsightCloud] Redis listener task successfully cancelled.")
    
    if health_checker_task:
        print("[InsightCloud] Cancelling health checker task...")
        health_checker_task.cancel()
        try:
            await health_checker_task
        except asyncio.CancelledError:
            print("[InsightCloud] Health checker task successfully cancelled.")
    

app = FastAPI(
    title="NeuraCity InsightCloud",
    description="The central analytics and visualization backend for all NeuraCity modules.",
    version="1.0.0",
    lifespan=lifespan
)

# --- API Endpoints (These remain 100% unchanged) ---

@app.get("/stats/events_per_day", summary="Get Historical Event Counts Per Day")
def get_events_per_day():
    return analytics.get_events_per_day()

@app.get("/stats/events_by_module", summary="Get Historical Event Counts by Source Module")
def get_events_by_module():
    return analytics.get_events_by_module()

@app.get("/stats/anomalies", summary="Detect Anomalous Event Spikes")
def find_anomalies():
    return analytics.find_anomalies()

@app.get("/stats/module_health", summary="Get Health Status of All Modules")
def get_module_health():
    """
    Returns the current health status of all registered modules based on
    proactive checks and event monitoring.
    """
    return health_checker.get_status()

@app.get("/stats/realtime_overview", summary="Get Live System Overview")
def get_realtime_overview():
    return realtime.live_analytics.get_overview()

@app.post("/system/refresh_cache", summary="Manually Refresh Historical Data Cache")
async def refresh_cache():
    success = await analytics.refresh_data_cache()
    return {"status": "success" if success else "failed", "message": "Data cache refresh completed."}