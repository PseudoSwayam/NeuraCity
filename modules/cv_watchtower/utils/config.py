# File: modules/cv_watchtower/utils/config.py

import os
from utils.config_loader import settings

# --- Model Configuration ---
MODEL_PATH = settings.YOLO_MODEL_PATH
DETECTION_CONFIDENCE_THRESHOLD = settings.DETECTION_CONFIDENCE_THRESHOLD
MPS_ENABLED = True

# Use your MacBook's webcam for single-camera, real-time testing
SINGLE_CAMERA_SOURCE = 0

# Showcase mode uses 6 pre-recorded videos for a high-impact demo
SHOWCASE_VIDEO_SOURCES = {
    "Fall Cam": os.path.join(settings.VIDEOS_DIR, "fall_test.mp4"),
    "Loitering Cam": os.path.join(settings.VIDEOS_DIR, "loitering_test.mp4"),
    "Abandoned Bag Cam": os.path.join(settings.VIDEOS_DIR, "abandoned_bag_test.mp4"),
    "Fight Cam": os.path.join(settings.VIDEOS_DIR, "fight_test.mp4"),
    "Fire Cam": os.path.join(settings.VIDEOS_DIR, "fire_test.mp4"),
    "Normal Activity Cam": os.path.join(settings.VIDEOS_DIR, "normal_activity.mp4"),
}

# --- Event Detection Parameters ---
# These are tuning parameters specific to this module's logic, so they stay here.
LOITERING_TIME_REALISTIC = 10.0
ABANDONED_OBJECT_TIME_REALISTIC = 20.0
LOITERING_TIME_SHOWCASE = 5.0
ABANDONED_OBJECT_TIME_SHOWCASE = 7.0
INTRUSION_ZONE = [(50, 600), (400, 600), (400, 720), (50, 720)]
LOITERING_DISTANCE_THRESHOLD = 50
FIRE_COLOR_THRESHOLD = 0.15
FIRE_CHECK_AREA = [0, 0, 1280, 720]

# --- Alerting & Integration ---
EVENT_COOLDOWN_SECONDS = 15.0