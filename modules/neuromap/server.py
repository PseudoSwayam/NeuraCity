# File: modules/neuromap/server.py
# Hosts the NeuraCity NeuroMap frontend application.

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI(
    title="NeuraCity NeuroMap Host",
    description="Serves the interactive map interface for the NeuraCity platform.",
)

# --- Mount the Static Frontend Files ---
# This tells FastAPI to serve the built Vue.js application.
# The 'dist' directory will be created when you run 'npm run build' in the frontend.
static_files_path = os.path.join(os.path.dirname(__file__), "frontend", "dist")

if not os.path.exists(static_files_path):
    print("\n" + "="*50)
    print("FATAL ERROR: The 'frontend/dist' directory was not found.")
    print("Please build the Vue.js application first by running the following commands:")
    print("1. cd modules/neuromap/frontend")
    print("2. npm install")
    print("3. npm run build")
    print("="*50 + "\n")
else:
    app.mount("/assets", StaticFiles(directory=os.path.join(static_files_path, "assets")), name="assets")

    @app.get("/")
    async def read_root():
        """Serves the main index.html of the frontend application."""
        return FileResponse(os.path.join(static_files_path, 'index.html'))

    # This catch-all is important for single-page applications (SPAs) like Vue
    @app.get("/{catchall:path}")
    def serve_spa(catchall: str):
        """Redirects all other paths to the index.html for the SPA to handle routing."""
        return FileResponse(os.path.join(static_files_path, 'index.html'))

# To run this server:
# python3 -m uvicorn modules.neuromap.server:app --host 0.0.0.0 --port 8004 --reload