# File: modules/insightcloud/healthcheck.py

import time
import asyncio
import httpx # httpx is a modern, async-ready HTTP client
from typing import Dict, List

class HealthCheck:
    """
    Proactively tracks the health of all NeuraCity modules by polling their health endpoints.
    This is a much more robust and decoupled approach.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(HealthCheck, cls).__new__(cls)
            # --- MODIFIED: Define module endpoints here ---
            cls.registered_modules: Dict[str, dict] = {
                'neuranlp_agent': {
                    "health_url": "http://localhost:8000/health",
                    "last_seen": 0, "status": "Unknown"
                },
                'reflex_system': {
                    "health_url": "http://localhost:8001/", # Root URL works as health check
                    "last_seen": 0, "status": "Unknown"
                },
                'insightcloud': { # The service can check itself
                    "health_url": "http://localhost:8002/docs", # An easy way to check if the server is up
                    "last_seen": 0, "status": "Unknown"
                },
                'cv_watchtower': {
                    # This module is a script, not a server. We will ping it based on Redis events.
                    "health_url": None, 
                    "last_seen": 0, "status": "Unknown"
                },
                'iot_pulsenet': {
                    "health_url": None, # Future IoT service will also use Redis events
                    "last_seen": 0, "status": "Unknown"
                }
            }
            cls.check_interval_seconds = 30 # Check every 30 seconds
            cls.unhealthy_threshold_seconds = 65
        return cls._instance

    def ping_from_event(self, module_name: str):
        """Allows event-driven updates for non-server modules like cv_watchtower."""
        if module_name in self.registered_modules:
            module = self.registered_modules[module_name]
            module["last_seen"] = time.time()
            module["status"] = "Healthy"

    async def _check_endpoint(self, module_name: str, url: str):
        """Asynchronously checks a single module's health endpoint."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
            
            if 200 <= response.status_code < 300:
                self.registered_modules[module_name]["status"] = "Healthy"
                self.registered_modules[module_name]["last_seen"] = time.time()
                print(f"[HealthCheck] Ping successful for {module_name}")
            else:
                self.registered_modules[module_name]["status"] = "Unhealthy"
        except httpx.RequestError:
            self.registered_modules[module_name]["status"] = "Unhealthy"

    async def start_background_checker(self):
        """Starts a continuous loop to check module health in the background."""
        print("[HealthCheck] Starting background health checker task...")
        while True:
            for module, details in self.registered_modules.items():
                if details["health_url"]: # Only check modules that have a URL
                    await self._check_endpoint(module, details["health_url"])
            await asyncio.sleep(self.check_interval_seconds)

    def get_status(self) -> List[Dict]:
        """Returns the current health status of all registered modules."""
        current_time = time.time()
        status_list = []
        for module, details in self.registered_modules.items():
            # For server modules, their own check determines status.
            # For event-driven modules, we check the last time we saw an event from them.
            if not details["health_url"] and (current_time - details["last_seen"]) > self.unhealthy_threshold_seconds:
                 details["status"] = "Unhealthy"
                 
            status_list.append({
                "module": module,
                "status": details["status"],
                "last_seen_iso": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(details["last_seen"])) if details["last_seen"] > 0 else "Never"
            })
        return status_list

health_checker = HealthCheck()