# File: modules/alerts_and_notifications/main.py

import sys
import os
import asyncio
import json
import aioredis
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, status
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from modules.userhub.database import get_db
from modules.userhub.dependencies import get_current_user
from modules.userhub.schemas import User as UserSchema
from utils.config_loader import settings
from .event_processor import EventProcessor
from .channels.websocket_manager import websocket_manager


# --- Your perfect lifespan manager is unchanged ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the startup and shutdown of the background Redis listener.
    """
    print("[Alerts Main] FastAPI server starting up...")
    processor = EventProcessor()
    app.state.event_processor = processor
    # Authenticate on startup
    asyncio.create_task(processor.authenticate_with_userhub())
    # Start the Redis listener and pass it the processor instance
    app.state.redis_listener_task = asyncio.create_task(redis_listener(processor))
    yield
    print("[Alerts Main] FastAPI server shutting down...")
    app.state.redis_listener_task.cancel()
    try:
        await app.state.redis_listener_task
    except asyncio.CancelledError:
        print("[Alerts Main] Redis listener task successfully cancelled.")

# Your app initialization is unchanged
app = FastAPI(
    title="NeuraCity Alerts & Notifications Service",
    description="Provides real-time event notifications via WebSockets and Webhooks.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows connections from any domain
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# --- Your perfect WebSocket endpoint is unchanged ---
@app.websocket("/ws/alerts")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str, # The frontend must provide the user's JWT token
    db: Session = Depends(get_db)
):
    """
    Accepts WebSocket connections from AUTHENTICATED users and maps the
    connection to their user ID.
    """
    try:
        # Authenticate the user based on the provided token
        user: UserSchema = await get_current_user(token=token, db=db)
        if not user:
            # If the token is invalid, close the connection
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # If authenticated, connect them and map the socket to their ID
        await websocket_manager.connect(websocket, user.id)
        
        while True:
            await websocket.receive_text() # Keep connection alive
            
    except WebSocketDisconnect:
        if user: # If user was authenticated before disconnecting
            websocket_manager.disconnect(websocket, user.id)

@app.get("/", summary="Health Check")
def health_check():
    """Provides a simple health check for the system."""
    # We check the Redis listener task to make sure the core process is running.
    if app.state.redis_listener_task and not app.state.redis_listener_task.done():
        return {"status": "ok", "redis_listener": "active"}
    else:
        return {"status": "error", "redis_listener": "inactive"}

# --- Your perfect Redis listener logic is unchanged ---
async def redis_listener(processor: EventProcessor):
    """
    This is your original 'main()' function, now adapted to run as a
    persistent background task for the lifetime of the server.
    """
    redis = None
    try:
        redis = await aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")
        pubsub = redis.pubsub()
        await pubsub.subscribe(settings.REDIS_EVENT_CHANNEL)
        print(f"[Alerts Main] Successfully subscribed to Redis channel '{settings.REDIS_EVENT_CHANNEL}'. Waiting for events...")

        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    event_data = json.loads(message["data"])
                    await processor.process_and_dispatch(event_data)
                except json.JSONDecodeError:
                    print(f"[Alerts Main] WARNING: Received non-JSON message: {message['data']}")
    
    except asyncio.CancelledError:
        print("[Alerts Main] Redis listener task is being cancelled.")
    except aioredis.RedisError as e:
        print(f"[Alerts Main] FATAL: Could not connect to Redis. {e}")
    finally:
        if redis:
            await redis.close()
        print("[Alerts Main] Redis listener has shut down.")