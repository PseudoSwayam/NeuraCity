# File: modules/alerts_and_notifications/event_processor.py

import asyncio
from .utils.config import MESSAGE_TEMPLATES
from .channels.log_channel import LogChannel
from .channels.webhook_channel import WebhookChannel
from .channels.websocket_manager import websocket_manager

class SafeDict(dict):
    """A helper class to prevent crashes when formatting strings with missing keys."""
    def __missing__(self, key):
        return f'{{{key}}}'

class EventProcessor:
    def __init__(self):
        self.channels = [
            LogChannel(),
            WebhookChannel()
        ]
        print(f"[EventProcessor] Initialized with {len(self.channels)} external channels.")

    def _format_message(self, event_data: dict) -> str:
        """
        Creates a polished, human-readable message, safely handling all variations
        of event data from different modules.
        """
        event_type = event_data.get("event_type", "DEFAULT")
        payload = event_data.get("payload", {})
        
        formatting_data = payload.copy()
        formatting_data['event_type'] = event_type

        template = MESSAGE_TEMPLATES.get(event_type, MESSAGE_TEMPLATES["DEFAULT"])

        return template.format_map(SafeDict(**formatting_data))

    async def process_and_dispatch(self, raw_event_data: dict):
        """
        Main handler that formats an event and dispatches it concurrently to all channels.
        """
        print(f"[EventProcessor] Received event of type '{raw_event_data.get('event_type')}'")
        
        formatted_message = self._format_message(raw_event_data)
        
        print(f"[EventProcessor] Dispersing formatted message: \"{formatted_message}\"")

        websocket_payload = {
            "human_readable_message": formatted_message,
            "raw_event_data": raw_event_data
        }

        # Concurrently run the broadcast to the dashboard and send to all background channels
        # This is the most performant and robust way to handle dispatching.
        tasks = [
            websocket_manager.broadcast(websocket_payload),
            *(channel.send(formatted_message, raw_event_data) for channel in self.channels)
        ]
        
        # `return_exceptions=True` ensures that if one channel fails (e.g., webhook is down),
        # it doesn't crash the entire notification process for the others.
        await asyncio.gather(*tasks, return_exceptions=True)