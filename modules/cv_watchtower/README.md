# 🧍‍♀️ CV Watchtower

The CV Watchtower is the Computer Vision module of NeuraCity.

## 🎯 Goal

Detect real-time visual events across campus via CCTV feeds or edge cameras, such as:
- Fall Detection
- Loitering Detection
- Lone Woman Detection
- Raised Hand / Help Gestures
- Distress Behavior

## 📦 Folder Structure (Recommended)

```bash
cv_watchtower/
├── models/           # YOLOv8 or custom models
├── scripts/          # Training, inference, data collection
├── data/             # Sample labeled data (if needed)
├── utils/            # Preprocessing, annotations, visualizers
└── README.md
```

## ✅ Tasks

- [ ] Train/integrate YOLOv8 models for key detections
- [ ] Setup real-time inference pipeline (OpenCV/streamlit)
- [ ] Trigger outputs via API or event logger

Please update this README with model versions, data sources, and usage instructions as you proceed.