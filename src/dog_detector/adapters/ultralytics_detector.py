from typing import Optional
from ultralytics import YOLO
from dog_detector.ports.detector import DetectorPort
from dog_detector.domain.model import Frame, DetectionResult


def calculate_overlap_ratio(dog_box, couch_box):
    """
    Calculate fraction of dog's bounding box that overlaps with couch box.
    Returns 0.0 if no overlap, up to 1.0 if dog is completely within couch.
    box format: [x1, y1, x2, y2]
    """
    d_x1, d_y1, d_x2, d_y2 = dog_box
    c_x1, c_y1, c_x2, c_y2 = couch_box

    inter_x1 = max(d_x1, c_x1)
    inter_y1 = max(d_y1, c_y1)
    inter_x2 = min(d_x2, c_x2)
    inter_y2 = min(d_y2, c_y2)

    if inter_x2 <= inter_x1 or inter_y2 <= inter_y1:
        return 0.0

    intersection_area = (inter_x2 - inter_x1) * (inter_y2 - inter_y1)
    dog_area = (d_x2 - d_x1) * (d_y2 - d_y1)

    if dog_area <= 0:
        return 0.0

    return intersection_area / dog_area


class UltralyticsDetector(DetectorPort):
    def __init__(
        self,
        model_path=None,
        model=None,
        conf_threshold=0.25,
        person_confidence_threshold=None,
        min_overlap_threshold=0.3,
    ):
        if model is not None:
            self.model = model
        elif model_path is not None:
            self.model = YOLO(model_path)
        else:
            self.model = YOLO("yolov8m.pt")
        self.conf_threshold = conf_threshold
        self.person_confidence_threshold = person_confidence_threshold or conf_threshold
        self.min_overlap_threshold = min_overlap_threshold
        self.PERSON_CLASS = 0
        self.DOG_CLASS = 16
        self.COUCH_CLASS = 57

    def detect(self, frame: Frame, image_filename: Optional[str] = None) -> DetectionResult:
        # Ultralytics accepts numpy arrays directly
        results = self.model(frame, conf=self.conf_threshold, verbose=False)

        person_boxes = []
        dog_boxes = []
        couch_boxes = []
        confidences = {"person": 0.0, "dog": 0.0, "couch": 0.0}

        # We assume single image input, so results[0]
        result = results[0]

        for box in result.boxes:
            class_id = int(box.cls[0])
            bbox = box.xyxy[0].tolist()
            conf = float(box.conf[0])

            if class_id == self.PERSON_CLASS:
                person_boxes.append(bbox)
                confidences["person"] = max(confidences["person"], conf)
            elif class_id == self.DOG_CLASS:
                dog_boxes.append(bbox)
                confidences["dog"] = max(confidences["dog"], conf)
            elif class_id == self.COUCH_CLASS:
                couch_boxes.append(bbox)
                confidences["couch"] = max(confidences["couch"], conf)

        dog_on_couch = False
        max_overlap_ratio = 0.0
        for dog_box in dog_boxes:
            for couch_box in couch_boxes:
                overlap = calculate_overlap_ratio(dog_box, couch_box)
                max_overlap_ratio = max(max_overlap_ratio, overlap)
                if overlap >= self.min_overlap_threshold:
                    dog_on_couch = True
                    break
            if dog_on_couch:
                break

        person_on_couch = False
        if not dog_on_couch:
            for person_box in person_boxes:
                for couch_box in couch_boxes:
                    if calculate_overlap_ratio(person_box, couch_box) > 0:
                        person_on_couch = True
                        break
                if person_on_couch:
                    break

        return DetectionResult(
            dog_on_couch=dog_on_couch,
            confidence=confidences,
            boxes={"person": person_boxes, "dog": dog_boxes, "couch": couch_boxes},
            image_filename=image_filename,
            overlap_ratio=max_overlap_ratio,
        )
