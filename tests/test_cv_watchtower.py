import pytest
import sys
import os

# Add the project's root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Import the function we want to test
from modules.cv_watchtower.processing import event_detector

def test_fall_detection_logic():
    """Tests the heuristic for fall detection."""
    # Test case 1: A standing person (height > width)
    standing_bbox = [100, 100, 150, 300] # width=50, height=200
    is_fallen, _ = event_detector._check_fall(standing_bbox, conf=0.9)
    assert not is_fallen
    
    # Test case 2: A fallen person (width > height * 1.5)
    fallen_bbox = [100, 100, 300, 150] # width=200, height=50
    is_fallen, details = event_detector._check_fall(fallen_bbox, conf=0.9)
    assert is_fallen
    assert "bbox" in details

def test_intrusion_detection_logic():
    """Tests the point-in-polygon logic for intrusion."""
    # Define a simple square zone for the test
    event_detector.INTRUSION_ZONE = [(10, 10), (100, 10), (100, 100), (10, 100)]
    
    # Test case 1: A point inside the zone
    inside_point = (50, 50)
    is_intruding, _ = event_detector._check_intrusion(inside_point, conf=0.9)
    assert is_intruding

    # Test case 2: A point outside the zone
    outside_point = (200, 200)
    is_intruding, _ = event_detector._check_intrusion(outside_point, conf=0.9)
    assert not is_intruding