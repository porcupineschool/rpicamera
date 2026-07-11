"""Simple GUI to preview the Pi camera and capture photos/video."""

import os
from datetime import datetime
from tkinter import Tk, Frame, Label, Button, StringVar, messagebox

from PIL import Image, ImageTk
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput

CAPTURE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "captures")
PREVIEW_SIZE = (640, 480)
PREVIEW_INTERVAL_MS = 66  # ~15 fps


def timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pi Camera Control")

        os.makedirs(CAPTURE_DIR, exist_ok=True)

        self.picam2 = Picamera2()
        self.video_config = self.picam2.create_video_configuration(main={"size": PREVIEW_SIZE})
        self.still_config = self.picam2.create_still_configuration()
        self.picam2.configure(self.video_config)
        self.picam2.start()

        self.recording = False
        self.encoder = None

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
        frame = self.picam2.capture_array("main")
        image = Image.fromarray(frame)
        photo = ImageTk.PhotoImage(image=image)
        self.preview_label.configure(image=photo)
        self.preview_label.image = photo  # keep a reference so it isn't garbage collected
        self.root.after(PREVIEW_INTERVAL_MS, self.update_preview)

    def take_photo(self):
        if self.recording:
            return
        filename = os.path.join(CAPTURE_DIR, f"photo_{timestamp()}.jpg")
        self.status_var.set("Capturing photo...")
        self.root.update_idletasks()
        try:
            self.picam2.switch_mode_and_capture_file(self.still_config, filename)
            self.status_var.set(f"Saved {os.path.basename(filename)}")
        except Exception as exc:
            messagebox.showerror("Capture failed", str(exc))
            self.status_var.set("Ready")

    def toggle_recording(self):
        if not self.recording:
            filename = os.path.join(CAPTURE_DIR, f"video_{timestamp()}.mp4")
            self.encoder = H264Encoder()
            self.picam2.start_recording(self.encoder, FfmpegOutput(filename))
            self.recording = True
            self.record_button.configure(text="Stop Recording")
            self.photo_button.configure(state="disabled")
            self.status_var.set(f"Recording to {os.path.basename(filename)}...")
        else:
            self.picam2.stop_recording()
            self.recording = False
            self.record_button.configure(text="Start Recording")
            self.photo_button.configure(state="normal")
            self.status_var.set("Ready")

    def on_close(self):
        if self.recording:
            self.picam2.stop_recording()
        self.picam2.stop()
        self.root.destroy()


def main():
    root = Tk()
    CameraApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
