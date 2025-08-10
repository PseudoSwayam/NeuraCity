# File: utils/config_loader.py
# The single source of truth for all configuration across the NeuraCity project.

import os
from dotenv import load_dotenv

class ConfigLoader:
    """
    Loads all project-wide configuration from the root .env file and
    provides default values, making settings accessible to all modules.
    """
    def __init__(self):
        # Find the project root by going one level up from this file's directory (utils/)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        dotenv_path = os.path.join(project_root, '.env')
        
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path=dotenv_path)
            print("[ConfigLoader] SUCCESS: .env file loaded successfully from project root.")
        else:
            print("[ConfigLoader] WARNING: .env file not found. Relying on system environment variables.")

        # --- API Keys & Secrets ---
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

        # --- Service URLs & Ports ---
        self.NEURANLP_AGENT_HOST = os.getenv("NEURANLP_AGENT_HOST", "http://localhost:8000")
        self.REFLEX_SYSTEM_HOST = os.getenv("REFLEX_SYSTEM_HOST", "http://localhost:8001")
        self.INSIGHTCLOUD_HOST = os.getenv("INSIGHTCLOUD_HOST", "http://localhost:8002")
        self.ALERTS_SERVICE_HOST = os.getenv("ALERTS_SERVICE_HOST", "http://localhost:8003")

        # Specific API endpoints derived from the host URLs
        self.REFLEX_API_BASE_URL = f"{self.REFLEX_SYSTEM_HOST}/api"

        # --- Webhook URL ---
        self.WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://webhook.site/adb60c2d-1eec-4edf-9eaa-5600bd8bc563")

        # --- Infrastructure Configuration ---
        self.REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
        self.REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
        self.REDIS_EVENT_CHANNEL = os.getenv("REDIS_EVENT_CHANNEL", "campus_notifications")

        # --- LLM & AI Model Configuration ---
        self.OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
        
        # --- File Paths ---
        self.PROJECT_ROOT_DIR = project_root
        self.DOCS_DIR = os.path.join(self.PROJECT_ROOT_DIR, "docs")
        self.VIDEOS_DIR = os.path.join(self.PROJECT_ROOT_DIR, "videos")
        
        # --- cv_watchtower Specific Settings ---
        # Note: We keep these in the central config for easier management.
        self.YOLO_MODEL_PATH = "modules/cv_watchtower/models/yolov8n.pt"
        self.DETECTION_CONFIDENCE_THRESHOLD = 0.4
        
# --- Singleton Instance ---
# This ensures the .env file is loaded only once and all modules share the exact same settings object.
settings = ConfigLoader()