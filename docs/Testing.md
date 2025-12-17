# Testing Guide

Comprehensive testing documentation for the Couch Nagger project.

## Test Suite Overview

The project includes two types of tests:

1. **Unit Tests** - Fast, isolated tests for pure functions
2. **Integration Tests** - End-to-end tests using real images and models

## Running Tests

### Run All Tests

```bash
pytest tests/
```

### Run with Verbose Output

```bash
pytest tests/ -v
```

### Run Specific Test Class

```bash
pytest tests/test_dog_detector.py::TestBoxOverlap
pytest tests/test_dog_detector.py::TestDogDetector
```

### Run Single Test

```bash
pytest tests/test_dog_detector.py::TestDogDetector::test_dog_on_couch_detected
```

## Unit Tests: TestBoxOverlap

Tests the geometric overlap detection algorithm.

### test_boxes_completely_overlap

Tests when one box is completely inside another.

```python
box1 = [0, 0, 100, 100]  # Outer box
box2 = [25, 25, 75, 75]   # Inner box
assert boxes_overlap(box1, box2) == True
```

### test_boxes_no_overlap

Tests when boxes are completely separated.

```python
box1 = [0, 0, 50, 50]
box2 = [100, 100, 150, 150]
assert boxes_overlap(box1, box2) == False
```

### test_boxes_partial_overlap

Tests when boxes partially intersect.

```python
box1 = [0, 0, 100, 100]
box2 = [50, 50, 150, 150]
assert boxes_overlap(box1, box2) == True
```

### test_boxes_edge_touching

Tests edge case where boxes only touch at edges.

```python
box1 = [0, 0, 50, 50]
box2 = [50, 50, 100, 100]  # Touches at corner
assert boxes_overlap(box1, box2) == False  # Edges don't count as overlap
```

## Integration Tests: TestDogDetector

Tests the full detection pipeline with real images.

### Test Images

The `images/` directory contains stratified test cases:

1. **test_dog_on_couch.jpg** - Positive case: dog clearly on couch
2. **test_dog_on_floor.jpg** - Negative case: dog present but on floor
3. **test_empty_couch.jpg** - Negative case: couch but no dog
4. **test_person_on_couch.jpg** - Negative case: person on couch (not dog)
5. **test_dog_on_couch_grayscale_3ch.jpg** - Edge case: low light/grayscale
6. **test_rpicam_couch.jpg** - Real world case: Raspberry Pi camera image

### test_dog_on_couch_detected

Validates positive detection scenario.

```python
def test_dog_on_couch_detected(self):
    image_path = IMAGE_DIR / "test_dog_on_couch.jpg"
    result = self.detector.check_image(str(image_path))
    assert result['dog_on_couch'] == True
    assert result['confidence']['dog'] > 0.5
    assert result['confidence']['couch'] > 0.5
```

**Expected behavior:**
- Detects both dog and couch
- Reports overlap
- Confidence scores > 0.5

### test_dog_on_floor_not_triggered

Validates that detector doesn't false positive when dog is not on couch.

```python
def test_dog_on_floor_not_triggered(self):
    image_path = IMAGE_DIR / "test_dog_on_floor.jpg"
    result = self.detector.check_image(str(image_path))
    assert result['dog_on_couch'] == False
```

**Expected behavior:**
- Detects dog
- May or may not detect couch
- No overlap reported

### test_empty_couch_not_triggered

Validates no false positive when only couch present.

```python
def test_empty_couch_not_triggered(self):
    image_path = IMAGE_DIR / "test_empty_couch.jpg"
    result = self.detector.check_image(str(image_path))
    assert result['dog_on_couch'] == False
```

**Expected behavior:**
- May detect couch
- No dog detected
- No overlap reported

### test_person_on_couch_not_triggered

Validates that detector distinguishes between dogs and people.

```python
def test_person_on_couch_not_triggered(self):
    image_path = IMAGE_DIR / "test_person_on_couch.jpg"
    result = self.detector.check_image(str(image_path))
    assert result['dog_on_couch'] == False
```

**Expected behavior:**
- May detect person (class 0) but ignores it
- May detect couch
- No dog detected
- No overlap reported

### test_dog_on_couch_low_light

Validates detection in challenging lighting conditions.

```python
def test_dog_on_couch_low_light(self):
    image_path = IMAGE_DIR / "test_dog_on_couch_grayscale_3ch.jpg"
    result = self.detector.check_image(str(image_path))
    assert result['dog_on_couch'] == True
```

**Expected behavior:**
- Handles grayscale/low-light images
- Still detects dog and couch
- May have lower confidence scores

### test_rpicam_couch_detected

Validates detection with Raspberry Pi camera images.

```python
def test_rpicam_couch_detected(self):
    image_path = IMAGE_DIR / "test_rpicam_couch.jpg"
    result = self.detector.check_image(str(image_path), conf_threshold=0.3)
    assert result['confidence']['couch'] > 0.2
```

**Expected behavior:**
- Works with real camera images
- Adjusts confidence threshold as needed
- Detects couch in real environment

## Debug Utilities

### debug_detection.py

Utility script for debugging detection results.

```bash
python tests/debug_detection.py
```

**Output:**

```
Detections in test_rpicam_couch.jpg:
------------------------------------------------------------
Class ID:  57 | Name: couch          | Confidence: 0.753
  BBox: [123.4, 234.5, 678.9, 890.1]
Class ID:  16 | Name: dog            | Confidence: 0.891
  BBox: [234.5, 345.6, 456.7, 678.9]

Looking for:
  Dog (class 16): FOUND
  Couch (class 57): FOUND
```

Use this to:
- Verify YOLO detections
- Check confidence scores
- Debug false negatives
- Inspect bounding box coordinates

## Adding New Tests

### Adding Test Images

1. Add image to `images/` directory
2. Use descriptive filename (e.g., `test_cat_on_couch.jpg`)
3. Document expected detection result

### Writing New Test Cases

```python
def test_new_scenario(self):
    """Test description"""
    image_path = IMAGE_DIR / "test_new_scenario.jpg"
    result = self.detector.check_image(str(image_path))
    
    # Add assertions
    assert result['dog_on_couch'] == expected_value
    assert result['confidence']['dog'] > threshold
```

## Test Coverage

Current test coverage:

- **Overlap Algorithm**: 100% coverage
- **Detection Pipeline**: ~90% coverage
- **Error Handling**: Limited coverage

### Areas for Improvement

1. **Error handling tests**
   - Invalid image paths
   - Corrupted image files
   - Out of memory scenarios

2. **Performance tests**
   - Inference time benchmarks
   - Memory usage monitoring

3. **Edge cases**
   - Multiple dogs on couch
   - Multiple couches in scene
   - Partial dog/couch visibility

## Continuous Integration

To run tests in CI/CD pipeline:

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest
      - name: Run tests
        run: pytest tests/ -v
```

## Test Best Practices

1. **Use descriptive test names** - Name reflects what is being tested
2. **One assertion per test** - Tests should be focused
3. **Test both positive and negative cases** - Don't just test happy path
4. **Use realistic test data** - Test images should represent real usage
5. **Document expected behavior** - Add comments explaining expectations
6. **Keep tests independent** - Tests shouldn't depend on execution order
7. **Fast feedback loop** - Unit tests should run in milliseconds

## Troubleshooting Tests

**Tests fail after model update:**
- Re-download test images or adjust confidence thresholds
- Update expected confidence scores in assertions

**Intermittent failures:**
- Check if confidence threshold is too strict
- Verify test images haven't been modified
- Ensure consistent random seed (if applicable)

**Slow test execution:**
- Use smaller model (yolov8n.pt) for testing
- Reduce test image resolution
- Mock YOLOv8 model for unit tests

For more information, see [Configuration](Configuration.md) for tuning parameters.
