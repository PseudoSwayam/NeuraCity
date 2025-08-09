# File: modules/insightcloud/healthcheck.py

import time
import asyncio
import httpx
from typing import Dict, List

class HealthCheck:
    """
    Proactively and passively tracks the health of all NeuraCity modules.
    This is the definitive, robust implementation.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(HealthCheck, cls).__new__(cls)
            cls.registered_modules: Dict[str, dict] = {
                'neuranlp_agent': {"type": "server", "url": "http://localhost:8000/health", "last_seen": 0.0, "status": "Unknown"},
                'reflex_system':  {"type": "server", "url": "http://localhost:8001/", "last_seen": 0.0, "status": "Unknown"},
                'insightcloud':   {"type": "server", "url": "http://localhost:8002/docs", "last_seen": 0.0, "status": "Unknown"},
                'cv_watchtower':  {"type": "event_driven", "last_seen": 0.0, "status": "Unknown"},
                'iot_pulsenet':   {"type": "event_driven", "last_seen": 0.0, "status": "Unknown"}
            }
            cls.check_interval_seconds = 20 # Check more frequently for faster updates
            cls.unhealthy_threshold_seconds = 65.0
            # A persistent client for making HTTP requests
            cls.http_client: httpx.AsyncClient | None = None
        return cls._instance

    def initialize_client(self):
        """Creates the persistent HTTP client."""
        if self.http_client is None:
            self.http_client = httpx.AsyncClient(timeout=5.0)
            print("[HealthCheck] HTTP client initialized.")

    async def close_client(self):
        """Gracefully closes the HTTP client."""
        if self.http_client:
            await self.http_client.aclose()
            self.http_client = None
            print("[HealthCheck] HTTP client closed.")

    def ping_from_event(self, module_name: str):
        """Passively updates status for event-driven modules like cv_watchtower."""
        if module_name in self.registered_modules and self.registered_modules[module_name]["type"] == "event_driven":
            module = self.registered_modules[module_name]
            module["last_seen"] = time.time()
            if module["status"] != "Healthy":
                print(f"[HealthCheck] Status for {module_name} is now Healthy (via event).")
            module["status"] = "Healthy"
            
    async def _check_endpoint(self, module_name: str, url: str):
        """Asynchronously checks a single module's health endpoint."""
        if not self.http_client:
            print("[HealthCheck] ERROR: HTTP client not initialized. Cannot perform active check.")
            return

        current_status = self.registered_modules[module_name]["status"]
        new_status = current_status
        
        try:
            response = await self.http_client.get(url)
            new_status = "Healthy" if 200 <= response.status_code < 400 else "Unresponsive"
        except httpx.RequestError as e:
            new_status = "Unreachable"
            print(f"[HealthCheck] Ping failed for {module_name}: {e}")
        
        if current_status != new_status:
             print(f"[HealthCheck] Status change for {module_name}: {new_status}")

        self.registered_modules[module_name]["status"] = new_status
        if new_status == "Healthy":
            self.registered_modules[module_name]["last_seen"] = time.time()

    async def start_background_checker(self):
        """The main loop for the proactive health checker background task."""
        print("[HealthCheck] Starting background health checker task...")
        while True:
            await asyncio.sleep(self.check_interval_seconds)
            print("[HealthCheck] Running scheduled health checks...")
            tasks = [self._check_endpoint(name, details["url"]) 
                     for name, details in self.registered_modules.items() if details["type"] == "server"]
            await asyncio.gather(*tasks)

    def get_status(self) -> List[Dict]:
        """Returns the current health status of all registered modules."""
        current_time = time.time()
        for module_name, details in self.registered_modules.items():
            if details["type"] == "event_driven":
                if (current_time - details["last_seen"]) > self.unhealthy_threshold_seconds and details["status"] == "Healthy":
                    details["status"] = "Unhealthy (No Recent Events)"
        
        return [
            {
                "module": name,
                "status": details["status"],
                "last_seen_iso": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(details["last_seen"])) if details["last_seen"] > 0 else "Never"
            } for name, details in self.registered_modules.items()
        ]

health_checker = HealthCheck()