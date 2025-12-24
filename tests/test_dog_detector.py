import cv2
import pytest
from pathlib import Path

from dog_detector.adapters.ultralytics_detector import (
    UltralyticsDetector,
    calculate_overlap_ratio,
)

TEST_DIR = Path(__file__).parent
PROJECT_ROOT = TEST_DIR.parent
IMAGE_DIR = PROJECT_ROOT / "assets" / "test-images"


class TestOverlapRatio:
    def test_no_overlap_returns_zero(self):
        dog_box = [0, 0, 50, 50]
        couch_box = [100, 100, 150, 150]
        assert calculate_overlap_ratio(dog_box, couch_box) == 0.0

    def test_complete_overlap_returns_one(self):
        dog_box = [25, 25, 75, 75]
        couch_box = [0, 0, 100, 100]
        assert calculate_overlap_ratio(dog_box, couch_box) == 1.0

    def test_partial_overlap_returns_fraction(self):
        dog_box = [0, 0, 100, 100]
        couch_box = [50, 50, 150, 150]
        ratio = calculate_overlap_ratio(dog_box, couch_box)
        assert 0.0 < ratio < 1.0
        assert ratio == pytest.approx(0.25, rel=0.01)

    def test_edge_touching_returns_zero(self):
        dog_box = [0, 0, 50, 50]
        couch_box = [50, 50, 100, 100]
        assert calculate_overlap_ratio(dog_box, couch_box) == 0.0

    def test_dog_half_on_couch(self):
        dog_box = [0, 0, 100, 100]
        couch_box = [50, 0, 150, 100]
        ratio = calculate_overlap_ratio(dog_box, couch_box)
        assert ratio == pytest.approx(0.5, rel=0.01)

    def test_small_overlap_below_threshold(self):
        dog_box = [0, 0, 100, 100]
        couch_box = [90, 90, 200, 200]
        ratio = calculate_overlap_ratio(dog_box, couch_box)
        assert ratio < 0.3


class TestUltralyticsDetector:
    @pytest.fixture
    def detector(self):
        return UltralyticsDetector(model_path="yolov8m.pt", min_overlap_threshold=0.3)

    @pytest.fixture
    def detector_strict(self):
        return UltralyticsDetector(model_path="yolov8m.pt", min_overlap_threshold=0.5)

    def test_fonzy_on_couch(self, detector):
        image_path = IMAGE_DIR / "fonzy_on_couch.png"
        if not image_path.exists():
            pytest.skip(f"Test image not found: {image_path}")
        frame = cv2.imread(str(image_path))
        result = detector.detect(frame)
        assert result.dog_on_couch is True
        assert result.confidence["dog"] > 0.5
        assert result.confidence["couch"] > 0.5
        assert result.overlap_ratio > 0.0

    def test_fonzy_sitting_on_couch(self, detector):
        image_path = IMAGE_DIR / "fonzy_sitting_on_couch.png"
        if not image_path.exists():
            pytest.skip(f"Test image not found: {image_path}")
        frame = cv2.imread(str(image_path))
        result = detector.detect(frame)
        assert result.dog_on_couch is True
        assert result.confidence["dog"] > 0.5
        assert result.confidence["couch"] > 0.5

    def test_fonzy_sleeping_on_couch(self, detector):
        image_path = IMAGE_DIR / "fonzy_sleeping_on_couch.png"
        if not image_path.exists():
            pytest.skip(f"Test image not found: {image_path}")
        frame = cv2.imread(str(image_path))
        result = detector.detect(frame)
        assert result.dog_on_couch is True
        assert result.confidence["dog"] > 0.5
        assert result.confidence["couch"] > 0.5

    def test_fonzy_getting_off_couch(self, detector):
        image_path = IMAGE_DIR / "fonzy_getting_off_couch.png"
        if not image_path.exists():
            pytest.skip(f"Test image not found: {image_path}")
        frame = cv2.imread(str(image_path))
        result = detector.detect(frame)
        assert result.confidence["dog"] > 0.5
        assert result.confidence["couch"] > 0.5

    def test_detection_result_contains_boxes(self, detector):
        image_path = IMAGE_DIR / "fonzy_on_couch.png"
        if not image_path.exists():
            pytest.skip(f"Test image not found: {image_path}")
        frame = cv2.imread(str(image_path))
        result = detector.detect(frame)
        assert "dog" in result.boxes
        assert "couch" in result.boxes
        assert "person" in result.boxes
        assert len(result.boxes["dog"]) > 0
        assert len(result.boxes["couch"]) > 0

    def test_overlap_ratio_included_in_result(self, detector):
        image_path = IMAGE_DIR / "fonzy_on_couch.png"
        if not image_path.exists():
            pytest.skip(f"Test image not found: {image_path}")
        frame = cv2.imread(str(image_path))
        result = detector.detect(frame)
        assert hasattr(result, "overlap_ratio")
        assert isinstance(result.overlap_ratio, float)
        assert 0.0 <= result.overlap_ratio <= 1.0

    def test_higher_threshold_reduces_detections(self, detector, detector_strict):
        image_path = IMAGE_DIR / "fonzy_getting_off_couch.png"
        if not image_path.exists():
            pytest.skip(f"Test image not found: {image_path}")
        frame = cv2.imread(str(image_path))
        result_normal = detector.detect(frame)
        result_strict = detector_strict.detect(frame)
        assert result_normal.overlap_ratio == result_strict.overlap_ratio
        if result_normal.dog_on_couch and not result_strict.dog_on_couch:
            assert result_normal.overlap_ratio < 0.5

    def test_image_filename_passed_through(self, detector):
        image_path = IMAGE_DIR / "fonzy_on_couch.png"
        if not image_path.exists():
            pytest.skip(f"Test image not found: {image_path}")
        frame = cv2.imread(str(image_path))
        result = detector.detect(frame, image_filename="test_image.png")
        assert result.image_filename == "test_image.png"
