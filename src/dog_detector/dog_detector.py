# dog_detector.py
from ultralytics import YOLO


def boxes_overlap(box1, box2):
    """Check if two bounding boxes overlap.
    box format: [x1, y1, x2, y2]
    """
    x1_min, y1_min, x1_max, y1_max = box1
    x2_min, y2_min, x2_max, y2_max = box2

    # No overlap if one box is completely to the left/right/above/below the other
    if x1_max <= x2_min or x2_max <= x1_min:
        return False
    if y1_max <= y2_min or y2_max <= y1_min:
        return False

    return True


class DogDetector:
    def __init__(self, model_path='yolov8m.pt'):
        self.model = YOLO(model_path)
        self.DOG_CLASS = 16
        self.COUCH_CLASS = 57

    def check_image(self, image_path, conf_threshold=0.25):
        """Returns dict with detection results."""
        results = self.model(image_path, conf=conf_threshold)

        dog_boxes = []
        couch_boxes = []
        confidences = {'dog': 0.0, 'couch': 0.0}

        for box in results[0].boxes:
            class_id = int(box.cls[0])
            bbox = box.xyxy[0].tolist()
            conf = float(box.conf[0])

            if class_id == self.DOG_CLASS:
                dog_boxes.append(bbox)
                confidences['dog'] = max(confidences['dog'], conf)
            elif class_id == self.COUCH_CLASS:
                couch_boxes.append(bbox)
                confidences['couch'] = max(confidences['couch'], conf)

        # Check for overlap
        dog_on_couch = False
        for dog_box in dog_boxes:
            for couch_box in couch_boxes:
                if boxes_overlap(dog_box, couch_box):
                    dog_on_couch = True
                    break
            if dog_on_couch:
                break

        return {
            'dog_on_couch': dog_on_couch,
            'confidence': confidences
        }