from fastapi import FastAPI, Request
from pydantic import BaseModel
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)

class Location(BaseModel):
    location: str

class Announcement(BaseModel):
    message: str

class Notification(BaseModel):
    department: str
    message: str

@app.post("/api/actions/call_security")
async def mock_call_security(payload: Location):
    logging.info(f"✅ MOCK SERVER: Received call for security at location: {payload.location}")
    return {"status": "success", "message": f"Mock security dispatched to {payload.location}."}

@app.post("/api/actions/send_announcement")
async def mock_send_announcement(payload: Announcement):
    logging.info(f"✅ MOCK SERVER: Received announcement: '{payload.message}'")
    return {"status": "success", "message": f"Mock announcement sent."}

@app.post("/api/actions/notify_admin")
async def mock_notify_admin(payload: Notification):
    logging.info(f"✅ MOCK SERVER: Received notification for {payload.department}: '{payload.message}'")
    return {"status": "success", "message": f"Mock notification sent to {payload.department}."}

@app.get("/")
def read_root():
    return {"message": "Mock ReflexSystem API is running."}

if __name__ == "__main__":
    import uvicorn
    # Run this on port 8001 as configured in config.py
    uvicorn.run(app, host="0.0.0.0", port=8001)