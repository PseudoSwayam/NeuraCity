# File: modules/cv_watchtower/processing/event_detector.py

import cv2
import time
import numpy as np
from typing import List, Dict, Any
from ..utils.config import INTRUSION_ZONE, LOITERING_DISTANCE_THRESHOLD, FIRE_COLOR_THRESHOLD, FIRE_CHECK_AREA

# COCO Class IDs
CLASS_IDS = {
    'person': 0, 'backpack': 24, 'handbag': 26, 'suitcase': 28, 'knife': 43
}

def detect_events(
    yolo_results,
    person_tracker: Dict,
    object_tracker: Dict,
    frame: np.ndarray,
    loitering_time_threshold: float,
    abandoned_obj_time_threshold: float
) -> List[Dict]:
    """Analyzes YOLOv8 results for high-level events using dynamic time thresholds."""
    if not yolo_results or len(yolo_results) == 0:
        return []

    results = yolo_results[0]
    detected_events, current_time = [], time.time()
    
    current_detections = results.boxes.data.cpu().numpy()
    if current_detections.shape[1] < 7: return []

    persons = [det for det in current_detections if int(det[6]) == CLASS_IDS['person']]
    bags = [det for det in current_detections if int(det[6]) in [CLASS_IDS['backpack'], CLASS_IDS['handbag']]]
    weapons = [det for det in current_detections if int(det[6]) == CLASS_IDS['knife']]

    # --- Run all detection checks ---
    is_fire, fire_details = _check_fire(frame)
    if is_fire:
        detected_events.append({"event_type": "FIRE_SMOKE_DETECTED", "details": fire_details})

    is_abandoned, abandoned_details = _check_abandoned_object(
        persons, bags, current_time, object_tracker, abandoned_obj_time_threshold
    )
    if is_abandoned:
        detected_events.append({"event_type": "ABANDONED_OBJECT", "details": abandoned_details})

    for person_det in persons:
        x1, y1, x2, y2, track_id, conf, _ = person_det
        track_id = int(track_id)
        bbox = [int(x1), int(y1), int(x2), int(y2)]
        center = (int((x1 + x2) / 2), int((y1 + y2) / 2))

        is_fallen, details = _check_fall(bbox, conf)
        if is_fallen: detected_events.append({"event_type": "FALL_DETECTED", "details": details})

        is_intruding, details = _check_intrusion(center, conf)
        if is_intruding: detected_events.append({"event_type": "INTRUSION_DETECTED", "details": details})
        
        is_loitering, details = _check_loitering(track_id, center, current_time, conf, person_tracker, loitering_time_threshold)
        if is_loitering: detected_events.append({"event_type": "LOITERING_DETECTED", "details": details})
        
        is_violent, details = _check_violence(track_id, center, current_time, weapons, conf, person_tracker)
        if is_violent: detected_events.append({"event_type": "VIOLENCE_DETECTED", "details": details})

    return detected_events

# --- All Helper Functions Below This Line ---
# (They now correctly accept and use the time_threshold where needed)

def _check_fall(bbox, conf):
    width, height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    if width > height * 1.5:
        return True, {"bbox": bbox, "confidence": round(float(conf), 2)}
    return False, {}

def _check_intrusion(center_point, conf):
    zone_polygon = np.array(INTRUSION_ZONE, np.int32)
    if cv2.pointPolygonTest(zone_polygon, center_point, False) > 0:
        return True, {"position": center_point, "confidence": round(float(conf), 2)}
    return False, {}

def _update_person_tracker(track_id, center, current_time, person_tracker):
    if track_id not in person_tracker:
        person_tracker[track_id] = {"first_seen": current_time, "positions": [], "velocities": [], "alerts": {}}
    obj = person_tracker[track_id]
    obj["last_seen"] = current_time
    if len(obj["positions"]) > 0:
        obj["velocities"].append(np.linalg.norm(np.array(center) - np.array(obj["positions"][-1])))
    obj["positions"].append(center)
    if len(obj["positions"]) > 30:
        obj["positions"].pop(0)
        if obj["velocities"]: obj["velocities"].pop(0)

def _check_loitering(track_id, center, current_time, conf, person_tracker, time_threshold):
    _update_person_tracker(track_id, center, current_time, person_tracker)
    obj = person_tracker[track_id]
    distance = np.linalg.norm(np.array(center) - np.array(obj["positions"][0]))
    duration = current_time - obj["first_seen"]
    if duration > time_threshold and distance < LOITERING_DISTANCE_THRESHOLD and not obj["alerts"].get("loitering"):
        obj["alerts"]["loitering"] = True
        return True, {"track_id": track_id, "duration": round(duration), "confidence": round(float(conf), 2)}
    return False, {}
    
def _check_violence(track_id, center, current_time, weapons, conf, person_tracker):
    _update_person_tracker(track_id, center, current_time, person_tracker)
    obj = person_tracker.get(track_id, {})
    if obj.get("velocities") and len(obj["velocities"]) > 3 and np.mean(obj["velocities"]) > 150 and not obj["alerts"].get("violence"):
        obj["alerts"]["violence"] = True
        return True, {"track_id": track_id, "reason": "Aggressive Movement", "confidence": round(float(conf), 2)}
    person_box = [center[0] - 75, center[1] - 150, center[0] + 75, center[1] + 150] # Larger area
    for w in weapons:
        weapon_center = ((w[0] + w[2]) / 2, (w[1] + w[3]) / 2)
        if person_box[0] < weapon_center[0] < person_box[2] and person_box[1] < weapon_center[1] < person_box[3]:
            if not obj.get("alerts", {}).get("weapon"):
                if "alerts" not in obj: obj["alerts"] = {}
                obj["alerts"]["weapon"] = True
                return True, {"track_id": track_id, "reason": "Weapon Detected", "confidence": round(float(w[5]), 2)}
    return False, {}

def _check_abandoned_object(persons, bags, current_time, object_tracker, time_threshold):
    for bag_det in bags:
        x1, y1, x2, y2, track_id, conf, _ = bag_det
        track_id_str = f"bag_{int(track_id)}"
        center = (int((x1 + x2) / 2), int((y1 + y2) / 2))
        if track_id_str not in object_tracker:
            object_tracker[track_id_str] = {"center": center, "first_seen": current_time, "alerts": {}}
        object_tracker[track_id_str]["center"] = center
            
    for key, obj in object_tracker.items():
        person_is_nearby = any(np.linalg.norm(np.array(obj["center"]) - np.array([(p[0]+p[2])/2, (p[1]+p[3])/2])) < 150 for p in persons)
        if person_is_nearby:
            obj["first_seen"] = current_time
            continue
        duration = current_time - obj["first_seen"]
        if duration > time_threshold and not obj["alerts"].get("abandoned"):
            obj["alerts"]["abandoned"] = True
            return True, {"object_id": key, "duration": round(duration)}
    return False, {}

def _check_fire(frame):
    roi = frame[FIRE_CHECK_AREA[1]:FIRE_CHECK_AREA[3], FIRE_CHECK_AREA[0]:FIRE_CHECK_AREA[2]]
    if roi.size == 0: return False, {}
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    lower = np.array([0, 120, 120])
    upper = np.array([40, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)
    fire_pixel_percentage = cv2.countNonZero(mask) / (roi.shape[0] * roi.shape[1])
    if fire_pixel_percentage > FIRE_COLOR_THRESHOLD:
        return True, {"pixel_percentage": round(fire_pixel_percentage * 100, 2)}
    return False, {}