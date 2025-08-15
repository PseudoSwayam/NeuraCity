# File: modules/insightcloud/app.py

from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
import asyncio
from . import analytics, realtime
from .healthcheck import health_checker
import sys, os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from modules.userhub.dependencies import get_current_user, require_role
from modules.userhub.models import UserRole

# Global handles for background tasks for graceful shutdown
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

@app.post("/health/ping/{module_name}", summary="Allows a module to report its own health")
def report_health(module_name: str):
    """
    An endpoint for event-driven or script-based modules like cv_watchtower to actively
    report that they are alive and running.
    """
    health_checker.ping_from_event(module_name)
    return {"status": f"Ping received and health updated for {module_name}"}

@app.get("/stats/module_health", summary="Get Health Status of All Modules")
def get_module_health():
    return health_checker.get_status()

@app.get("/stats/events_per_day", summary="Get Historical Event Counts Per Day", dependencies=[Depends(require_role(UserRole.admin))])
def get_events_per_day():
    return analytics.get_events_per_day()

@app.get("/stats/events_by_module", summary="Get Historical Event Counts by Source Module", dependencies=[Depends(require_role(UserRole.admin))])
def get_events_by_module():
    return analytics.get_events_by_module()

@app.get("/stats/anomalies", summary="Detect Anomalous Event Spikes", dependencies=[Depends(require_role(UserRole.admin))])
def find_anomalies():
    return analytics.find_anomalies()

@app.get("/stats/realtime_overview", summary="Get Live System Overview")
def get_realtime_overview():
    return realtime.live_analytics.get_overview()

@app.get("/stats/system_summary", summary="Get a simple text summary of system status", dependencies=[Depends(require_role(UserRole.admin))])
def get_system_summary():
    """
    Provides a pre-formatted, LLM-friendly text summary of the current
    system health and recent activity.
    """
    health_status = health_checker.get_status()
    live_overview = realtime.live_analytics.get_overview()

    healthy_modules = [m['module'] for m in health_status if m['status'] == 'Healthy']
    unhealthy_modules = [m['module'] for m in health_status if m['status'] != 'Healthy' and m['status'] != 'Unknown']

    summary = (
        f"NeuraCity System Status Summary:\n"
        f"- Healthy Modules: {', '.join(healthy_modules) or 'None'}\n"
        f"- Unhealthy/Unresponsive Modules: {', '.join(unhealthy_modules) or 'None'}\n"
        f"- Live Events Since Startup: {live_overview['live_total_events_since_startup']}\n"
        f"- Most recent event type: {live_overview.get('most_recent_event', {}).get('event_type', 'N/A')}"
    )
    return {"summary": summary}

@app.post("/system/refresh_cache", summary="Manually Refresh Historical Data Cache", dependencies=[Depends(require_role(UserRole.admin))])
async def refresh_cache():
    success = await analytics.refresh_data_cache()
    return {"status": "success" if success else "failed", "message": "Data cache refresh completed."}