# src/dog_detector/settings.py
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


def _load_env_file(path: str) -> None:
    """
    Minimal .env loader.
    Only sets values that are not already present in os.environ.
    """
    p = Path(path)
    if not p.exists():
        return

    for raw in p.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


def _getenv(key: str, default: str | None = None) -> str | None:
    v = os.getenv(key)
    return v if v is not None else default


def _getenv_int(key: str, default: int) -> int:
    v = os.getenv(key)
    return int(v) if v is not None else default


def _getenv_float(key: str, default: float) -> float:
    v = os.getenv(key)
    return float(v) if v is not None else default


@dataclass(frozen=True)
class ModelSettings:
    # e.g. "yolov8n.pt"
    model_path: str = "yolov8n.pt"
    confidence_threshold: float = 0.20
    person_confidence_threshold: float = 0.25

    # Optional: where to store/download weights (shared across releases)
    # If None, Ultralytics uses its defaults/current working dir.
    model_dir: Optional[str] = None


@dataclass(frozen=True)
class DetectionSettings:
    check_interval: float = 10.0
    alert_cooldown: float = 300.0
    test_mode: bool = False
    test_alert_every_n: int = 0
    min_overlap_threshold: float = 0.3  # 0.0-1.0: fraction of dog's box that must overlap couch


@dataclass(frozen=True)
class CameraSettings:
    width: int = 640
    height: int = 480
    image_dir: Optional[str] = None
    save_images: bool = False
    save_detection_images: bool = False
    detection_image_dir: Optional[str] = None


@dataclass(frozen=True)
class LoggingSettings:
    level: str = "INFO"
    file: str = "logs/couch-nagger.log"


@dataclass(frozen=True)
class AudioSettings:
    # ALSA device string (e.g. "plughw:3,1" or "default")
    alsa_device: str = "default"

    # Either a direct wav path OR a directory to choose from
    alert_sound: str = "/usr/share/sounds/alsa/Front_Center.wav"
    alert_sound_dir: Optional[str] = None

    # If you’re using aplay, quiet mode keeps logs clean
    aplay_quiet: bool = True

    alert_volume: float = 0.8


@dataclass(frozen=True)
class AppSettings:
    model: ModelSettings
    detection: DetectionSettings
    camera: CameraSettings
    logging: LoggingSettings
    audio: AudioSettings
    base_dir: Optional[str] = None

    @staticmethod
    def load(env_file: Optional[str] = None) -> "AppSettings":
        """
        Load settings. If env_file is provided, it is read first (without overriding existing env vars).
        """
        if env_file:
            _load_env_file(env_file)

        # Base directory for resolving shared paths (models, logs, captures)
        base_dir = _getenv("BASE_DIR")

        def _resolve_path(path: Optional[str]) -> Optional[str]:
            """Resolve path relative to BASE_DIR if set and path is relative."""
            if not path or not base_dir:
                return path
            p = Path(path)
            if p.is_absolute():
                return path
            return str(Path(base_dir) / path)

        model = ModelSettings(
            model_path=_getenv("MODEL_PATH", "yolov8n.pt") or "yolov8n.pt",
            confidence_threshold=_getenv_float("CONFIDENCE_THRESHOLD", 0.20),
            person_confidence_threshold=_getenv_float("PERSON_CONFIDENCE_THRESHOLD", 0.25),
            model_dir=_resolve_path(_getenv("MODEL_DIR")),
        )

        detection = DetectionSettings(
            check_interval=_getenv_float("CHECK_INTERVAL", 10.0),
            alert_cooldown=_getenv_float("ALERT_COOLDOWN", 300.0),
            test_mode=(_getenv("TEST_MODE", "0") == "1"),
            test_alert_every_n=_getenv_int("TEST_ALERT_EVERY_N", 0),
            min_overlap_threshold=_getenv_float("MIN_OVERLAP_THRESHOLD", 0.3),
        )

        camera = CameraSettings(
            width=_getenv_int("CAMERA_RESOLUTION_WIDTH", 640),
            height=_getenv_int("CAMERA_RESOLUTION_HEIGHT", 480),
            image_dir=_resolve_path(_getenv("IMAGE_DIR")),
            save_images=(_getenv("SAVE_IMAGES", "0") == "1"),
            save_detection_images=(_getenv("SAVE_DETECTION_IMAGES", "0") == "1"),
            detection_image_dir=_resolve_path(_getenv("DETECTION_IMAGE_DIR")),
        )

        logging_cfg = LoggingSettings(
            level=_getenv("LOG_LEVEL", "INFO") or "INFO",
            file=_resolve_path(_getenv("LOG_FILE", "logs/couch-nagger.log"))
            or "logs/couch-nagger.log",
        )

        audio = AudioSettings(
            alsa_device=_getenv("ALSA_DEVICE", "default") or "default",
            alert_sound=_getenv("ALERT_SOUND", "/usr/share/sounds/alsa/Front_Center.wav")
            or "/usr/share/sounds/alsa/Front_Center.wav",
            alert_sound_dir=_getenv("ALERT_SOUND_DIR"),
            aplay_quiet=(_getenv("APLAY_QUIET", "1") != "0"),
            alert_volume=_getenv_float("ALERT_VOLUME", 0.8),
        )

        settings = AppSettings(
            model=model,
            detection=detection,
            camera=camera,
            logging=logging_cfg,
            audio=audio,
            base_dir=base_dir,
        )

        settings._validate()
        return settings

    def _validate(self) -> None:
        if self.camera.width <= 0 or self.camera.height <= 0:
            raise ValueError("Camera width/height must be positive")

        if not (0.0 <= self.model.confidence_threshold <= 1.0):
            raise ValueError("CONFIDENCE_THRESHOLD must be between 0 and 1")

        if self.detection.check_interval <= 0:
            raise ValueError("CHECK_INTERVAL must be > 0")

        if self.detection.alert_cooldown < 0:
            raise ValueError("ALERT_COOLDOWN must be >= 0")
