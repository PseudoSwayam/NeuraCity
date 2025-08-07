# 🧠 NeuraNLP Agent

> The AI Brain of the NeuraCity Smart Campus Project

The `neuranlp_agent` is a modular, multi-modal, API-first AI assistant. It serves as the primary natural language processing interface for students and staff, capable of answering queries, understanding context, and triggering real-world actions through the NeuraCity ecosystem.

---

## ✨ Core Features

*   **🗣️ Natural Language Queries**: Responds to a wide range of campus-related questions using a powerful Large Language Model.
*   **🔊 Multimodal Interaction**: Supports both **text** and **voice** inputs (Speech-to-Text via Whisper) and outputs (Text-to-Speech via gTTS).
*   **🧠 Intelligent Action Triggering**: Can reason about user requests and call external APIs to perform real-world actions, such as dispatching security or sending announcements, with a built-in safety confirmation step.
*   **✅ High Resilience**: Uses the **Google Gemini API** as its primary LLM, with a seamless, automatic **fallback to a local Ollama-Mistral instance** if the cloud API is unavailable.
*   **📚 Persistent Memory**: Utilizes a `ChromaDB` vector store to remember past conversations and retrieve information from indexed campus documents (e.g., FAQs, event schedules), ensuring contextual and accurate responses.
*   **🚀 Scalable & Performant**: Built with FastAPI and designed with modern best practices like lazy loading of AI models and non-blocking TTS to ensure a responsive and scalable API.

---

## 🛠️ Technology Stack

*   **Backend Framework**: `FastAPI`
*   **AI Orchestration**: `LangChain`
*   **Primary LLM**: Google Gemini (`gemini-1.0-pro`)
*   **Fallback LLM**: Ollama (`mistral`)
*   **Vector Database**: `ChromaDB`
*   **Speech-to-Text**: `OpenAI Whisper`
*   **Text-to-Speech**: `gTTS` (Google Text-to-Speech)
*   **Audio Processing**: `pydub`

---

## 🏗️ Project Structure

```bash
The module is designed for clarity, separation of concerns, and ease of maintenance.
NeuraCity/
├── docs/ # Place documents for memory here
│ ├── campus_faq.txt
│ └── events_schedule.txt
└── modules/
└── neuranlp_agent/
├── main.py # FastAPI application and endpoints
├── agent_core.py # Core LangChain agent logic & LLM handling
├── voice_handler.py # Handles STT and TTS
├── memory/
│ └── memory_handler.py# Manages ChromaDB storage and retrieval
├── utils/
│ ├── api_triggers.py # Functions to call the ReflexSystem API
│ └── config.py # Centralized configuration
├── prompts/
│ └── base_prompt.txt # Defines the agent's persona
├── requirements.txt # All Python dependencies
└── README.md # This file
```

---

## ⚙️ Setup and Installation

Follow these steps to get the agent running locally.

### 1. Prerequisites

*   Python 3.9+
*   An active Google AI Studio API key for Gemini.
*   (Optional, for fallback) [Ollama](https://ollama.com/) installed and running with the `mistral` model (`ollama pull mistral`).

### 2. Initial Setup

Navigate to the project's root `NeuraCity` directory and set up the Python virtual environment.

```bash
# 1. Go to the project root directory
cd /path/to/your/NeuraCity

# 2. Create a virtual environment
python3 -m venv venv

# 3. Activate the environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# 4. Install all required packages
pip install -r requirements.txt
```

### 3. Environment Variables
Create a .env file in the NeuraCity root directory. Populate it with your API key and other optional settings.

.env file:

```bash
# REQUIRED: Your Google AI Studio API key
GEMINI_API_KEY="your_google_api_key_here"

# Set this to avoid warnings from the tokenizer library in a server environment
TOKENIZERS_PARALLELISM=false

# OPTIONAL: Only change if your local services run on different ports
# OLLAMA_BASE_URL="http://localhost:11434"
# REFLEX_API_BASE_URL="http://localhost:8001/api"
```

### 4. Prepare Memory Documents
The agent can ingest text documents to build its knowledge base.

Ensure the docs/ directory exists in the NeuraCity root.
Place relevant .txt files inside, such as campus_faq.txt and events_schedule.txt. The paths are configured in utils/config.py.
---

▶️ Running the Application
For local development, you need three terminals running simultaneously.

Terminal 1: Start Redis 
Redis acts as our high-speed message broker for events.
```bash
# This command will run a Redis container in the background
docker run -d --name redis-stack-server -p 6379:6379 redis/redis-stack-server:latest
```

Terminal 2: Start the ReflexSystem
This is the production-ready microservice that handles real-world actions.
```bash
# In your NeuraCity root directory, with (venv) active
python3 -m uvicorn modules.reflex_system.main:app --host 0.0.0.0 --port 8001 --reload
```
The reflex_system is now running at http://localhost:8001.

Terminal 3: Start the NeuraNLP Agent
This is the main application server for our agent.
```bash
# In your NeuraCity root directory, with (venv) active
python3 -m uvicorn modules.neuranlp_agent.main:app --host 0.0.0.0 --port 8000 --reload
```

The agent is now live. You can view the interactive API documentation at http://localhost:8000/docs.

---

## 📖 API Usage & Examples
The primary endpoint is POST /query. It accepts multipart/form-data.

Parameters

|Name	  |  Type	  |    Data Type	      |                        Description                               |
|-------|---------|---------------------|------------------------------------------------------------------|
|query	|  Form	  |  string	Required.   | The user's text query or a placeholder if mode is voice.         |
|mode	  |  Form	  |  string	Required.   | Either "text" or "voice". Defaults to "text".                    |
|file	  |  File	  |  binary	Optional.   | The audio file (.mp3, .wav, etc.) is required if mode is "voice".|


Example 1: Text Query (Information Retrieval)

```bash
curl -X 'POST' \
  'http://localhost:8000/query' \
  -H 'Content-Type: multipart/form-data' \
  -F 'query=Where is Professor Sharma’s office?' \
  -F 'mode=text'
```
Successful Response (200 OK):

```json
{
  "response": "Professor Sharma's office is in the Engineering building, room 301.",
  "source": "gemini",
  "audio_output": null
}
```
Example 2: Voice Query (STT + TTS)

```bash
curl -X 'POST' \
  'http://localhost:8000/query' \
  -H 'Content-Type: multipart/form-data' \
  -F 'query=voice request' \
  -F 'mode=voice' \
  -F 'file=@/path/to/your/audio.mp3'
Successful Response (200 OK):
```

```json
{
  "response": "The AI Club is hosting a workshop on Large Language Models today at 3 PM in the main auditorium.",
  "source": "gemini",
  "audio_output": "BASE64_ENCODED_AUDIO_STRING..."
}
```
---

## 🏛️ Architectural Highlights
- **Decoupled & Modular:** All components (agent, memory, actions) are self-contained. The agent communicates with the ReflexSystem and MobileApp via APIs, allowing them to be developed, deployed, and scaled independently.
- **Lazy Loading:** Heavy AI models like OpenAI Whisper are loaded "lazily" (on the first request) rather than on server startup. This prevents crashes in forked server environments and improves startup time.
- **Production-Ready TTS:** The system uses gTTS, a fast, non-blocking library that generates audio in-memory, ensuring the API remains responsive during voice generation.

---

## 🚀 Future Extensions
This module was built with extensibility in mind. Potential future features include:
- 📸 Multi-modal Inputs: Accepting image-based queries (e.g., "Where is this building?").
- 🏷️ Intent Classification: A lightweight model to quickly classify user intent for faster routing to API triggers without full LLM reasoning.
- 🌍 Contextual Awareness: Incorporating time, date, and user location for more relevant, personalized responses.
