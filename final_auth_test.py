# File: final_auth_test.py

import requests
import json

# --- CONFIGURATION ---
USERHUB_URL = "http://localhost:8005"
NEURANLP_AGENT_URL = "http://localhost:8000"

# --- Use the credentials for the ADMIN/SUPERADMIN user you created ---
ADMIN_EMAIL = "admin_email"
ADMIN_PASSWORD = "admin_password"

def run_test():
    """Performs the full, authenticated end-to-end test."""
    print("--- 🚀 Starting Final NeuraCity Integration Test ---")

    # 1. AUTHENTICATE with UserHub to get a token
    print(f"\n[Step 1] Authenticating as admin user '{ADMIN_EMAIL}'...")
    token_payload = {
        'username': ADMIN_EMAIL,
        'password': ADMIN_PASSWORD
    }
    try:
        response = requests.post(f"{USERHUB_URL}/auth/token", data=token_payload)
        response.raise_for_status()
        token_data = response.json()
        access_token = token_data['access_token']
        print("✅ SUCCESS: Authentication successful. Received JWT token.")
    except requests.exceptions.RequestException as e:
        print(f"❌ FATAL ERROR: Could not authenticate with UserHub. {e}")
        return

    # 2. MAKE A SECURE, AUTHENTICATED QUERY to the NeuraNLP Agent
    print("\n[Step 2] Sending secure query to NeuraNLP Agent...")
    
    # --- THIS IS THE DEFINITIVE FIX ---
    # We construct the headers with the "Bearer" token.
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    # For multipart/form-data without an actual file, we use the 'data' parameter.
    # This correctly formats the request for FastAPI.
    form_data = {
        'query': 'What is the current system status?',
        'mode': 'text'
    }
    # --- END FIX ---

    try:
        # Use 'data' instead of 'files' for simple form fields
        response = requests.post(f"{NEURANLP_AGENT_URL}/query", headers=headers, data=form_data)
        response.raise_for_status()
        agent_response = response.json()
        
        print("\n--- ✅ FINAL TEST SUCCESSFUL ---")
        print("Agent's Response:")
        print(json.dumps(agent_response, indent=2))
        
        if "Authorization Error" in agent_response.get("response", ""):
            print("\n❌ TEST FAILED: Agent returned an authorization error.")
        else:
             print("\n✅ VALIDATION PASSED: The agent successfully used the secure tool!")

    except requests.exceptions.RequestException as e:
        print(f"❌ FATAL ERROR: Could not query the NeuraNLP Agent. {e}")
        if e.response:
             print(f"    Response Body: {e.response.text}")


if __name__ == "__main__":
    run_test()