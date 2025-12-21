import logging
import random
from pathlib import Path
import pygame
from dog_detector.ports.alert_sink import AlertSinkPort
from dog_detector.domain.model import DetectionResult

logger = logging.getLogger(__name__)

class AudioAlert(AlertSinkPort):
    def __init__(self,
                 sound_file: str = "/usr/share/sounds/alsa/Front_Center.wav",
                 sound_dir: str | None = None,
                 volume: float = 1.0):
        self.sound_file = sound_file
        self.sound_dir = Path(sound_dir) if sound_dir else None
        self.volume = max(0.0, min(1.0, volume))  # Clamp between 0.0 and 1.0

        # Initialize pygame mixer
        try:
            pygame.mixer.init()
        except Exception as e:
            logger.error(f"Failed to initialize audio mixer: {e}")

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

            logger.info(f"Playing alert sound: {sound_file} at volume {self.volume}")
            sound = pygame.mixer.Sound(sound_file)
            sound.set_volume(self.volume)
            sound.play()

            # Wait for sound to finish playing
            while pygame.mixer.get_busy():
                pygame.time.wait(100)

        except Exception as e:
            logger.error(f"Failed to play alert sound: {e}")
