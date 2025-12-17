import logging
import numpy as np
from dog_detector.ports.frame_source import FrameSourcePort
from dog_detector.domain.model import Frame

try:
    from picamera2 import Picamera2
except ImportError:
    Picamera2 = None

logger = logging.getLogger(__name__)

class Picamera2FrameSource(FrameSourcePort):
    def __init__(self, width=640, height=480):
        if Picamera2 is None:
            raise ImportError("Picamera2 is not available on this system.")
        
        self.width = width
        self.height = height
        self.camera = Picamera2()
        
        # Configure camera
        config = self.camera.create_still_configuration(
            main={"size": (self.width, self.height)}
        )
        self.camera.configure(config)
        self.camera.start()
        logger.info(f"Picamera2 initialized with resolution {width}x{height}")

    def get_frame(self) -> Frame:
        # capture_array returns the image as a numpy array (typically BGR or RGB depending on config, usually BGR for OpenCV compatibility if default)
        # picamera2 default is usually BGR/RGB? check docs if critical. 
        # Ultralytics handles both if channels are correct.
        return self.camera.capture_array()

    def __del__(self):
        if hasattr(self, 'camera') and self.camera:
            self.camera.stop()
