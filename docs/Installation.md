# Installation Guide

This guide covers setting up the Couch Nagger project from scratch.

## Prerequisites

- Python 3.8 or higher
- pip package manager
- ~500MB disk space for YOLOv8 model weights

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/slusset/couch-nagger.git
cd couch-nagger
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages including:

- **ultralytics** (8.3.225) - YOLOv8 implementation
- **torch** (2.9.0) - PyTorch deep learning framework
- **opencv-python** (4.12.0.88) - Computer vision library
- **numpy** (2.2.6) - Numerical computing
- **pillow** (12.0.0) - Image processing
- And other supporting libraries

### 4. Install Package in Development Mode

```bash
pip install -e .
```

This installs the `dog_detector` module in editable mode, allowing you to import it from anywhere.

### 5. Download YOLOv8 Model

The first time you run the detector, it will automatically download the YOLOv8m model (~50MB):

```python
from dog_detector import DogDetector
detector = DogDetector()  # Downloads yolov8m.pt on first run
```

Alternatively, you can download it manually:

```bash
wget https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8m.pt
```

## Verify Installation

Run the test suite to verify everything is working:

```bash
pytest tests/
```

You should see all tests passing:

```
tests/test_dog_detector.py::TestBoxOverlap::test_boxes_completely_overlap PASSED
tests/test_dog_detector.py::TestBoxOverlap::test_boxes_no_overlap PASSED
...
```

## Platform-Specific Notes

### Linux

No additional configuration needed. PyTorch will use CPU by default.

### macOS

For Apple Silicon (M1/M2), PyTorch will automatically use MPS acceleration when available.

### Windows

Ensure Microsoft Visual C++ 14.0 or greater is installed for some dependencies.

### Raspberry Pi

For Raspberry Pi deployments:

1. Use a lighter model for better performance:
   ```python
   detector = DogDetector(model_path='yolov8n.pt')  # Nano model
   ```

2. Consider reducing image resolution before detection

3. Expected inference time: ~2-5 seconds per image on Pi 4

## GPU Support (Optional)

To enable CUDA GPU acceleration:

1. Install CUDA toolkit (11.8 or 12.1)
2. Install PyTorch with CUDA support:
   ```bash
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
   ```

## Troubleshooting

**Import Error**: If you get `ModuleNotFoundError: No module named 'dog_detector'`, make sure you ran `pip install -e .`

**Model Download Fails**: Check your internet connection and try downloading the model manually

**Out of Memory**: Use a smaller model (yolov8n.pt) or reduce image resolution

For more issues, see the [Troubleshooting](Troubleshooting) page.
