# Troubleshooting Guide

Common issues and solutions for the Couch Nagger project.

## Installation Issues

### ModuleNotFoundError: No module named 'dog_detector'

**Problem:** Can't import the dog_detector module.

**Solution:**
```bash
# Make sure you're in the project root directory
cd couch-nagger

# Install in editable mode
pip install -e .

# Verify installation
python -c "from dog_detector import DogDetector; print('Success!')"
```

### Model Download Fails

**Problem:** YOLOv8 model doesn't download automatically.

**Solution 1:** Check internet connection and retry.

**Solution 2:** Download manually:
```bash
wget https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8m.pt
# Place in project root or specify path in code
```

**Solution 3:** Use different mirror:
```python
from ultralytics import YOLO
model = YOLO('yolov8m.pt', verbose=True)  # Shows download progress
```

### Dependency Installation Errors

**Problem:** Error installing torch, opencv-python, or other dependencies.

**For Windows:**
```bash
# Install Visual C++ Build Tools first
# Then retry pip install
pip install --upgrade pip
pip install -r requirements.txt
```

**For Linux:**
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install python3-dev python3-pip
sudo apt-get install libgl1-mesa-glx  # For OpenCV

pip install -r requirements.txt
```

**For macOS:**
```bash
# Use Homebrew
brew install python3
pip3 install -r requirements.txt
```

## Detection Issues

### False Negatives (Missing Detections)

**Problem:** Dog is clearly on couch but not detected.

**Diagnosis:**
```python
from dog_detector import DogDetector

detector = DogDetector()
result = detector.check_image('problematic_image.jpg')

print(f"Dog detected: {result['confidence']['dog'] > 0}")
print(f"Dog confidence: {result['confidence']['dog']:.3f}")
print(f"Couch detected: {result['confidence']['couch'] > 0}")
print(f"Couch confidence: {result['confidence']['couch']:.3f}")
```

**Solutions:**

1. **Lower confidence threshold:**
   ```python
   result = detector.check_image('image.jpg', conf_threshold=0.15)
   ```

2. **Use larger model:**
   ```python
   detector = DogDetector(model_path='yolov8l.pt')
   ```

3. **Enhance image:**
   ```python
   import cv2
   img = cv2.imread('dark_image.jpg')
   enhanced = cv2.convertScaleAbs(img, alpha=1.5, beta=30)
   cv2.imwrite('enhanced.jpg', enhanced)
   result = detector.check_image('enhanced.jpg')
   ```

4. **Check with debug script:**
   ```bash
   python tests/debug_detection.py
   ```

### False Positives (Incorrect Detections)

**Problem:** System reports dog on couch when there isn't one.

**Solutions:**

1. **Increase confidence threshold:**
   ```python
   result = detector.check_image('image.jpg', conf_threshold=0.5)
   ```

2. **Check detection details:**
   ```python
   result = detector.check_image('image.jpg')
   if result['dog_on_couch']:
       print(f"Dog conf: {result['confidence']['dog']:.3f}")
       print(f"Couch conf: {result['confidence']['couch']:.3f}")
       # Require high confidence for both
       if result['confidence']['dog'] > 0.7 and result['confidence']['couch'] > 0.6:
           print("High confidence - likely correct")
   ```

3. **Verify with visualization:**
   ```python
   from ultralytics import YOLO
   model = YOLO('yolov8m.pt')
   results = model('image.jpg')
   results[0].plot()  # Shows bounding boxes
   ```

### Dog and Couch Detected But No Overlap

**Problem:** Both objects detected but `dog_on_couch` is False.

**Diagnosis:**
```python
from ultralytics import YOLO
from dog_detector import boxes_overlap

model = YOLO('yolov8m.pt')
results = model('image.jpg')

dog_boxes = []
couch_boxes = []

for box in results[0].boxes:
    class_id = int(box.cls[0])
    bbox = box.xyxy[0].tolist()
    
    if class_id == 16:  # Dog
        dog_boxes.append(bbox)
        print(f"Dog box: {bbox}")
    elif class_id == 57:  # Couch
        couch_boxes.append(bbox)
        print(f"Couch box: {bbox}")

# Check overlap
for dog in dog_boxes:
    for couch in couch_boxes:
        print(f"Overlap: {boxes_overlap(dog, couch)}")
```

**Solutions:**

1. Box coordinates might be close but not overlapping. This is actually correct behavior - dog might be near but not on couch.

2. If you want to detect "near couch" as well, modify overlap logic:
   ```python
   def boxes_near(box1, box2, margin=50):
       # Expand boxes by margin
       x1_min, y1_min, x1_max, y1_max = box1
       x2_min, y2_min, x2_max, y2_max = box2
       
       box1_expanded = [x1_min-margin, y1_min-margin, 
                        x1_max+margin, y1_max+margin]
       
       return boxes_overlap(box1_expanded, box2)
   ```

## Performance Issues

### Slow Detection Speed

**Problem:** Detection takes too long.

**Measured Performance:**
```python
import time
from dog_detector import DogDetector

detector = DogDetector()

start = time.time()
result = detector.check_image('image.jpg')
elapsed = time.time() - start

print(f"Detection took {elapsed:.2f} seconds")
```

**Solutions:**

1. **Use smaller model:**
   ```python
   detector = DogDetector(model_path='yolov8n.pt')  # Much faster
   ```

2. **Resize images:**
   ```python
   from PIL import Image
   
   img = Image.open('large_image.jpg')
   img.thumbnail((640, 640))
   img.save('resized.jpg')
   result = detector.check_image('resized.jpg')
   ```

3. **Enable GPU (if available):**
   ```bash
   # Install PyTorch with CUDA
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
   
   # Verify GPU available
   python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
   ```

4. **Reduce check frequency:**
   ```python
   # Instead of checking every second
   time.sleep(10)  # Check every 10 seconds
   ```

### Out of Memory Errors

**Problem:** `RuntimeError: CUDA out of memory` or system freezes.

**Solutions:**

1. **Use smaller model:**
   ```python
   detector = DogDetector(model_path='yolov8n.pt')
   ```

2. **Process smaller images:**
   ```python
   from PIL import Image
   
   img = Image.open('huge_image.jpg')
   img.thumbnail((640, 640))
   img.save('small.jpg')
   ```

3. **Clear CUDA cache (if using GPU):**
   ```python
   import torch
   torch.cuda.empty_cache()
   ```

4. **Reduce batch size (if processing multiple images):**
   ```python
   # Process one at a time instead of batching
   for img in images:
       result = detector.check_image(img)
   ```

## Raspberry Pi Issues

### Very Slow on Raspberry Pi

**Problem:** Detection takes 5+ seconds on Raspberry Pi.

**Solutions:**

1. **Use nano model:**
   ```python
   detector = DogDetector(model_path='yolov8n.pt')
   ```

2. **Reduce image size from Pi Camera:**
   ```python
   from picamera2 import Picamera2
   
   picam = Picamera2()
   config = picam.create_still_configuration(
       main={"size": (640, 480)}  # Smaller resolution
   )
   picam.configure(config)
   ```

3. **Increase check interval:**
   ```python
   time.sleep(15)  # Check every 15 seconds instead of 5
   ```

4. **Consider motion detection first:**
   ```python
   # Only run YOLO when motion detected
   if has_motion():
       result = detector.check_image('frame.jpg')
   ```

### Pi Camera Not Working

**Problem:** Camera not detected or errors capturing images.

**Solutions:**

1. **Enable camera:**
   ```bash
   sudo raspi-config
   # Interface Options -> Camera -> Enable
   sudo reboot
   ```

2. **Install picamera2:**
   ```bash
   sudo apt-get install python3-picamera2
   ```

3. **Check camera:**
   ```bash
   libcamera-still -o test.jpg
   ```

4. **Use correct imports:**
   ```python
   # For newer Pi OS (Bookworm)
   from picamera2 import Picamera2
   
   # For older Pi OS
   from picamera import PiCamera
   ```

## Test Failures

### Tests Fail After Model Update

**Problem:** Tests pass locally but fail in CI or after updating YOLO.

**Solution:**

Update expected confidence thresholds in tests:
```python
def test_dog_on_couch_detected(self):
    result = self.detector.check_image(str(image_path))
    assert result['dog_on_couch'] == True
    # Adjust these thresholds if model changed
    assert result['confidence']['dog'] > 0.4  # Was 0.5
    assert result['confidence']['couch'] > 0.4  # Was 0.5
```

### Import Errors in Tests

**Problem:** Tests can't find modules.

**Solution:**
```bash
# Install package in editable mode
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

## Image Quality Issues

### Poor Detection in Low Light

**Problem:** Detection fails in dim lighting.

**Solutions:**

1. **Enhance image first:**
   ```python
   import cv2
   
   img = cv2.imread('dark.jpg')
   # Increase brightness and contrast
   enhanced = cv2.convertScaleAbs(img, alpha=1.5, beta=30)
   cv2.imwrite('bright.jpg', enhanced)
   
   result = detector.check_image('bright.jpg', conf_threshold=0.20)
   ```

2. **Use CLAHE (Contrast Limited Adaptive Histogram Equalization):**
   ```python
   import cv2
   
   img = cv2.imread('dark.jpg')
   lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
   l, a, b = cv2.split(lab)
   
   clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
   l = clahe.apply(l)
   
   enhanced = cv2.merge([l, a, b])
   enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
   cv2.imwrite('enhanced.jpg', enhanced)
   ```

3. **Improve lighting:**
   - Add lights near camera
   - Use IR illuminator for night vision
   - Position camera to avoid backlighting

### Blurry Images from Motion

**Problem:** Detection fails because images are blurry.

**Solutions:**

1. **Increase camera shutter speed**
2. **Wait for motion to stop before capturing**
3. **Use motion detection to trigger capture**
4. **Capture multiple frames and use the sharpest one**

## Network/Connectivity Issues

### Can't Download Model

**Problem:** Firewall or network blocks model download.

**Solution:**

Download from alternative source:
```bash
# Try direct download
curl -L -o yolov8m.pt \
  https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8m.pt

# Or use wget
wget https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8m.pt
```

## Getting Help

### Debug Checklist

Before asking for help, try these steps:

1. **Check Python version:**
   ```bash
   python --version  # Should be 3.8+
   ```

2. **Verify installation:**
   ```bash
   pip list | grep ultralytics
   pip list | grep torch
   ```

3. **Test basic detection:**
   ```python
   from dog_detector import DogDetector
   detector = DogDetector()
   print("Detector initialized successfully")
   ```

4. **Run debug script:**
   ```bash
   python tests/debug_detection.py
   ```

5. **Check logs:**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

### Reporting Issues

When reporting issues, include:

1. **System information:**
   ```bash
   python --version
   pip list
   uname -a  # or systeminfo on Windows
   ```

2. **Error message** (full traceback)

3. **Minimal reproducible example**

4. **Sample image** (if relevant)

5. **Expected vs actual behavior**

### Community Resources

- **GitHub Issues**: https://github.com/slusset/couch-nagger/issues
- **Ultralytics Docs**: https://docs.ultralytics.com
- **YOLOv8 FAQ**: https://github.com/ultralytics/ultralytics/discussions

## Common Error Messages

### "No module named 'torch'"

```bash
pip install torch torchvision
```

### "FileNotFoundError: [Errno 2] No such file or directory"

Check that image path is correct:
```python
from pathlib import Path
img_path = Path('image.jpg')
print(f"Exists: {img_path.exists()}")
print(f"Absolute path: {img_path.absolute()}")
```

### "RuntimeError: Couldn't load custom C++ ops"

Usually harmless. If causing issues:
```bash
pip uninstall torch torchvision
pip install torch torchvision --no-cache-dir
```

### "PIL.UnidentifiedImageError: cannot identify image file"

Image file is corrupted or not a valid image:
```python
from PIL import Image
try:
    img = Image.open('file.jpg')
    img.verify()
    print("Image is valid")
except Exception as e:
    print(f"Image error: {e}")
```

For additional help, see [Architecture](Architecture.md) and [Configuration](Configuration.md).
