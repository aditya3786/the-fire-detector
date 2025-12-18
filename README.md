# 🔥 Fire and Smoke Detection System

A real-time fire and smoke detection system using YOLOv8 with webcam support and Firebase alert integration.

## 📋 Overview

This project implements a deep learning-based fire and smoke detection system that can:
- Detect fire and smoke in real-time using webcam or video feeds
- Send automatic alerts to Firebase when fire/smoke is detected
- Process images, videos, or live camera streams
- Save annotated detection results

## 🎯 Features

- **Real-time Detection**: Process live webcam feeds with low latency
- **YOLOv8 Integration**: State-of-the-art object detection model
- **Firebase Alerts**: Automatic push notifications when fire/smoke is detected
- **Multiple Input Sources**: Support for webcam, video files, and RTSP streams
- **Custom Trained Models**: Pre-trained weights for fire and smoke detection
- **FPS Monitoring**: Real-time frame rate display
- **Video Recording**: Option to save annotated detection results

## 🗂️ Project Structure

```
├── webcam_fire_detect.py       # Main webcam detection script
├── detect_fire.py              # Detection with Firebase integration
├── firebase_alert.py           # Firebase alert module
├── yolo.py                     # YOLO model utilities
├── data.yaml                   # Dataset configuration
├── convert_annotations.py      # Annotation format converter
├── split_dataset.py            # Train/val/test dataset splitter
├── firedetectionfinal.ipynb    # Training notebook
├── weights/
│   ├── best.pt                 # Trained model weights
│   └── best_swapped.pt         # Alternative model weights
├── data/
│   ├── train/                  # Training images and labels
│   ├── val/                    # Validation images and labels
│   └── test/                   # Test images and labels
└── runs/                       # Detection results and outputs
```

## 🚀 Installation

### Prerequisites

- Python 3.8+
- CUDA-capable GPU (optional, but recommended)
- Webcam or video source

### Setup

1. Clone the repository:
```bash
cd DEEP\ LEARNING\ PROJECT
```

2. Install required packages:
```bash
pip install ultralytics opencv-python torch firebase-admin
```

3. (Optional) For Firebase integration, add your `serviceAccountKey.json` file to the project root.

## 💻 Usage

### Basic Webcam Detection

Run fire detection on your default webcam:
```bash
python webcam_fire_detect.py --weights weights/best_swapped.pt --device 0 --conf 0.35 --imgsz 640 --source 0
```

### Save Detection Video

Save the annotated video output:
```bash
python webcam_fire_detect.py --weights weights/best_swapped.pt --device 0 --conf 0.35 --imgsz 640 --source 0 --save
```

### Detection with Firebase Alerts

Run detection with automatic Firebase notifications:
```bash
python detect_fire.py
```

### Command Line Arguments

- `--weights`: Path to trained model weights (default: `weights/best.pt`)
- `--device`: CUDA device ID or 'cpu' (default: `0`)
- `--conf`: Confidence threshold for detections (default: `0.35`)
- `--imgsz`: Inference image size (default: `640`)
- `--source`: Camera index or video path (default: `0` for webcam)
- `--save`: Save annotated video output
- `--out`: Output video file path (default: `runs/webcam_fire.mp4`)

## 🎓 Model Training

The model was trained on a fire and smoke dataset with the following characteristics:

- **Classes**: `smoke`, `fire`
- **Training Images**: 14,122
- **Validation Images**: 3,099
- **Test Images**: 4,306

To train your own model, use the provided [firedetectionfinal.ipynb](firedetectionfinal.ipynb) notebook.

## 🔧 Firebase Setup

1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
2. Enable Realtime Database
3. Download your service account key as `serviceAccountKey.json`
4. Update the database URL in [detect_fire.py](detect_fire.py) and [firebase_alert.py](firebase_alert.py)

## 📊 Dataset Preparation

The project includes utilities for dataset management:

- **convert_annotations.py**: Convert annotation formats
- **split_dataset.py**: Split data into train/val/test sets
- **swapp(fire and smoke labels).ipynb**: Label swapping utilities

## 🎯 Model Performance

Two trained models are available:
- `best.pt`: Original trained model
- `best_swapped.pt`: Model with swapped fire/smoke labels

Choose the appropriate model based on your detection requirements.

## 🖥️ System Requirements

- **Minimum**: 
  - 4GB RAM
  - CPU with AVX support
  - Webcam (for real-time detection)

- **Recommended**:
  - 8GB+ RAM
  - NVIDIA GPU with CUDA support
  - 720p or higher resolution webcam

## 🐛 Troubleshooting

### Camera not opening
```bash
# Check available cameras
ls /dev/video*
# Try different source indices (0, 1, 2, etc.)
python webcam_fire_detect.py --source 1
```

### CUDA out of memory
```bash
# Use CPU instead
python webcam_fire_detect.py --device cpu
# Or reduce image size
python webcam_fire_detect.py --imgsz 320
```

## 📝 Notes

- Press `q` to quit the detection window
- Adjust `--conf` threshold for sensitivity (lower = more detections, higher = fewer false positives)
- For best results, ensure adequate lighting conditions
- Firebase alerts require valid service account credentials

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

## 📄 License

This project is available for educational and research purposes.

## 🙏 Acknowledgments

- YOLOv8 by Ultralytics
- Firebase by Google
- OpenCV library

---

**Note**: Ensure you have proper permissions before deploying this system in production environments. Always test thoroughly in your specific use case.
