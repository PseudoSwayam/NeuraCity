# File: modules/neuranlp_agent/utils/api_triggers.py

import requests
from fastapi import Header
from . import config
import logging
from utils.config_loader import settings
from typing import Optional

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


def get_system_health_summary(dummy_input: str = "", token: Optional[str] = None) -> str:
    """
    Makes an API call to InsightCloud to get a pre-formatted summary
    of the entire NeuraCity platform's health and recent activity.
    """
    api_url = f"{settings.INSIGHTCLOUD_HOST}/stats/system_summary"
    headers = {}
    if token:
        headers["Authorization"] = token
    try:
        response = requests.get(api_url, timeout=5, headers=headers)
        if response.status_code == 401:
            return "Authorization Error: You do not have the required permissions to view system health."
        response.raise_for_status()
        return response.json().get("summary", "Could not retrieve summary from InsightCloud.")
    except requests.exceptions.RequestException as e:
        return f"Failed to get system health data from InsightCloud: {e}"


def get_on_campus_users(input_arg: str = "") -> str:
    """
    Makes an API call to UserHub to get a list of all users
    who are currently checked in.
    """
    api_url = f"{settings.USERHUB_HOST}/attendance/on-campus"
    try:
        response = requests.get(api_url, timeout=5)
        response.raise_for_status()
        users = response.json()
        if not users:
            return "No users are currently checked in on campus."
        # Format the response for the LLM
        user_names = [user.get('full_name', 'Unknown User') for user in users]
        return f"The following users are currently on campus: {', '.join(user_names)}."
    except requests.exceptions.RequestException as e:
        return f"Failed to get attendance data: {e}"