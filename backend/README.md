# NeuraCity Backend Orchestration Hub

This directory contains the tools and documentation for running the complete NeuraCity backend platform.

---

## 🚀 One-Step Backend Launch

This is the fastest and most reliable way to get the entire NeuraCity backend running for development or a live demo.

### Prerequisites

1.  **Docker Desktop** is installed and running.
2.  Your project's Python virtual environment (`venv`) has been created and all dependencies from the root `requirements.txt` have been installed.
3.  Your root `.env` file is correctly configured with all necessary API keys and secrets.
4.  You have built the `NeuroMap` frontend by running `npm run build` inside `modules/neuromap/frontend/`.

### Launch Command

From the **NeuraCity project root directory**, run the following single command:

```bash
# First, ensure the script is executable (only needed once)
chmod +x backend/run_all_services.sh

# Now, run the script
./backend/run_all_services.sh
This script will automatically open a new, named terminal tab for each of the core backend microservices, creating a complete, running instance of the NeuraCity platform.
```

---

### 🛠️ Individual Service Guide
The run_all_services.sh script launches the following independent modules. You can also run them manually for isolated debugging. All commands should be run from the project root with your (venv) active.


|    Module     |	Default Port |	                        Manual Startup Command	Purpose                                            |
|---------------|--------------|-----------------------------------------------------------------------------------------------------|
|UserHub	      |    8005      |	python3 -m uvicorn modules.userhub.app:app --port 8005	Identity & Auth                            |
|ReflexSystem	  |    8001      |	python3 -m uvicorn modules.reflex_system.main:app --port 8001	Action Engine                        |
|Alerts & Notifs|	   8003	     |  python3 -m uvicorn modules.alerts_and_notifications.main:app --port 8003	Notification Dispatcher  |
|InsightCloud	  |    8002      |	python3 -m uvicorn modules.insightcloud.app:app --port 8002	Analytics & Health                     |
|NeuraNLP_Agent |	   8000      |	python3 -m uvicorn modules.neuranlp_agent.main:app --port 8000	Conversational AI                  |
|NeuroMap	      |    8004      |	python3 -m uvicorn modules.neuromap.server:app --port 8004	Frontend Host                          |

---

## 🔗 Key API Endpoints for Frontend Integration
## The frontend (Admin Panel, NeuraApp) will primarily interact with these endpoints:

### Authentication: POST http://localhost:8005/auth/token
  (The entry point for logging in. Returns a JWT token.)
  
### Conversational AI: POST http://localhost:8000/query
  (The main endpoint for sending user queries to the neuranlp_agent. Requires a Bearer <token> in the Authorization header for protected actions.)
  
### Live Alerts (WebSocket): ws://localhost:8003/ws/alerts?token=<JWT_TOKEN
  (The real-time WebSocket for the NeuroMap and dashboards. Requires a valid user token to connect.)
  
### Analytics & Health: GET http://localhost:8002/stats/...

The family of endpoints from InsightCloud for populating charts and status indicators on the dashboard. Most of these require an admin-level JWT token.
For detailed information on each module, please refer to the README.md inside its respective directory in /modules.
