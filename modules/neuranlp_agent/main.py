from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from .agent_core import agent_core
from .voice_handler import voice_handler
from .utils import config
import logging
import os

logging.basicConfig(level=config.LOGGING_LEVEL)

app = FastAPI(
    title="NeuraNLP Agent",
    description="The AI assistant agent for the NeuraCity smart campus.",
    version="1.0.0"
)

class QueryRequest(BaseModel):
    query: str
    mode: str = "text"

class QueryResponse(BaseModel):
    response: str
    source: str
    audio_output: str | None = None


@app.post("/query", response_model=QueryResponse)
async def handle_query(query: str = Form(...), mode: str = Form("text"), file: UploadFile = File(None)):
    """
    Handles student and staff queries.
    - **query**: The user's question or command.
    - **mode**: 'text' for text-based interaction, 'voice' for voice-based interaction.
    - **file**: The audio file (e.g., WAV, MP3) if mode is 'voice'.
    """
    user_query = query

    if mode == "voice":
        if not file:
            raise HTTPException(status_code=400, detail="Voice file is required for voice mode.")
        try:
            # Save the uploaded file temporarily
            temp_file_path = f"temp_{file.filename}"
            with open(temp_file_path, "wb") as buffer:
                buffer.write(await file.read())
            
            user_query = voice_handler.voice_to_text(temp_file_path)
            os.remove(temp_file_path) # Clean up the temp file
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing voice input: {str(e)}")


    if not user_query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    result = agent_core.run_query(user_query)
    
    audio_output = None
    if mode == "voice":
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
    uvicorn.run(app, host=config.HOST, port=config.PORT)