import cv2
import time
import numpy as np
from typing import List, Dict, Any
from ..utils.config import INTRUSION_ZONE, LOITERING_TIME_SECONDS, LOITERING_DISTANCE_THRESHOLD

def detect_events(yolo_results, tracked_objects: Dict[int, Any]) -> List[Dict[str, Any]]:
    """
    Analyzes YOLOv8 tracking results to identify high-level events.

    Args:
        yolo_results: The output from the YOLOv8 model's .track() method.
        tracked_objects (dict): A stateful dictionary to track objects over time.
    
    Returns:
        A list of dictionaries, where each dictionary represents a detected event.
    """
    if yolo_results is None or len(yolo_results) == 0:
        return []

    results = yolo_results[0]
    detected_events = []
    
    # Get current detections with tracking IDs
    current_detections = results.boxes.data.cpu().numpy()
    
    if current_detections.shape[1] < 7: # Ensure tracker IDs are present
        return []

    # Process each detected person
    for det in current_detections:
        x1, y1, x2, y2, track_id, conf, class_id = det
        if int(class_id) != 0:  # COCO class ID for 'person' is 0
            continue
            
        track_id = int(track_id)
        bbox = [int(x1), int(y1), int(x2), int(y2)]
        center_point = (int((x1 + x2) / 2), int((y1 + y2) / 2))

        # 1. Fall Detection
        is_fallen, details = _check_fall(bbox, conf)
        if is_fallen:
            detected_events.append({
                "event_type": "FALL_DETECTED", "camera_id": None, "details": details
            })

        # 2. Intrusion Detection
        is_intruding, details = _check_intrusion(center_point, conf)
        if is_intruding:
            detected_events.append({
                "event_type": "INTRUSION_DETECTED", "camera_id": None, "details": details
            })

        # 3. Loitering Detection (Stateful)
        is_loitering, details = _check_loitering(track_id, center_point, conf, tracked_objects)
        if is_loitering:
            detected_events.append({
                "event_type": "LOITERING_DETECTED", "camera_id": None, "details": details
            })

    return detected_events


# --- Private Helper Functions for Event Logic ---

def _check_fall(bbox, conf):
    """Heuristic for fall detection: person is lying down (width > height)."""
    x1, y1, x2, y2 = bbox
    width = x2 - x1
    height = y2 - y1
    
    # If the bounding box is wider than it is tall, it's a potential fall.
    # We add a threshold to avoid detecting people bending over.
    if width > height * 1.5:
        return True, {"bbox": bbox, "confidence": float(conf)}
    return False, {}

def _check_intrusion(center_point, conf):
    """Checks if a person's center point is inside the predefined restricted zone."""
    zone_polygon = np.array(INTRUSION_ZONE, np.int32)
    
    # Use OpenCV's pointPolygonTest to check if the point is inside
    is_inside = cv2.pointPolygonTest(zone_polygon, center_point, False) > 0
    if is_inside:
        return True, {"position": center_point, "confidence": float(conf)}
    return False, {}

def _check_loitering(track_id, center_point, conf, tracked_objects):
    """Checks if a tracked object has been stationary for a set duration."""
    current_time = time.time()
    
    if track_id not in tracked_objects:
        # New object detected, initialize its state
        tracked_objects[track_id] = {
            "first_seen": current_time,
            "last_seen": current_time,
            "positions": [center_point],
            "alerted": False
        }
        return False, {}
        
    # Update object's state
    obj = tracked_objects[track_id]
    obj["last_seen"] = current_time
    
    # Calculate distance from its first recorded position
    start_pos = np.array(obj["positions"][0])
    current_pos = np.array(center_point)
    distance = np.linalg.norm(start_pos - current_pos)
    
    duration = current_time - obj["first_seen"]
    
    # Check if object has been loitering and hasn't been alerted for yet
    if (duration > LOITERING_TIME_SECONDS and 
        distance < LOITERING_DISTANCE_THRESHOLD and 
        not obj["alerted"]):
        
        obj["alerted"] = True # Set flag to prevent repeated alerts for the same event
        return True, {
            "track_id": track_id,
            "duration": round(duration, 2),
            "position": center_point,
            "confidence": float(conf)
        }
    return False, {}