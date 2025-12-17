import cv2
import logging
from dog_detector.ports.frame_source import FrameSourcePort
from dog_detector.domain.model import Frame

logger = logging.getLogger(__name__)

class FileFrameSource(FrameSourcePort):
    def __init__(self, file_path: str):
        self.file_path = file_path
        logger.info(f"FileFrameSource initialized with {file_path}")

    def get_frame(self) -> Frame:
        frame = cv2.imread(self.file_path)
        if frame is None:
            raise RuntimeError(f"Failed to load image from {self.file_path}")
        return frame
