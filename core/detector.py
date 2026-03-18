from ultralytics import YOLO
import os
os.environ["YOLO_HUB_SYNC"] = "0"
import cv2
import numpy as np
import mss

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODEL_PATH = os.path.join(_ROOT, "AI", "best.pt")
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(
        f"Missing YOLO weights at '{MODEL_PATH}'. "
        "Expected AI/best.pt in the project root."
    )
model = YOLO(MODEL_PATH)
sct = mss.mss()
cap = cv2.VideoCapture(0)

def detect_cards(source_mode="webcam", source_monitor=1, conf_thresh=0.6, iou=0.15, imgsz=1280, display=False):
    detected = {"player": [], "community": []}
    frame = None  # ✅ always define frame

    # Grab frame
    if source_mode == "screen":
        monitor = sct.monitors[source_monitor]
        frame = cv2.cvtColor(np.array(sct.grab(monitor)), cv2.COLOR_BGRA2BGR)
    else:
        ret, frame = cap.read()
        if not ret:
            return detected, None  # ✅ return tuple

    results = model.predict(source=frame, conf=conf_thresh, iou=iou, imgsz=imgsz, verbose=False)

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            label = model.names[cls]
            conf = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # Send to "player" list only (GameState handles slot order)
            detected["player"].append((label, conf))

            if display:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # ✅ Removed extra OpenCV window (keeps only Tkinter UI)
    # if display:
    #     cv2.imshow("PokerBot Detection", frame)
    #     cv2.waitKey(1)

    return detected, frame  # ✅ now always returns frame
