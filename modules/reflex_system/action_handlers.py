# File: modules/reflex_system/action_handlers.py

import datetime
from .utils.logger import logger
from .event_publisher import publisher  # <-- IMPORT THE PUBLISHER

SYSTEM_LOG_FILE = "system_action_log.txt"

def _log_system_action(log_message: str):
    """Appends a timestamped log message to a system-wide log file."""
    timestamp = datetime.datetime.now().isoformat()
    with open(SYSTEM_LOG_FILE, "a") as f:
        f.write(f"{timestamp} - {log_message}\n")

async def handle_security_call(location: str) -> dict: # <-- Added async
    logger.info(f"ACTION: Security dispatch initiated for location: '{location}'.")
    _log_system_action(f"[HIGH-PRIORITY SECURITY ALERT] Dispatched to: {location}")

    event_payload = {"location": location, "timestamp": datetime.datetime.now().isoformat()}
    await publisher.publish_event(event_type="SECURITY_ALERT", payload=event_payload)
    
    return {"status": "success", "message": "..."}

async def handle_announcement(message: str) -> dict: # <-- Added async
    logger.info(f"ACTION: Campus announcement being broadcasted: '{message}'.")
    _log_system_action(f"[CAMPUS ANNOUNCEMENT] Broadcasted: {message}")

    event_payload = {"message": message, "timestamp": datetime.datetime.now().isoformat()}
    await publisher.publish_event(event_type="CAMPUS_ANNOUNCEMENT", payload=event_payload)

    return {"status": "success", "message": "..."}

async def handle_admin_notification(department: str, message: str) -> dict: # <-- Added async
    logger.info(f"ACTION: Notifying admin of '{department}' department with message: '{message}'.")
    _log_system_action(f"[DEPT NOTIFICATION] Sent to {department}: {message}")
    
    event_payload = {"department": department, "message": message, "timestamp": datetime.datetime.now().isoformat()}
    await publisher.publish_event(event_type="ADMIN_NOTIFICATION", payload=event_payload)

    return {"status": "success", "message": "..."}