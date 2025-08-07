# File: memorycore/vector_memory.py
# Handles all ChromaDB (Vector) memory operations.

import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any
import logging

# Configure logger for this specific component
logger = logging.getLogger(__name__)

DB_PATH = 'memorycore/dbs/vector'
COLLECTION_NAME = "neuracity_vector_memory"

class VectorMemory:
    """Manages the ChromaDB instance for semantic search."""
    def __init__(self, db_path: str = DB_PATH):
        logger.info("[MemoryCore-Vector] Initializing ChromaDB client...")
        self.client = chromadb.PersistentClient(path=db_path)
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=self.embedding_function
        )
        logger.info(f"[MemoryCore-Vector] Connected to ChromaDB collection '{COLLECTION_NAME}'.")

    def add(self, source: str, type: str, text_content: str, metadata: Dict[str, Any]):
        """Adds a new document to the vector database."""
        metadata.update({'source': source, 'type': type})
        unique_id = str(hash(text_content))
        try:
            self.collection.add(
                documents=[text_content],
                metadatas=[metadata],
                ids=[unique_id]
            )
            logger.info(f"[MemoryCore-Vector] Added vector memory from '{source}'.")
        except Exception as e:
            logger.error(f"Failed to add vector memory: {e}")

    def query(self, query_text: str, top_k: int = 3) -> List[str]:
        """Queries for semantically similar documents."""
        try:
            results = self.collection.query(query_texts=[query_text], n_results=top_k)
            return results.get('documents', [[]])[0]
        except Exception as e:
            logger.error(f"Failed to query vector memory: {e}")
            return []

    def load_document(self, file_path: str):
        """Loads and indexes a text file, chunking by paragraph."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                chunks = [chunk for chunk in content.split('\n\n') if chunk.strip()]
                if not chunks: return
                
                self.collection.add(
                    documents=chunks,
                    ids=[str(hash(chunk)) for chunk in chunks]
                )
            logger.info(f"[MemoryCore-Vector] Successfully loaded and indexed document: {file_path}")
        except FileNotFoundError:
             logger.warning(f"[MemoryCore-Vector] Document not found at {file_path}. Skipping.")
        except Exception as e:
            logger.error(f"Failed to load document {file_path}: {e}")