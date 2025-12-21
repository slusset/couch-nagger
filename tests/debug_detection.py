from ultralytics import YOLO
from pathlib import Path

# Load model
model = YOLO('yolov8m.pt')

# Run detection
image_path = Path('../assets/test-images/test_rpicam_couch.jpg')
results = model(str(image_path))

print(f"\nDetections in {image_path.name}:")
print("-" * 60)

for box in results[0].boxes:
    class_id = int(box.cls[0])
    class_name = results[0].names[class_id]
    conf = float(box.conf[0])
    bbox = box.xyxy[0].tolist()

    print(f"Class ID: {class_id:3d} | Name: {class_name:15s} | Confidence: {conf:.3f}")
    print(f"  BBox: [{bbox[0]:.1f}, {bbox[1]:.1f}, {bbox[2]:.1f}, {bbox[3]:.1f}]")

print("\nLooking for:")
print(f"  Dog (class 16): {'FOUND' if any(int(box.cls[0]) == 16 for box in results[0].boxes) else 'NOT FOUND'}")
print(f"  Couch (class 57): {'FOUND' if any(int(box.cls[0]) == 57 for box in results[0].boxes) else 'NOT FOUND'}")
