# Vehicle Detection and License Plate Recognition System

This is a Python-based application that uses computer vision and optical character recognition (OCR) to detect vehicles in a video stream, identify their license plates, and log the information into a database. The application features a graphical user interface (GUI) to display the live video feed and the collected data.

## Features

- **Real-time Vehicle Detection**: Detects multiple vehicle types (cars, trucks, buses) in a video file using the YOLOv8 model.
- **License Plate Recognition**: Utilizes a hybrid approach: Omni-LPR for accurate license plate detection and bounding box extraction, followed by Pytesseract for robust optical character recognition (OCR) on the cropped plate images. Includes intelligent post-processing for Indian license plate formats.
- **Improved OCR Accuracy**: Enhanced image pre-processing and post-processing with contextual rules lead to more accurate license plate recognition, especially for Indian formats.
- **Efficient Logging**: Temporal filtering prevents redundant logging of the same license plate multiple times.
- **Database Logging**: Records the timestamp, vehicle type, and license plate number for each detected vehicle in an SQLite database (`vehicle_log.db`).
- **Graphical User Interface**: A user-friendly interface built with Tkinter that displays the video feed with bounding boxes and a real-time log of detected vehicles.

## Project Structure

The application is organized into several modules, each with a specific responsibility:

```
ANPR_Application/
├── app.py                  # Main script to run the application
├── main_ui.py              # Defines the GUI layout and components
├── vehicle_detector.py     # Handles vehicle detection using OpenCV and YOLOv8
├── anpr_module.py          # Performs OCR to recognize license plates using Omni-LPR (detection) and Pytesseract (recognition)
├── database_logger.py      # Manages all SQLite database operations
├── requirements.txt        # Lists all Python dependencies
├── vehicle_log.db          # SQLite database file (created on first run)
└── yolov8n.pt              # YOLOv8 nano model weights (downloaded automatically by ultralytics)
```

## Setup and Installation

Follow these steps to set up and run the project on your local machine.

### 1. Prerequisites

- **Python 3.13+**
- **NVIDIA GPU with CUDA 11.8+** (for GPU acceleration with Omni-LPR, optional but recommended for performance)
- **Tesseract OCR Engine**: Pytesseract requires the Tesseract OCR engine to be installed on your system. Follow the instructions [here](https://tesseract-ocr.github.io/tessdoc/Installation.html) for your operating system.

### 2. Clone the Repository

First, get the project files onto your machine. If you have git, you can clone it. Otherwise, download and extract the source code.

```bash
# Navigate to the project directory
cd path/to/ANPR_Application

# Create a virtual environment named 'venv'
python3 -m venv venv
```

### 3. Activate the Virtual Environment

- **On macOS and Linux:**
  ```bash
  source venv/bin/activate
  ```
- **On Windows:**
  ```bash
  .\venv\Scripts\activate
  ```

### 4. Install Python Dependencies

With the virtual environment active, install all the required libraries from the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### 5. Download YOLOv8 Model Files

The vehicle detection module uses the YOLOv8 nano model (`yolov8n.pt`), which will be automatically downloaded by the `ultralytics` library the first time it's used.

## How to Run the Application

The application uses the `omni-lpr` service, which runs in the background. You need to start this service first, and then run the main application.

1.  **Start the Omni-LPR Service (in a separate terminal):**
    Open a new terminal, activate your virtual environment, and run:
    ```bash
    TRANSPORT=sse omni-lpr --host 0.0.0.0 --port 8000
    ```
    Keep this terminal open and running in the background.

2.  **Run the Main Application:**
    In your original terminal (where your virtual environment is active), run:
    ```bash
    python app.py
    ```

## Usage

1.  Launch the application.
2.  Click the **"Load Video"** button.
3.  Select a video file (e.g., in `.mp4` format) from your local file system.
4.  The application will start processing the video. Detected vehicles will be marked with a green bounding box, and the right-side panel will populate with license plate data as it is detected and logged.

## Dependencies

- **OpenCV-Python (4.11.0.86)**: For video processing and computer vision tasks.
- **NumPy (2.1.0)**: For numerical operations, especially with image data.
- **ultralytics**: For YOLOv8 vehicle detection.
- **requests**: For making HTTP requests to the Omni-LPR service.
- **omni-lpr**: For accurate license plate detection.
- **pytesseract**: For robust optical character recognition.
- **Pillow**: Image processing library, a dependency for Pytesseract.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
