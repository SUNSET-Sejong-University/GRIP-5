# Gesture Responsive Intelligent Prosthetic (GRIP) - 5

<div align="center">
  <img src="https://github.com/SUNSET-Sejong-University/GRIP-5/blob/main/media/GRIP5-v1-Circuit-Diag.png?raw=true" alt="GRIP-5 Circuit Diagram" width="600"/>
</div>

## Overview

**GRIP-5** (Gesture Responsive Intelligent Prosthetic) is an advanced prosthetic hand system that uses computer vision and machine learning to interpret hand gestures and translate them into precise prosthetic movements. This project combines gesture recognition with real-time motion control to create a more natural and intuitive prosthetic experience.

The system utilizes MediaPipe's hand landmark detection to recognize and track hand positions, enabling seamless gesture-to-motion mapping for prosthetic control.

---

## 🎯 Key Features

- **Real-time Gesture Recognition** - Uses MediaPipe to detect and track 21 hand landmarks for accurate gesture classification
- **Intelligent Motion Control** - Python-based gesture processing with C++ optimization for low-latency prosthetic response
- **Circuit Integration** - Professionally designed electronics to interface gesture commands with motor control
- **Scalable Architecture** - Modular design allowing for extension to multiple gesture types
- **Computer Vision Pipeline** - Robust hand detection and tracking with environmental adaptability

---

## 🔧 Technology Stack

This project is built with a hybrid technology approach:

| Technology | Percentage | Purpose |
|-----------|-----------|---------|
| **Python** | 68.1% | Gesture recognition, ML models, control logic |
| **C++** | 31.9% | Real-time motor control, hardware optimization, performance-critical operations |

### Key Libraries & Tools

- **MediaPipe** - Hand landmark detection and gesture tracking
- **OpenCV** - Computer vision pipeline and image processing
- **TensorFlow/PyTorch** - Machine learning model inference
- **Hardware Drivers** - C++ interfaces for motor and sensor communication

---

## 📋 Hand Gesture Recognition

The system uses MediaPipe's hand landmark model to detect 21 keypoints on the human hand:

<div align="center">
  <img src="https://github.com/SUNSET-Sejong-University/GRIP-5/blob/main/media/hand-landmarks.png?raw=true" alt="MediaPipe Hand Landmarks" width="500"/>
  <p><em>MediaPipe Hand Landmark Points - Used for gesture classification and motion mapping</em></p>
</div>

These 21 landmarks enable:
- **Finger position tracking** - Each finger joint is monitored in 3D space
- **Gesture classification** - Combinations of landmark positions are mapped to specific prosthetic movements
- **Motion prediction** - Smooth interpolation between gestures for natural prosthetic behavior

---

## 🛠️ Circuit Design

The GRIP-5 system integrates carefully designed electronics to convert gesture commands into prosthetic actuation:

<div align="center">
  <img src="https://github.com/SUNSET-Sejong-University/GRIP-5/blob/main/media/GRIP5-v1-Circuit-Diag.png?raw=true" alt="GRIP-5 Circuit Diagram" width="700"/>
  <p><em>GRIP-5 v1 Circuit Architecture - Hardware interface for prosthetic control</em></p>
</div>

The circuit diagram shows:
- **Sensor Input Stage** - Camera and IMU sensor interfaces
- **Processing Unit** - Main controller for running gesture recognition
- **Motor Driver Stage** - Precision control for prosthetic actuators
- **Power Management** - Battery monitoring and distribution

---

## 📁 Project Structure

```
GRIP-5/
├── README.md
├── media/
│   ├── GRIP5-v1-Circuit-Diag.png      # Hardware circuit design
│   └── hand-landmarks.png              # MediaPipe hand landmark reference
├── src/
│   ├── gesture_recognition/
│   │   └── hand_detector.py            # MediaPipe gesture detection
│   ├── prosthetic_control/
│   │   ├── motor_controller.cpp        # C++ motor control interface
│   │   └── motion_mapper.py            # Gesture-to-motion mapping
│   └── utils/
│       └── config.py                   # Configuration settings
├── models/
│   └── gesture_models/                 # Trained ML models
├── tests/
│   └── test_gestures.py                # Unit tests
└── requirements.txt                    # Python dependencies
```

---

## 🚀 Installation & Setup

### Prerequisites

- Python 3.8+
- C++ compiler (GCC 9+ or MSVC)
- OpenCV 4.5+
- CUDA 11.0+ (optional, for GPU acceleration)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/SUNSET-Sejong-University/GRIP-5.git
   cd GRIP-5
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Build C++ components**
   ```bash
   cd src/prosthetic_control
   mkdir build && cd build
   cmake ..
   make
   ```

5. **Run gesture recognition**
   ```bash
   python src/gesture_recognition/hand_detector.py
   ```

---

## 💻 Usage

### Basic Gesture Recognition

```python
from src.gesture_recognition.hand_detector import GestureRecognizer
import cv2

# Initialize the gesture recognizer
recognizer = GestureRecognizer()

# Capture video from webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Detect gestures
    gesture, confidence = recognizer.detect(frame)
    
    # Display results
    cv2.putText(frame, f"Gesture: {gesture} ({confidence:.2f})", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("GRIP-5 Gesture Recognition", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

### Prosthetic Control

```cpp
#include "motor_controller.h"

int main() {
    MotorController controller;
    controller.initialize();
    
    // Map gesture to motor commands
    controller.executeGesture("open_hand", 100);  // intensity: 0-100
    
    return 0;
}
```

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork the repository** and create a feature branch
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and test thoroughly
   ```bash
   python -m pytest tests/
   ```

3. **Commit with clear messages**
   ```bash
   git commit -m "Add feature: description of changes"
   ```

4. **Push and create a Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run linters and formatters
black src/
pylint src/
```

---

## 📊 Performance

- **Gesture Detection Latency**: < 50ms
- **Hand Tracking FPS**: 30+ FPS on standard hardware
- **Motor Response Time**: < 100ms
- **Accuracy**: 95%+ gesture recognition confidence

---

## 📝 License

This project is licensed under the **GNU General Public License v3.0**. See the LICENSE file for details.

---

## 🙏 Acknowledgments

- **MediaPipe** - For providing robust hand landmark detection models
- **OpenCV** - Computer vision library backbone
- **SUNSET Lab** - Sejong University research group
- **Contributors** - All team members and contributors to this project

---

## 📧 Contact & Support

- **Organization**: [SUNSET Lab - Sejong University](https://github.com/SUNSET-Sejong-University)
- **Project Issues**: [GitHub Issues](https://github.com/SUNSET-Sejong-University/GRIP-5/issues)
- **Discussions**: [GitHub Discussions](https://github.com/SUNSET-Sejong-University/GRIP-5/discussions)

---

## 🔬 Research & Publications

For more information about the GRIP-5 project and underlying research, please visit the [SUNSET Lab](https://github.com/SUNSET-Sejong-University) organization page.

---

<div align="center">
  <p><strong>GRIP-5: Making Prosthetics More Intuitive Through Gesture Recognition</strong></p>
  <p>Built with ❤️ by the SUNSET Lab at Sejong University</p>
</div>
