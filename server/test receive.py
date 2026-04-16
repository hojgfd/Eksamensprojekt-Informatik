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
                data = json.loads(message)
                request_id = data["request_id"]
                data.pop("request_id")
                with _lock:
                    slot = _pending.get(request_id)
                if slot:
                    slot["data"] = data
                    slot["event"].set()

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

    result = send_message(_lock, "yolo", timeout)
    if result:
        return Response(result, mimetype="image/jpeg")
    else:
        return jsonify({"error": "No Pi connected or did not respond in time"}), 500

@app.get("/dict")
def dict():
    timeout = float(request.args.get("timeout", 10))

    result = send_message(_lock, "yolo_dict", timeout)
    if result:
        return jsonify(result)
    else:
        return jsonify({"error": "No Pi connected or did not respond in time"}), 500

def send_message(_lock, action:str, timeout:float=10):
    with _lock:
        ws = _pi_ws
    if ws is None:
        print("No Pi connected")
        return False

    request_id = str(uuid.uuid4())
    slot = {"event": threading.Event(), "data": None}

    with _lock:
        _pending[request_id] = slot

    ws.send(json.dumps({"action": action, "request_id": request_id}))

    # Block this thread until the Pi replies (or timeout)
    arrived = slot["event"].wait(timeout=timeout)

    with _lock:
        _pending.pop(request_id, None)

    if not arrived or slot["data"] is None:
        print("Pi did not respond in time")
        return False

    return slot["data"]

# ── run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # threaded=True lets /capture and /pi run in separate threads concurrently
    app.run(host="0.0.0.0", port=5000, threaded=True)