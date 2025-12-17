from abc import ABC, abstractmethod
from dog_detector.domain.model import DetectionResult

class AlertSinkPort(ABC):
    @abstractmethod
    def alert(self, result: DetectionResult) -> None:
        """
        Triggers an alert based on the detection result.
        """
        pass
