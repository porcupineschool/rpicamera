# rpicamera

A small Tkinter app to preview and control a Raspberry Pi HQ Camera (or any
libcamera-compatible CSI camera): live preview, snap photos, record video.

Runs on the Raspberry Pi only (it needs the camera hardware) — edit and review
the code on your Mac, push to GitHub, then pull and run it on the Pi.

This app targets **Raspbian Buster** and uses the legacy `picamera` (v1)
library, since Buster predates the picamera2/libcamera stack. (If you ever
reflash to a newer Raspberry Pi OS, switch to a picamera2-based version
instead — ask if you need that variant.)

## One-time setup on the Raspberry Pi

1. Enable the camera interface:
   ```
   sudo raspi-config
   ```
   Go to **Interface Options > Camera > Enable**, then reboot.

2. Confirm the camera is detected:
   ```
   vcgencmd get_camera
   ```
   You should see `supported=1 detected=1`.

3. Install system packages (these are easiest to get via apt — they don't
   always install cleanly with pip on Raspberry Pi OS):
   ```
   sudo apt update
   sudo apt install -y python3-picamera python3-pil python3-tk python3-numpy ffmpeg
   ```

4. Clone this repo on the Pi:
   ```
   git clone https://github.com/porcupineschool/rpicamera.git
   cd rpicamera
   ```

## Running

From a terminal on the Pi (with a desktop/monitor, or via VNC — this is a GUI
app, not headless):
```
python3 src/camera_app.py
```

Or open `src/camera_app.py` in Thonny and press Run.

Captured photos and videos are saved to the `captures/` folder.

## Workflow

- Edit code on the Mac.
- `git push` from the Mac.
- `git pull` on the Pi, then re-run the app to test.
