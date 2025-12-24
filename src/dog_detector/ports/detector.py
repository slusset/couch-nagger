from abc import ABC, abstractmethod
from typing import Optional
from dog_detector.domain.model import Frame, DetectionResult


class DetectorPort(ABC):
    @abstractmethod
    def detect(self, frame: Frame, image_filename: Optional[str] = None) -> DetectionResult:
        """
        Analyzes the frame and returns detection results.
        """
        pass
