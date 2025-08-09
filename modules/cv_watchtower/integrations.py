import requests
import datetime
from .utils.config import REFLEX_SYSTEM_URL

# IMPORTANT: This assumes memorycore is in the project's Python path.
from memorycore.memory_manager import get_memory_core

def log_event_to_memorycore(event_data: dict):
    """Stores a detailed computer vision event into the structured memory (SQLite)."""
    try:
        memory = get_memory_core()
        memory.structured.add(
            source="cv_watchtower",
            type=event_data.get("event_type", "generic_cv_event"),
            details_dict=event_data
        )
        print(f"[Integration] Successfully logged '{event_data.get('event_type')}' event to MemoryCore.")
    except Exception as e:
        print(f"[Integration] ERROR: Could not log event to MemoryCore. {e}")


def trigger_reflex_alert(event_data: dict):
    """Sends a trigger to the reflex_system for immediate action."""
    event_type = event_data.get("event_type")
    location = event_data.get("camera_id", "Unknown Camera")
    
    # Map CV event types to reflex system actions
    if event_type == "FALL_DETECTED":
        endpoint = "/actions/call_security"
        payload = {"location": f"{location} (Possible Fall Detected)"}
        print(f"[Integration] Triggering high-priority security alert for a fall at {location}.")
        
    elif event_type == "INTRUSION_DETECTED":
        endpoint = "/actions/notify_admin"
        payload = {
            "department": "Security",
            "message": f"Intrusion detected in a restricted zone at {location}."
        }
        print(f"[Integration] Triggering admin notification for intrusion at {location}.")

    else:
        # For other event types like loitering, we might only log them
        # or send a lower-priority notification in the future.
        print(f"[Integration] Event '{event_type}' detected. No reflex trigger configured for this type.")
        return

    try:
        response = requests.post(f"{REFLEX_SYSTEM_URL}{endpoint}", json=payload)
        response.raise_for_status()
        print(f"[Integration] Successfully triggered reflex action. Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"[Integration] ERROR: Could not trigger reflex action. {e}")