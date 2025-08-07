import whisper
import pyttsx3
from pydub import AudioSegment
import os
import base64

class VoiceHandler:
    def __init__(self):
        self.whisper_model = whisper.load_model("base")
        self.tts_engine = pyttsx3.init()

    def voice_to_text(self, audio_file_path: str) -> str:
        """Converts voice input to text using Whisper."""
        try:
            # Convert to WAV if not already
            if not audio_file_path.endswith(".wav"):
                sound = AudioSegment.from_file(audio_file_path)
                wav_path = "temp.wav"
                sound.export(wav_path, format="wav")
                audio_file_path = wav_path

            result = self.whisper_model.transcribe(audio_file_path)
            return result["text"]
        except Exception as e:
            print(f"Error in voice_to_text: {e}")
            return ""

    def text_to_voice(self, text: str, output_path="response.mp3") -> str:
        """Converts text response to speech and returns the base64 encoded audio."""
        try:
            self.tts_engine.save_to_file(text, output_path)
            self.tts_engine.runAndWait()
            
            with open(output_path, "rb") as audio_file:
                encoded_string = base64.b64encode(audio_file.read()).decode('utf-8')
            
            os.remove(output_path) # Clean up the audio file
            return encoded_string
        except Exception as e:
            print(f"Error in text_to_voice: {e}")
            return ""

voice_handler = VoiceHandler()