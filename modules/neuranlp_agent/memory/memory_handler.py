import chromadb
from chromadb.utils import embedding_functions
from ..utils import config
import logging

logging.basicConfig(level=config.LOGGING_LEVEL)

class MemoryHandler:
    def __init__(self, db_path=config.VECTOR_DB_PATH):
        self.client = chromadb.PersistentClient(path=db_path)
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name="neuranlp_memory",
            embedding_function=self.embedding_function
        )

    def store_interaction(self, query: str, response: str):
        """Stores a query-response pair in the vector database."""
        try:
            self.collection.add(
                documents=[f"User query: {query}\nAI response: {response}"],
                ids=[str(hash(query + response))]
            )
            logging.info("Stored interaction in memory.")
        except Exception as e:
            logging.error(f"Failed to store interaction: {e}")

    def retrieve_memory(self, query: str, top_k: int = 3):
        """Retrieves the top-k most similar interactions from memory."""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k
            )
            logging.info(f"Retrieved {len(results['documents'][0])} memories.")
            return results['documents'][0]
        except Exception as e:
            logging.error(f"Failed to retrieve memory: {e}")
            return []

    def load_documents(self, doc_paths: list):
        """Loads and indexes documents from a list of file paths."""
        for doc_path in doc_paths:
            try:
                with open(doc_path, 'r') as f:
                    content = f.read()
                    # Simple chunking by paragraph
                    chunks = content.split('\n\n')
                    self.collection.add(
                        documents=chunks,
                        ids=[str(hash(chunk)) for chunk in chunks]
                    )
                logging.info(f"Loaded and indexed document: {doc_path}")
            except Exception as e:
                logging.error(f"Failed to load document {doc_path}: {e}")

# Initialize and load documents
memory_handler = MemoryHandler()
memory_handler.load_documents(config.DOCUMENT_SOURCES)