from pathlib import Path

from dog_detector import DogDetector, boxes_overlap

# Get the test file's directory
TEST_DIR = Path(__file__).parent
PROJECT_ROOT = TEST_DIR.parent
IMAGE_DIR = PROJECT_ROOT / "images"


class TestBoxOverlap:
    def test_boxes_completely_overlap(self):
        box1 = [0, 0, 100, 100]
        box2 = [25, 25, 75, 75]
        assert boxes_overlap(box1, box2) == True

    def test_boxes_no_overlap(self):
        box1 = [0, 0, 50, 50]
        box2 = [100, 100, 150, 150]
        assert boxes_overlap(box1, box2) == False

    def test_boxes_partial_overlap(self):
        box1 = [0, 0, 100, 100]
        box2 = [50, 50, 150, 150]
        assert boxes_overlap(box1, box2) == True

    def test_boxes_edge_touching(self):
        box1 = [0, 0, 50, 50]
        box2 = [50, 50, 100, 100]
        assert boxes_overlap(box1, box2) == False  # edges touching = no overlap


class TestDogDetector:
    def setup_method(self):
        self.detector = DogDetector(model_path='yolov8m.pt')

    def test_dog_on_couch_detected(self):
        image_path = IMAGE_DIR / "test_dog_on_couch.jpg"
        result = self.detector.check_image(str(image_path))
        assert result['dog_on_couch'] == True
        assert result['confidence']['dog'] > 0.5
        assert result['confidence']['couch'] > 0.5

    def test_dog_on_floor_not_triggered(self):
        image_path = IMAGE_DIR / "test_dog_on_floor.jpg"
        result = self.detector.check_image(str(image_path))
        assert result['dog_on_couch'] == False

    def test_empty_couch_not_triggered(self):
        image_path = IMAGE_DIR / "test_empty_couch.jpg"
        result = self.detector.check_image(str(image_path))
        assert result['dog_on_couch'] == False

    def test_person_on_couch_not_triggered(self):
        image_path = IMAGE_DIR / "test_person_on_couch.jpg"
        result = self.detector.check_image(str(image_path))
        assert result['dog_on_couch'] == False

    def test_dog_on_couch_low_light(self):
        image_path = IMAGE_DIR / "test_dog_on_couch_grayscale_3ch.jpg"
        result = self.detector.check_image(str(image_path))
        assert result['dog_on_couch'] == True

    def test_rpicam_couch_detected(self):
        image_path = IMAGE_DIR / "test_rpicam_couch.jpg"
        result = self.detector.check_image(str(image_path))
        assert result['confidence']['couch'] > 0.5

    def test_fonzy_on_couch(self):
        image_path = IMAGE_DIR / "fonzy_on_couch.png"
        result = self.detector.check_image(str(image_path))
        assert result['dog_on_couch'] == True
        assert result['confidence']['dog'] > 0.5
        assert result['confidence']['couch'] > 0.5

    def test_fonzy_sitting_on_couch(self):
        image_path = IMAGE_DIR / "fonzy_sitting_on_couch.png"
        result = self.detector.check_image(str(image_path))
        assert result['dog_on_couch'] == True
        assert result['confidence']['dog'] > 0.5
        assert result['confidence']['couch'] > 0.5

    def test_fonzy_sleeping_on_couch(self):
        image_path = IMAGE_DIR / "fonzy_sleeping_on_couch.png"
        result = self.detector.check_image(str(image_path))
        assert result['dog_on_couch'] == True
        assert result['confidence']['dog'] > 0.5
        assert result['confidence']['couch'] > 0.5

    def test_fonzy_getting_off_couch(self):
        image_path = IMAGE_DIR / "fonzy_getting_off_couch.png"
        result = self.detector.check_image(str(image_path))
        assert result['dog_on_couch'] == True
        assert result['confidence']['dog'] > 0.5
        assert result['confidence']['couch'] > 0.5