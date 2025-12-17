# Couch Nagger Wiki

Welcome to the Couch Nagger documentation! This project uses computer vision to detect when your dog (Fonzy) is on the couch and can trigger automated responses.

## Overview

Couch Nagger is a Python-based dog detection system that uses YOLOv8 object detection to identify when a dog is sitting on a couch. The system analyzes images, detects both dogs and couches, and determines if there's overlap between them.

## Key Features

- **Real-time object detection** using YOLOv8m model
- **Bounding box overlap detection** to determine if dog is on couch
- **Confidence scoring** for both dog and couch detections
- **Comprehensive test suite** with multiple test scenarios
- **Support for various lighting conditions** including low-light scenarios

## Quick Start

```python
from dog_detector import DogDetector

detector = DogDetector(model_path='yolov8m.pt')
result = detector.check_image('path/to/image.jpg')

if result['dog_on_couch']:
    print(f"Dog detected on couch! Confidence: {result['confidence']}")
```

## Documentation Pages

- **[Installation](Installation)** - Setup instructions and dependencies
- **[Architecture](Architecture)** - System design and component overview
- **[API Reference](API-Reference)** - Detailed API documentation
- **[Testing](Testing)** - Test suite and validation scenarios
- **[Configuration](Configuration)** - Model selection and tuning parameters
- **[Examples](Examples)** - Usage examples and common patterns
- **[Troubleshooting](Troubleshooting)** - Common issues and solutions

## Project Goals

The primary goal is to keep Fonzy off the couch through automated detection and alerts. The system is designed to be:

- Accurate in various lighting conditions
- Fast enough for near-real-time monitoring
- Easy to integrate with notification systems
- Extensible for additional object detection scenarios

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/slusset/couch-nagger/blob/main/LICENSE) file for details.
