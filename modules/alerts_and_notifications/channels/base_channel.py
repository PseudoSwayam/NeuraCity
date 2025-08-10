# File: modules/alerts_and_notifications/channels/base_channel.py

from abc import ABC, abstractmethod

class BaseChannel(ABC):
    """Abstract Base Class for all notification delivery channels."""
    
    @abstractmethod
    async def send(self, message: str, event_data: dict):
        """
        The method that every channel must implement to send a notification.
        
        Args:
            message (str): The formatted, human-readable message.
            event_data (dict): The original, raw event payload for structured sending.
        """
        pass