import cv2
import time
from ultralytics import YOLO
from ..utils.config import MODEL_PATH, DETECTION_CONFIDENCE_THRESHOLD, MPS_ENABLED, EVENT_COOLDOWN_SECONDS
from . import event_detector 

from ..integrations import log_event_to_memorycore, trigger_reflex_alert
import datetime

class StreamProcessor:
    """
    Manages the processing of a single video stream for event detection,
    now with an event cooldown mechanism.
    """
    def __init__(self, camera_id: str, stream_source):
        self.camera_id = camera_id
        self.stream_source = stream_source
        self.device = "mps" if MPS_ENABLED else "cpu"
        print(f"[Processor-{self.camera_id}] Initializing with device: {self.device}")
        
        self.model = YOLO(MODEL_PATH)
        self.tracked_objects = {}
        self.last_alert_times = {}

    def run(self):
        """Starts the video processing loop for this stream."""
        print(f"[Processor-{self.camera_id}] Attempting to open video capture for source: '{self.stream_source}'")
        cap = cv2.VideoCapture(self.stream_source)
        
        if not cap.isOpened():
            # More explicit error logging
            print(f"[Processor-{self.camera_id}] ERROR: cap.isOpened() returned False. The camera could not be accessed or the file path is incorrect.")
            return

        print(f"[Processor-{self.camera_id}] Video stream opened successfully. Starting detection loop...")
        
        while cap.isOpened(): # More robust loop condition
            success, frame = cap.read()
            if not success:
                print(f"[Processor-{self.camera_id}] Stream ended or failed to read frame.")
                break # Exit loop if stream ends

            # Run YOLOv8 tracking on the frame
            results = self.model.track(
                frame,
                persist=True,
                conf=DETECTION_CONFIDENCE_THRESHOLD,
                device=self.device,
                verbose=False # Quieter logs for cleaner output
            )

            detected_events = event_detector.detect_events(results, self.tracked_objects)
            
            if detected_events:
                self.handle_detected_events(detected_events)

            # Keep a small sleep to yield CPU if running very fast
            time.sleep(0.01)

        print(f"[Processor-{self.camera_id}] Releasing video capture.")
        cap.release()
        
    def handle_detected_events(self, events: list):
        """Processes events, checking against a cooldown before triggering alerts."""
        current_time = time.time()
        
        for event in events:
            event_type = event['event_type']
            
            last_alert = self.last_alert_times.get(event_type, 0)
            if (current_time - last_alert) < EVENT_COOLDOWN_SECONDS:
                continue

            self.last_alert_times[event_type] = current_time
            
            event["camera_id"] = self.camera_id
            event["timestamp"] = datetime.datetime.now().isoformat()
            
            print(f"!!! [Processor-{self.camera_id}] TRIGGERING EVENT: {event['event_type']} with details: {event['details']}!!!")
            
            log_event_to_memorycore(event)
            trigger_reflex_alert(event)