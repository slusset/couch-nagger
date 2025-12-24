import time
import logging

from dog_detector.domain.model import DetectionResult
from dog_detector.ports.frame_source import FrameSourcePort
from dog_detector.ports.detector import DetectorPort
from dog_detector.ports.alert_sink import AlertSinkPort
from dog_detector.settings import AppSettings

logger = logging.getLogger(__name__)


class CouchMonitorApp:
    def __init__(
        self,
        frame_source: FrameSourcePort,
        detector: DetectorPort,
        alert_sink: AlertSinkPort,
        settings: AppSettings,
    ):
        self.frame_source = frame_source
        self.detector = detector
        self.alert_sink = alert_sink
        self.check_interval = settings.detection.check_interval
        self.alert_cooldown = settings.detection.alert_cooldown
        self.test_mode = settings.detection.test_mode

        self.last_alert_time = 0.0
        self.running = False

    def check_and_alert(self):
        try:
            # 1. Get Frame
            frame, image_filename = self.frame_source.get_frame()

            # 2. Detect
            result = self.detector.detect(frame, image_filename=image_filename)

            # Log detailed detection information
            image_info = f"image={image_filename}" if image_filename else "image=live_camera"
            logger.info(
                f"{image_info} | "
                f"dog_on_couch={result.dog_on_couch} | "
                f"confidences: dog={result.confidence.get('dog', 0.0):.3f}, "
                f"person={result.confidence.get('person', 0.0):.3f}, "
                f"couch={result.confidence.get('couch', 0.0):.3f}"
            )

            # Log if person detected on couch
            if result.boxes.get("person") and result.boxes.get("couch"):
                logger.info(
                    f"{image_info} | Person detected on couch (no alert triggered). "
                    f"Person confidence: {result.confidence.get('person', 0.0):.3f}"
                )

            if result.dog_on_couch:
                current_time = time.time()
                time_since_last_alert = current_time - self.last_alert_time

                if time_since_last_alert > self.alert_cooldown:
                    logger.info(
                        f"{image_info} | Dog detected on couch! Triggering alert. "
                        f"Dog confidence: {result.confidence.get('dog', 0.0):.3f}"
                    )
                    # 3. Alert
                    self.alert_sink.alert(result)
                    self.last_alert_time = current_time
                else:
                    remaining = int(self.alert_cooldown - time_since_last_alert)
                    logger.info(
                        f"{image_info} | Dog on couch, but alert is on cooldown ({remaining}s remaining). "
                        f"Dog confidence: {result.confidence.get('dog', 0.0):.3f}"
                    )

        except Exception as e:
            logger.error(f"Error during check cycle: {e}", exc_info=True)

    def run(self):
        self.running = True
        logger.info("Starting CouchMonitorApp...")
        try:
            tick = 0
            while self.running:
                tick += 1
                if self.test_mode:
                    self.alert_sink.alert(
                        DetectionResult(dog_on_couch=True, confidence={}, boxes={})
                    )
                self.check_and_alert()
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            logger.info("Stopping CouchMonitorApp...")
        finally:
            self.running = False
