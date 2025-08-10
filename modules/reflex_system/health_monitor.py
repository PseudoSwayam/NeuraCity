# File: modules/reflex_system/health_monitor.py

import asyncio
import httpx
import time
from typing import Dict, Any

# --- Import from sibling modules and the central config ---
from .action_handlers import handle_admin_notification
from .utils.logger import logger
from utils.config_loader import settings

# --- Health Monitor Configuration ---
CHECK_INTERVAL_MINUTES = 5
UNHEALTHY_THRESHOLD_MINUTES = 10

# --- MODIFICATION: Added 'alerts_and_notifications' to the critical list ---
CRITICAL_MODULES = [
    "neuranlp_agent",
    "cv_watchtower",
    "alerts_and_notifications"
    # 'iot_pulsenet' will be added here in the future
]

# In-memory state to track how long modules have been unhealthy
unhealthy_since: Dict[str, float] = {}

async def monitor_system_health():
    """
    The main background task that runs periodically to check the health of all
    NeuraCity modules by polling the InsightCloud API.
    """
    logger.info("[HealthMonitor] Starting background system health monitoring task...")
    
    # Give the rest of the system a moment to start up before the first check
    await asyncio.sleep(60)

    async with httpx.AsyncClient(timeout=10.0) as client:
        while True:
            logger.info("[HealthMonitor] Running scheduled system health check...")
            try:
                # 1. Fetch the system health report from InsightCloud
                health_report_url = f"{settings.INSIGHTCLOUD_HOST}/stats/module_health"
                response = await client.get(health_report_url)
                response.raise_for_status()
                module_statuses = response.json()
                
                # 2. Analyze the report
                await _analyze_health_report(module_statuses)
                
            except httpx.RequestError as e:
                logger.error(f"[HealthMonitor] Could not connect to InsightCloud to get health report: {e}")
            except Exception as e:
                logger.error(f"[HealthMonitor] An unexpected error occurred during health check: {e}")
                
            # 3. Wait for the next cycle
            logger.info(f"[HealthMonitor] Health check complete. Waiting for {CHECK_INTERVAL_MINUTES} minutes.")
            await asyncio.sleep(CHECK_INTERVAL_MINUTES * 60)


async def _analyze_health_report(statuses: list[dict]):
    """
    Analyzes the health report from InsightCloud and triggers alerts for critical
    modules that have been unhealthy for too long.
    """
    global unhealthy_since
    current_time = time.time()
    
    for module in statuses:
        module_name = module.get("module")
        status = module.get("status")
        
        if module_name not in CRITICAL_MODULES:
            continue
            
        is_healthy = (status == "Healthy")

        if is_healthy:
            if module_name in unhealthy_since:
                logger.info(f"[HealthMonitor] Good News: Module '{module_name}' has recovered and is now Healthy.")
                unhealthy_since.pop(module_name)
        else: # Module is unhealthy/unresponsive/stale etc.
            if module_name not in unhealthy_since:
                logger.warning(f"[HealthMonitor] ATTENTION: Module '{module_name}' is reporting an Unhealthy status. Starting timer.")
                unhealthy_since[module_name] = current_time
            else:
                unhealthy_duration_minutes = (current_time - unhealthy_since[module_name]) / 60
                logger.warning(
                    f"[HealthMonitor] Module '{module_name}' remains Unhealthy "
                    f"for {unhealthy_duration_minutes:.1f} minutes."
                )
                
                if unhealthy_duration_minutes >= UNHEALTHY_THRESHOLD_MINUTES:
                    logger.critical(
                        f"[HealthMonitor] CRITICAL: Module '{module_name}' has exceeded the "
                        f"unhealthy threshold of {UNHEALTHY_THRESHOLD_MINUTES} minutes. Triggering SRE alert."
                    )
                    
                    alert_message = (
                        f"CRITICAL SYSTEM ALERT: The '{module_name}' module is unresponsive and has been "
                        f"unhealthy for over {UNHEALTHY_THRESHOLD_MINUTES} minutes. "
                        f"Please investigate immediately."
                    )
                    
                    # Use one of this module's own actions to send the notification
                    await handle_admin_notification(
                        department="SRE_Team",
                        message=alert_message,
                        source_module="health_monitor" # Identify the source of the alert
                    )
                    
                    # Reset the timer after alerting to prevent spam
                    unhealthy_since[module_name] = current_time