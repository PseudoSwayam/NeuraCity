# 🧬 MemoryCore

MemoryCore stores vector logs of activity, events, and queries for retrieval.

## 🎯 Goal

Create a searchable memory system that answers:
- “What happened in Lab A on 17 July?”
- “Show last 24h activity near Library”

## 📦 Folder Structure (Recommended)

```bash
memorycore/
├── vector_db/        # ChromaDB, FAISS or similar
├── ingestors/        # Feed from CV, IoT, NLP
├── retrievers/       # APIs to access logs
└── README.md
```

## ✅ Tasks

- [ ] Log all events with timestamp, location, type
- [ ] Create time-based + semantic retrievers
- [ ] Interface with NLP agent and InsightCloud

Please document memory schema, embeddings, and sample logs here.