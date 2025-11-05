from ultralytics import YOLO
from PIL import Image
import cv2

# Load pre-trained model (downloads automatically on first run)
model = YOLO('yolov8n.pt')  # 'n' = nano (fastest, smallest)

# Test with an image
image_path = 'test_dog_on_couch.jpg'
results = model(image_path)

# Display results
for result in results:
    # Print detected objects
    for box in result.boxes:
        class_id = int(box.cls[0])
        class_name = result.names[class_id]
        confidence = float(box.conf[0])
        bbox = box.xyxy[0].tolist()  # [x1, y1, x2, y2]

        print(f"{class_name}: {confidence:.2f} at {bbox}")

    # Save annotated image
    result.save('result.jpg')

# Or just show it
result.show()


def dog_on_couch(results):
    dog_boxes = []
    couch_boxes = []

    for box in results[0].boxes:
        class_id = int(box.cls[0])
        bbox = box.xyxy[0].tolist()

        if class_id == 16:  # dog
            dog_boxes.append(bbox)
        elif class_id == 57:  # couch
            couch_boxes.append(bbox)

    # Check if any dog box overlaps with couch box
    for dog in dog_boxes:
        for couch in couch_boxes:
            if boxes_overlap(dog, couch):
                return True
    return False