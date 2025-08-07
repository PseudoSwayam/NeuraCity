# 🧠 MemoryCore: The Centralized Memory of NeuraCity

> The shared, multi-backend memory system for all NeuraCity AI agents and modules.
> Co-created by Swayam and his wife.

---

## 🏛️ Architectural Purpose

`MemoryCore` serves as the long-term, persistent brain for the entire NeuraCity smart campus platform. It is designed to be a universal, centralized service that any module (like `neuranlp_agent` or `reflex_system`) can use to store and retrieve information.

This centralized approach prevents data silos, ensures a single source of truth, and allows for emergent, intelligent behaviors as different agents can learn from each other's recorded experiences.

## ✨ Core Features

*   **🧠 Dual-Backend Design**: Combines two distinct types of memory to handle different data needs:
    *   **Vector Memory (`ChromaDB`)**: Used for storing and retrieving information based on semantic meaning and similarity. Perfect for conversations, documents, and unstructured knowledge.
    *   **Structured Memory (`SQLite`)**: Used for storing and retrieving discrete, timestamped events. Perfect for creating a searchable, auditable log of actions and sensor readings.
*   **🧩 Unified & Simple Interface**: Provides a single `MemoryManager` class as an access point. This abstraction allows other modules to interact with "memory" without needing to know the complex details of the underlying databases.
*   **✔️ Singleton Pattern**: Ensures that only one instance of the database connections is created, guaranteeing efficient and safe access across the entire application.
*   **📚 Document Ingestion**: Capable of loading external text documents (like campus FAQs) directly into the vector memory to bootstrap the platform's knowledge base.
*   **Scalable by Design**: Built to be independent and persistent. The underlying databases can be scaled or migrated without requiring changes to the agent modules that rely on them.

---

## 🛠️ Technology Stack

*   **Vector Memory**: `ChromaDB` for state-of-the-art semantic search.
*   **Structured Memory**: `SQLite` for a lightweight, file-based, and universally compatible event log.
*   **Embeddings**: `Sentence Transformers` (via `chromadb.utils.embedding_functions`).

---

## 🏗️ Project Structure

The module is self-contained within the `memorycore` directory at the project root.
```bash
NeuraCity/
└── memorycore/
├── init.py # Makes memorycore a Python package
├── memory_manager.py # The unified public interface for all other modules
├── structured_memory.py # Internal handler for SQLite (events)
├── vector_memory.py # Internal handler for ChromaDB (knowledge)
└── dbs/ # Secure location for the database files
    ├── structured/
    └── vector/
```

---

## 📖 How to Use `MemoryCore` in Other Modules

`MemoryCore` is designed to be used as a simple, imported utility. All interactions are handled through a global "getter" function.

### 1. Getting an Instance of the Memory Core

In any other module (e.g., `some_agent.py`), import and call the singleton accessor:

```python
# Import the getter function from the memorycore
from memorycore.memory_manager import get_memory_core

# Get the single, shared instance of the memory manager
memory = get_memory_core()
2. Using the Vector Memory (for AI Agents)
Ideal for storing and retrieving conversational context or knowledge.
```

Adding a memory:

```bash
# Create the text to be embedded and some metadata
convo_text = "User said: 'Where is the library?' | Agent responded: 'It is in the main plaza.'"
metadata = {"user_id": "user123"}

# Use the .vector property to access ChromaDB functions
memory.vector.add(
    source='neuranlp_agent', 
    type='conversation',
    text_content=convo_text,
    metadata=metadata
)
```

Querying for similar memories:

```
# The agent needs to find information related to a new query
user_query = "How do I get to the main library?"

# The .vector.query function returns a list of semantically similar text strings
similar_memories = memory.vector.query(user_query, top_k=3)

# >> similar_memories might contain: 
# >> ["User said: 'Where is the library?' | Agent responded: 'It is in the main plaza.'", ...]```
```

### 3. Using the Structured Memory (for Action/Event Systems)

Ideal for creating a chronological, auditable log of important events.

#### Adding an event:

```python
# Define the structured details of the event
event_details = {
    "location": "Main Gate",
    "status": "dispatched",
    "priority": "high"
}

# Use the .structured property to access SQLite functions
memory.structured.add(
    source='reflex_system',
    type='security_alert',
    details_dict=event_details
)
```

Note: Querying the structured memory is done via standard sqlite3 tools for direct, auditable access, as demonstrated in the project's testing guides.

---

🚀 Future Extensibility
- Backend Migration: To scale, the structured_memory.py could be updated to connect to a production database like PostgreSQL, or vector_memory.py could connect to a cloud-native vector DB. No changes would be needed in the agent modules.
- Advanced Queries: New methods can be added to MemoryManager to support more complex cross-database queries, such as "Find all conversations that happened just before a security alert at the library."
- API Layer: The MemoryCore can easily be exposed via its own FastAPI server, turning it into a fully-fledged, standalone microservice if the need arises.
