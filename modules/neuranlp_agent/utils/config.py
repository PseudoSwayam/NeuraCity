import os
from dotenv import load_dotenv
from utils.config_loader import settings

# Correct, robust paths to the documents
DOCUMENT_SOURCES = [
    os.path.join(settings.DOCS_DIR, "campus_faq.txt"),
    os.path.join(settings.DOCS_DIR, "events_schedule.txt")
]

# --- Logging and Server Configuration ---
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
HOST = "0.0.0.0"
PORT = 8000