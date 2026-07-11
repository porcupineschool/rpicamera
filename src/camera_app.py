"""Simple GUI to preview the Pi camera and capture photos/video.

Uses the legacy `picamera` (v1) library, for Raspberry Pi OS versions
(e.g. Raspbian Buster) that predate the picamera2/libcamera stack.
"""

import io
import os
from datetime import datetime
from tkinter import Tk, Frame, Label, Button, StringVar, messagebox

import numpy as np
import picamera
from PIL import Image, ImageTk

CAPTURE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "captures")
PREVIEW_SIZE = (640, 480)
PREVIEW_INTERVAL_MS = 100  # ~10 fps


def timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pi Camera Control")

        os.makedirs(CAPTURE_DIR, exist_ok=True)

        self.camera = picamera.PiCamera()
        self.camera.resolution = PREVIEW_SIZE

        self.recording = False
        self.preview_job = None
        self.video_path = None

        self.preview_label = Label(root)
        self.preview_label.pack()

        self.status_var = StringVar(value="Ready")
        Label(root, textvariable=self.status_var).pack(pady=(4, 8))

        button_row = Frame(root)
        button_row.pack(pady=(0, 8))

        self.photo_button = Button(button_row, text="Take Photo", command=self.take_photo, width=15)
        self.photo_button.pack(side="left", padx=5)

        self.record_button = Button(button_row, text="Start Recording", command=self.toggle_recording, width=15)
        self.record_button.pack(side="left", padx=5)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.update_preview()

    def update_preview(self):
        stream = io.BytesIO()
        self.camera.capture(stream, format="rgb", use_video_port=True)
        frame = np.frombuffer(stream.getvalue(), dtype=np.uint8)
        frame = frame.reshape((PREVIEW_SIZE[1], PREVIEW_SIZE[0], 3))
        image = Image.fromarray(frame)
        photo = ImageTk.PhotoImage(image=image)
        self.preview_label.configure(image=photo)
        self.preview_label.image = photo  # keep a reference so it isn't garbage collected
        self.preview_job = self.root.after(PREVIEW_INTERVAL_MS, self.update_preview)

    def take_photo(self):
        if self.recording:
            return
        filename = os.path.join(CAPTURE_DIR, f"photo_{timestamp()}.jpg")
        self.status_var.set("Capturing photo...")
        self.root.update_idletasks()
        try:
            self.camera.capture(filename)
            self.status_var.set(f"Saved {os.path.basename(filename)}")
        except Exception as exc:
            messagebox.showerror("Capture failed", str(exc))
            self.status_var.set("Ready")

    def toggle_recording(self):
        if not self.recording:
            self.video_path = os.path.join(CAPTURE_DIR, f"video_{timestamp()}.h264")
            if self.preview_job is not None:
                self.root.after_cancel(self.preview_job)
                self.preview_job = None
            self.camera.start_recording(self.video_path)
            self.recording = True
            self.record_button.configure(text="Stop Recording")
            self.photo_button.configure(state="disabled")
            self.status_var.set(f"Recording to {os.path.basename(self.video_path)}...")
        else:
            self.camera.stop_recording()
            self.recording = False
            self.record_button.configure(text="Start Recording")
            self.photo_button.configure(state="normal")
            self.status_var.set(f"Saved {os.path.basename(self.video_path)}")
            self.update_preview()

    def on_close(self):
        if self.preview_job is not None:
            self.root.after_cancel(self.preview_job)
        if self.recording:
            self.camera.stop_recording()
        self.camera.close()
        self.root.destroy()


def main():
    root = Tk()
    CameraApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
