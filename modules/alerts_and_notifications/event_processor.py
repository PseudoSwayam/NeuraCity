# File: modules/alerts_and_notifications/event_processor.py
# (Definitive, Final Version)

from .utils.config import MESSAGE_TEMPLATES
from .channels.log_channel import LogChannel
from .channels.webhook_channel import WebhookChannel

# A simple helper class to safely format strings
class SafeDict(dict):
    def __missing__(self, key):
        # If a key like {reason} is in the template but not in the data,
        # it will be replaced with the text "{reason}" instead of crashing.
        return f'{{{key}}}'

class EventProcessor:
    def __init__(self):
        self.channels = [
            LogChannel(),
            WebhookChannel()
        ]
        print(f"[EventProcessor] Initialized with {len(self.channels)} active channels.")

    def _format_message(self, event_data: dict) -> str:
        """Creates a human-readable message, safely handling missing keys."""
        event_type = event_data.get("event_type", "DEFAULT")
        payload = event_data.get("payload", {})
        
        # Use our SafeDict to prevent crashes from missing template keys
        safe_payload = SafeDict(**payload)
        
        template = MESSAGE_TEMPLATES.get(event_type, MESSAGE_TEMPLATES["DEFAULT"])

        # Also add event_type to the payload in case the DEFAULT template needs it
        if 'event_type' not in safe_payload:
            safe_payload['event_type'] = event_type
            
        return template.format_map(safe_payload)

    async def process_and_dispatch(self, raw_event_data: dict):
        """Main handler for formatting and dispatching events."""
        print(f"[EventProcessor] Received event of type '{raw_event_data.get('event_type')}'")
        
        formatted_message = self._format_message(raw_event_data)
        
        print(f"[EventProcessor] Dispersing formatted message: \"{formatted_message}\"")
        
        for channel in self.channels:
            try:
                await channel.send(formatted_message, raw_event_data)
            except Exception as e:
                print(f"[EventProcessor] ERROR: A channel failed to send. Details: {e}")