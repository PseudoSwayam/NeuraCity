# File: modules/neuromap/server.py

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import httpx
import sys
import os

# Ensure the project root is in the path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from utils.config_loader import settings

# This dictionary acts as a simple in-memory cache for the service token.
token_cache = {"access_token": None}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """On startup, this will automatically log in to UserHub to get a service token."""
    print("[NeuroMap Server] Starting up and authenticating as a system service...")
    auth_url = f"{settings.USERHUB_HOST}/auth/token"
    credentials = {
        "username": settings.SYSTEM_ADMIN_EMAIL,
        "password": settings.SYSTEM_ADMIN_PASSWORD
    }
    
    if not all(credentials.values()):
        print("❌ FATAL: System admin credentials not found in .env file.")
    else:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(auth_url, data=credentials, timeout=10)
                response.raise_for_status()
                token_cache["access_token"] = response.json()["access_token"]
                print("✅ [NeuroMap Server] Successfully authenticated with UserHub.")
        except httpx.RequestError as e:
            print(f"❌ FATAL: Could not authenticate NeuroMap with UserHub on startup. {e}")
    
    yield
    print("[NeuroMap Server] Shutting down.")


app = FastAPI(
    title="NeuraCity NeuroMap Host",
    description="Serves the interactive map interface and provides secure WebSocket tokens.",
    lifespan=lifespan
)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)


@app.get("/api/get-websocket-token", response_class=JSONResponse)
async def get_websocket_token():
    """A secure endpoint for the frontend to fetch the service token."""
    if token_cache["access_token"]:
        return {"token": token_cache["access_token"]}
    else:
        return JSONResponse(status_code=503, content={"error": "Service Unavailable: Auth token not ready."})

# --- Static file serving logic ---
frontend_path = os.path.join(os.path.dirname(__file__), "frontend", "dist")

@app.get("/{catchall:path}")
async def serve_spa(request: Request, catchall: str):
    static_file_path = os.path.join(frontend_path, catchall)
    if os.path.isfile(static_file_path):
        return FileResponse(static_file_path)
    return FileResponse(os.path.join(frontend_path, 'index.html'))