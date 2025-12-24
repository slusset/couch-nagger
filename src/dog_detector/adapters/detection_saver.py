import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

import cv2

from dog_detector.domain.model import DetectionResult, Frame
from dog_detector.ports.detection_saver import DetectionSaverPort

logger = logging.getLogger(__name__)

BOX_COLORS = {
    "dog": (0, 0, 255),
    "couch": (0, 255, 0),
    "person": (255, 0, 0),
}


class DetectionImageSaver(DetectionSaverPort):
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Detection images will be saved to {self.output_dir}")

    def save(self, frame: Frame, result: DetectionResult) -> Optional[str]:
        annotated = frame.copy()

        for label, boxes in result.boxes.items():
            color = BOX_COLORS.get(label, (128, 128, 128))
            for box in boxes:
                x1, y1, x2, y2 = map(int, box)
                cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
                cv2.putText(
                    annotated,
                    label,
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color,
                    2,
                )

        overlap_text = f"overlap: {result.overlap_ratio:.2f}"
        status_text = "ON COUCH" if result.dog_on_couch else "off couch"
        cv2.putText(
            annotated,
            f"{status_text} | {overlap_text}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255) if result.dog_on_couch else (0, 255, 0),
            2,
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = self.output_dir / f"detection_{timestamp}.jpg"
        cv2.imwrite(str(filename), annotated)
        logger.debug(f"Saved detection image: {filename}")
        return str(filename)
