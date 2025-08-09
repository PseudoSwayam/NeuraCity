# --- Model Configuration ---
MODEL_PATH = "modules/cv_watchtower/models/yolov8n.pt"
DETECTION_CONFIDENCE_THRESHOLD = 0.6  # Only detect objects with > 60% confidence
MPS_ENABLED = True  # Set to True to use Apple Silicon GPU, False for CPU

# --- Camera Stream Configuration ---
# Add paths to video files or integer IDs for webcams (e.g., 0, 1)
# Each entry is a tuple: (Camera ID/Name, Source Path)
CAMERA_STREAMS = {
    "LobbyCam-01": 0,  # Use the default webcam
    #"Courtyard-File": "path/to/your/test_video.mp4" # Use a video file for testing
}

# --- Event Detection Parameters ---
# Intrusion Detection: Define a "restricted zone" as a list of points (x, y)
# These example coordinates define a rectangle in the bottom-left corner of a 1280x720 frame.
INTRUSION_ZONE = [(50, 600), (300, 600), (300, 700), (50, 700)]

# Loitering Detection
LOITERING_TIME_SECONDS = 10  # A person is "loitering" if they stay in the same area for 10s
LOITERING_DISTANCE_THRESHOLD = 50  # ...within a 50-pixel radius

# --- Integration API Endpoints ---
REFLEX_SYSTEM_URL = "http://localhost:8001/api"