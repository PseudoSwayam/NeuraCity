# File: tests/test_reflex_system.py

import pytest
import sys
import os

# --- THIS IS THE CRUCIAL FIX for PATH ---
# Adds the project's root directory to the Python path.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
# ----------------------------------------

# --- THIS IS THE CRUCIAL FIX for TESTING ---
# Import the specialized TestClient from FastAPI. It's designed to work with FastAPI apps.
from fastapi.testclient import TestClient
# -----------------------------------------

# Import your FastAPI app object
from modules.reflex_system.main import app

# Create a client instance using the TestClient. This is the new way.
client = TestClient(app)

def test_health_check():
    """Tests the root health check endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ReflexSystem API is operational."}

def test_call_security_success():
    """Tests the /api/actions/call_security endpoint with valid data."""
    payload = {"location": "Main Library"}
    response = client.post("/api/actions/call_security", json=payload)
    
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == "success"
    assert "Main Library" in json_response["message"]

def test_call_security_validation_error():
    """Tests that the API correctly rejects invalid data (e.g., a too-short location)."""
    payload = {"location": "a"}  # Invalid payload, less than 3 characters
    response = client.post("/api/actions/call_security", json=payload)
    
    # A 422 error code means "Unprocessable Entity," which is FastAPI's validation error.
    assert response.status_code == 422