# File: memorycore/structured_memory.py
# Handles all SQLite (Structured) memory operations.

import sqlite3
import json
import datetime
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

DB_PATH = 'memorycore/dbs/structured/neuracity_events.db'

class StructuredMemory:
    """Manages the SQLite database for structured event logging."""
    def __init__(self, db_path: str = DB_PATH):
        import os
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