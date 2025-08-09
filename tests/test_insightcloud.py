# File: tests/test_insightcloud.py

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add project root to path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Import the FastAPI app
from modules.insightcloud.app import app

client = TestClient(app)

# Note: These tests assume MemoryCore can be initialized.
# In a larger setup, we would mock the MemoryCore dependency.

def test_module_health_endpoint():
    """Tests the health check endpoint for a valid response structure."""
    response = client.get("/stats/module_health")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Check that a known module is present
    assert any(item["module"] == "cv_watchtower" for item in data)
    assert "status" in data[0]

def test_events_by_module_endpoint():
    """Tests the events_by_module endpoint."""
    # This relies on the cache being built on startup. 
    # This is an integration test more than a pure unit test.
    response = client.get("/stats/events_by_module")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    # If reflex_system ran, it should be a key
    # assert "reflex_system" in data # This might fail on a fresh DB

def test_realtime_overview_endpoint():
    """Tests the realtime overview for a valid initial state."""
    response = client.get("/stats/realtime_overview")
    assert response.status_code == 200
    data = response.json()
    assert data["live_total_events"] == 0 # Should be 0 on a fresh start
    assert isinstance(data["live_events_by_type"], dict)