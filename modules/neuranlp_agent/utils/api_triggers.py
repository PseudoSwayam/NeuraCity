# File: modules/neuranlp_agent/utils/api_triggers.py

import requests
from . import config
import logging
from utils.config_loader import settings

# This line correctly sets up the logger based on your module's specific config
logging.basicConfig(level=config.LOGGING_LEVEL)


def call_security(location: str) -> dict:
    """Dispatches security and identifies itself as the source module."""
    api_url = f"{settings.REFLEX_API_BASE_URL}/actions/call_security"
    payload = {
        "location": location,
        "source_module": "neuranlp_agent"
    }
    
    try:
        logging.info(f"Triggering CallSecurity API with payload: {payload}")
        response = requests.post(api_url, json=payload, timeout=5)
        response.raise_for_status()
        logging.info(f"API call to {api_url} was successful.")
        return response.json()
    except requests.exceptions.RequestException as e:
        error_message = f"API trigger failed for call_security: {e}"
        logging.error(error_message)
        return {"status": "error", "message": error_message}


def send_announcement(message: str) -> dict:
    """Sends a campus-wide announcement and identifies itself as the source module."""
    api_url = f"{settings.REFLEX_API_BASE_URL}/actions/send_announcement"
    
    payload = {
        "message": message,
        "source_module": "neuranlp_agent"
    }

    try:
        logging.info(f"Triggering SendAnnouncement API with payload: {payload}")
        response = requests.post(api_url, json=payload, timeout=5)
        response.raise_for_status()
        logging.info("API call for announcement was successful.")
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send announcement: {e}")
        return {"error": str(e)}


def notify_admin(department: str, message: str) -> dict:
    """Notifies a department admin and identifies itself as the source module."""
    api_url = f"{settings.REFLEX_API_BASE_URL}/actions/notify_admin"

    payload = {
        "department": department,
        "message": message,
        "source_module": "neuranlp_agent"
    }
    
    try:
        logging.info(f"Triggering NotifyAdmin API with payload: {payload}")
        response = requests.post(api_url, json=payload, timeout=5)
        response.raise_for_status()
        logging.info(f"API call to notify admin of '{department}' was successful.")
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to notify admin: {e}")
        return {"error": str(e)}