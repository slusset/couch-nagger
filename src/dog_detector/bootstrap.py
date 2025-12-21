#!/usr/bin/env python3
"""
Couch Nagger - Raspberry Pi Monitor (Hexagonal Architecture)

Continuously monitors the couch using Pi Camera and alerts when dog detected.
"""

import logging
import os
import sys
from pathlib import Path
from ultralytics import YOLO

from dog_detector.adapters.audio_alert import AudioAlert
from dog_detector.adapters.file_source import FileFrameSource
# Adapters
from dog_detector.adapters.ultralytics_detector import UltralyticsDetector
# Ports & Domain
from dog_detector.app.couch_monitor import CouchMonitorApp
from dog_detector.settings import AppSettings

# Attempt to import Picamera adapter
try:
    from dog_detector.adapters.picamera2_source import Picamera2FrameSource
    PICAMERA_AVAILABLE = True
except ImportError:
    PICAMERA_AVAILABLE = False


def load_yolo_model(model_dir: str, model_name: str):
    d = Path(model_dir)
    d.mkdir(parents=True, exist_ok=True)

    old_cwd = os.getcwd()
    try:
        os.chdir(d)  # ensures ultralytics downloads here
        return YOLO(model_name)  # downloads if missing
    finally:
        os.chdir(old_cwd)

def setup_logging(log_level_str, log_file_path):
    log_level = getattr(logging, log_level_str.upper())
    
    # Create logs directory if it doesn't exist
    log_file = Path(log_file_path)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.info("Logging initialized")

def main():
    env_file = os.getenv("COUCH_NAGGER_ENV_FILE")
    settings = AppSettings.load(env_file=env_file)
    setup_logging(settings.logging.level, settings.logging.file)
    logger = logging.getLogger("Main")

    logger.info("Initializing Couch Nagger (Hexagonal)...")

    # 1. Adapter: Frame Source
    frame_source = None
    if PICAMERA_AVAILABLE:
        try:
            frame_source = Picamera2FrameSource(
                width=settings.camera.width,
                height=settings.camera.height
            )
            logger.info("Using Picamera2FrameSource")
        except Exception as e:
            logger.error(f"Failed to initialize Picamera2: {e}")
    
    if frame_source is None:
        logger.warning("Picamera2 not available or failed. Falling back to FileFrameSource.")
        test_img = Path(settings.camera.image_dir) / 'fonzy_sitting_on_couch.png'
        if test_img.exists():
            frame_source = FileFrameSource(str(test_img))
            logger.info(f"Using FileFrameSource with {test_img}")
        else:
            logger.error(f"Test image not found at {test_img}. Cannot initialize frame source.")
            sys.exit(1)

    # 2. Adapter: Detector
    logger.info(f"Loading detector model: {settings.model.model_path}")
    try:
        # If MODEL_DIR is set, load model from that directory
        if settings.model.model_dir:
            logger.info(f"Using model directory: {settings.model.model_dir}")
            yolo_model = load_yolo_model(settings.model.model_dir, settings.model.model_path)
            detector = UltralyticsDetector(
                model=yolo_model,
                conf_threshold=settings.model.confidence_threshold
            )
        else:
            detector = UltralyticsDetector(
                model_path=settings.model.model_path,
                conf_threshold=settings.model.confidence_threshold
            )
    except Exception as e:
        logger.error(f"Failed to initialize detector: {e}")
        sys.exit(1)

    # 3. Adapter: Alert Sink
    alert_sink = AudioAlert(
        sound_file=settings.audio.alert_sound,
        sound_dir=settings.audio.alert_sound_dir,
        volume=settings.audio.alert_volume
    )

    # 4. App: Monitor
    app = CouchMonitorApp(
        frame_source=frame_source,
        detector=detector,
        alert_sink=alert_sink,
        settings=settings
    )

    # Run
    try:
        app.run()
    except Exception as e:
        logger.error(f"Application crashed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
