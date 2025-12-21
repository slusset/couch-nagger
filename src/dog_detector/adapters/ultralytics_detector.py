from ultralytics import YOLO
from dog_detector.ports.detector import DetectorPort
from dog_detector.domain.model import Frame, DetectionResult

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

class UltralyticsDetector(DetectorPort):
    def __init__(self, model_path=None, model=None, conf_threshold=0.25):
        if model is not None:
            self.model = model
        elif model_path is not None:
            self.model = YOLO(model_path)
        else:
            self.model = YOLO('yolov8m.pt')
        self.conf_threshold = conf_threshold
        self.PERSON_CLASS = 0
        self.DOG_CLASS = 16
        self.COUCH_CLASS = 57

    def detect(self, frame: Frame) -> DetectionResult:
        # Ultralytics accepts numpy arrays directly
        results = self.model(frame, conf=self.conf_threshold, verbose=False)

        person_boxes = []
        dog_boxes = []
        couch_boxes = []
        confidences = {'person': 0.0, 'dog': 0.0, 'couch': 0.0}

        # We assume single image input, so results[0]
        result = results[0]

        for box in result.boxes:
            class_id = int(box.cls[0])
            bbox = box.xyxy[0].tolist()
            conf = float(box.conf[0])

            if class_id == self.PERSON_CLASS:
                person_boxes.append(bbox)
                confidences['person'] = max(confidences['person'], conf)
            elif class_id == self.DOG_CLASS:
                dog_boxes.append(bbox)
                confidences['dog'] = max(confidences['dog'], conf)
            elif class_id == self.COUCH_CLASS:
                couch_boxes.append(bbox)
                confidences['couch'] = max(confidences['couch'], conf)

        # Check for overlap - dog or person on couch
        dog_on_couch = False
        for dog_box in dog_boxes:
            for couch_box in couch_boxes:
                if boxes_overlap(dog_box, couch_box):
                    dog_on_couch = True
                    break
            if dog_on_couch:
                break

        # Check for person on couch (without dog)
        person_on_couch = False
        if not dog_on_couch:  # Only check if dog isn't already on couch
            for person_box in person_boxes:
                for couch_box in couch_boxes:
                    if boxes_overlap(person_box, couch_box):
                        person_on_couch = True
                        break
                if person_on_couch:
                    break

        return DetectionResult(
            dog_on_couch=dog_on_couch or person_on_couch,  # Alert if either is on couch
            confidence=confidences,
            boxes={'person': person_boxes, 'dog': dog_boxes, 'couch': couch_boxes}
        )
