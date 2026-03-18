# AI Poker Detector

Real-time Texas Hold'em helper that:

- Detects cards from a **webcam** (or screen capture) using a trained **YOLOv8** model
- Stabilizes detections into a hand state (player + community cards)
- Displays **best hand**, **win % vs opponents (Monte Carlo)**, and **next-card improvement chance**

## Quick start (Windows)

### 1) Install Python

- Install **Python 3.10+** and make sure `python` and `pip` work in PowerShell.

### 2) Install dependencies

From the project folder:

```powershell
pip install -r requirements.txt
```

### 3) Run the app

```powershell
python main_ui.py
```

## Model weights

This repo includes the YOLO weights at:

- `AI\best.pt`

If you replace the weights, keep the filename the same or update `MODEL_PATH` in `core/detector.py`.

## Webcam vs monitor capture

The detector supports both sources:

- **Webcam**: OpenCV `VideoCapture(...)`
- **Monitor**: `mss` screen capture

If you want to switch modes, see `detect_cards(...)` in `core/detector.py`.

## Common issues

- **`ModuleNotFoundError: ...`**
  - Re-run `pip install -r requirements.txt`
- **Black/empty camera feed**
  - Your camera might not be index `0`. Change `cv2.VideoCapture(0)` to `cv2.VideoCapture(1)` in `core/detector.py`.
- **No detections**
  - Confirm your weights path is correct and the model file exists.
  - Try lowering `conf_thresh` and/or adjusting `imgsz`/`iou` in `detect_cards(...)`.

## Repo layout (high level)

- `main_ui.py`: Tkinter GUI entry point
- `main.py`: console-only entry point
- `core/`: detection + game state + evaluation + probability code
- `ui/`: Tkinter UI components and assets

## License

See `LICENSE`.

