# File: modules/insightcloud/app.py

from fastapi import FastAPI, Depends, Response, status
from contextlib import asynccontextmanager
import asyncio
import sys, os
from fastapi.middleware.cors import CORSMiddleware

# This sys.path logic is essential for a multi-module project and is correct.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# These imports from your other modules are perfect.
from . import analytics, realtime
from .healthcheck import health_checker
from modules.userhub.dependencies import get_current_user, require_role
from modules.userhub.models import UserRole
from modules.userhub.schemas import User as UserSchema


# Your lifespan manager for background tasks is perfect.
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[InsightCloud] Application starting up...")
    
    global redis_listener_task, health_checker_task
    
    health_checker.initialize_client()
    redis_listener_task = await realtime.live_analytics.register_with_reflex()
    health_checker_task = asyncio.create_task(health_checker.start_background_checker())
    await analytics.refresh_data_cache()
    
    yield
    
    print("[InsightCloud] Application shutting down...")
    tasks = [t for t in [redis_listener_task, health_checker_task] if t]
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    await health_checker.close_client()
    print("[InsightCloud] Shutdown complete.")

app = FastAPI(
    title="NeuraCity InsightCloud",
    description="The central analytics and visualization backend for all NeuraCity modules.",
    version="1.0.0",
    lifespan=lifespan
)

# Your CORS Middleware is essential and correctly configured.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], # Must include "OPTIONS" for CORS preflight
    allow_headers=["*"],
)


# --- Public Endpoints (Unchanged and Correct) ---

@app.post("/health/ping/{module_name}", summary="Allows a module to report its own health")
def report_health(module_name: str):
    health_checker.ping_from_event(module_name)
    return {"status": f"Ping received and health updated for {module_name}"}

@app.get("/stats/module_health", summary="Get Health Status of All Modules")
def get_module_health():
    return health_checker.get_status()

@app.get("/stats/realtime_overview", summary="Get Live System Overview")
def get_realtime_overview():
    return realtime.live_analytics.get_overview()

# --- Secure Endpoints (Unchanged and Correct) ---
# Your 'Depends' in the decorator is the standard way, and the fix below will make it work.
@app.get("/stats/events_per_day", summary="Get Historical Event Counts Per Day", dependencies=[Depends(require_role(UserRole.admin))])
def get_events_per_day():
    return analytics.get_events_per_day()

@app.get("/stats/events_by_module", summary="Get Historical Event Counts by Source Module", dependencies=[Depends(require_role(UserRole.admin))])
def get_events_by_module():
    return analytics.get_events_by_module()

@app.get("/stats/anomalies", summary="Detect Anomalous Event Spikes", dependencies=[Depends(require_role(UserRole.admin))])
def find_anomalies():
    return analytics.find_anomalies()

@app.get("/stats/system_summary", summary="Get a simple text summary of system status", dependencies=[Depends(require_role(UserRole.admin))])
def get_system_summary():
    health_status = health_checker.get_status()
    live_overview = realtime.live_analytics.get_overview()
    healthy_modules = [m['module'] for m in health_status if m['status'] == 'Healthy']
    unhealthy_modules = [m['module'] for m in health_status if m['status'] not in ['Healthy', 'Unknown']]
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


# --- THE DEFINITIVE AND FINAL FIX: Manual Preflight Handler ---
# This new endpoint explicitly handles the browser's OPTIONS request.
# It MUST be placed after your other /stats/ endpoints to avoid shadowing them.
@app.options("/stats/{rest_of_path:path}")
async def options_preflight_handler(rest_of_path: str):
    """
    This is a preflight (CORS) handler that manually responds to all OPTIONS
    requests for any path under /stats/. It returns a simple 200 OK, and the
    CORSMiddleware automatically attaches the necessary 'Access-Control-Allow-*'
    headers to this response. This resolves the 405 Method Not Allowed error
    for all the secure GET endpoints above.
    """
    return Response(status_code=status.HTTP_200_OK)
# --- END OF THE FINAL FIX ---


# Root health check to confirm the service is online.
@app.get("/")
def read_root():
    return {"message": "InsightCloud API is operational."}