# File: modules/reflex_system/action_handlers.py

import datetime
from .utils.logger import logger
from .event_publisher import publisher

# --- MODIFICATION 1 of 1: Import the new unified memory core ---
from memorycore.memory_manager import get_memory_core


SYSTEM_LOG_FILE = "system_action_log.txt"

def _log_system_action(log_message: str):
    """Appends a timestamped log message to a system-wide log file."""
    timestamp = datetime.datetime.now().isoformat()
    with open(SYSTEM_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} - {log_message}\n")

async def handle_security_call(location: str) -> dict:
    """Handles security dispatch, logs action, publishes event, and records to structured MemoryCore."""
    logger.info(f"ACTION: Security dispatch initiated for location: '{location}'.")
    _log_system_action(f"[HIGH-PRIORITY SECURITY ALERT] Dispatched to: {location}")

    # --- ADDED: Record this critical action to the centralized structured memory ---
    event_details = {"location": location, "status": "dispatched"}
    get_memory_core().structured.add("reflex_system", "security_alert", event_details)

    event_payload = {"location": location, "timestamp": datetime.datetime.now().isoformat()}
    await publisher.publish_event(event_type="SECURITY_ALERT", payload=event_payload)
    
    return {"status": "success", "message": "Security team dispatched and event recorded."}

async def handle_announcement(message: str) -> dict:
    """Handles announcement, logs action, publishes event, and records to structured MemoryCore."""
    logger.info(f"ACTION: Campus announcement being broadcasted: '{message}'.")
    _log_system_action(f"[CAMPUS ANNOUNCEMENT] Broadcasted: {message}")

    # --- ADDED: Record this action to the centralized structured memory ---
    event_details = {"message_snippet": f"{message[:75]}..."}
    get_memory_core().structured.add("reflex_system", "announcement", event_details)

    event_payload = {"message": message, "timestamp": datetime.datetime.now().isoformat()}
    await publisher.publish_event(event_type="CAMPUS_ANNOUNCEMENT", payload=event_payload)

    return {"status": "success", "message": "Announcement broadcasted and event recorded."}

async def handle_admin_notification(department: str, message: str) -> dict:
    """Handles admin notification, logs action, publishes event, and records to structured MemoryCore."""
    logger.info(f"ACTION: Notifying admin of '{department}' department with message: '{message}'.")
    _log_system_action(f"[DEPT NOTIFICATION] Sent to {department}: {message}")
    
    # --- ADDED: Record this action to the centralized structured memory ---
    event_details = {"department": department, "message_snippet": f"{message[:75]}..."}
    get_memory_core().structured.add("reflex_system", "admin_notification", event_details)

    event_payload = {"department": department, "message": message, "timestamp": datetime.datetime.now().isoformat()}
    await publisher.publish_event(event_type="ADMIN_NOTIFICATION", payload=event_payload)

    return {"status": "success", "message": "Notification sent and event recorded."}