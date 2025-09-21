import cv2
from ultralytics import YOLO

# Load the YOLOv8 model
# This will download yolov8n.pt if it's not present
model = YOLO('yolov8n.pt')

# COCO class IDs for vehicles: car, motorcycle, bus, truck
VEHICLE_CLASS_IDS = [2, 3, 5, 7]

def detect_vehicles(frame):
    """Detects vehicles in a single frame using YOLOv8."""
    detected_vehicles = []

    # Perform inference
    results = model.predict(frame, verbose=False)

    # Process results
    for result in results:
        for box in result.boxes:
            # Check if the detected object is a vehicle
            if box.cls in VEHICLE_CLASS_IDS:
                # Get class name
                vehicle_type = result.names[int(box.cls)]
                
                # Get bounding box coordinates in (x, y, w, h) format
                x1, y1, x2, y2 = box.xyxy[0]
                x = int(x1)
                y = int(y1)
                w = int(x2 - x1)
                h = int(y2 - y1)
                
                # Append to list
                detected_vehicles.append(((x, y, w, h), vehicle_type))
                
    # The second return value (frame) is kept for compatibility with the old signature
    # although it's not modified in this function.
    return detected_vehicles, frame

def is_license_plate_likely(vehicle_roi):
    """
    Checks if a license plate is likely within the vehicle's bounding box.
    This is a simplified check based on aspect ratio and contour shape.
    """
    if vehicle_roi is None or vehicle_roi.size == 0:
        return False
        
    gray_roi = cv2.cvtColor(vehicle_roi, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray_roi, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 150)

    contours, _ = cv2.findContours(edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.04 * peri, True)
        if len(approx) == 4:  # Look for four-sided contours
            (x, y, w, h) = cv2.boundingRect(approx)
            aspect_ratio = w / float(h)
            # Check for aspect ratio typical of a license plate
            if w > 20 and h > 10 and 2.0 < aspect_ratio < 5.5:
                return True
    return False
    return detected_vehicles, frame