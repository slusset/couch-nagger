# Configuration Guide

This guide covers configuration options and tuning parameters for optimal detection performance.

## Model Selection

Choose the right YOLOv8 model based on your requirements:

### Model Comparison

| Model | Size | Speed (CPU) | mAP | Use Case |
|-------|------|-------------|-----|----------|
| yolov8n.pt | 6 MB | ~50ms | 37.3 | Raspberry Pi, edge devices |
| yolov8s.pt | 22 MB | ~100ms | 44.9 | Balanced for mobile |
| yolov8m.pt | 50 MB | ~150ms | 50.2 | **Default - best balance** |
| yolov8l.pt | 87 MB | ~250ms | 52.9 | High accuracy needed |
| yolov8x.pt | 136 MB | ~400ms | 53.9 | Maximum accuracy |

### Changing Models

```python
from dog_detector import DogDetector

# Lightweight for Raspberry Pi
detector = DogDetector(model_path='yolov8n.pt')

# High accuracy for critical applications
detector = DogDetector(model_path='yolov8x.pt')
```

**Model Download:**
Models are automatically downloaded on first use. You can pre-download:

```bash
wget https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8n.pt
wget https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8s.pt
wget https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8m.pt
wget https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8l.pt
wget https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8x.pt
```

## Confidence Threshold Tuning

The confidence threshold determines how certain the model must be before reporting a detection.

### Default Threshold

```python
result = detector.check_image('image.jpg')  # Uses 0.25 default
```

### Adjusting Threshold

```python
# More lenient - catches more detections (may have false positives)
result = detector.check_image('image.jpg', conf_threshold=0.15)

# Default - balanced
result = detector.check_image('image.jpg', conf_threshold=0.25)

# Stricter - fewer false positives (may miss some detections)
result = detector.check_image('image.jpg', conf_threshold=0.5)

# Very strict - high precision
result = detector.check_image('image.jpg', conf_threshold=0.7)
```

### Threshold Guidelines

**Low confidence (0.15-0.25):**
- Use when: Low light conditions, distant objects, or need to catch all instances
- Trade-off: More false positives
- Example: Raspberry Pi camera in poor lighting

**Medium confidence (0.25-0.5):**
- Use when: Standard conditions, typical use cases
- Trade-off: Balanced precision/recall
- Example: Webcam in normal indoor lighting (default)

**High confidence (0.5-0.7):**
- Use when: Need high precision, can't afford false alarms
- Trade-off: May miss some valid detections
- Example: Automated alert system where false alerts are costly

**Very high confidence (0.7+):**
- Use when: Only want extremely obvious detections
- Trade-off: Will miss many valid cases
- Example: Testing or debugging

### Adaptive Thresholding

Adjust threshold based on recent results:

```python
def adaptive_check(detector, image_path, recent_false_positives):
    # Increase threshold if too many false positives
    if recent_false_positives > 5:
        threshold = 0.5
    elif recent_false_positives > 2:
        threshold = 0.35
    else:
        threshold = 0.25
    
    return detector.check_image(image_path, conf_threshold=threshold)
```

## Image Preprocessing

Preprocess images for better detection:

### Resize Large Images

```python
from PIL import Image

def preprocess_image(image_path, max_size=1280):
    img = Image.open(image_path)
    
    # Resize if too large
    if max(img.size) > max_size:
        img.thumbnail((max_size, max_size), Image.LANCZOS)
        output_path = 'temp_resized.jpg'
        img.save(output_path)
        return output_path
    
    return image_path

# Use it
processed = preprocess_image('large_image.jpg')
result = detector.check_image(processed)
```

### Enhance Low-Light Images

```python
import cv2
import numpy as np

def enhance_contrast(image_path):
    img = cv2.imread(image_path)
    
    # Convert to LAB color space
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # Apply CLAHE to L channel
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    l = clahe.apply(l)
    
    # Merge and convert back
    enhanced_lab = cv2.merge([l, a, b])
    enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
    
    output_path = 'temp_enhanced.jpg'
    cv2.imwrite(output_path, enhanced)
    return output_path

# Use with lower threshold for low-light
enhanced = enhance_contrast('dark_image.jpg')
result = detector.check_image(enhanced, conf_threshold=0.20)
```

## Performance Optimization

### GPU Acceleration

Enable CUDA if available:

```python
import torch

if torch.cuda.is_available():
    print(f"GPU available: {torch.cuda.get_device_name(0)}")
else:
    print("Using CPU")

# Model automatically uses GPU if available
detector = DogDetector()  # Will use GPU if CUDA installed
```

### Batch Processing

Process multiple images efficiently:

```python
from pathlib import Path

def batch_detect(detector, image_dir, conf_threshold=0.25):
    results = {}
    
    # Get all images
    images = list(Path(image_dir).glob('*.jpg'))
    
    # Process each
    for img_path in images:
        result = detector.check_image(str(img_path), conf_threshold)
        results[img_path.name] = result
    
    return results

# Use it
detector = DogDetector()
results = batch_detect(detector, 'images/', conf_threshold=0.3)

for filename, result in results.items():
    if result['dog_on_couch']:
        print(f"{filename}: DOG ON COUCH!")
```

### Reduce Inference Frequency

For real-time monitoring, don't check every frame:

```python
import time

def smart_monitor(detector, image_source, check_interval=10):
    """Check every N seconds instead of continuously"""
    while True:
        result = detector.check_image(image_source)
        
        if result['dog_on_couch']:
            send_alert()
            time.sleep(300)  # Wait 5 min after alert
        else:
            time.sleep(check_interval)  # Check every 10 sec
```

## Platform-Specific Configuration

### Raspberry Pi

```python
# Use lightweight model
detector = DogDetector(model_path='yolov8n.pt')

# Lower threshold for Pi camera quality
result = detector.check_image('rpicam.jpg', conf_threshold=0.20)

# Resize images before detection
from PIL import Image
img = Image.open('rpicam.jpg')
img.thumbnail((640, 640))
img.save('resized.jpg')
result = detector.check_image('resized.jpg')
```

**Recommended Pi Settings:**
- Model: yolov8n.pt
- Threshold: 0.20-0.30
- Image size: 640x640 or smaller
- Check interval: 5-10 seconds

### Desktop/Server

```python
# Use medium or large model for accuracy
detector = DogDetector(model_path='yolov8m.pt')

# Standard threshold
result = detector.check_image('webcam.jpg', conf_threshold=0.25)

# Can handle larger images
result = detector.check_image('4k_image.jpg')
```

**Recommended Desktop Settings:**
- Model: yolov8m.pt or yolov8l.pt
- Threshold: 0.25-0.40
- Image size: Original (will be auto-resized by YOLO)
- Check interval: 1-5 seconds

### GPU Server

```python
# Use largest model for maximum accuracy
detector = DogDetector(model_path='yolov8x.pt')

# Strict threshold for precision
result = detector.check_image('image.jpg', conf_threshold=0.50)

# Can batch process
images = ['img1.jpg', 'img2.jpg', 'img3.jpg']
results = [detector.check_image(img) for img in images]
```

**Recommended GPU Settings:**
- Model: yolov8l.pt or yolov8x.pt
- Threshold: 0.30-0.50
- Image size: Original
- Check interval: Real-time possible

## Environment Variables

Configure via environment variables:

```bash
# Set model path
export YOLO_MODEL_PATH="/path/to/models/yolov8m.pt"

# Set confidence threshold
export DETECTION_THRESHOLD="0.35"

# Use in code
import os
from dog_detector import DogDetector

model_path = os.getenv('YOLO_MODEL_PATH', 'yolov8m.pt')
threshold = float(os.getenv('DETECTION_THRESHOLD', '0.25'))

detector = DogDetector(model_path=model_path)
result = detector.check_image('image.jpg', conf_threshold=threshold)
```

## Logging and Monitoring

Add logging to track performance:

```python
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def monitored_detection(detector, image_path, conf_threshold=0.25):
    start_time = time.time()
    
    try:
        result = detector.check_image(image_path, conf_threshold)
        inference_time = time.time() - start_time
        
        logger.info(
            f"Detection completed in {inference_time:.2f}s - "
            f"Dog: {result['dog_on_couch']}, "
            f"Confidence: dog={result['confidence']['dog']:.2f}, "
            f"couch={result['confidence']['couch']:.2f}"
        )
        
        return result
    except Exception as e:
        logger.error(f"Detection failed: {e}")
        raise

# Use it
detector = DogDetector()
result = monitored_detection(detector, 'image.jpg')
```

## Testing Different Configurations

Experiment to find optimal settings:

```python
def test_configurations(detector, test_images):
    """Test various thresholds on test images"""
    thresholds = [0.15, 0.25, 0.35, 0.50]
    
    for threshold in thresholds:
        print(f"\nTesting threshold: {threshold}")
        
        for img_path in test_images:
            result = detector.check_image(img_path, conf_threshold=threshold)
            print(f"  {img_path}: {result['dog_on_couch']} "
                  f"(dog: {result['confidence']['dog']:.2f}, "
                  f"couch: {result['confidence']['couch']:.2f})")

# Run tests
detector = DogDetector()
test_images = [
    'images/test_dog_on_couch.jpg',
    'images/test_dog_on_floor.jpg',
    'images/test_empty_couch.jpg'
]
test_configurations(detector, test_images)
```

## Best Practices

1. **Start with defaults** - Use yolov8m.pt and 0.25 threshold
2. **Profile your use case** - Test with real images from your environment
3. **Monitor false positives/negatives** - Adjust based on actual performance
4. **Preprocess images** - Resize large images, enhance low-light
5. **Use appropriate hardware** - Match model size to available resources
6. **Log results** - Track confidence scores and inference times
7. **Test edge cases** - Validate with various lighting and angles

For more information, see [Architecture](Architecture.md) and [Troubleshooting](Troubleshooting.md).
