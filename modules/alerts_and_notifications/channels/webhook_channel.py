# File: modules/alerts_and_notifications/channels/webhook_channel.py

import httpx
from .base_channel import BaseChannel
from ..utils.config import WEBHOOK_URL

class WebhookChannel(BaseChannel):
    """A notification channel that sends event data to a specified webhook URL."""
    
    async def send(self, message: str, event_data: dict):
        # The webhook payload includes both the simple message and the raw event data
        # for maximum flexibility on the receiving end.
        payload = {
            "human_readable_message": message,
            "raw_event_data": event_data
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(WEBHOOK_URL, json=payload, timeout=10.0)
                response.raise_for_status()
            print(f"[WebhookChannel] Successfully sent notification to {WEBHOOK_URL}")
        except httpx.RequestError as e:
            print(f"[WebhookChannel] ERROR: Could not send webhook. {e}")