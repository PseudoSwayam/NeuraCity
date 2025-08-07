import os
from dotenv import load_dotenv

load_dotenv()

# Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Ollama Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")

# Reflex System API Configuration
REFLEX_API_BASE_URL = os.getenv("REFLEX_API_BASE_URL", "http://localhost:8001/api")

# Voice Handler Configuration
TTS_ENGINE = os.getenv("TTS_ENGINE", "pyttsx3") # or "gTTS"

# Memory Configuration
VECTOR_DB_PATH = "./modules/neuranlp_agent/memory/vectordb"
DOCUMENT_SOURCES = ["./docs/campus_faq.txt", "./docs/events_schedule.txt"] # Example document paths

# Logging Configuration
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")

# Server Configuration
HOST = "0.0.0.0"
PORT = 8000