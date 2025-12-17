from abc import ABC, abstractmethod
from dog_detector.domain.model import Frame

class FrameSourcePort(ABC):
    @abstractmethod
    def get_frame(self) -> Frame:
        """
        Captures and returns a single frame.
        Raises an exception if capture fails.
        """
        pass
