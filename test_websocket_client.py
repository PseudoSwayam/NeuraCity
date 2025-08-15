# File: test_websocket_client.py
# A dedicated client to test the Alerts & Notifications WebSocket.

import asyncio
import websockets
import json

ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbGVydHMtc3lzdGVtQG5ldXJhY2l0eS5kZXYiLCJleHAiOjE3NTUyNzM2MTV9.bwhxEng_PnGx91b72-2FQzjb1Nodt674kgfB4_cjiPk"
WEBSOCKET_URL = f"ws://localhost:8003/ws/alerts?token={ACCESS_TOKEN}"

async def listen_for_alerts():
    """Connects to the WebSocket and prints any messages it receives."""
    print(f"--- Attempting to connect to WebSocket at {WEBSOCKET_URL} ---")
    try:
        async with websockets.connect(WEBSOCKET_URL) as websocket:
            print("✅ WebSocket connection successful! Waiting for alerts...")
            # This loop will run forever, listening for server messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    print("\n--- NEW ALERT RECEIVED ---")
                    print(f"  Message: {data.get('human_readable_message')}")
                    raw_event = data.get('raw_event_data', {})
                    payload = raw_event.get('payload', {})
                    print(f"  Source Event: {raw_event.get('event_type')}")
                    if payload.get('camera_id'):
                        print(f"  From Camera: {payload.get('camera_id')}")
                    else:
                        print(f"  Full Location: {payload.get('location')}")
                    print("------------------------\n")
                except json.JSONDecodeError:
                    print(f"Received non-JSON message: {message}")

    except websockets.exceptions.ConnectionClosedError as e:
        print(f"❌ Connection closed with error: {e}")
    except ConnectionRefusedError:
        print(f"❌ Connection refused. Is the alerts_and_notifications server running on port 8003?")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(listen_for_alerts())
    except KeyboardInterrupt:
        print("\n--- Test client shut down. ---")