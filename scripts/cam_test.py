from picamera2 import Picamera2
from time import sleep

picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration(main={"size": (640, 480)}))
picam2.start()
sleep(1)
picam2.capture_file("/tmp/picam2.jpg")
print("wrote /tmp/picam2.jpg")
picam2.stop()