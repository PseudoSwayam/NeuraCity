from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import Optional
from .agent_core import agent_core
from .voice_handler import voice_handler
from .utils import config
import logging
import os

# Set up basic logging
logging.basicConfig(level=config.LOGGING_LEVEL)

# Initialize the FastAPI app
app = FastAPI(
    title="NeuraNLP Agent",
    description="The AI assistant agent for the NeuraCity smart campus.",
    version="1.0.0"
)


# --- Pydantic Models for Request and Response ---

class QueryResponse(BaseModel):
    response: str
    source: str
    audio_output: Optional[str] = None


# --- API Endpoints ---

@app.post("/query", response_model=QueryResponse)
async def handle_query(query: str = Form(...), mode: str = Form("text"), file: UploadFile = File(None)):
    """
    Handles student and staff queries.
    - query: The user's question or command.
    - mode: 'text' for text-based interaction, 'voice' for voice-based interaction.
    - file: The audio file (e.g., WAV, MP3) if mode is 'voice'.
    """
    # All of the following logic is now correctly indented to be inside the function
    user_query = query

    if mode == "voice":
        if not file:
            raise HTTPException(status_code=400, detail="Voice file is required for voice mode.")
        
        # Define a temporary path for the uploaded audio file
        temp_file_path = f"temp_{file.filename}"
        try:
            # Save the uploaded file to disk
            with open(temp_file_path, "wb") as buffer:
                buffer.write(await file.read())
            
            # Convert the audio file to text
            user_query = voice_handler.voice_to_text(temp_file_path)
            
        except Exception as e:
            # If any error occurs, raise an HTTP exception
            raise HTTPException(status_code=500, detail=f"Error processing voice input: {str(e)}")
        finally:
            # Ensure the temporary file is deleted even if errors occur
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    # Check if the final query is empty
    if not user_query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    # Run the query through the main agent core
    result = agent_core.run_query(user_query)

    # Generate voice output if the mode is 'voice' and there wasn't an error
    audio_output = None
    if mode == "voice" and result and "error" not in result.get("response", "").lower():
        audio_output = voice_handler.text_to_voice(result["response"])
    
    # Return the final structured response
    return QueryResponse(response=result["response"], source=result["source"], audio_output=audio_output)


@app.get("/health")
def health_check():
    # Return statement is now correctly indented
    return {"status": "ok"}


@app.get("/sample_queries")
def get_sample_queries():
    # Return statement is now correctly indented
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


# The special entry point for running the app directly
# Corrected 'name == "main"' to '__name__ == "__main__"'
if __name__ == "__main__":
    import uvicorn
    # This allows running the script with `python3 main.py`
    uvicorn.run(app, host=config.HOST, port=config.PORT, reload=True)