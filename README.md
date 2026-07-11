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
   sudo apt install -y python3-picamera python3-pil python3-pil.imagetk python3-tk python3-numpy
   ```
   Note: Buster's `raspbian.raspberrypi.org` mirror has been retired now that
   Buster is end-of-life, so `apt update` will show a 404 for it — that's
   expected and safe to ignore, the packages above still come from the repos
   that are still up.

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

Captured photos are saved as `.jpg` and videos as raw `.h264` in the
`captures/` folder. `.h264` files play fine in VLC; if you need `.mp4`
files, convert them later on a machine with a working `ffmpeg` install:
```
ffmpeg -r 30 -i video.h264 -c copy video.mp4
```

## Desktop icon

To launch the app by clicking an icon on the Pi's desktop instead of typing a
command:

```
cp ~/rpicamera/rpicamera.desktop ~/Desktop/
chmod +x ~/Desktop/rpicamera.desktop
```

Then, on the Pi's desktop, right-click the new icon and choose **"Trust"** (or
similar wording, e.g. "Allow Launching") — Raspberry Pi OS requires this once
per launcher file before it will run on double-click.

If your Pi username isn't `pi`, edit the `Path=` line in
`rpicamera.desktop` to match your actual home directory first.

## Workflow

- Edit code on the Mac.
- `git push` from the Mac.
- `git pull` on the Pi, then re-run the app to test.
