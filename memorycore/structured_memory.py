# File: memorycore/structured_memory.py

import sqlite3
import json
import datetime
from typing import List, Dict, Any
import logging
import os

logger = logging.getLogger(__name__)

DB_PATH = 'memorycore/dbs/structured/neuracity_events.db'

class StructuredMemory:
    """Manages the SQLite database for structured event logging."""
    def __init__(self, db_path: str = DB_PATH):
        # Ensure the directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        logger.info("[MemoryCore-Structured] Initializing SQLite connection...")
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_table()
        logger.info(f"[MemoryCore-Structured] Connected to SQLite DB at '{db_path}'.")
        
    def _create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                source TEXT NOT NULL,
                type TEXT NOT NULL,
                details TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def add(self, source: str, type: str, details_dict: Dict[str, Any]):
        """Adds a new structured event to the database."""
        cursor = self.conn.cursor()
        timestamp = datetime.datetime.now().isoformat()
        details_json = json.dumps(details_dict)
        
        cursor.execute(
            "INSERT INTO events (timestamp, source, type, details) VALUES (?, ?, ?, ?)",
            (timestamp, source, type, details_json)
        )
        self.conn.commit()
        logger.info(f"[MemoryCore-Structured] Added structured event from '{source}'.")

    # --- THIS IS THE ONLY ADDITION ---
    # This new method is required by the `insightcloud` module to build its
    # analytics cache. It does not change any of your existing, working code.
    def get_recent_events(self, n: int = 1000) -> List[sqlite3.Row]:
        """
        Retrieves the 'n' most recent events from the database.
        
        Args:
            n (int): The maximum number of events to return.
            
        Returns:
            A list of sqlite3.Row objects, which behave like dictionaries.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM events ORDER BY timestamp DESC LIMIT ?", (n,))
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"[MemoryCore-Structured] Failed to get recent events: {e}")
            return []
    # --- END ADDITION ---