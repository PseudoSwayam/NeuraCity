# File: modules/reflex_system/event_publisher.py

import redis.asyncio as redis
import json
from .utils.logger import logger

REDIS_HOST = "localhost"
REDIS_PORT = 6379
EVENT_CHANNEL = "campus_notifications"

class EventPublisher:
    _instance = None
    _redis_client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventPublisher, cls).__new__(cls)
            try:
                # Add a health check to be more explicit about connection status
                cls._redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, auto_close_connection_pool=False)
                logger.info(f"Redis client initialized for {REDIS_HOST}:{REDIS_PORT}")
            except Exception as e:
                logger.error(f"FATAL: Could not create Redis client: {e}")
                cls._redis_client = None
        return cls._instance

    async def check_connection(self):
        """Pings the Redis server to ensure the connection is alive."""
        if not self._redis_client:
            return False
        try:
            await self._redis_client.ping()
            logger.info("Redis connection is active.")
            return True
        except Exception as e:
            logger.error(f"Redis connection check failed: {e}")
            return False

    async def publish_event(self, event_type: str, payload: dict):
        """Publishes a structured event to the central Redis channel."""
        if not await self.check_connection():
            logger.error("Cannot publish event: Redis connection is not active.")
            return

        event_message = {
            "event_type": event_type,
            "payload": payload
        }
        try:
            message_json = json.dumps(event_message)
            # The publish command returns the number of clients that received the message.
            num_clients = await self._redis_client.publish(EVENT_CHANNEL, message_json)
            logger.info(f"Published event '{event_type}' to '{EVENT_CHANNEL}'. Message received by {num_clients} client(s).")
        except Exception as e:
            logger.error(f"Failed to publish event to Redis: {e}")

publisher = EventPublisher()