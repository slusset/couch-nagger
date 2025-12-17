# API Reference

Complete API documentation for the Couch Nagger modules.

## dog_detector.DogDetector

Main class for detecting dogs on couches.

### Constructor

```python
DogDetector(model_path='yolov8m.pt')
```

Initializes a new dog detector instance.

**Parameters:**

- `model_path` (str, optional): Path to YOLOv8 model file. Defaults to 'yolov8m.pt'.
  - Supports: yolov8n.pt, yolov8s.pt, yolov8m.pt, yolov8l.pt, yolov8x.pt
  - Model will be downloaded automatically if not found

**Example:**

```python
# Use default medium model
detector = DogDetector()

# Use lightweight nano model for Raspberry Pi
detector = DogDetector(model_path='yolov8n.pt')

# Use custom model path
detector = DogDetector(model_path='/path/to/custom/model.pt')
```

### Methods

#### check_image

```python
check_image(image_path, conf_threshold=0.25)
```

Analyzes an image to detect if a dog is on a couch.

**Parameters:**

- `image_path` (str): Path to the image file to analyze
  - Supported formats: JPG, PNG, BMP, TIFF
  - Can be absolute or relative path

- `conf_threshold` (float, optional): Minimum confidence threshold for detections. Defaults to 0.25.
  - Range: 0.0 to 1.0
  - Lower values = more detections (more false positives)
  - Higher values = fewer detections (more false negatives)
  - Recommended: 0.25-0.5 for most use cases

**Returns:**

`dict` with the following structure:

```python
{
    'dog_on_couch': bool,      # True if dog detected on couch
    'confidence': {
        'dog': float,          # Highest dog detection confidence (0.0-1.0)
        'couch': float         # Highest couch detection confidence (0.0-1.0)
    }
}
```

**Example:**

```python
detector = DogDetector()

# Basic usage
result = detector.check_image('path/to/image.jpg')
print(f"Dog on couch: {result['dog_on_couch']}")
print(f"Dog confidence: {result['confidence']['dog']:.2f}")
print(f"Couch confidence: {result['confidence']['couch']:.2f}")

# With custom threshold
result = detector.check_image('path/to/image.jpg', conf_threshold=0.5)

# Check multiple images
images = ['img1.jpg', 'img2.jpg', 'img3.jpg']
for img in images:
    result = detector.check_image(img)
    if result['dog_on_couch']:
        print(f"Alert: Dog detected in {img}!")
```

**Behavior:**

- Returns `dog_on_couch=False` if no dog detected
- Returns `dog_on_couch=False` if no couch detected
- Returns `dog_on_couch=True` only if both dog and couch detected AND their bounding boxes overlap
- Confidence values are 0.0 if corresponding object not detected
- Uses highest confidence if multiple dogs or couches detected

### Class Attributes

```python
DogDetector.DOG_CLASS = 16     # COCO class ID for dogs
DogDetector.COUCH_CLASS = 57   # COCO class ID for couches/sofas
```

## dog_detector.boxes_overlap

Utility function for checking bounding box overlap.

```python
boxes_overlap(box1, box2)
```

**Parameters:**

- `box1` (list): First bounding box as [x1, y1, x2, y2]
  - x1, y1: top-left corner coordinates
  - x2, y2: bottom-right corner coordinates

- `box2` (list): Second bounding box as [x1, y1, x2, y2]

**Returns:**

`bool`: True if boxes overlap, False otherwise

**Example:**

```python
from dog_detector import boxes_overlap

dog_box = [100, 100, 300, 300]
couch_box = [200, 200, 500, 400]

if boxes_overlap(dog_box, couch_box):
    print("Dog is on the couch!")
```

**Algorithm:**

Boxes overlap if they intersect in both X and Y dimensions:

- Returns False if boxes only touch at edges
- Returns True for partial or complete overlap
- O(1) time complexity

## Usage Patterns

### Single Image Detection

```python
from dog_detector import DogDetector

detector = DogDetector()
result = detector.check_image('photo.jpg')

if result['dog_on_couch']:
    print("Alert: Dog on couch!")
```

### Batch Processing

```python
import os
from dog_detector import DogDetector

detector = DogDetector()
image_dir = 'images/'

for filename in os.listdir(image_dir):
    if filename.endswith(('.jpg', '.png')):
        path = os.path.join(image_dir, filename)
        result = detector.check_image(path)
        print(f"{filename}: {result['dog_on_couch']}")
```

### With Confidence Filtering

```python
detector = DogDetector()
result = detector.check_image('image.jpg')

if result['dog_on_couch']:
    dog_conf = result['confidence']['dog']
    couch_conf = result['confidence']['couch']
    
    if dog_conf > 0.8 and couch_conf > 0.7:
        print("High confidence detection!")
    else:
        print("Low confidence - manual review recommended")
```

### Integration with Notifications

```python
import time
from dog_detector import DogDetector

detector = DogDetector()

while True:
    result = detector.check_image('webcam_snapshot.jpg')
    
    if result['dog_on_couch']:
        send_alert(f"Fonzy on couch! Confidence: {result['confidence']['dog']:.0%}")
        time.sleep(300)  # Wait 5 minutes before next alert
    
    time.sleep(10)  # Check every 10 seconds
```

## Error Handling

The detector may raise the following exceptions:

- `FileNotFoundError`: If image_path does not exist
- `PIL.UnidentifiedImageError`: If image format is unsupported or corrupted
- `RuntimeError`: If model fails to load
- `torch.OutOfMemoryError`: If insufficient memory for inference

**Example with error handling:**

```python
from dog_detector import DogDetector
import logging

detector = DogDetector()

try:
    result = detector.check_image('photo.jpg')
except FileNotFoundError:
    logging.error("Image file not found")
except Exception as e:
    logging.error(f"Detection failed: {e}")
```

## Performance Notes

- First detection is slower due to model initialization
- Subsequent detections are faster (model cached in memory)
- GPU acceleration automatic if CUDA available
- Expected inference time:
  - CPU: 100-200ms per image
  - GPU: 10-30ms per image
  - Raspberry Pi: 2-5 seconds per image

For more details, see [Architecture](Architecture.md) and [Configuration](Configuration.md).
