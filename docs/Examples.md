# Usage Examples

Practical examples for common use cases with Couch Nagger.

## Basic Detection

### Single Image Check

```python
from dog_detector import DogDetector

detector = DogDetector()
result = detector.check_image('photo.jpg')

if result['dog_on_couch']:
    print("Alert: Dog detected on couch!")
    print(f"Confidence: {result['confidence']['dog']:.0%}")
else:
    print("All clear!")
```

### Multiple Images

```python
images = ['morning.jpg', 'afternoon.jpg', 'evening.jpg']
detector = DogDetector()

for img in images:
    result = detector.check_image(img)
    status = "ON COUCH" if result['dog_on_couch'] else "OK"
    print(f"{img}: {status}")
```

## Webcam Monitoring

### Continuous Monitoring

```python
import cv2
import time
from dog_detector import DogDetector

detector = DogDetector()
cap = cv2.VideoCapture(0)  # 0 = default webcam

last_alert_time = 0
alert_cooldown = 300  # 5 minutes in seconds

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Save frame temporarily
    cv2.imwrite('temp_frame.jpg', frame)
    
    # Check for dog
    result = detector.check_image('temp_frame.jpg')
    
    if result['dog_on_couch']:
        current_time = time.time()
        if current_time - last_alert_time > alert_cooldown:
            print("ALERT: Fonzy is on the couch!")
            # Add your alert mechanism here
            last_alert_time = current_time
    
    # Check every 10 seconds
    time.sleep(10)

cap.release()
```

### Optimized Webcam Loop

```python
import cv2
import time
from dog_detector import DogDetector

class CouchMonitor:
    def __init__(self, check_interval=10, alert_cooldown=300):
        self.detector = DogDetector()
        self.check_interval = check_interval
        self.alert_cooldown = alert_cooldown
        self.last_alert_time = 0
    
    def send_alert(self, confidence):
        """Override this to customize alerts"""
        print(f"ALERT: Dog on couch! Confidence: {confidence:.0%}")
    
    def run(self):
        cap = cv2.VideoCapture(0)
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                cv2.imwrite('temp_frame.jpg', frame)
                result = self.detector.check_image('temp_frame.jpg')
                
                if result['dog_on_couch']:
                    current_time = time.time()
                    if current_time - self.last_alert_time > self.alert_cooldown:
                        self.send_alert(result['confidence']['dog'])
                        self.last_alert_time = current_time
                
                time.sleep(self.check_interval)
        finally:
            cap.release()

# Use it
monitor = CouchMonitor(check_interval=10, alert_cooldown=300)
monitor.run()
```

## Raspberry Pi Camera

### Basic Pi Camera Setup

```python
from picamera2 import Picamera2
import time
from dog_detector import DogDetector

# Initialize
picam = Picamera2()
config = picam.create_still_configuration()
picam.configure(config)
picam.start()

detector = DogDetector(model_path='yolov8n.pt')  # Lightweight model

try:
    while True:
        # Capture image
        picam.capture_file('current.jpg')
        
        # Detect
        result = detector.check_image('current.jpg', conf_threshold=0.20)
        
        if result['dog_on_couch']:
            print("Dog detected!")
            # Save evidence
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            picam.capture_file(f'evidence_{timestamp}.jpg')
        
        time.sleep(10)
        
finally:
    picam.stop()
```

### Pi with Motion Detection

```python
from picamera2 import Picamera2
import cv2
import numpy as np
from dog_detector import DogDetector

class MotionDetector:
    def __init__(self):
        self.picam = Picamera2()
        self.detector = DogDetector(model_path='yolov8n.pt')
        self.prev_frame = None
        self.motion_threshold = 5000
    
    def has_motion(self, frame):
        if self.prev_frame is None:
            self.prev_frame = frame
            return False
        
        # Calculate difference
        diff = cv2.absdiff(self.prev_frame, frame)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 25, 255, cv2.THRESH_BINARY)
        
        motion_pixels = np.sum(thresh) / 255
        self.prev_frame = frame
        
        return motion_pixels > self.motion_threshold
    
    def run(self):
        self.picam.start()
        
        try:
            while True:
                # Capture frame
                frame = self.picam.capture_array()
                
                # Only run detection if motion detected
                if self.has_motion(frame):
                    cv2.imwrite('motion.jpg', frame)
                    result = self.detector.check_image('motion.jpg')
                    
                    if result['dog_on_couch']:
                        print("Dog on couch detected after motion!")
                
                time.sleep(1)
        finally:
            self.picam.stop()

# Use it
motion_detector = MotionDetector()
motion_detector.run()
```

## Notification Integration

### Email Alerts

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from dog_detector import DogDetector

def send_email_alert(image_path, confidence):
    sender = "your_email@gmail.com"
    receiver = "alert_recipient@gmail.com"
    password = "your_app_password"
    
    msg = MIMEMultipart()
    msg['Subject'] = f"Alert: Dog on Couch! ({confidence:.0%} confidence)"
    msg['From'] = sender
    msg['To'] = receiver
    
    # Add text
    text = MIMEText(f"Fonzy was detected on the couch at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    msg.attach(text)
    
    # Add image
    with open(image_path, 'rb') as f:
        img = MIMEImage(f.read())
        msg.attach(img)
    
    # Send
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)

# Use with detector
detector = DogDetector()
result = detector.check_image('current.jpg')

if result['dog_on_couch']:
    send_email_alert('current.jpg', result['confidence']['dog'])
```

### Pushover Notifications

```python
import requests
from dog_detector import DogDetector

def send_pushover_alert(message, image_path=None):
    PUSHOVER_TOKEN = "your_app_token"
    PUSHOVER_USER = "your_user_key"
    
    data = {
        'token': PUSHOVER_TOKEN,
        'user': PUSHOVER_USER,
        'message': message,
        'title': 'Couch Alert!'
    }
    
    files = None
    if image_path:
        files = {'attachment': open(image_path, 'rb')}
    
    response = requests.post(
        'https://api.pushover.net/1/messages.json',
        data=data,
        files=files
    )
    
    return response.json()

# Use it
detector = DogDetector()
result = detector.check_image('current.jpg')

if result['dog_on_couch']:
    send_pushover_alert(
        f"Fonzy on couch! Confidence: {result['confidence']['dog']:.0%}",
        'current.jpg'
    )
```

### Slack Integration

```python
from slack_sdk import WebClient
from dog_detector import DogDetector

def send_slack_alert(channel, image_path, confidence):
    client = WebClient(token="xoxb-your-token")
    
    # Upload image
    response = client.files_upload(
        channels=channel,
        file=image_path,
        title="Dog on Couch Alert",
        initial_comment=f"Fonzy detected on couch! Confidence: {confidence:.0%}"
    )
    
    return response

# Use it
detector = DogDetector()
result = detector.check_image('current.jpg')

if result['dog_on_couch']:
    send_slack_alert('#alerts', 'current.jpg', result['confidence']['dog'])
```

## Sound/Audio Alerts

### Play Sound

```python
import pygame
from dog_detector import DogDetector

def play_alert_sound():
    pygame.mixer.init()
    pygame.mixer.music.load('alert.mp3')
    pygame.mixer.music.play()
    
    # Wait for sound to finish
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

# Use it
detector = DogDetector()
result = detector.check_image('current.jpg')

if result['dog_on_couch']:
    play_alert_sound()
```

### Text-to-Speech

```python
import pyttsx3
from dog_detector import DogDetector

def speak_alert(message):
    engine = pyttsx3.init()
    engine.say(message)
    engine.runAndWait()

# Use it
detector = DogDetector()
result = detector.check_image('current.jpg')

if result['dog_on_couch']:
    speak_alert("Fonzy, get off the couch now!")
```

## Batch Processing

### Process Directory

```python
from pathlib import Path
from dog_detector import DogDetector
import json

def batch_process_directory(directory, output_file='results.json'):
    detector = DogDetector()
    results = {}
    
    image_paths = list(Path(directory).glob('*.jpg'))
    total = len(image_paths)
    
    for i, img_path in enumerate(image_paths, 1):
        print(f"Processing {i}/{total}: {img_path.name}")
        
        result = detector.check_image(str(img_path))
        results[img_path.name] = {
            'dog_on_couch': result['dog_on_couch'],
            'confidence_dog': result['confidence']['dog'],
            'confidence_couch': result['confidence']['couch']
        }
    
    # Save results
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    return results

# Use it
results = batch_process_directory('images/')
dog_on_couch_count = sum(1 for r in results.values() if r['dog_on_couch'])
print(f"Found {dog_on_couch_count} images with dog on couch")
```

### Generate Report

```python
from pathlib import Path
from dog_detector import DogDetector
import csv
from datetime import datetime

def generate_report(image_dir, output_csv='detection_report.csv'):
    detector = DogDetector()
    
    with open(output_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Filename', 'Timestamp', 'Dog Detected', 
                        'Dog Confidence', 'Couch Confidence'])
        
        for img_path in Path(image_dir).glob('*.jpg'):
            result = detector.check_image(str(img_path))
            
            writer.writerow([
                img_path.name,
                datetime.now().isoformat(),
                result['dog_on_couch'],
                f"{result['confidence']['dog']:.3f}",
                f"{result['confidence']['couch']:.3f}"
            ])
    
    print(f"Report saved to {output_csv}")

# Use it
generate_report('images/')
```

## Advanced: Video Processing

### Process Video File

```python
import cv2
from dog_detector import DogDetector

def process_video(video_path, sample_rate=30):
    """Process video, checking every Nth frame"""
    detector = DogDetector()
    cap = cv2.VideoCapture(video_path)
    
    frame_count = 0
    detections = []
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Only check every Nth frame
        if frame_count % sample_rate == 0:
            cv2.imwrite('temp_frame.jpg', frame)
            result = detector.check_image('temp_frame.jpg')
            
            if result['dog_on_couch']:
                timestamp = frame_count / cap.get(cv2.CAP_PROP_FPS)
                detections.append({
                    'frame': frame_count,
                    'timestamp': timestamp,
                    'confidence': result['confidence']['dog']
                })
                print(f"Detection at {timestamp:.1f}s")
    
    cap.release()
    return detections

# Use it
detections = process_video('recording.mp4', sample_rate=30)
print(f"Found {len(detections)} instances of dog on couch")
```

For more examples and configuration options, see [Configuration](Configuration.md).
