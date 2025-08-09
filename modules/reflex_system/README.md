# Reflex System

> The Action-Execution Engine of the NeuraCity Smart Campus Project

The `reflex_system` is a dedicated microservice that acts as the hands and nervous system of the NeuraCity platform. Its sole responsibility is to receive authenticated commands from other modules (like `neuranlp_agent` and `cv_watchtower`) and execute them as real-world actions.

It is designed to be highly reliable, secure, and decoupled, ensuring that the AI's reasoning is safely translated into concrete, auditable outcomes.

---

## ✨ Core Capabilities

*   **🛡️ Secure Action Endpoints**: Provides a set of well-defined API endpoints (`/api/actions/...`) for critical campus operations.
*   **📡 Event Broadcasting**: Upon successfully executing an action, it publishes a structured event to the central **Redis message bus**. This allows any number of other services (like `InsightCloud` or a live dashboard) to be notified of real-time actions.
*   **✍️ Auditable Logging**: Every action it takes is logged to two places:
    1.  A local, human-readable `system_action_log.txt` file for simple auditing.
    2.  The centralized `MemoryCore` (SQLite) for long-term, structured storage and analysis.
*   **✅ Robust Validation**: Uses `Pydantic` models to strictly validate all incoming requests, ensuring data integrity and preventing malformed commands.
*   **🔬 Independently Testable**: Comes with a suite of `pytest` unit tests to guarantee its logic and API contracts are stable and reliable.

![System Architecture](diagram.svg)

---

## 🛠️ Technology Stack

*   **Backend Framework**: `FastAPI`
*   **Data Validation**: `Pydantic`
*   **Event Publishing**: `Redis` (via the `redis-py` async client)
*   **Logging**: Python's native `logging` + `MemoryCore` integration.

---

## 🏗️ Project Structure

The module is self-contained and follows the clean architecture standard of the NeuraCity project.
```bash
modules/reflex_system/
├── main.py # FastAPI app with all API routes
├── action_handlers.py # The core business logic for each action
├── event_publisher.py # Manages the connection and publishing to Redis
├── models.py # Pydantic models for request validation
└── utils/
  └── logger.py # Centralized logging configuration
```
---

## ▶️ How to Run

The `reflex_system` is designed to be a continuous, standalone service.

1.  **Prerequisites**: Ensure that **Redis** is running (e.g., via Docker) subscribe to its notifications.
    ```bash
    docker run -d --name neura-redis -p 6379:6379 redis/redis-stack-server:latest
    docker exec -it neura-redis redis-cli
      > SUBSCRIBE campus_notifications
    ```
2.  **Activate Environment**: Open a terminal, navigate to the `NeuraCity` project root, and activate the virtual environment (`source venv/bin/activate`).
3.  **Start the neuranlp_agent**: Use the following command to start the GenAi agent. It is configured to run on port `8000`.
    ```bash
    python3 -m uvicorn modules.neuranlp_agent.main:app --host 0.0.0.0 --port 8000 --reload
    ```
4.  **Start the Server**: Use the following robust command to launch the service. It is configured to run on port `8001`.

    ```bash
    python3 -m uvicorn modules.reflex_system.main:app --host 0.0.0.0 --port 8001 --reload
    ```
5.  **Health Check**: You can verify that the service is running by navigating to **`http://localhost:8001/`** in your browser, where you should see an operational status message. The full interactive API documentation is available at **`http://localhost:8001/docs`**.

---

## Perform a Test Query:

In the browser docs for the agent, send a POST /query request that triggers an action:
query: "There is an emergency in the main library, send help immediately."
mode: "text"
You have successfully tested the system when you observe the following:
```
✅ The browser gets a 200 OK success response from the agent.
✅ The neuranlp_agent terminal shows the agent's reasoning process.
✅ The reflex_system terminal shows it received an API call and published an event.
✅ The redis-cli subscriber terminal prints the JSON payload of the event.
✅ Unit Testing
```

This project includes unit tests for the reflex_system to ensure its reliability.
To run the tests:
```bash
# Ensure your (venv) is active and you are in the project root
pytest
```