import tkinter as tk
import cv2
import threading
import argparse
from PIL import Image, ImageTk

# Import your custom modules
from main_ui import MainUI
import vehicle_detector
import anpr_module
import database_logger

# Define Toll Rates (Placeholder values - customize as needed)
TOLL_RATES = {
    'car': 50.0,
    'truck': 150.0,
    'bus': 150.0, # Assuming bus falls under HCV for simplicity
    'Unknown': 0.0 # Default for unknown vehicle types
}

def calculate_toll_charge(vehicle_type):
    """Calculates the toll charge based on vehicle type."""
    return TOLL_RATES.get(vehicle_type, 0.0)

def process_video_cli(video_path):
    """Processes a video file from the command line without a GUI."""
    print(f"CLI mode: Processing video at {video_path}")
    video_cap = cv2.VideoCapture(video_path)
    if not video_cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return

    database_logger.init_db()
    processed_plates = set()
    frame_count = 0

    while video_cap.isOpened():
        ret, frame = video_cap.read()
        if not ret:
            break

        # Process every 5th frame to speed up CLI processing
        if frame_count % 5 == 0:
            vehicles, _ = vehicle_detector.detect_vehicles(frame)

            for (box, vehicle_type) in vehicles:
                x, y, w, h = box
                # Ensure ROI is within frame boundaries
                if x > 0 and y > 0 and w > 0 and h > 0:
                    vehicle_roi = frame[y:y+h, x:x+w]

                    if vehicle_detector.is_license_plate_likely(vehicle_roi):
                        plate_number = anpr_module.recognize_plate(vehicle_roi)
                        toll_charge = calculate_toll_charge(vehicle_type)

                        if plate_number and plate_number not in processed_plates:
                            processed_plates.add(plate_number)
                            database_logger.log_vehicle(plate_number, vehicle_type, toll_charge)
                            print(f"Logged: Plate={plate_number}, Type={vehicle_type}, Toll={toll_charge}")
        
        frame_count += 1

    video_cap.release()
    print("CLI processing finished.")

class Application:
    def __init__(self, root):
        self.root = root
        self.ui = MainUI(root)
        self.ui.set_load_video_callback(self.start_video_processing)
        self.ui.set_clear_database_callback(self.clear_database_and_refresh)

        # --- Application State ---
        self.video_path = None
        self.video_cap = None
        self.processing_thread = None
        self.is_processing = False
        self.processed_plates = set()

        # Initialize the database
        database_logger.init_db()
        self.refresh_log_display()

    def start_video_processing(self, video_path):
        """Callback to start processing a new video."""
        if self.is_processing:
            self.stop_processing()

        self.video_path = video_path
        self.video_cap = cv2.VideoCapture(self.video_path)
        if not self.video_cap.isOpened():
            print(f"Error: Could not open video file {self.video_path}")
            return

        self.is_processing = True
        self.processed_plates.clear()
        self.processing_thread = threading.Thread(target=self.process_video_loop, daemon=True)
        self.processing_thread.start()

    def process_video_loop(self):
        """The main loop for video processing in a separate thread for the GUI."""
        while self.is_processing and self.video_cap.isOpened():
            ret, frame = self.video_cap.read()
            if not ret:
                break

            display_frame = cv2.resize(frame, (800, 600))
            vehicles, _ = vehicle_detector.detect_vehicles(frame)

            for (box, vehicle_type) in vehicles:
                x, y, w, h = box
                if x > 0 and y > 0 and w > 0 and h > 0:
                    vehicle_roi = frame[y:y+h, x:x+w]

                    if vehicle_detector.is_license_plate_likely(vehicle_roi):
                        plate_number = anpr_module.recognize_plate(vehicle_roi)
                        toll_charge = calculate_toll_charge(vehicle_type)

                        if plate_number and plate_number not in self.processed_plates:
                            self.processed_plates.add(plate_number)
                            database_logger.log_vehicle(plate_number, vehicle_type, toll_charge)
                            print(f"Logged: {plate_number}, Type: {vehicle_type}, Toll: {toll_charge}")
                            self.root.after(0, self.refresh_log_display)

                rx, ry, rw, rh = int(x*800/frame.shape[1]), int(y*600/frame.shape[0]), int(w*800/frame.shape[1]), int(h*600/frame.shape[0])
                cv2.rectangle(display_frame, (rx, ry), (rx + rw, ry + rh), (0, 255, 0), 2)
                cv2.putText(display_frame, vehicle_type, (rx, ry - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            self.update_ui_frame(display_frame)

        self.stop_processing()

    def update_ui_frame(self, frame):
        """Convert and update the frame in the UI thread."""
        if self.is_processing:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.root.after(0, self.ui.update_video_frame, rgb_frame)

    def refresh_log_display(self):
        """Fetches logs from the DB and updates the UI table."""
        logs = database_logger.get_all_logs()
        self.ui.update_log_table(logs)

    def clear_database_and_refresh(self):
        """Clears the database and refreshes the UI display."""
        database_logger.clear_logs()
        self.refresh_log_display()
        print("Database cleared.")

    def stop_processing(self):
        """Stops the video processing thread and releases resources."""
        self.is_processing = False
        if self.video_cap:
            self.video_cap.release()
        self.processing_thread = None

    def on_close(self):
        """Handles window closing events."""
        self.stop_processing()
        self.root.destroy()

def main():
    """Main function to run the application."""
    parser = argparse.ArgumentParser(description="Vehicle Detection and ANPR System.")
    parser.add_argument("--input", type=str, help="Path to the video file to process in CLI mode.")
    args = parser.parse_args()

    if args.input:
        process_video_cli(args.input)
    else:
        root = tk.Tk()
        app = Application(root)
        root.protocol("WM_DELETE_WINDOW", app.on_close)
        root.mainloop()

if __name__ == "__main__":
    main()
