# Architecture Overview

This document describes the design and architecture of the Couch Nagger system.

## System Components

```
couch-nagger/
├── src/
│   └── dog_detector/
│       ├── __init__.py
│       └── dog_detector.py       # Core detection logic
├── tests/
│   ├── test_dog_detector.py      # Automated tests
│   └── debug_detection.py        # Debug utilities
├── images/                        # Test images
└── spike.py                       # Experimental code
```

## Core Module: DogDetector

The `DogDetector` class is the main interface for the system.

### Design Principles

1. **Single Responsibility**: The detector focuses solely on image analysis
2. **Dependency Injection**: Model path can be configured at initialization
3. **Clean API**: Simple `check_image()` method returns structured results
4. **Testability**: Pure functions for overlap detection enable easy unit testing

### Class Structure

```python
class DogDetector:
    def __init__(self, model_path='yolov8m.pt')
    def check_image(self, image_path, conf_threshold=0.25)
```

**Initialization**:
- Loads YOLOv8 model (downloads if not present)
- Stores class IDs for dog (16) and couch (57)

**Detection Pipeline**:
1. Load image using YOLOv8
2. Run inference with confidence threshold
3. Filter detections for dogs and couches
4. Check for bounding box overlap
5. Return structured results with confidence scores

## Bounding Box Overlap Detection

The `boxes_overlap()` function implements a geometric intersection algorithm:

```python
def boxes_overlap(box1, box2):
    """Check if two bounding boxes overlap.
    box format: [x1, y1, x2, y2]
    """
```

### Algorithm

Two boxes overlap if they intersect in both X and Y dimensions:

- No overlap if one box is completely left/right of the other
- No overlap if one box is completely above/below the other
- Otherwise, boxes overlap

This is an efficient O(1) algorithm that avoids calculating intersection areas.

### Edge Cases

- **Touching edges**: Considered non-overlapping (`<=` comparison)
- **Complete containment**: Returns True
- **Partial overlap**: Returns True

## YOLO Integration

### Model Selection

The project uses YOLOv8m (medium) by default:

- **Accuracy**: Good balance of speed and accuracy
- **Size**: ~50MB model file
- **Inference**: ~100-200ms on modern CPU

Alternative models:

| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| yolov8n | 6MB | Fastest | Lower |
| yolov8s | 22MB | Fast | Good |
| yolov8m | 50MB | Medium | Better |
| yolov8l | 87MB | Slow | Best |
| yolov8x | 136MB | Slowest | Best |

### COCO Class IDs

YOLOv8 is trained on the COCO dataset with 80 classes:

- Class 16: Dog
- Class 57: Couch (sofa)

Other potentially useful classes:
- Class 15: Cat
- Class 0: Person
- Class 56: Chair

## Data Flow

```
┌─────────────┐
│ Image Input │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ YOLOv8 Detector │
└──────┬──────────┘
       │
       ▼
┌──────────────────┐
│ Filter Classes   │
│ (Dog=16,Couch=57)│
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Overlap Check    │
│ (Geometric Test) │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Result Dictionary│
│ - dog_on_couch   │
│ - confidence     │
└──────────────────┘
```

## Extensibility Points

### 1. Custom Confidence Thresholds

```python
result = detector.check_image(path, conf_threshold=0.5)  # More strict
```

### 2. Additional Object Classes

Extend the detector to track other objects:

```python
self.CAT_CLASS = 15
self.CHAIR_CLASS = 56
```

### 3. Notification Integration

The detector focuses on detection only. Integrate with notification systems:

```python
if result['dog_on_couch']:
    send_notification("Fonzy is on the couch!")
    play_sound("off.wav")
```

### 4. Image Sources

While the current implementation uses static images, it can be extended to:

- Webcam/USB camera feeds
- IP camera streams (RTSP)
- Raspberry Pi Camera Module
- Motion-triggered captures

## Performance Considerations

### Inference Time

- **Desktop CPU**: 100-200ms per image
- **Desktop GPU**: 10-30ms per image
- **Raspberry Pi 4**: 2-5 seconds per image

### Memory Usage

- Model weights: ~50MB (yolov8m)
- Runtime memory: ~500MB-1GB

### Optimization Strategies

1. **Model quantization**: Use INT8 quantized models
2. **Image preprocessing**: Resize images to 640x640 before detection
3. **Batch processing**: Process multiple images in a single inference
4. **Caching**: Skip detection if scene hasn't changed

## Testing Architecture

The test suite follows a layered approach:

### Unit Tests

- `TestBoxOverlap`: Tests geometric overlap algorithm
- Pure functions, fast execution, no dependencies

### Integration Tests

- `TestDogDetector`: Tests full detection pipeline
- Uses real images and YOLOv8 model
- Validates end-to-end behavior

### Test Images

Stratified test scenarios:

1. **Positive cases**: Dog clearly on couch
2. **Negative cases**: Dog on floor, empty couch, person on couch
3. **Edge cases**: Low light, grayscale, different camera angles

See [Testing](Testing.md) page for details.
