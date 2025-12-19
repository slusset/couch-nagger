import logging
import random
import subprocess
from pathlib import Path
from dog_detector.ports.alert_sink import AlertSinkPort
from dog_detector.domain.model import DetectionResult

logger = logging.getLogger(__name__)

class AudioAlert(AlertSinkPort):
    def __init__(self,
                 sound_file: str = "/usr/share/sounds/alsa/Front_Center.wav",
                 sound_dir: str | None = None,
                 alsa_device='default',
                 quiet=True):
        self.sound_file = sound_file
        self.sound_dir = Path(sound_dir) if sound_dir else None
        self.alsa_device = alsa_device

    def _pick_sound_file(self) -> str | None:
        if not self.sound_dir:
            return self.sound_file

        if not self.sound_dir.exists() or not self.sound_dir.is_dir():
            logger.error(f"Alert sound directory not found: {self.sound_dir}")
            return None

        candidates = [
            path
            for path in self.sound_dir.iterdir()
            if path.is_file() and path.suffix.lower() in {".wav", ".mp3", ".ogg"}
        ]
        if not candidates:
            logger.error(f"No alert sounds found in: {self.sound_dir}")
            return None

        return str(random.choice(candidates))

    def alert(self, result: DetectionResult) -> None:
        try:
            sound_file = self._pick_sound_file()
            if not sound_file:
                return
            logger.info(f"Playing alert sound: {sound_file}")
            subprocess.run(["aplay", "-D", self.alsa_device, "-q", sound_file], check=False)
        except FileNotFoundError:
            logger.error("aplay command not found. Is alsa-utils installed?")
        except Exception as e:
            logger.error(f"Failed to play alert sound: {e}")
