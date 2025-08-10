# File: modules/alerts_and_notifications/event_processor.py

from .utils.config import MESSAGE_TEMPLATES
from .channels.log_channel import LogChannel
from .channels.webhook_channel import WebhookChannel

class EventProcessor:
    def __init__(self):
        # This is where we register all our active notification channels.
        # Adding a new channel (like an EmailChannel) is as simple as adding it to this list.
        self.channels = [
            LogChannel(),
            WebhookChannel()
        ]
        print(f"[EventProcessor] Initialized with {len(self.channels)} active channels.")

    def _format_message(self, event_data: dict) -> str:
        """Creates a human-readable message from a raw event payload."""
        event_type = event_data.get("event_type", "DEFAULT")
        payload = event_data.get("payload", {})
        
        # Get the template for this event type, or the default if not found
        template = MESSAGE_TEMPLATES.get(event_type, MESSAGE_TEMPLATES["DEFAULT"])
        
        # The .format_map() method safely handles missing keys
        return template.format_map(payload)

    async def process_and_dispatch(self, raw_event_data: dict):
        """
        The main handler for incoming events. It formats the message
        and sends it to all registered channels concurrently.
        """
        print(f"[EventProcessor] Received event of type '{raw_event_data.get('event_type')}'")
        
        # 1. Create the human-readable message
        formatted_message = self._format_message(raw_event_data)
        
        # 2. Dispatch to all channels
        for channel in self.channels:
            try:
                await channel.send(formatted_message, raw_event_data)
            except Exception as e:
                print(f"[EventProcessor] ERROR: Channel failed to send. {e}")