# File: modules/insightcloud/realtime.py

import asyncio
import json
import aioredis
from collections import Counter
# Import the new health_checker that uses the active pinging model
from .healthcheck import health_checker

# --- Configuration (unchanged) ---
REDIS_HOST = "localhost"
REDIS_PORT = 6379
EVENT_CHANNEL = "campus_notifications"

class RealtimeAnalytics:
    """Manages the Redis subscription and updates live analytics data."""
    _instance = None
    
    def __new__(cls):
        # This singleton pattern is perfect and remains unchanged.
        if cls._instance is None:
            cls._instance = super(RealtimeAnalytics, cls).__new__(cls)
            cls.live_event_count: int = 0
            cls.live_event_types: Counter = Counter()
            cls.last_event: dict = {}
        return cls._instance

    async def register_with_reflex(self):
        """
        Starts the Redis subscription and returns the background task handle.
        """
        print("[Realtime] Starting Redis subscription...")
        try:
            self.redis = await aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}")
            self.pubsub = self.redis.pubsub()
            await self.pubsub.subscribe(EVENT_CHANNEL)
            
            task = asyncio.create_task(self._event_listener())
            print(f"[Realtime] Successfully subscribed to Redis channel: '{EVENT_CHANNEL}'")
            return task
        except Exception as e:
            print(f"[Realtime] FATAL: Could not subscribe to Redis. Live analytics disabled. {e}")
            return None

    async def _event_listener(self):
        """
        The core loop that listens for messages from Redis.
        It now only has two simple jobs: update live stats and ping event-driven modules.
        """
        print("[Realtime] Event listener is now running in the background.")
        try:
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    try:
                        event_data = json.loads(message["data"])
                        event_type = event_data.get("event_type", "unknown")
                        
                        # --- 1. Update live stats (no change) ---
                        self.live_event_count += 1
                        self.live_event_types[event_type] += 1
                        self.last_event = event_data
                        
                        # --- 2. THE ONLY CHANGE IS HERE (SIMPLIFIED LOGIC) ---
                        # We only need to ping the health of modules that DON'T have a web server.
                        # The other modules are actively pinged by healthcheck.py.
                        event_payload = event_data.get('payload', {})
                        
                        if "camera_id" in event_payload:
                            # If an event has a camera_id, we know cv_watchtower is alive.
                            health_checker.ping_from_event('cv_watchtower')
                        
                        # (Future) Example for IoT_PulseNet
                        # elif "sensor_id" in event_payload:
                        #     health_checker.ping_from_event('iot_pulsenet')
                        # --- END CHANGE ---
                        
                        print(f"[Realtime] Received live event: '{event_type}'.")

                    except (json.JSONDecodeError, KeyError) as e:
                        print(f"[Realtime] WARNING: Could not parse message from Redis: {e}")

        except asyncio.CancelledError:
            print("[Realtime] Event listener is shutting down.")
        finally:
            if hasattr(self, 'redis') and self.redis:
                await self.redis.close()

    def get_overview(self) -> dict:
        """Returns a snapshot of the current live statistics (no change)."""
        return {
            "live_total_events_since_startup": self.live_event_count,
            "live_events_by_type": dict(self.live_event_types),
            "most_recent_event": self.last_event
        }

# Singleton instance (no change)
live_analytics = RealtimeAnalytics()