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


def load_config():
    """Load configuration from environment variables."""
    return {
        'model_path': os.getenv('MODEL_PATH', 'yolov8m.pt'),
        'confidence_threshold': float(os.getenv('CONFIDENCE_THRESHOLD', '0.25')),
        'check_interval': float(os.getenv('CHECK_INTERVAL', '10.0')),
        'alert_cooldown': float(os.getenv('ALERT_COOLDOWN', '300.0')),
        'camera_width': int(os.getenv('CAMERA_RESOLUTION_WIDTH', '640')),
        'camera_height': int(os.getenv('CAMERA_RESOLUTION_HEIGHT', '480')),
        'log_level': os.getenv('LOG_LEVEL', 'INFO'),
        'log_file': os.getenv('LOG_FILE', 'logs/couch-nagger.log'),
        'test_image': os.getenv('TEST_IMAGE', 'images/test_dog_on_couch.jpg'),
        'alert_sound': os.getenv('ALERT_SOUND', '/usr/share/sounds/alsa/Front_Center.wav'),
        'alert_sound_dir': os.getenv('ALERT_SOUND_DIR'),
    }


def main():
    config = load_config()
    setup_logging(config['log_level'], config['log_file'])
    logger = logging.getLogger("Main")

    logger.info("Initializing Couch Nagger (Hexagonal)...")

    # 1. Adapter: Frame Source
    frame_source = None
    if PICAMERA_AVAILABLE:
        try:
            frame_source = Picamera2FrameSource(
                width=config['camera_width'],
                height=config['camera_height']
            )
            logger.info("Using Picamera2FrameSource")
        except Exception as e:
            logger.error(f"Failed to initialize Picamera2: {e}")
    
    if frame_source is None:
        logger.warning("Picamera2 not available or failed. Falling back to FileFrameSource.")
        test_img = config['test_image']
        if os.path.exists(test_img):
            frame_source = FileFrameSource(test_img)
            logger.info(f"Using FileFrameSource with {test_img}")
        else:
            logger.error(f"Test image not found at {test_img}. Cannot initialize frame source.")
            sys.exit(1)

    # 2. Adapter: Detector
    logger.info(f"Loading detector model: {config['model_path']}")
    try:
        detector = UltralyticsDetector(
            model_path=config['model_path'],
            conf_threshold=config['confidence_threshold']
        )
    except Exception as e:
        logger.error(f"Failed to initialize detector: {e}")
        sys.exit(1)

    # 3. Adapter: Alert Sink
    alert_sink = AudioAlert(
        sound_file=config['alert_sound'],
        sound_dir=config['alert_sound_dir'],
    )

    # 4. App: Monitor
    app = CouchMonitorApp(
        frame_source=frame_source,
        detector=detector,
        alert_sink=alert_sink,
        check_interval=config['check_interval'],
        alert_cooldown=config['alert_cooldown']
    )

    # Run
    try:
        app.run()
    except Exception as e:
        logger.error(f"Application crashed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
