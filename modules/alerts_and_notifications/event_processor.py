# File: modules/alerts_and_notifications/event_processor.py

import asyncio
import httpx
from typing import Set
from utils.config_loader import settings
from .utils.config import MESSAGE_TEMPLATES, EVENT_TO_ROLE_MAPPING
from .channels.log_channel import LogChannel
from .channels.webhook_channel import WebhookChannel
from .channels.websocket_manager import websocket_manager

class SafeDict(dict):
    def __missing__(self, key): return f'{{{key}}}'

class EventProcessor:
    def __init__(self):
        self.admin_token: str | None = None
        self.channels = [LogChannel(), WebhookChannel()]
        print("[EventProcessor] Initialized.")

    async def authenticate_with_userhub(self):
        """Logs in as the system's service account to get an auth token."""
        auth_url = f"{settings.USERHUB_HOST}/auth/token"
        admin_email = settings.SYSTEM_ADMIN_EMAIL
        admin_password = settings.SYSTEM_ADMIN_PASSWORD
        if not all([admin_email, admin_password]):
            print("[EventProcessor] FATAL: System admin credentials not found in .env file.")
            return

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(auth_url, data={"username": admin_email, "password": admin_password})
                response.raise_for_status()
                self.admin_token = response.json()["access_token"]
                print("[EventProcessor] Successfully authenticated with UserHub as system admin.")
            except httpx.RequestError as e:
                print(f"[EventProcessor] FATAL: Could not authenticate with UserHub: {e}")
                
    async def get_user_ids_for_roles(self, roles: list) -> Set[int]:
        """Queries UserHub's protected endpoint to get all user IDs for a given list of roles."""
        if not self.admin_token: return set()
        
        user_ids = set()
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        async with httpx.AsyncClient() as client:
            tasks = [client.get(f"{settings.USERHUB_HOST}/users/by-role/{role.value}", headers=headers) for role in roles]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            for res in responses:
                if isinstance(res, httpx.Response) and res.status_code == 200:
                    for user in res.json(): user_ids.add(user['id'])
        return user_ids
        
    def _format_message(self, event_data: dict) -> str:
        """
        Creates a polished, human-readable message, safely handling all variations
        of event data from different modules.
        """
        event_type = event_data.get("event_type", "DEFAULT")
        payload = event_data.get("payload", {})
        
        formatting_data = payload.copy()
        formatting_data['event_type'] = event_type

        template = MESSAGE_TEMPLATES.get(event_type, MESSAGE_TEMPLATES["DEFAULT"])

        return template.format_map(SafeDict(**formatting_data))

    async def process_and_dispatch(self, raw_event_data: dict):
        if not self.admin_token:
            await self.authenticate_with_userhub()
            if not self.admin_token: return
        
        event_type = raw_event_data.get("event_type", "DEFAULT")
        formatted_message = self._format_message(raw_event_data)
        
        print(f"[EventProcessor] Processing message: \"{formatted_message}\"")

        # 1. Look up the target roles for this event type.
        target_roles = EVENT_TO_ROLE_MAPPING.get(event_type)
        
        if not target_roles:
            print(f"[EventProcessor] Event '{event_type}' has no roles mapped. Skipping targeted broadcast.")
            return
            
        # 2. Query UserHub to get the list of user IDs for those roles.
        target_user_ids = await self.get_user_ids_for_roles(target_roles)
        print(f"[EventProcessor] Event '{event_type}' is being sent to {len(target_user_ids)} user(s) with roles: {[r.value for r in target_roles]}")
        
        # 3. Create the payload and dispatch it to the specific users.
        websocket_payload = { "human_readable_message": formatted_message, "raw_event_data": raw_event_data }
        
        # All channels (log, webhook, targeted ws) run concurrently.
        tasks = [
            websocket_manager.broadcast_to_users(target_user_ids, websocket_payload),
            *(channel.send(formatted_message, raw_event_data) for channel in self.channels)
        ]
        await asyncio.gather(*tasks, return_exceptions=True)