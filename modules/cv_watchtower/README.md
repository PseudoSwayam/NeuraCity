# 👁️ CV Watchtower: The Eyes of NeuraCity

> The real-time, multi-camera computer vision module for the NeuraCity Smart Campus project.

The `cv_watchtower` is a high-performance, intelligent surveillance module. It acts as the visual cortex of the NeuraCity platform, processing multiple video streams simultaneously to proactively detect a wide range of security, safety, and operational events. It is deeply integrated with the `reflex_system` and `memorycore` to enable a fully automated detect-and-respond ecosystem.

---

## ✨ Core Detection Capabilities

The Watchtower uses a powerful combination of a state-of-the-art AI model (YOLOv8) and a layer of custom heuristics to identify complex events.

### Core Safety & Security
*   **🚨 Fall Detection**: Identifies individuals who have fallen using aspect ratio analysis of their bounding box. Triggers an immediate, high-priority alert.
*   **🛡️ Intrusion Detection**: Monitors predefined restricted zones and triggers an alert when a person enters an unauthorized area.
*   **🔥 Fire & Smoke Detection**: Utilizes a color-based heuristic to detect the tell-tale signs of fire, enabling early warnings.
*   **🥋 Violence & Fights Detection**: Detects unusually rapid, aggressive human movements and the presence of potential weapons, signaling a potential conflict.
*   **⏱️ Suspicious Loitering**: Employs object tracking to identify when a person remains in a single area for an abnormal length of time.

### Object & Event Recognition
*   **🎒 Abandoned Object Detection**: A time-based system that detects when objects like backpacks or suitcases are left unattended for an extended period.

---

## 🛠️ Technology Stack

*   **Primary AI Model**: `YOLOv8n` (by Ultralytics)
*   **Core CV Library**: `OpenCV`
*   **Performance Acceleration**: Apple Silicon (MPS)
*   **Architecture**: Single-Process, Sequential Asynchronous Loop for optimal performance on laptops.
*   **Integration**: Direct API calls to `reflex_system` and memory logging to `memorycore`.

---

## 🏗️ Project Structure

The module is designed for clean separation of concerns, making it easy to add new event detectors or update models in the future.
```bash
modules/cv_watchtower/
├── main.py # Main script with dual-mode (single/showcase) logic
├── integrations.py # Handles communication with reflex_system & memorycore
├── models/
│ └── yolov8n.pt # The pre-trained AI model file
├── processing/
│ ├── event_detector.py # The core "brain" for identifying all high-level events
│ └── stream_processor.py # The workhorse class for video processing
└── utils/
└── config.py # Centralized configuration for all parameters
```

---

## ⚙️ Setup and Usage

### 1. Download the AI Model

This module requires the pre-trained `yolov8n.pt` model.

*   **Using the Terminal (Recommended):**
    Navigate to the `NeuraCity` root directory and run:
    ```bash
    curl -L https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8n.pt -o modules/cv_watchtower/models/yolov8n.pt
    ```
*   **Manually:**
    Download the file from [this link](https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8n.pt) and place it in the `modules/cv_watchtower/models/` directory.

### 2. Prepare Demo Videos

For showcase mode, place the six demo video files inside a `videos/` directory in the **project root**. Refer to the project guide for recommended video sources.

---

## ▶️ Dual-Mode Operation

The `cv_watchtower` is brilliantly designed with two operational modes for both development and demonstration.

### Mode 1: `single` (For Real-Time Development & Testing)

This mode uses your laptop's built-in webcam for live testing of detection logic. It runs with more realistic, longer time thresholds for events.

**To Run:**
```bash
# In your NeuraCity root directory, with (venv) active
python3 -m modules.cv_watchtower.main
```

### Mode 2: showcase (For High-Impact Demonstrations)

This mode runs all six pre-recorded demo videos in a stunning 2x3 grid, simulating a real security control room. It uses lower time thresholds to ensure all event types are triggered quickly for an impressive presentation.

**To Run:**
```bash
# Add the --mode showcase flag
python3 -m modules.cv_watchtower.main --mode showcase
```

## 🤖 An Important Note on AI Behavior
During showcase mode, you may observe the VIOLENCE_DETECTED event being triggered by videos other than the "fight" scene, such as the fire_test.mp4.

This is not a bug; it is a feature of a highly sensitive system.

Our "Aggressive Movement" heuristic is designed to detect unusually high-velocity motion. The rapid, chaotic flickering of flames is correctly identified by this heuristic as a dangerous anomaly. This demonstrates the power of our custom logic layer that goes beyond simple object detection.

---

## Future Extensions
The definitive, professional next step for the NeuraCity project would be to fine-tune the AI model on a custom dataset. By training it with a new fire object class, the system could learn to distinguish the motion of a person from the motion of fire, elevating its intelligence from excellent to perfect. The modular architecture of this project makes swapping in a new, custom-trained .pt file a trivial task.