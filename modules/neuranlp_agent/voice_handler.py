import whisper
from pydub import AudioSegment
import os
import base64
from gtts import gTTS
import io

class VoiceHandler:
    """A class to handle both Speech-to-Text and Text-to-Speech operations."""
    def __init__(self):
        print("Initializing VoiceHandler and loading Whisper model...")
        # Whisper model is loaded only when this class is created
        self.whisper_model = whisper.load_model("base")
        print("Whisper model loaded.")

    def voice_to_text(self, audio_file_path: str) -> str:
        """Converts voice input from an audio file to text using Whisper."""
        try:
            sound = AudioSegment.from_file(audio_file_path)
            wav_path = "temp_audio.wav"
            sound.export(wav_path, format="wav")
            result = self.whisper_model.transcribe(wav_path)
            
            if os.path.exists(wav_path):
                os.remove(wav_path)
                
            return result.get("text", "")
        except Exception as e:
            print(f"Error in voice_to_text: {e}")
            return ""

    def text_to_voice(self, text: str) -> str:
        """Converts text response to speech using gTTS and returns base64 encoded audio."""
        try:
            tts = gTTS(text=text, lang='en')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            encoded_string = base64.b64encode(fp.read()).decode('utf-8')
            return encoded_string
        except Exception as e:
            print(f"Error in text_to_voice: {e}")
            return ""

# --- The Singleton Pattern ---
# This ensures that the heavy VoiceHandler is created only once, and only when first needed.
_voice_handler_instance = None

def get_voice_handler():
    """Gets the single, shared instance of the VoiceHandler."""
    global _voice_handler_instance
    if _voice_handler_instance is None:
        _voice_handler_instance = VoiceHandler()
    return _voice_handler_instance