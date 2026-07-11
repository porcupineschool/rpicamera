"""Simple GUI to preview the Pi camera and capture photos/video.

Uses the legacy `picamera` (v1) library, for Raspberry Pi OS versions
(e.g. Raspbian Buster) that predate the picamera2/libcamera stack.
"""

import io
import os
import time
from datetime import datetime
from tkinter import Tk, Frame, Label, Button, Entry, StringVar, messagebox

import numpy as np
import picamera
from PIL import Image, ImageTk

CAPTURE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "captures")
PREVIEW_SIZE = (640, 480)
PREVIEW_INTERVAL_MS = 100  # ~10 fps
DEFAULT_FRAMERATE = 30


def timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pi Camera Control")

        os.makedirs(CAPTURE_DIR, exist_ok=True)

        self.camera = picamera.PiCamera()
        self.camera.resolution = PREVIEW_SIZE
        self.camera.framerate = DEFAULT_FRAMERATE

        self.recording = False
        self.preview_job = None
        self.video_path = None
        self.manual_exposure = False

        self.preview_label = Label(root)
        self.preview_label.pack()

        self.status_var = StringVar(value="Ready")
        Label(root, textvariable=self.status_var).pack(pady=(4, 8))

        delay_row = Frame(root)
        delay_row.pack(pady=(0, 4))

        Label(delay_row, text="Delay (seconds):").pack(side="left", padx=(0, 5))
        self.delay_var = StringVar(value="0")
        Entry(delay_row, textvariable=self.delay_var, width=5).pack(side="left")

        exposure_row = Frame(root)
        exposure_row.pack(pady=(0, 4))

        Label(exposure_row, text="Shutter speed (ms, 0=auto):").pack(side="left", padx=(0, 5))
        self.shutter_var = StringVar(value="0")
        Entry(exposure_row, textvariable=self.shutter_var, width=6).pack(side="left", padx=(0, 5))
        Button(exposure_row, text="Apply", command=self.apply_exposure).pack(side="left")

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
        try:
            delay = int(self.delay_var.get())
            if delay < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid delay", "Enter a whole number of seconds (0 or more).")
            return

        self.photo_button.configure(state="disabled")
        self.record_button.configure(state="disabled")
        self._countdown(delay)

    def _countdown(self, remaining):
        if remaining > 0:
            self.status_var.set(f"Taking photo in {remaining}...")
            self.root.after(1000, self._countdown, remaining - 1)
        else:
            self._capture_photo()

    def _capture_photo(self):
        filename = os.path.join(CAPTURE_DIR, f"photo_{timestamp()}.jpg")
        self.status_var.set("Capturing photo...")
        self.root.update_idletasks()
        try:
            # A manually fixed exposure doesn't survive the sensor mode switch
            # that a full-resolution still capture normally triggers, so stay
            # on the video port (same stream the preview uses) instead.
            self.camera.capture(filename, use_video_port=self.manual_exposure)
            self.status_var.set(f"Saved {os.path.basename(filename)}")
        except Exception as exc:
            messagebox.showerror("Capture failed", str(exc))
            self.status_var.set("Ready")
        finally:
            self.photo_button.configure(state="normal")
            self.record_button.configure(state="normal")

    def apply_exposure(self):
        if self.recording:
            messagebox.showerror("Cannot change exposure", "Stop recording before changing exposure settings.")
            return
        try:
            shutter_ms = int(self.shutter_var.get())
            if shutter_ms < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid shutter speed", "Enter a whole number of milliseconds (0 for auto).")
            return

        try:
            if shutter_ms == 0:
                self.camera.exposure_mode = "auto"
                self.camera.shutter_speed = 0
                self.camera.framerate = DEFAULT_FRAMERATE
                self.manual_exposure = False
                self.status_var.set("Exposure set to auto")
            else:
                shutter_us = shutter_ms * 1000
                # framerate must be slow enough to allow this shutter speed
                self.camera.framerate = min(DEFAULT_FRAMERATE, 1_000_000 / shutter_us)
                self.camera.exposure_mode = "auto"
                self.camera.shutter_speed = shutter_us

                # Give the auto-exposure algorithm time to adapt its gain to
                # the new shutter speed before locking it in — otherwise the
                # gain from the previous (often much faster) shutter speed
                # gets frozen in place and photos come out black.
                self.status_var.set("Adjusting exposure, please wait...")
                self.root.update_idletasks()
                time.sleep(max(1.0, (shutter_us / 1_000_000) * 3))

                self.camera.exposure_mode = "off"
                self.manual_exposure = True
                self.status_var.set(f"Exposure set to {shutter_ms}ms (preview will update more slowly)")
        except Exception as exc:
            messagebox.showerror("Failed to set exposure", str(exc))
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
