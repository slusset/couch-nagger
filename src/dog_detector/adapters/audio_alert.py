import subprocess
import logging
from dog_detector.ports.alert_sink import AlertSinkPort
from dog_detector.domain.model import DetectionResult

logger = logging.getLogger(__name__)

class AudioAlert(AlertSinkPort):
    def __init__(self, sound_file: str = "/usr/share/sounds/alsa/Front_Center.wav"):
        self.sound_file = sound_file

    def alert(self, result: DetectionResult) -> None:
        if result.dog_on_couch:
            try:
                logger.info(f"Playing alert sound: {self.sound_file}")
                subprocess.run(['aplay', '-q', self.sound_file], check=False)
            except FileNotFoundError:
                logger.error("aplay command not found. Is alsa-utils installed?")
            except Exception as e:
                logger.error(f"Failed to play alert sound: {e}")
