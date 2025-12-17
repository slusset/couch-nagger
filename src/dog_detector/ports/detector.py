from abc import ABC, abstractmethod
from dog_detector.domain.model import Frame, DetectionResult

class DetectorPort(ABC):
    @abstractmethod
    def detect(self, frame: Frame) -> DetectionResult:
        """
        Analyzes the frame and returns detection results.
        """
        pass
