# File: modules/insightcloud/app.py

from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
from . import analytics, realtime
from .healthcheck import health_checker

# --- Global handles for background tasks for graceful shutdown ---
redis_listener_task = None
health_checker_task = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages the startup and shutdown of background services and clients."""
    global redis_listener_task, health_checker_task
    print("[InsightCloud] Application starting up...")
    
    # 1. Initialize the persistent HTTP client for the Health Checker
    health_checker.initialize_client()

    # 2. Start the background tasks
    redis_listener_task = await realtime.live_analytics.register_with_reflex()
    health_checker_task = asyncio.create_task(health_checker.start_background_checker())
    
    # 3. Build the initial analytics cache
    await analytics.refresh_data_cache()
    
    yield
    
    # --- On Application Shutdown ---
    print("[InsightCloud] Application shutting down...")
    
    # 1. Cancel background tasks
    tasks = [t for t in [redis_listener_task, health_checker_task] if t]
    for task in tasks:
        task.cancel()
    
    # Wait for tasks to acknowledge cancellation
    await asyncio.gather(*tasks, return_exceptions=True)

    # 2. Gracefully close the health checker's HTTP client
    await health_checker.close_client()
    print("[InsightCloud] Shutdown complete.")
    

app = FastAPI(
    title="NeuraCity InsightCloud",
    description="The central analytics and visualization backend for all NeuraCity modules.",
    version="1.0.0",
    lifespan=lifespan
)

# --- API Endpoints (These remain unchanged and will now work correctly) ---

@app.get("/stats/module_health", summary="Get Health Status of All Modules")
def get_module_health():
    return health_checker.get_status()

# ... (rest of your existing, perfect endpoints: /events_per_day, /realtime_overview, etc.)

@app.get("/stats/events_per_day")
def get_events_per_day(): return analytics.get_events_per_day()
@app.get("/stats/events_by_module")
def get_events_by_module(): return analytics.get_events_by_module()
@app.get("/stats/anomalies")
def find_anomalies(): return analytics.find_anomalies()
@app.get("/stats/realtime_overview")
def get_realtime_overview(): return realtime.live_analytics.get_overview()
@app.post("/system/refresh_cache")
async def refresh_cache():
    success = await analytics.refresh_data_cache()
    return {"status": "success" if success else "failed"}