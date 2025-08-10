# File: modules/alerts_and_notifications/channels/websocket_manager.py

import asyncio
from typing import Set
from fastapi import WebSocket

class WebSocketManager:
    """
    Manages all active WebSocket connections for the Admin Dashboard.
    This version includes self-healing logic to automatically clean up
    stale or dead connections during a broadcast.
    """
    
    def __init__(self):
        # A set provides fast addition and removal of unique connections
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        """Accepts a new client connection and adds it to the active pool."""
        await websocket.accept()
        self.active_connections.add(websocket)
        print(f"[WebSocket] Client connected: {websocket.client}. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """
        Removes a client connection. This is typically called on a clean
        disconnect signal from the client.
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"[WebSocket] Client cleanly disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast(self, payload: dict):
        """
        Sends a JSON payload to all connected clients and gracefully handles
        and removes any stale connections that fail during the send operation.
        """
        if not self.active_connections:
            return
        # A temporary set to hold any connections that fail during the broadcast.
        stale_connections = set()
        
        # Phase 1: Attempt to send the message to every connected client.
        for connection in self.active_connections:
            try:
                await connection.send_json(payload)
            except Exception as e:
                # If sending a message to a client fails, it means the connection is stale
                # We mark it for removal.
                print(f"[WebSocket] Found stale connection. Marking for removal. Error: {type(e).__name__}")
                stale_connections.add(connection)
        
        # Phase 2: Clean up any stale connections that were identified.
        if stale_connections:
            print(f"[WebSocket] Removing {len(stale_connections)} stale connection(s)...")
            for connection in stale_connections:
                if connection in self.active_connections:
                    self.active_connections.remove(connection)
            print(f"[WebSocket] Cleanup complete. Total active clients now: {len(self.active_connections)}")

        if self.active_connections:
            print(f"[WebSocket] Broadcast successful to {len(self.active_connections)} active client(s).")

websocket_manager = WebSocketManager()