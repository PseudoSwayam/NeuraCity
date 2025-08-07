import datetime
from .utils.logger import logger

SYSTEM_LOG_FILE = "system_action_log.txt"

def _log_system_action(log_message: str):
    """Appends a timestamped log message to a system-wide log file."""
    timestamp = datetime.datetime.now().isoformat()
    with open(SYSTEM_LOG_FILE, "a") as f:
        f.write(f"{timestamp} - {log_message}\n")

async def handle_security_call(location: str) -> dict:
    """
    Handles the logic for dispatching security.
    - Logs the incident to a central system log.
    - In the future, this would trigger a PagerDuty alert, a radio call, etc.
    """
    logger.info(f"ACTION: Security dispatch initiated for location: '{location}'.")
    _log_system_action(f"[HIGH-PRIORITY SECURITY ALERT] Dispatched to: {location}")
    
    return {
        "status": "success",
        "message": f"Security team has been dispatched to {location}. The incident is now logged."
    }

async def handle_announcement(message: str) -> dict:
    """
    Handles logic for sending a campus-wide announcement.
    - Logs the announcement to the system log.
    - In the future, this would push to a mobile app notification service or digital signboards.
    """
    logger.info(f"ACTION: Campus announcement being broadcasted: '{message}'.")
    _log_system_action(f"[CAMPUS ANNOUNCEMENT] Broadcasted: {message}")
    
    return {
        "status": "success",
        "message": "The campus-wide announcement has been broadcasted and logged."
    }

async def handle_admin_notification(department: str, message: str) -> dict:
    """

    Handles logic for notifying a department admin.
    - Logs the notification to the system log.
    - In the future, this would send an email, a Slack message, or create a service ticket.
    """
    logger.info(f"ACTION: Notifying admin of '{department}' department with message: '{message}'.")
    _log_system_action(f"[DEPT NOTIFICATION] Sent to {department}: {message}")
    
    return {
        "status": "success",
        "message": f"A notification has been sent to the {department} admin. A service ticket has been created."
    }