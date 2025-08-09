# File: modules/cv_watchtower/utils/config.py

# --- Model Configuration ---
MODEL_PATH = "modules/cv_watchtower/models/yolov8n.pt" # Always use the efficient nano model now
DETECTION_CONFIDENCE_THRESHOLD = 0.4
MPS_ENABLED = True

# Use your MacBook's webcam for single-camera, real-time testing
SINGLE_CAMERA_SOURCE = 0

# Showcase mode uses 6 pre-recorded videos for a high-impact demo
SHOWCASE_VIDEO_SOURCES = {
    "Fall Cam": "videos/fall_test.mp4",
    "Loitering Cam": "videos/loitering_test.mp4",
    "Abandoned Bag Cam": "videos/abandoned_bag_test.mp4",
    "Fight Cam": "videos/fight_test.mp4",
    "Fire Cam": "videos/fire_test.mp4",
    "Normal Activity Cam": "videos/normal_activity.mp4",
}

# --- Event Detection Parameters (Now tuned slightly differently for each mode) ---
# Realistic, longer thresholds for single-camera mode
LOITERING_TIME_REALISTIC = 10.0
ABANDONED_OBJECT_TIME_REALISTIC = 20.0

# Lowered, faster thresholds for showcase mode
LOITERING_TIME_SHOWCASE = 5.0
ABANDONED_OBJECT_TIME_SHOWCASE = 7.0

# General parameters (used by both modes)
INTRUSION_ZONE = [(50, 600), (400, 600), (400, 720), (50, 720)]
LOITERING_DISTANCE_THRESHOLD = 50
FIRE_COLOR_THRESHOLD = 0.15
FIRE_CHECK_AREA = [0, 0, 1280, 720]

# --- Alerting & Integration ---
EVENT_COOLDOWN_SECONDS = 15.0
REFLEX_SYSTEM_URL = "http://localhost:8001/api"