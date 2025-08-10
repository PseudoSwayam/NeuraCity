# File: modules/alerts_and_notifications/event_processor.py

from .utils.config import MESSAGE_TEMPLATES
from .channels.log_channel import LogChannel
from .channels.webhook_channel import WebhookChannel

# --- MODIFICATION: Import the new WebSocketManager ---
from .channels.websocket_manager import websocket_manager

# Your existing SafeDict helper class is perfect and unchanged.
class SafeDict(dict):
    def __missing__(self, key):
        return f'{{{key}}}'

class EventProcessor:
    def __init__(self):
        # Your existing channels for logging and webhooks are unchanged.
        self.channels = [
            LogChannel(),
            WebhookChannel()
        ]
        print(f"[EventProcessor] Initialized with {len(self.channels)} external channels.")

    def _format_message(self, event_data: dict) -> str:
        """Creates a human-readable message, safely handling missing keys."""
        event_type = event_data.get("event_type", "DEFAULT")
        payload = event_data.get("payload", {})
        
        safe_payload = SafeDict(**payload)
        template = MESSAGE_TEMPLATES.get(event_type, MESSAGE_TEMPLATES.get(event_type.replace('CV_', '').replace('NLP_', ''), MESSAGE_TEMPLATES["DEFAULT"]))
        
        if 'event_type' not in safe_payload:
            safe_payload['event_type'] = event_type
            
        return template.format_map(safe_payload)

    async def process_and_dispatch(self, raw_event_data: dict):
        """
        Main handler that formats an event and dispatches it to all channels,
        including broadcasting to WebSocket clients for the live dashboard.
        """
        print(f"[EventProcessor] Received event of type '{raw_event_data.get('event_type')}'")
        
        formatted_message = self._format_message(raw_event_data)
        
        print(f"[EventProcessor] Dispersing formatted message: \"{formatted_message}\"")

        # 1. Dispatch to background channels (webhook, log file) concurrently.
        # This is a slightly more performant way to run them.
        background_tasks = [
            channel.send(formatted_message, raw_event_data) for channel in self.channels
        ]
        
        # 2. At the same time, broadcast to all active WebSocket clients.
        websocket_payload = {
            "human_readable_message": formatted_message,
            "raw_event_data": raw_event_data
        }
        background_tasks.append(websocket_manager.broadcast(websocket_payload))

        # 3. Run all tasks concurrently.
        import asyncio
        await asyncio.gather(*background_tasks, return_exceptions=True)