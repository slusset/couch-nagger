# couch-nagger

Automated couch watcher and nagger to keep Fonzy off the couch!

## Overview

Couch Nagger uses YOLOv8 computer vision to detect when your dog is on the couch. Built with Python and designed to work on everything from Raspberry Pi to desktop computers, it provides a simple API for integration with notification systems, smart home devices, or automated alerts.

## Features

- 🐕 **Accurate dog detection** using state-of-the-art YOLOv8 model
- 🛋️ **Couch detection** with geometric overlap analysis  
- ⚡ **Fast inference** - configurable models from nano to extra-large
- 🎯 **Confidence scoring** for both dog and couch detections
- 🔧 **Easy integration** with notifications, cameras, and automation
- 🧪 **Comprehensive tests** ensuring reliable operation
- 📸 **Multi-platform** - works with webcams, Raspberry Pi Camera, IP cameras
- 🌙 **Low-light support** - detection works in various lighting conditions

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/slusset/couch-nagger.git
cd couch-nagger

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Raspberry Pi Setup

For Raspberry Pi (Bookworm or newer), we use a specific workflow to integrate with system camera libraries.

1.  **Install `uv`** (if not already installed):
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.local/bin/env
    ```

2.  **Bootstrap System Dependencies**:
    Run the provided script to install `python3-picamera2`, `rpicam-apps`, and other required system packages.
    ```bash
    ./scripts/pi_bootstrap.sh
    ```

3.  **Create Environment & Install**:
    We use the system python and system site packages to access the pre-installed camera libraries.
    ```bash
    # Create venv using system python and site packages
    uv venv .venv --python /usr/bin/python3 --system-site-packages
    source .venv/bin/activate

    # Install couch-nagger with Pi support
    uv pip install -e ".[raspberrypi]"
    ```

4.  **Verify Setup**:
    Run the health check script to ensure everything is working:
    ```bash
    ./scripts/pi_health_check.sh
    ```
    
    Or manually check camera access:
    ```bash
    python scripts/cam_test.py
    ```

### Basic Usage

```python
from dog_detector import DogDetector

# Initialize detector
detector = DogDetector()

# Check an image
result = detector.check_image('photo.jpg')

if result['dog_on_couch']:
    print(f"Alert! Dog detected on couch!")
    print(f"Confidence: {result['confidence']['dog']:.0%}")
```

## Documentation

Complete documentation is available in the [`docs/`](docs/) directory:

- **[Home](docs/Home.md)** - Project overview and quick start
- **[Installation](docs/Installation.md)** - Detailed setup instructions
- **[Architecture](docs/Architecture.md)** - System design and components
- **[API Reference](docs/API-Reference.md)** - Complete API documentation
- **[Configuration](docs/Configuration.md)** - Model selection and tuning
- **[Examples](docs/Examples.md)** - Usage examples and integrations
- **[Testing](docs/Testing.md)** - Test suite and validation
- **[Troubleshooting](docs/Troubleshooting.md)** - Common issues and solutions

## Example Integrations

### Webcam Monitoring

```python
import cv2
import time
from dog_detector import DogDetector

detector = DogDetector()
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    cv2.imwrite('temp.jpg', frame)
    
    result = detector.check_image('temp.jpg')
    if result['dog_on_couch']:
        print("Dog on couch!")
        # Add your alert here
    
    time.sleep(10)  # Check every 10 seconds
```

### Raspberry Pi Camera

```python
from picamera2 import Picamera2
from dog_detector import DogDetector

picam = Picamera2()
detector = DogDetector(model_path='yolov8n.pt')  # Lightweight model

picam.start()
picam.capture_file('snapshot.jpg')
result = detector.check_image('snapshot.jpg', conf_threshold=0.20)
```

See [Examples](docs/Examples.md) for more integration patterns including notifications, email alerts, and video processing.

## System Requirements

- Python 3.8 or higher
- 500MB-1GB RAM (depending on model)
- ~500MB disk space for model weights
- Optional: CUDA-capable GPU for faster inference

### Platform Support

- ✅ Linux (Ubuntu, Debian, etc.)
- ✅ macOS (Intel and Apple Silicon)
- ✅ Windows 10/11
- ✅ Raspberry Pi 3/4/5

## Testing

Run the test suite:

```bash
pytest tests/
```

The project includes comprehensive tests:
- Unit tests for overlap detection algorithm
- Integration tests with real images
- Edge case validation (low light, multiple objects, etc.)

See [Testing](docs/Testing.md) for details.

## Performance

| Platform | Model | Inference Time |
|----------|-------|----------------|
| Desktop CPU | yolov8m | 100-200ms |
| Desktop GPU | yolov8m | 10-30ms |
| Raspberry Pi 4 | yolov8n | 2-5s |

See [Configuration](docs/Configuration.md) for optimization tips.

## Project Structure

```
couch-nagger/
├── src/
│   └── dog_detector/
│       ├── __init__.py
│       └── dog_detector.py      # Core detection logic
├── tests/
│   ├── test_dog_detector.py     # Test suite
│   └── debug_detection.py       # Debug utilities
├── images/                       # Test images
├── docs/                         # Documentation
├── requirements.txt              # Python dependencies
├── setup.py                      # Package setup
└── README.md                     # This file
```

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

See [Architecture](docs/Architecture.md) for design details.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- Trained on [COCO dataset](https://cocodataset.org/)
- Inspired by the need to keep Fonzy off the furniture! 🐕

## Support

- 📖 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/slusset/couch-nagger/issues)
- 💬 [Discussions](https://github.com/slusset/couch-nagger/discussions)

---

**Note:** This project is for educational and personal use. Detection accuracy may vary based on camera quality, lighting conditions, and environment.
