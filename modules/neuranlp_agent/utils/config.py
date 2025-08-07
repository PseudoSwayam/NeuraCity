import os
from dotenv import load_dotenv

load_dotenv()

# --- Absolute Path Configuration ---
# This makes file paths robust, regardless of where the script is run from.
# It assumes 'config.py' is in '.../neuranlp_agent/utils/'
UTILS_DIR = os.path.dirname(os.path.abspath(__file__))
AGENT_ROOT_DIR = os.path.dirname(UTILS_DIR)
MODULES_DIR = os.path.dirname(AGENT_ROOT_DIR)
PROJECT_ROOT_DIR = os.path.dirname(MODULES_DIR)


# --- API and Model Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
REFLEX_API_BASE_URL = os.getenv("REFLEX_API_BASE_URL", "http://localhost:8001/api")

# --- Voice and Memory Configuration ---
TTS_ENGINE = os.getenv("TTS_ENGINE", "pyttsx3")
VECTOR_DB_PATH = os.path.join(AGENT_ROOT_DIR, "memory", "vectordb")

# Correct, robust paths to the documents
DOC_1 = os.path.join(PROJECT_ROOT_DIR, "docs", "campus_faq.txt")
DOC_2 = os.path.join(PROJECT_ROOT_DIR, "docs", "events_schedule.txt")
DOCUMENT_SOURCES = [DOC_1, DOC_2]

# --- Logging and Server Configuration ---
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
HOST = "0.0.0.0"
PORT = 8000