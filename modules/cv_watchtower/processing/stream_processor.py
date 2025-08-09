# File: modules/cv_watchtower/processing/stream_processor.py

import cv2
import time
from ultralytics import YOLO
from .utils.config import MODEL_PATH, DETECTION_CONFIDENCE_THRESHOLD, MPS_ENABLED
from .processing import event_detector
from .integrations import log_event_to_memorycore, trigger_reflex_alert
import datetime

class StreamProcessor:
    """

    Manages the processing of a single video stream for event detection.
    """
    def __init__(self, camera_id: str, stream_source):
        self.camera_id = camera_id
        self.stream_source = stream_source
        self.device = "mps" if MPS_ENABLED else "cpu"
        print(f"[Processor-{self.camera_id}] Initializing with device: {self.device}")
        
        # Load the YOLOv8 model
        self.model = YOLO(MODEL_PATH)
        
        # State dictionary to track objects for loitering detection
        self.tracked_objects = {}

    def run(self):
        """Starts the video processing loop for this stream."""
        cap = cv2.VideoCapture(self.stream_source)
        if not cap.isOpened():
            print(f"[Processor-{self.camera_id}] ERROR: Cannot open video stream.")
            return

        print(f"[Processor-{self.camera_id}] Video stream opened. Starting detection...")
        while True:
            success, frame = cap.read()
            if not success:
                print(f"[Processor-{self.camera_id}] Stream ended. Looping...")
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0) # Loop video file
                continue

            # Run YOLOv8 tracking on the frame
            results = self.model.track(
                frame,
                persist=True,        # Keep tracking the same objects
                conf=DETECTION_CONFIDENCE_THRESHOLD,
                device=self.device
            )

            # Analyze results for high-level events
            detected_events = event_detector.detect_events(results, self.tracked_objects)
            
            # If any events are detected, process them
            if detected_events:
                self.handle_detected_events(detected_events, frame)

            # (Optional) Display the annotated frame
            # annotated_frame = results[0].plot()
            # cv2.imshow(f"NeuraCity Watchtower - {self.camera_id}", annotated_frame)
            # if cv2.waitKey(1) & 0xFF == ord("q"):
            #     break

        cap.release()
        # cv2.destroyAllWindows()
        
    def handle_detected_events(self, events: list, frame):
        """Processes a list of detected events by triggering alerts and logging."""
        for event in events:
            # Add common metadata to the event
            event["camera_id"] = self.camera_id
            event["timestamp"] = datetime.datetime.now().isoformat()
            
            print(f"[Processor-{self.camera_id}] DETECTED EVENT: {event['event_type']} with details: {event['details']}")
            
            # 1. Log every significant event to the MemoryCore
            log_event_to_memorycore(event)
            
            # 2. Trigger an immediate alert for critical events
            trigger_reflex_alert(event)