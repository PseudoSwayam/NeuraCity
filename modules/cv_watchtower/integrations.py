# File: modules/cv_watchtower/integrations.py

import requests
import datetime
import copy  # <-- 1. IMPORT THE COPY MODULE

from .utils.config import REFLEX_SYSTEM_URL
from memorycore.memory_manager import get_memory_core

def log_event_to_memorycore(event_data: dict):
    """
    Stores a detailed computer vision event into the structured memory (SQLite).
    """
    try:
        memory = get_memory_core()
        # --- 2. THE FIX: Work on a deep copy to avoid modifying the original data ---
        data_to_log = copy.deepcopy(event_data)

        # Now, safely convert the 'details' field in the copy to a string for logging
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
    # This function now receives the original, unmodified event_data dictionary,
    # because the logging function worked on a copy.
    
    event_type = event_data.get("event_type")
    location = event_data.get("camera_id", "Unknown Camera")
    details = event_data.get("details", {}) # This will now be a dictionary as expected
    
    endpoint = None
    payload = None

    if event_type == "FALL_DETECTED":
        endpoint = "/actions/call_security"
        payload = {"location": f"{location} (CRITICAL: Possible Fall Detected)"}

    elif event_type == "VIOLENCE_DETECTED":
        endpoint = "/actions/call_security"
        # This .get() call will now succeed
        reason = details.get("reason", "Aggressive Behavior") 
        payload = {"location": f"{location} (CRITICAL: {reason})"}

    elif event_type == "FIRE_SMOKE_DETECTED":
        endpoint = "/actions/call_security"
        payload = {"location": f"{location} (CRITICAL: Fire/Smoke Detected)"}
        
    elif event_type == "ABANDONED_OBJECT":
        endpoint = "/actions/notify_admin"
        payload = {
            "department": "Security", 
            "message": f"High Priority: Unattended object detected at {location} for over {details.get('duration')} seconds."
        }
    
    elif event_type == "INTRUSION_DETECTED":
        endpoint = "/actions/notify_admin"
        payload = {
            "department": "Security", 
            "message": f"Alert: Intrusion detected in restricted zone at {location}."
        }

    # Low priority events might just be logged for now without a reflex trigger.
    elif event_type == "LOITERING_DETECTED":
        print(f"[Integration] Low priority event '{event_type}' detected at {location}. Logging only.")
        return
        
    else:
        print(f"[Integration] Event '{event_type}' has no configured reflex trigger.")
        return

    # Send the request only if an endpoint and payload were defined.
    try:
        if endpoint and payload:
            response = requests.post(f"{REFLEX_SYSTEM_URL}{endpoint}", json=payload)
            response.raise_for_status() # Raise an exception for HTTP errors
            print(f"[Integration] Successfully triggered reflex action: {endpoint}")
    except requests.exceptions.RequestException as e:
        print(f"[Integration] ERROR: Could not trigger reflex action. {e}")