# File: modules/cv_watchtower/processing/stream_processor.py

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
    with an event cooldown mechanism and separated state trackers.
    """
    def __init__(self, camera_id: str, stream_source, frame_queue):
        self.camera_id = camera_id
        self.stream_source = stream_source
        self.frame_queue = frame_queue
        self.device = "mps" if MPS_ENABLED else "cpu"
        self.model = YOLO(MODEL_PATH)
        
        # Use separate, dedicated dictionaries for each stateful detection logic.
        # This prevents object types from interfering with each other.
        self.person_tracker = {}
        self.object_tracker = {}

        # Stores the last time an alert was sent for a specific event type.
        self.last_alert_times = {}

    def run(self):
        """Starts the video processing loop for this stream."""
        print(f"[Processor-{self.camera_id}] Attempting to open video capture for source: '{self.stream_source}'")
        cap = cv2.VideoCapture(self.stream_source)
        
        if not cap.isOpened():
            print(f"[Processor-{self.camera_id}] ERROR: cap.isOpened() returned False. Camera or file is inaccessible.")
            return

        print(f"[Processor-{self.camera_id}] Video stream opened successfully. Starting detection loop...")
        
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                # If it's a file, we're done. If it's a camera, maybe try to reconnect.
                if isinstance(self.stream_source, str):
                    print(f"[Processor-{self.camera_id}] End of video file reached.")
                    break
                else:
                    print(f"[Processor-{self.camera_id}] Failed to read frame from camera. Retrying...")
                    time.sleep(1)
                    continue

            # Run YOLOv8 tracking on the frame, filtering for relevant classes to improve performance
            results = self.model.track(
                frame,
                persist=True,
                conf=DETECTION_CONFIDENCE_THRESHOLD,
                device=self.device,
                classes=[0, 24, 26, 28, 43], # person, backpack, handbag, suitcase, knife
                verbose=False # Quieter logs for cleaner output
            )

            # Pass the correct state dictionaries to the event detector.
            detected_events = event_detector.detect_events(
                yolo_results=results,
                person_tracker=self.person_tracker,
                object_tracker=self.object_tracker,
                frame=frame
            )
            
            # Annotate frame BEFORE putting it in the queue for the grid display
            annotated_frame = results[0].plot()
            if detected_events:
                self.handle_detected_events(detected_events)
                # Display the primary event on the frame for the grid view
                event_text = detected_events[0]['event_type']
                cv2.putText(annotated_frame, event_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3, cv2.LINE_AA)

            # Put the processed frame into the shared queue for the main display
            self.frame_queue.put((self.camera_id, annotated_frame))

        print(f"[Processor-{self.camera_id}] Releasing video capture.")
        cap.release()
        
    def handle_detected_events(self, events: list):
        """Processes events, checking against a cooldown before triggering alerts."""
        current_time = time.time()
        
        for event in events:
            event_type = event['event_type']
            
            last_alert = self.last_alert_times.get(event_type, 0)
            if (current_time - last_alert) < EVENT_COOLDOWN_SECONDS:
                print(f"[{self.camera_id}] Cooldown active for '{event_type}'. Ignoring.")
                continue

            # If not in cooldown, process the event fully
            self.last_alert_times[event_type] = current_time
            
            event["camera_id"] = self.camera_id
            event["timestamp"] = datetime.datetime.now().isoformat()
            
            print(f"!!! [{self.camera_id}] TRIGGERING EVENT: {event['event_type']} with details: {event['details']}!!!")
            
            # Integrate with other NeuraCity modules
            log_event_to_memorycore(event)
            trigger_reflex_alert(event)