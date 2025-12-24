from abc import ABC, abstractmethod
from typing import Optional

from dog_detector.domain.model import DetectionResult, Frame


class DetectionSaverPort(ABC):
    @abstractmethod
    def save(self, frame: Frame, result: DetectionResult) -> Optional[str]:
        pass
