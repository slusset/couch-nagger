from pathlib import Path
from datetime import datetime

try:
    from picamera2 import Picamera2
except ImportError:
    Picamera2 = None

class Camera:
    def __init__(self, width=640, height=480, out_dir="captures"):
        self.width = width
        self.height = height
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.cam = None

    def start(self):
        if not Picamera2:
            return False
        self.cam = Picamera2()
        cfg = self.cam.create_still_configuration(main={"size": (self.width, self.height)})
        self.cam.configure(cfg)
        self.cam.start()
        return True

    def capture_file(self) -> str:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = self.out_dir / f"current_{ts}.jpg"
        self.cam.capture_file(str(path))
        return str(path)

    def stop(self):
        if self.cam:
            self.cam.stop()