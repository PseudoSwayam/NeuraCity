# File: modules/alerts_and_notifications/channels/websocket_manager.py

import asyncio
from typing import Set, Dict
from fastapi import WebSocket

class WebSocketManager:
    """
    Manages active WebSocket connections, associating each with a specific user ID.
    This enables broadcasting notifications only to users with the correct role.
    """
    
    def __init__(self):
        # This dictionary maps a user ID to a SET of their active WebSocket connections.
        # A user might have the dashboard open on multiple tabs or devices.
        self.active_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """Accepts a new client connection and maps it to a user ID."""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        print(f"[WebSocket] Client connected for user_id: {user_id}. Total unique users: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket, user_id: int):
        """Removes a client connection for a specific user."""
        if user_id in self.active_connections:
            user_sockets = self.active_connections[user_id]
            user_sockets.remove(websocket)
            # If that was the user's last connection, remove their entry completely.
            if not user_sockets:
                del self.active_connections[user_id]
        print(f"[WebSocket] Client disconnected for user_id: {user_id}. Total unique users: {len(self.active_connections)}")

    async def broadcast_to_users(self, user_ids: Set[int], payload: dict):
        """Sends a JSON payload ONLY to the WebSockets of specified user IDs."""
        if not self.active_connections or not user_ids:
            return

        all_tasks = []
        target_connections_count = 0
        
        # Iterate through the user IDs that need to be notified
        for user_id in user_ids:
            # Check if this user has any active connections
            if user_id in self.active_connections:
                user_websockets = self.active_connections[user_id]
                for ws in user_websockets:
                    all_tasks.append(ws.send_json(payload))
                    target_connections_count += 1
        
        if all_tasks:
            # Concurrently send the message to all targeted connections.
            await asyncio.gather(*all_tasks, return_exceptions=True)
            print(f"[WebSocket] Targeted broadcast successful to {target_connections_count} client(s) for {len(user_ids)} target user(s).")

websocket_manager = WebSocketManager()