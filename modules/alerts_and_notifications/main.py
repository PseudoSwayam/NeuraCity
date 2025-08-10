# File: modules/alerts_and_notifications/main.py

import sys
import os
import asyncio
import json
import aioredis
from .utils.config import REDIS_HOST, REDIS_PORT, EVENT_CHANNEL
from .event_processor import EventProcessor

# Add the project root to the path to allow importing 'memorycore' etc. if needed later
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    
async def main():
    """
    Connects to Redis, listens for messages on the event channel, and
    dispatches them to the EventProcessor for handling.
    """
    print("[Alerts Main] Initializing Alerts & Notifications service...")
    processor = EventProcessor()
    
    try:
        redis = await aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}")
        pubsub = redis.pubsub()
        await pubsub.subscribe(EVENT_CHANNEL)
        print(f"[Alerts Main] Successfully subscribed to Redis channel '{EVENT_CHANNEL}'. Waiting for events...")

        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    event_data = json.loads(message["data"])
                    await processor.process_and_dispatch(event_data)
                except json.JSONDecodeError:
                    print(f"[Alerts Main] Received non-JSON message: {message['data']}")

    except aioredis.RedisError as e:
        print(f"[Alerts Main] FATAL: Could not connect to Redis. {e}")
    except KeyboardInterrupt:
        print("\n[Alerts Main] Shutdown signal received.")
    finally:
        print("[Alerts Main] Service shutting down.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[Alerts Main] Exiting.")