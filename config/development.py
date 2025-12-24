"""Development configuration for local testing."""

CONFIG = {
    # Model settings
    "model_path": "yolov8m.pt",  # Use medium model on dev machine
    "confidence_threshold": 0.25,
    "person_confidence_threshold": 0.30,
    # Detection settings
    "check_interval": 5,  # Check more frequently in dev
    "alert_cooldown": 60,  # Shorter cooldown for testing
    # Camera settings (webcam)
    "camera_width": 1280,
    "camera_height": 720,
    # Logging
    "log_level": "DEBUG",
    "log_file": "logs/development.log",
    # Storage
    "image_dir": "captures/dev",
}
