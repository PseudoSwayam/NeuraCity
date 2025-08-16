#!/bin/bash
# -------------------------------------------------------------
# NeuraCity - Core Backend Services Startup Script
# -------------------------------------------------------------
# This script launches all ESSENTIAL backend services required for the
# NeuraCity platform to operate.
#
# Specialized, data-generating modules like CV_Watchtower and IoT_PulseNet
# should be run manually in a separate terminal when needed.

echo "🚀 Starting NeuraCity Core Backend Services..."

# Ensure this script is run from the project's root directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ ERROR: This script must be run from the NeuraCity root directory."
    exit 1
fi

# Activate the virtual environment
source venv/bin/activate

# Function to run a command in a new terminal tab on macOS
run_in_new_tab() {
    # This command navigates to the project root, activates the venv, prints a
    # clear title, and then executes the server command.
    osascript -e "tell application \"Terminal\" to do script \"cd '$(pwd)' && source venv/bin/activate && echo '--- 🛰️ Starting $2 ---' && $1\""
}

# 1. Verify Infrastructure (Redis & PostgreSQL)
if ! docker ps | grep -q "redis-stack-server"; then
    echo "⚠️  Redis container not found. Please start it with 'docker run...'"
else
    echo "✅ Redis is running."
fi
if ! docker ps | grep -q "neuracity-postgres"; then
    echo "⚠️  PostgreSQL container not found. Please start it with 'docker run...'"
else
    echo "✅ PostgreSQL is running."
fi

# 2. Start Core API Services in new tabs
# These are the persistent servers that should always be online.

echo "-> 🚀 Launching UserHub (Identity Service on Port 8005)..."
run_in_new_tab "python3 -m uvicorn modules.userhub.app:app --host 0.0.0.0 --port 8005" "UserHub"
sleep 2

echo "-> 🚀 Launching ReflexSystem (Action Engine on Port 8001)..."
run_in_new_tab "python3 -m uvicorn modules.reflex_system.main:app --host 0.0.0.0 --port 8001" "ReflexSystem"
sleep 2

echo "-> 🚀 Launching Alerts & Notifications (Port 8003)..."
run_in_new_tab "python3 -m uvicorn modules.alerts_and_notifications.main:app --host 0.0.0.0 --port 8003" "Alerts & Notifications"
sleep 2

echo "-> 🚀 Launching InsightCloud (Analytics Service on Port 8002)..."
run_in_new_tab "python3 -m uvicorn modules.insightcloud.app:app --host 0.0.0.0 --port 8002" "InsightCloud"
sleep 2

# 3. Start User-Facing Application Servers
echo "-> 🚀 Launching NeuroMap Server (Frontend Host on Port 8004)..."
run_in_new_tab "python3 -m uvicorn modules.neuromap.server:app --host 0.0.0.0 --port 8004" "NeuroMap"
sleep 2

echo "-> 🚀 Launching NeuraNLP_Agent (Conversational AI on Port 8000)..."
run_in_new_tab "python3 -m uvicorn modules.neuranlp_agent.main:app --host 0.0.0.0 --port 8000" "NeuraNLP_Agent"
sleep 2

echo ""
echo "✅ All NeuraCity CORE backend services have been launched in new terminal tabs!"
echo ""
echo "--------------------------------------------------------------------------------"
echo "  To generate live visual events, run the following in a NEW terminal:"
echo "  source venv/bin/activate"
echo "  python3 -m modules.cv_watchtower.main --mode showcase"
echo "--------------------------------------------------------------------------------"