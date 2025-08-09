# File: modules/cv_watchtower/integrations.py

import requests
import datetime
import copy
import time
from .utils.config import REFLEX_SYSTEM_URL
from memorycore.memory_manager import get_memory_core

# --- ADDED: The URL for InsightCloud's ping endpoint ---
INSIGHTCLOUD_URL = "http://localhost:8002"

# --- ADDED: A global variable to track the last ping time ---
_last_ping_time = 0

def ping_insight_cloud():
    """Pings InsightCloud every 15 seconds to report that cv_watchtower is alive."""
    global _last_ping_time
    current_time = time.time()
    # To avoid spamming the endpoint, we only send a ping periodically
    if (current_time - _last_ping_time) > 15:
        try:
            # Calls the new '/health/ping/{module_name}' endpoint in InsightCloud
            requests.post(f"{INSIGHTCLOUD_URL}/health/ping/cv_watchtower", timeout=2)
            _last_ping_time = current_time
            print("[Integration] Sent health ping to InsightCloud.")
        except requests.exceptions.RequestException:
            # It's okay if this fails; the system should not crash.
            print("[Integration] Warning: Could not send health ping to InsightCloud.")


# --- Your other two functions remain unchanged ---
def log_event_to_memorycore(event_data: dict):
    """Stores a detailed computer vision event into the structured memory (SQLite)."""
    try:
        memory = get_memory_core()
        data_to_log = copy.deepcopy(event_data)

        if 'details' in data_to_log and isinstance(data_to_log['details'], dict):
             data_to_log['details'] = str(data_to_log['details'])

        memory.structured.add(
            source="cv_watchtower",
            type=data_to_log.get("event_type", "generic_cv_event"),
            details_dict=data_to_log
        )
        print(f"[Integration] Successfully logged '{data_to_log.get('event_type')}' event to MemoryCore.")
    except Exception as e:
        print(f"[Integration] ERROR: Could not log event to MemoryCore. {e}")


def trigger_reflex_alert(event_data: dict):
    """Sends a trigger to the reflex_system based on the event's priority."""
    event_type = event_data.get("event_type")
    location = event_data.get("camera_id", "Unknown Camera")
    details = event_data.get("details", {})
    
    endpoint = None
    payload = None

    if event_type in ["FALL_DETECTED", "VIOLENCE_DETECTED", "FIRE_SMOKE_DETECTED"]:
        endpoint = "/actions/call_security"
        reason = "Generic Emergency"
        if event_type == "FALL_DETECTED": reason = "Possible Fall Detected"
        if event_type == "VIOLENCE_DETECTED": reason = details.get("reason", "Aggressive Behavior")
        if event_type == "FIRE_SMOKE_DETECTED": reason = "Fire/Smoke Detected"
        payload = {"location": f"{location} (CRITICAL: {reason})"}
    
    elif event_type == "ABANDONED_OBJECT":
        endpoint = "/actions/notify_admin"
        payload = {"department": "Security", "message": f"High Priority: Unattended object at {location} for >{details.get('duration')}s."}
    
    elif event_type == "INTRUSION_DETECTED":
        endpoint = "/actions/notify_admin"
        payload = {"department": "Security", "message": f"Alert: Intrusion detected in restricted zone at {location}."}

    else:
        return

    try:
        if endpoint and payload:
            response = requests.post(f"{REFLEX_SYSTEM_URL}{endpoint}", json=payload)
            response.raise_for_status()
            print(f"[Integration] Successfully triggered reflex action: {endpoint}")
    except requests.exceptions.RequestException as e:
        print(f"[Integration] ERROR: Could not trigger reflex action. {e}")