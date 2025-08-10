# File: modules/alerts_and_notifications/channels/log_channel.py

import datetime
from .base_channel import BaseChannel

NOTIFICATION_LOG_FILE = "notifications_sent.log"

class LogChannel(BaseChannel):
    """A notification channel that writes formatted alerts to a local log file."""
    
    async def send(self, message: str, event_data: dict):
        timestamp = datetime.datetime.now().isoformat()
        log_entry = f"{timestamp} | [NOTIFICATION] | {message}\n"
        
        try:
            with open(NOTIFICATION_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(log_entry)
            print(f"[LogChannel] Successfully wrote notification to {NOTIFICATION_LOG_FILE}")
        except Exception as e:
            print(f"[LogChannel] ERROR: Failed to write to log file. {e}")