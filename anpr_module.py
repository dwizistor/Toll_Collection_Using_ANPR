import cv2
import pytesseract
from PIL import Image
import re
import requests
import base64
import json

OMNI_LPR_API_URL = "http://localhost:8000/api/v1/tools/detect_and_recognize_plate/invoke"

STATE_CODES = [
    "AP", "AR", "AS", "BR", "CG", "GA", "GJ", "HR", "HP", "JH", "KA", "KL",
    "MP", "MH", "MN", "ML", "MZ", "NL", "OD", "PB", "RJ", "SK", "TN", "TS",
    "TR", "UP", "UK", "WB", "AN", "CH", "DN", "DD", "DL", "LD", "PY"
]

PLATE_REGEX = re.compile(r'^([A-Z]{2})([0-9]{2})([A-Z]{1,2})([0-9]{4})$')

def post_process_plate(text: str) -> str:
    """Cleans and corrects a license plate string using contextual rules."""
    cleaned_text = ''.join(filter(str.isalnum, text)).upper()

    # Correction for common OCR errors
    cleaned_text = cleaned_text.replace('IND', '') # Remove IND from the beginning
    if cleaned_text.startswith("MP4Y"):
        cleaned_text = cleaned_text.replace("4Y", "04", 1)

    match = PLATE_REGEX.match(cleaned_text)
    if not match:
        return ""

    p1 = match.group(1)
    if p1 not in STATE_CODES:
        return ""

    return cleaned_text

def recognize_plate(image):
    """
    Detects a license plate using Omni-LPR and recognizes it using Tesseract.
    """
    plate_number = None
    
    try:
        # 1. Use Omni-LPR for detection
        _, buffer = cv2.imencode('.jpg', image)
        encoded_image = base64.b64encode(buffer).decode('utf-8')

        payload = {
            "image_base64": encoded_image,
            "detector_model": "yolo-v9-s-608-license-plate-end2end",
        }
        headers = {"Content-Type": "application/json"}

        response = requests.post(OMNI_LPR_API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        
        results = response.json()

        if not results.get('content'):
            return None

        content = results['content'][0]
        if not content.get('data'):
            return None

        plate_data = content['data']

        if plate_data and isinstance(plate_data, list):
            best_detection_confidence = 0
            for plate_info in plate_data:
                detection_confidence = plate_info.get('detection', {}).get('confidence', 0)
                if detection_confidence > best_detection_confidence:
                    best_detection_confidence = detection_confidence
                    bbox = plate_info.get('detection', {}).get('bounding_box')
                    if not bbox:
                        continue

                    # 2. Crop the license plate
                    x1, y1, x2, y2 = int(bbox['x1']), int(bbox['y1']), int(bbox['x2']), int(bbox['y2'])
                    plate_roi = image[y1:y2, x1:x2]

                    # 3. Use Pytesseract for recognition
                    pil_image = Image.fromarray(cv2.cvtColor(plate_roi, cv2.COLOR_BGR2RGB))
                    text = pytesseract.image_to_string(pil_image, config='--psm 6')

                    # 4. Post-process
                    corrected_plate = post_process_plate(text)
                    if corrected_plate:
                        plate_number = corrected_plate

    except requests.exceptions.RequestException:
        return None
    except Exception:
        return None

    return plate_number