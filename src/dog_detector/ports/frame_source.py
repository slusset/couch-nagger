from abc import ABC, abstractmethod
from dog_detector.domain.model import Frame
from typing import Tuple, Optional


class FrameSourcePort(ABC):
    @abstractmethod
    def get_frame(self) -> Tuple[Frame, Optional[str]]:
        """
        Captures and returns a single frame with optional filename.
        Raises an exception if capture fails.
        """
        pass
