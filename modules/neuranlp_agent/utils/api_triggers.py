import requests
from . import config
import logging

logging.basicConfig(level=config.LOGGING_LEVEL)

def call_security(location: str):
    """Dispatches security to a given location."""
    try:
        response = requests.post(f"{config.REFLEX_API_BASE_URL}/actions/call_security", json={"location": location})
        response.raise_for_status()
        logging.info(f"Security dispatched to {location}.")
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to call security: {e}")
        return {"error": str(e)}

def send_announcement(message: str):
    """Sends a campus-wide announcement."""
    try:
        response = requests.post(f"{config.REFLEX_API_BASE_URL}/actions/send_announcement", json={"message": message})
        response.raise_for_status()
        logging.info(f"Announcement sent: {message}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send announcement: {e}")
        return {"error": str(e)}

def notify_admin(department: str, message: str):
    """Notifies the admin of a specific department."""
    try:
        response = requests.post(f"{config.REFLEX_API_BASE_URL}/actions/notify_admin", json={"department": department, "message": message})
        response.raise_for_status()
        logging.info(f"Notification sent to {department} admin: {message}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to notify admin: {e}")
        return {"error": str(e)}