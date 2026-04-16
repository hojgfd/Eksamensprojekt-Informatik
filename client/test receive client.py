import json
import time

import cv2
import numpy as np
import websocket
from flask import Flask

from ultralytics import YOLO
from opfange_bil import run_classification_model

SERVER_WS_URI   = "ws://localhost:5000/pi"  # <- change this
CAMERA_INDEX    = 0
RECONNECT_DELAY = 5    # seconds between WebSocket reconnects

model = YOLO("yolo26n.pt")
confidence_threshold = 0.3

# -- camera -------------------------------------------------------------------

def capture_frame() -> cv2.Mat:
    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    cap.read()
    ret, frame = cap.read()
    cap.release()
    return frame

def frame_to_bytes(frame: cv2.Mat) -> bytes:
    ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
    if not ok:
        raise RuntimeError("JPEG encode failed")
    return buf.tobytes()

# -- WebSocket client ---------------------------------------------------------

def send_bytes(request_id, bytes):
    header = request_id.encode("ascii").ljust(36, b"\x00")

def _on_open(ws):
    print("[ws] connected to server")

def _on_message(ws, message):
    if not isinstance(message, str):
        return
    try:
        data = json.loads(message)
    except json.JSONDecodeError:
        return

    action = data.get("action")

    if action == "image":
        request_id = data["request_id"]
        print(f"[ws] capture request  id={request_id}")
        try:
            frame = capture_frame()
            jpeg = frame_to_bytes(frame)

            header = request_id.encode("ascii").ljust(36, b"\x00")
            ws.send(bytes(header) + jpeg, websocket.ABNF.OPCODE_BINARY)
            print(f"[ws] sent {len(jpeg):,} bytes")
        except Exception as exc:
            print(f"[ws] capture failed: {exc}")
            ws.send(json.dumps({"error": str(exc), "request_id": request_id}))
    elif action == "yolo":
        request_id = data["request_id"]
        print(f"[ws] capture request  id={request_id}")
        try:
            frame = capture_frame()
            annotated_frame, counter = run_classification_model(model, frame, confidence_threshold)

            jpeg = frame_to_bytes(annotated_frame)
            header = request_id.encode("ascii").ljust(36, b"\x00")
            ws.send(bytes(header) + jpeg, websocket.ABNF.OPCODE_BINARY)
            print(f"[ws] sent {len(jpeg):,} bytes")
        except Exception as exc:
            print(f"[ws] capture failed: {exc}")
            ws.send(json.dumps({"error": str(exc), "request_id": request_id}))
    elif action == "yolo_dict":
        request_id = data["request_id"]
        print(f"[ws] capture request  id={request_id}")
        try:
            frame = capture_frame()
            annotated_frame, counter = run_classification_model(model, frame, confidence_threshold)

            counter["request_id"] = request_id
            ws.send(json.dumps(counter))
            print(f"[ws] sent yolo dict")
        except Exception as exc:
            print(f"[ws] capture failed: {exc}")
            ws.send(json.dumps({"error": str(exc), "request_id": request_id}))

def _on_error(ws, error):
    print(f"[ws] error: {error}")

def _on_close(ws, code, msg):
    print(f"[ws] disconnected ({code}: {msg})")

def ws_thread():
    while True:
        print(f"[ws] connecting to {SERVER_WS_URI} ...")
        app_ws = websocket.WebSocketApp(
            SERVER_WS_URI,
            on_open=_on_open,
            on_message=_on_message,
            on_error=_on_error,
            on_close=_on_close,
        )
        app_ws.run_forever(ping_interval=20, ping_timeout=15)
        print(f"[ws] retrying in {RECONNECT_DELAY}s ...")
        time.sleep(RECONNECT_DELAY)

if __name__ == "__main__":
    ws_thread()