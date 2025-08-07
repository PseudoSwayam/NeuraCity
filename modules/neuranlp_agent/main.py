from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import Optional
from .agent_core import agent_core
# MODIFIED: Import the GETTER function, not the object itself
from .voice_handler import get_voice_handler 
from .utils import config
import logging
import os

logging.basicConfig(level=config.LOGGING_LEVEL)

app = FastAPI(
    title="NeuraNLP Agent",
    description="The AI assistant agent for the NeuraCity smart campus.",
    version="1.0.0"
)

class QueryResponse(BaseModel):
    response: str
    source: str
    audio_output: Optional[str] = None

@app.post("/query", response_model=QueryResponse)
async def handle_query(query: str = Form(...), mode: str = Form("text"), file: Optional[UploadFile] = File(None)):
    """Handles student and staff queries.
    - query: The user's question or command.
    - mode: 'text' for text-based interaction, 'voice' for voice-based interaction.
    - file: The audio file (e.g., WAV, MP3) if mode is 'voice'.
    """
    # MODIFIED: Get the handler instance at the start of the request
    voice_handler = get_voice_handler() 

    # --- THE REST OF YOUR LOGIC IS IDENTICAL ---
    user_query = query

    if mode == "voice":
        if not file:
            raise HTTPException(status_code=400, detail="Voice file is required for voice mode.")
        
        temp_file_path = f"temp_{file.filename}"
        try:
            with open(temp_file_path, "wb") as buffer:
                buffer.write(await file.read())
            
            user_query = voice_handler.voice_to_text(temp_file_path)
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing voice input: {str(e)}")
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    if not user_query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    result = agent_core.run_query(user_query)

    audio_output = None
    if mode == "voice" and result and "error" not in result.get("response", "").lower():
        audio_output = voice_handler.text_to_voice(result["response"])
    
    return QueryResponse(response=result["response"], source=result["source"], audio_output=audio_output)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/sample_queries")
def get_sample_queries():
    return {
        "queries": [
            "Where is Prof. Sharma’s office?",
            "Is the AI Club hosting any event today?",
            "Send a safety alert to the main gate.",
            "What happened in Lab C yesterday?",
            "I saw a student faint. Call for help.",
            "Notify the facilities department that the water fountain on the second floor is broken."
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.HOST, port=config.PORT, reload=True)