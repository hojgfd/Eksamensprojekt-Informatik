"""
server.py — Flask version.

Install:  pip install flask flask-sock
Run:      python server.py

Endpoints:
  WS  ws://0.0.0.0:5000/pi       ← Pi connects here
  GET http://0.0.0.0:5000/status ← check if a Pi is connected
  GET http://0.0.0.0:5000/capture?timeout=10 ← request a photo (returns JPEG)
"""

import json
import threading
import uuid

from flask import Flask, jsonify, request, Response
from flask_sock import Sock

app = Flask(__name__)
sock = Sock(app)

# ── shared state (protected by a lock) ────────────────────────────────────────
_lock = threading.Lock()
_pi_ws = None                  # active WebSocket from the Pi
_pending: dict[str, dict] = {} # request_id → {"event": Event, "data": bytes|None}

# ── WebSocket endpoint (Pi connects here) ─────────────────────────────────────
@sock.route("/pi")
def pi_socket(ws):
    global _pi_ws
    with _lock:
        _pi_ws = ws
    print("[ws] Pi connected")

    try:
        while True:
            message = ws.receive()   # blocks until a message arrives
            if message is None:
                break

            if isinstance(message, bytes):
                # Header: first 36 bytes = request_id (ASCII), rest = JPEG
                request_id = message[:36].decode("ascii").rstrip("\x00")
                image_bytes = message[36:]
                with _lock:
                    slot = _pending.get(request_id)
                if slot:
                    slot["data"] = image_bytes
                    slot["event"].set()   # wake up the waiting /capture thread

            elif isinstance(message, str):
                print(f"[ws] Pi says: {message}")

    except Exception as exc:
        print(f"[ws] connection closed: {exc}")
    finally:
        with _lock:
            if _pi_ws is ws:
                _pi_ws = None
        print("[ws] Pi disconnected")


# ── HTTP endpoints ─────────────────────────────────────────────────────────────
@app.get("/status")
def status():
    with _lock:
        connected = _pi_ws is not None
    return jsonify({"pi_connected": connected})


@app.get("/capture")
def capture():
    timeout = float(request.args.get("timeout", 10))

    with _lock:
        ws = _pi_ws
    if ws is None:
        return jsonify({"error": "No Pi connected"}), 503

    request_id = str(uuid.uuid4())   # 36-char UUID
    slot = {"event": threading.Event(), "data": None}

    with _lock:
        _pending[request_id] = slot

    # Ask the Pi to take a photo
    ws.send(json.dumps({"action": "capture", "request_id": request_id}))

    # Block this thread until the Pi replies (or timeout)
    arrived = slot["event"].wait(timeout=timeout)

    with _lock:
        _pending.pop(request_id, None)

    if not arrived or slot["data"] is None:
        return jsonify({"error": "Pi did not respond in time"}), 504

    return Response(slot["data"], mimetype="image/jpeg")


# ── run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # threaded=True lets /capture and /pi run in separate threads concurrently
    app.run(host="0.0.0.0", port=5000, threaded=True)