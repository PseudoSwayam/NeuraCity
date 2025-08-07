# File: memorycore/memory_manager.py
# Unified interface to access all NeuraCity memory systems.

from .structured_memory import StructuredMemory
from .vector_memory import VectorMemory

class MemoryManager:
    """
    The main access point for NeuraCity's memory.
    It intelligently routes requests to the correct backend (Structured or Vector).
    """
    def __init__(self):
        # Initializes both memory types on startup
        self.structured = StructuredMemory()
        self.vector = VectorMemory()

    # Convenience methods can be added here as needed
    def load_external_documents(self, file_paths: list):
        """Helper to load initial knowledge base documents into vector memory."""
        for path in file_paths:
            self.vector.load_document(path)
        

# --- Singleton Accessor ---
_memory_core_instance = None

def get_memory_core():
    """Provides global access to the MemoryManager singleton instance."""
    global _memory_core_instance
    if _memory_core_instance is None:
        _memory_core_instance = MemoryManager()
    return _memory_core_instance