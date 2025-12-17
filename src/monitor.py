#!/usr/bin/env python3
"""
Couch Nagger - Raspberry Pi Monitor

Continuously monitors the couch using Pi Camera and alerts when dog detected.
"""

import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime

try:
    from picamera2 import Picamera2
except ImportError:
    Picamera2 = None
    logging.warning("picamera2 not available - camera monitoring disabled")

from dog_detector import DogDetector


class CouchMonitor:
    """Main monitoring class for couch detection."""
    
    def __init__(self, config=None):
        self.config = config or self._load_config()
        self._setup_logging()
        self.detector = None
        self.camera = None
        self.last_alert_time = 0
        self.running = False
        
    def _load_config(self):
        """Load configuration from environment variables."""
        return {
            'model_path': os.getenv('MODEL_PATH', 'yolov8n.pt'),
            'confidence_threshold': float(os.getenv('CONFIDENCE_THRESHOLD', '0.20')),
            'check_interval': int(os.getenv('CHECK_INTERVAL', '10')),
            'alert_cooldown': int(os.getenv('ALERT_COOLDOWN', '300')),
            'camera_width': int(os.getenv('CAMERA_RESOLUTION_WIDTH', '640')),
            'camera_height': int(os.getenv('CAMERA_RESOLUTION_HEIGHT', '480')),
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            'log_file': os.getenv('LOG_FILE', 'logs/couch-nagger.log'),
            'image_dir': os.getenv('IMAGE_DIR', 'captures'),
        }
    
    def _setup_logging(self):
        """Configure logging."""
        log_level = getattr(logging, self.config['log_level'].upper())
        
        # Create logs directory if it doesn't exist
        log_file = Path(self.config['log_file'])
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
        
        self.logger = logging.getLogger('CouchMonitor')
        self.logger.info("Logging initialized")
    
    def initialize(self):
        """Initialize detector and camera."""
        self.logger.info("Initializing couch monitor...")
        
        # Initialize detector
        self.logger.info(f"Loading model: {self.config['model_path']}")
        try:
            self.detector = DogDetector(model_path=self.config['model_path'])
            self.logger.info("Detector initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize detector: {e}")
            raise
        
        # Initialize camera if available
        if Picamera2:
            try:
                self.logger.info("Initializing Pi Camera...")
                self.camera = Picamera2()
                camera_config = self.camera.create_still_configuration(
                    main={"size": (self.config['camera_width'], 
                                  self.config['camera_height'])}
                )
                self.camera.configure(camera_config)
                self.camera.start()
                self.logger.info("Camera initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize camera: {e}")
                self.camera = None
        else:
            self.logger.warning("Camera not available - using test mode")
        
        # Create image directory
        Path(self.config['image_dir']).mkdir(parents=True, exist_ok=True)
        
        self.logger.info("Initialization complete")
        self.logger.info(f"Configuration: {self.config}")
    
    def capture_image(self):
        """Capture an image from the camera."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = f"{self.config['image_dir']}/current_{timestamp}.jpg"
        
        if self.camera:
            try:
                self.camera.capture_file(image_path)
                return image_path
            except Exception as e:
                self.logger.error(f"Failed to capture image: {e}")
                return None
        else:
            # Test mode - use a test image if available
            test_image = 'images/test_dog_on_couch.jpg'
            if Path(test_image).exists():
                self.logger.debug(f"Using test image: {test_image}")
                return test_image
            else:
                self.logger.warning("No camera and no test image available")
                return None
    
    def send_alert(self, image_path, confidence):
        """Send alert when dog detected on couch."""
        self.logger.warning(
            f"ALERT: Dog detected on couch! "
            f"Confidence: {confidence['dog']:.0%}"
        )
        
        # Save evidence
        if image_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            evidence_path = f"{self.config['image_dir']}/alert_{timestamp}.jpg"
            
            try:
                # Copy image to evidence directory
                import shutil
                shutil.copy2(image_path, evidence_path)
                self.logger.info(f"Evidence saved: {evidence_path}")
            except Exception as e:
                self.logger.error(f"Failed to save evidence: {e}")
        
        # TODO: Add notification integrations here
        # Example: send_pushover_notification()
        # Example: send_email_alert()
        # Example: send_slack_message()
    
    def check_couch(self):
        """Perform a single couch check."""
        # Capture image
        image_path = self.capture_image()
        if not image_path:
            self.logger.warning("No image to check")
            return False
        
        # Run detection
        try:
            result = self.detector.check_image(
                image_path, 
                conf_threshold=self.config['confidence_threshold']
            )
            
            self.logger.debug(
                f"Detection result: dog_on_couch={result['dog_on_couch']}, "
                f"dog_conf={result['confidence']['dog']:.3f}, "
                f"couch_conf={result['confidence']['couch']:.3f}"
            )
            
            # Check if alert needed
            if result['dog_on_couch']:
                current_time = time.time()
                time_since_last_alert = current_time - self.last_alert_time
                
                if time_since_last_alert > self.config['alert_cooldown']:
                    self.send_alert(image_path, result['confidence'])
                    self.last_alert_time = current_time
                else:
                    time_remaining = int(self.config['alert_cooldown'] - time_since_last_alert)
                    self.logger.info(
                        f"Dog on couch but alert on cooldown "
                        f"({time_remaining}s remaining)"
                    )
            
            return result['dog_on_couch']
            
        except Exception as e:
            self.logger.error(f"Detection failed: {e}")
            return False
    
    def run(self):
        """Main monitoring loop."""
        self.logger.info("Starting couch monitoring...")
        self.running = True
        
        try:
            while self.running:
                self.check_couch()
                time.sleep(self.config['check_interval'])
                
        except KeyboardInterrupt:
            self.logger.info("Received shutdown signal")
        except Exception as e:
            self.logger.error(f"Monitoring error: {e}", exc_info=True)
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Clean shutdown."""
        self.logger.info("Shutting down...")
        self.running = False
        
        if self.camera:
            try:
                self.camera.stop()
                self.logger.info("Camera stopped")
            except Exception as e:
                self.logger.error(f"Error stopping camera: {e}")
        
        self.logger.info("Shutdown complete")


def main():
    """Main entry point."""
    monitor = CouchMonitor()
    
    try:
        monitor.initialize()
        monitor.run()
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
