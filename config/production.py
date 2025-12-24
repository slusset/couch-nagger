"""Production configuration for Raspberry Pi."""

CONFIG = {
    # Model settings - optimized for Pi
    "model_path": "yolov8n.pt",  # Lightweight nano model
    "confidence_threshold": 0.20,  # Lower threshold for Pi camera
    "person_confidence_threshold": 0.25,
    # Detection settings
    "check_interval": 10,  # Check every 10 seconds
    "alert_cooldown": 300,  # 5 minute cooldown between alerts
    # Camera settings (Pi Camera)
    "camera_width": 640,
    "camera_height": 480,
    "save_images": True,
    # Logging
    "log_level": "INFO",
    "log_file": "/home/pi/couch-nagger/logs/couch-nagger.log",
    # Storage
    "image_dir": "/home/pi/couch-nagger/captures",
}
