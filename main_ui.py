import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk

class MainUI:
    def __init__(self, root, title="Vehicle Log System"):
        self.root = root
        self.root.title(title)
        self.root.geometry("1200x700")

        # --- Main Frames ---
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left Section: Video Display
        self.video_frame = ttk.LabelFrame(self.main_frame, text="Live Video Feed")
        self.video_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.video_label = ttk.Label(self.video_frame)
        self.video_label.pack(fill=tk.BOTH, expand=True)

        # Right Section: Logs and Controls
        self.right_panel = ttk.Frame(self.main_frame)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=5)

        # Controls Frame
        self.controls_frame = ttk.LabelFrame(self.right_panel, text="Controls")
        self.controls_frame.pack(fill=tk.X, pady=5)
        self.load_video_btn = ttk.Button(self.controls_frame, text="Load Video", command=self.load_video)
        self.load_video_btn.pack(pady=5, padx=10, fill=tk.X)
        self.clear_db_btn = ttk.Button(self.controls_frame, text="Clear Database", command=self.clear_database)
        self.clear_db_btn.pack(pady=5, padx=10, fill=tk.X)

        # Log Display Frame
        self.log_frame = ttk.LabelFrame(self.right_panel, text="Vehicle Logs")
        self.log_frame.pack(fill=tk.BOTH, expand=True)

        # Log Table
        self.log_tree = ttk.Treeview(self.log_frame, columns=("Timestamp", "Vehicle Type", "License Plate", "Toll Charge"), show='headings')
        self.log_tree.heading("Timestamp", text="Timestamp")
        self.log_tree.heading("Vehicle Type", text="Vehicle Type")
        self.log_tree.heading("License Plate", text="License Plate")
        self.log_tree.heading("Toll Charge", text="Toll Charge")
        self.log_tree.column("Timestamp", width=150)
        self.log_tree.column("Vehicle Type", width=100)
        self.log_tree.column("License Plate", width=120)
        self.log_tree.column("Toll Charge", width=80)
        self.log_tree.pack(fill=tk.BOTH, expand=True)

        # Callbacks (to be set by the main app)
        self.load_video_callback = None
        self.clear_database_callback = None

    def set_load_video_callback(self, callback):
        self.load_video_callback = callback

    def set_clear_database_callback(self, callback):
        self.clear_database_callback = callback

    def load_video(self):
        file_path = filedialog.askopenfilename(
            title="Select a video file",
            filetypes=(("MP4 files", "*.mp4"), ("All files", "*.*"))
        )
        if file_path and self.load_video_callback:
            self.load_video_callback(file_path)

    def clear_database(self):
        if self.clear_database_callback:
            self.clear_database_callback()

    def update_video_frame(self, frame):
        """Updates the video display with a new frame."""
        if frame is not None:
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

    def update_log_table(self, logs):
        """Updates the log table with new data."""
        # Clear existing data
        for i in self.log_tree.get_children():
            self.log_tree.delete(i)
        # Insert new data
        for row in logs:
            self.log_tree.insert("", "end", values=row)

if __name__ == '__main__':
    # Example of how to run the UI
    root = tk.Tk()
    app_ui = MainUI(root)

    # Example data to show how the table updates
    sample_logs = [
        ('2023-10-27 10:00:00', 'Car', 'XYZ789', 50.0),
        ('2023-10-27 10:01:00', 'Truck', 'TRK456', 120.0)
    ]
    app_ui.update_log_table(sample_logs)

    root.mainloop()