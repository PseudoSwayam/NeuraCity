# 🧠 NeuraNLP Agent

The GenAI + NLP module for handling user queries and triggering internal actions.

## 🎯 Goal

Build a LangChain-based chatbot that:
- Answers institutional questions (“Where’s Prof. X?”)
- Retrieves internal schedules, logs, or maps
- Optionally speaks back using TTS
- Triggers alerts or automation based on queries

## 📦 Folder Structure (Recommended)

```bash
neuranlp_agent/
├── agents/           # LangChain or OpenAI agents
├── prompts/          # System + user prompts
├── tools/            # Custom tools (e.g., DB search, API trigger)
└── README.md
```

## ✅ Tasks

- [ ] Set up local LLM or API (Ollama, OpenAI, Gemini)
- [ ] Build LangChain agent + tools
- [ ] Integrate with userhub, memorycore, reflex system

Add usage examples, endpoint info, and agent behavior details here as you progress.