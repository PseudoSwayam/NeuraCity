# File: modules/cv_watchtower/main.py

import cv2
import numpy as np
import time
import argparse
from .utils import config
from ultralytics import YOLO
from .processing import event_detector
from .integrations import log_event_to_memorycore, trigger_reflex_alert
import datetime

def create_grid(frames: dict, cam_ids: list, grid_shape=(2, 3)):
    """Stitches frames together into a single grid display."""
    if not cam_ids: return np.zeros((720, 1280, 3), dtype=np.uint8)

    # For a single camera, just return the frame itself.
    if len(cam_ids) == 1:
        frame = frames.get(cam_ids[0])
        if frame is not None:
            # Optionally resize a single feed to be larger for better viewing
            return cv2.resize(frame, (1280, 720)) 
        return np.zeros((720, 1280, 3), dtype=np.uint8)

    # Grid logic for multiple cameras
    rows, cols = grid_shape
    scale_h, scale_w = 360, 640
    grid = np.zeros((scale_h * rows, scale_w * cols, 3), dtype=np.uint8)

    for i in range(rows):
        for j in range(cols):
            idx = i * cols + j
            if idx < len(cam_ids):
                cam_id = cam_ids[idx]
                frame = frames.get(cam_id)
                if frame is not None:
                    resized = cv2.resize(frame, (scale_w, scale_h))
                    grid[i*scale_h:(i+1)*scale_h, j*scale_w:(j+1)*scale_w] = resized
                else:
                    placeholder = np.zeros((scale_h, scale_w, 3), dtype=np.uint8)
                    cv2.putText(placeholder, f"Connecting...", (50, scale_h//2), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    grid[i*scale_h:(i+1)*scale_h, j*scale_w:(j+1)*scale_w] = placeholder
    return grid

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NeuraCity Computer Vision Watchtower")
    parser.add_argument(
        "--mode", type=str, default="single", choices=["single", "showcase"],
        help="Operating mode: 'single' for webcam, 'showcase' for 6-video grid."
    )
    args = parser.parse_args()

    if args.mode == "showcase":
        print("[Watchtower Main] Starting in SHOWCASE mode...")
        camera_sources = config.SHOWCASE_VIDEO_SOURCES
        loitering_time = config.LOITERING_TIME_SHOWCASE
        abandoned_time = config.ABANDONED_OBJECT_TIME_SHOWCASE
    else: # Default is "single" mode
        print("[Watchtower Main] Starting in SINGLE camera mode...")
        camera_sources = {"MyWebcam": config.SINGLE_CAMERA_SOURCE}
        loitering_time = config.LOITERING_TIME_REALISTIC
        abandoned_time = config.ABANDONED_OBJECT_TIME_REALISTIC
    
    device = "mps" if config.MPS_ENABLED else "cpu"
    print(f"[Watchtower Main] Loading YOLOv8 model onto device: {device}")
    model = YOLO(config.MODEL_PATH)

    caps = {cam_id: cv2.VideoCapture(source) for cam_id, source in camera_sources.items()}
    for cam_id, cap in caps.items():
        if not cap.isOpened(): print(f"WARNING: Could not open stream for {cam_id}. It will be skipped.")

    person_tracker, object_tracker, last_alert_times, current_frames = {}, {}, {}, {}

    print("[Watchtower Main] Starting sequential processing loop...")
    try:
        while True:
            cam_ids_active = list(caps.keys())

            for cam_id, cap in caps.items():
                if not cap.isOpened(): continue
                success, frame = cap.read()
                if not success:
                    # If it's a file path and not an integer (webcam), loop the video
                    if isinstance(camera_sources[cam_id], str):
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                
                results = model.track(frame, persist=True, conf=config.DETECTION_CONFIDENCE_THRESHOLD,
                                      device=device, verbose=False, classes=[0, 24, 26, 28, 43])
                
                detected_events = event_detector.detect_events(
                    results, person_tracker, object_tracker, frame, loitering_time, abandoned_time)

                current_time = time.time()
                for event in detected_events:
                    event_type = event['event_type']
                    # Use a unique key for cooldown per camera AND per event type
                    cooldown_key = f"{cam_id}_{event_type}"
                    if (current_time - last_alert_times.get(cooldown_key, 0)) > config.EVENT_COOLDOWN_SECONDS:
                        last_alert_times[cooldown_key] = current_time
                        
                        event_data = {**event, "camera_id": cam_id, "timestamp": datetime.datetime.now().isoformat()}
                        
                        print(f"!!! [{cam_id}] TRIGGER: {event_data['event_type']} -> {event_data['details']}!!!")
                        log_event_to_memorycore(event_data)
                        trigger_reflex_alert(event_data)

                annotated_frame = results[0].plot()
                if detected_events:
                    # Add event text overlay for the visual showcase
                    event_text = detected_events[0]['event_type']
                    cv2.putText(annotated_frame, event_text, (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 4, cv2.LINE_AA)
                current_frames[cam_id] = annotated_frame

            grid_display = create_grid(current_frames, cam_ids_active)
            cv2.imshow("NeuraCity Watchtower", grid_display)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                print("\n[Watchtower Main] 'q' pressed. Shutting down.")
                break
                
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\n[Watchtower Main] Shutdown signal (Ctrl+C) received.")
    finally:
        print("[Watchtower Main] Releasing all video captures...")
        for cap in caps.values():
            cap.release()
        cv2.destroyAllWindows()
        print("[Watchtower Main] Program has finished.")