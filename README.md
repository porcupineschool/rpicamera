# rpicamera

A small Tkinter app to preview and control a Raspberry Pi HQ Camera (or any
libcamera-compatible CSI camera): live preview, snap photos, record video.

Runs on the Raspberry Pi only (it needs the camera hardware) — edit and review
the code on your Mac, push to GitHub, then pull and run it on the Pi.

## One-time setup on the Raspberry Pi

1. Make sure the camera is enabled and detected:
   ```
   libcamera-hello --list-cameras
   ```
   If nothing shows up, enable the camera interface with `sudo raspi-config`
   (Interface Options > Camera) and reboot.

2. Install system packages (picamera2 and Tk are easiest to get via apt —
   they don't always install cleanly with pip on Raspberry Pi OS):
   ```
   sudo apt update
   sudo apt install -y python3-picamera2 python3-pil python3-tk ffmpeg
   ```

3. Clone this repo on the Pi:
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
