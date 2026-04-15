"""
pi_client.py — Raspberry Pi side.

Install:  pip install opencv-python-headless websocket-client flask
Run:      python pi_client.py

Two things run at once:
  1. A WebSocket client that stays connected to the main server and responds
     to capture requests from it.
  2. A local Flask server (port 5001) so you can also hit the Pi directly:
       GET http://<pi-ip>:5001/capture   -> JPEG
       GET http://<pi-ip>:5001/status    -> JSON

Change SERVER_WS_URI to point at your server.
"""

import json
import threading
import time

import cv2
import numpy as np
import websocket
from flask import Flask, Response, jsonify

SERVER_WS_URI   = "ws://localhost:5000/pi"  # <- change this
CAMERA_INDEX    = 0
RECONNECT_DELAY = 5    # seconds between WebSocket reconnects
FRAME_TIMEOUT   = 5.0  # seconds without a new frame before reopening camera

# -- camera -------------------------------------------------------------------

_frame_lock   = threading.Lock()
_latest_frame = None
_frame_time   = 0.0   # epoch time of the last successfully received frame

def capture_jpeg() -> bytes:
    with _frame_lock:
        cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        cap.read()
        ret, frame = cap.read()
        cap.release()

    ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
    if not ok:
        raise RuntimeError("JPEG encode failed")
    return buf.tobytes()

# -- WebSocket client ---------------------------------------------------------

_ws_instance = None

def _on_open(ws):
    global _ws_instance
    _ws_instance = ws
    print("[ws] connected to server")
    ws.send(json.dumps({"status": "ready"}))

def _on_message(ws, message):
    if not isinstance(message, str):
        return
    try:
        data = json.loads(message)
        print(data)
    except json.JSONDecodeError:
        return

    if data.get("action") == "capture":
        request_id = data["request_id"]
        print(f"[ws] capture request  id={request_id}")
        try:
            jpeg = capture_jpeg()
            header = request_id.encode("ascii").ljust(36, b"\x00")
            ws.send(bytes(header) + jpeg, websocket.ABNF.OPCODE_BINARY)
            print(f"[ws] sent {len(jpeg):,} bytes")
        except Exception as exc:
            print(f"[ws] capture failed: {exc}")
            ws.send(json.dumps({"error": str(exc), "request_id": request_id}))

def _on_error(ws, error):
    print(f"[ws] error: {error}")

def _on_close(ws, code, msg):
    global _ws_instance
    _ws_instance = None
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

# -- local Flask server -------------------------------------------------------

flask_app = Flask(__name__)

@flask_app.get("/status")
def status():
    with _frame_lock:
        age = time.time() - _frame_time if _frame_time else None
    return jsonify({
        "camera_ready":     age is not None and age < FRAME_TIMEOUT,
        "frame_age_sec":    round(age, 2) if age is not None else None,
        "server_connected": _ws_instance is not None,
    })

@flask_app.get("/capture")
def local_capture():
    try:
        jpeg = capture_jpeg()
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
    return Response(jpeg, mimetype="image/jpeg")


# -- main ---------------------------------------------------------------------

if __name__ == "__main__":
    threading.Thread(target=ws_thread,      daemon=True).start()

    print("[flask] local API on http://0.0.0.0:5001")

    flask_app.run(host="0.0.0.0", port=5001, threaded=True)