from flask import Flask, render_template, request, redirect, session, jsonify, Response
import os, time
from datetime import date, timedelta
from database import get_db, init_db
from auth import auth
import random as rnd
from datetime import datetime, timedelta

import threading, json, uuid
from flask_sock import Sock

parking_spots = {i: None for i in range(1, 19)}
blocked_spots = {16, 17, 18}

app = Flask(__name__)
app.secret_key = "minmegethemmeligenøgle"
app.register_blueprint(auth)
sock = Sock(app)

@app.route('/update_server', methods=["GET", "POST"])
def update():
    os.system('cd /home/oscar1234/Eksamensprojekt-Informatik && git pull')
    os.system("touch /var/www/oscar1234_pythonanywhere_com_wsgi.py")
    return 'Updated and reloaded'

@app.route('/')
def home():
    init_db()
    return render_template("index.html")

@app.route('/live_data')
def live_data():
    init_db()
    db = get_db()

    rows = db.execute(
        "SELECT spots_left, spots_taken, timestamp FROM liveparkingdata ORDER BY timestamp ASC"
    ).fetchall()

    db.close()

    # Lav lister til grafen
    timestamps = [row["timestamp"] for row in rows]
    spots_left_list = [row["spots_left"] for row in rows]
    spots_taken_list = [row["spots_taken"] for row in rows]

    # Udtræk dato (YYYY-MM-DD)
    dates = sorted(list(set([t.split(" ")[0] for t in timestamps])))

    return render_template(
        "livedata.html",
        spots_left=spots_left_list[-1] if rows else 0,
        spots_taken=spots_taken_list[-1] if rows else 0,
        timestamps=timestamps,
        spots_left_list=spots_left_list,
        spots_taken_list=spots_taken_list,
        dates=dates
    )
@app.route('/reservation', methods=["GET", "POST"])
def reservation():
    init_db()
    db = get_db()

    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    # Fjern gamle reservationer
    db.execute("""
               UPDATE parking
               SET plate   = NULL,
                   date    = NULL,
                   user_id = NULL
               WHERE date < ?
               """, (tomorrow,))
    db.commit()

    # Hent pladser for i morgen
    spots = db.execute("""
                       SELECT *
                       FROM parking
                       ORDER BY id ASC
                       """).fetchall()

    db.close()

    #debug
    print(spots)
    for s in spots:
        print(dict(s))

    return render_template(
        "reservation.html",
        spots=spots,
        blocked=blocked_spots,
        tomorrow=tomorrow,
        user=session.get("user")
    )

@app.route("/reservation/reserver", methods=["POST"])
def reserve():
    if "user" not in session:
        return redirect("/login")

    user = session["user"]
    user_id = user["id"]

    plate = request.form.get("plade")
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    db = get_db()

    # Fjern gammel reservation fra samme bruger
    db.execute("""
        UPDATE parking
        SET plate = NULL,
            date = NULL,
            user_id = NULL
        WHERE user_id = ?
    """, (user_id,))

    # Hent alle brugere sorteret efter distance
    users = db.execute("""
        SELECT id, distance
        FROM users
        ORDER BY distance DESC
    """).fetchall()

    max_spots = 18 - len(blocked_spots)
    top_users = [u["id"] for u in users[:max_spots]]

    #  Hvor mange pladser er allerede taget?
    taken_spots = db.execute("""
        SELECT COUNT(*) as count FROM parking
        WHERE date = ?
    """, (tomorrow,)).fetchone()["count"]

    # Hvis brugeren ikke er i top distance til skolen og der stadig ikke er reserverede pladser
    if user_id not in top_users and taken_spots < max_spots:
        db.commit()
        db.close()
        return "Pladserne er reserveret til brugere med længere afstand (prøv igen senere)"

    # Find ledig plads
    spot = db.execute(f"""
        SELECT id FROM parking
        WHERE id NOT IN ({",".join(map(str, blocked_spots))})
        AND (date IS NULL OR date != ?)
        ORDER BY id ASC
        LIMIT 1
    """, (tomorrow,)).fetchone()

    # Lav reservation hvis muligt
    if spot:
        db.execute("""
            UPDATE parking
            SET plate = ?,
                date = ?,
                user_id = ?
            WHERE id = ?
        """, (plate, tomorrow, user_id, spot["id"]))
        db.commit()

    db.close()

    return redirect("/reservation")


@app.route('/upload_form')
def upload_form():
    return render_template("upload_form.html")

@app.route('/overblik')
def overblik():
    db = get_db()

    spots = db.execute("""
        SELECT *
        FROM parking
        ORDER BY id ASC
    """).fetchall()

    total_spots = len(spots)
    total_blocked_spots = len(blocked_spots)

    today = date.today()

    db.close()

    return render_template(
        "overblik.html",
        spots=spots,
        #occupied_spots=blocked_spots,
        total_spots=total_spots,
        unavailable_spots=total_blocked_spots,
        today=today

    )

# eksempel for curl:
# curl.exe -X POST http://127.0.0.1:5000/upload -F "image=@C:\Users\agc\Desktop\angry_bird_realistisk.jpg"
# curl.exe -X POST https://oscar1234.pythonanywhere.com/upload -F "image=@C:\Users\agc\Desktop\angry_bird_realistisk.jpg"
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' in request.files:
        file = request.files['image']
        if file.filename == '':
            return 'no selected file'

        file.save(f'server/uploads/images/image-{int(time.time())}{file.filename[file.filename.rfind("."):]}')

    if 'count' in request.files:
        file = request.files['count']
        if file.filename == '':
            return 'no selected file'

        file.save(f'server/uploads/counts/count-{int(time.time())}.csv')

    if 'count' in request.files or 'image' in request.files:
        return 'File uploaded successfully'
    else:
        return 'no image or count detected'

@app.route('/api/live_data', methods=['POST'])
def update_live_data():
    data = request.json

    spots_left = data.get("spots_left")
    spots_taken = data.get("spots_taken")

    if spots_left is None and spots_taken is None:
        return jsonify({"error": "Missing spots_left and/or spots_taken"}), 400

    init_db()
    db = get_db()

    db.execute("INSERT INTO liveparkingdata (spots_left, spots_taken) VALUES (?, ?)", (spots_left, spots_taken))

    db.commit()
    db.close()

    return jsonify({"status": "ok"})


@app.route('/get_schedule')
def get_schedule():
    return 'Skemamaxxing'


# ── shared state (protected by a lock) ────────────────────────────────────────-–—
pi_lock = threading.Lock()
pi_ws = None                  # active WebSocket from the Pi
pending: dict[str, dict] = {} # request_id → {"event": Event, "data": bytes|None}

# WebSocket endpoint (Pi connects here)
@sock.route("/pi")
def pi_socket(ws):
    global pi_ws
    with pi_lock:
        pi_ws = ws
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
                with pi_lock:
                    slot = pending.get(request_id)
                if slot:
                    slot["data"] = image_bytes
                    slot["event"].set()   # wake up the waiting /capture thread

            elif isinstance(message, str):
                data = json.loads(message)
                request_id = data["request_id"]
                data.pop("request_id")
                with pi_lock:
                    slot = pending.get(request_id)
                if slot:
                    slot["data"] = data
                    slot["event"].set()

                print(f"[ws] Pi says: {message}")

    except Exception as exc:
        print(f"[ws] connection closed: {exc}")
    finally:
        with pi_lock:
            if pi_ws is ws:
                pi_ws = None
        print("[ws] Pi disconnected")

@app.get("/status")
def status():
    with pi_lock:
        connected = pi_ws is not None
    return jsonify({"pi_connected": connected})

@app.get("/capture")
def capture():
    timeout = float(request.args.get("timeout", 10))

    result = send_message(pi_lock, "yolo", timeout)
    if result:
        return Response(result, mimetype="image/jpeg")
    else:
        return jsonify({"error": "No Pi connected or did not respond in time"}), 500

@app.get("/dict")
def yolo_dict():
    timeout = float(request.args.get("timeout", 10))

    result = send_message(pi_lock, "yolo_dict", timeout)
    if result:
        return jsonify(result)
    else:
        return jsonify({"error": "No Pi connected or did not respond in time"}), 500

def send_message(pi_lock, action:str, timeout:float=10):
    with pi_lock:
        ws = pi_ws
    if ws is None:
        print("No Pi connected")
        return None

    request_id = str(uuid.uuid4())
    slot = {"event": threading.Event(), "data": None}

    with pi_lock:
        pending[request_id] = slot

    ws.send(json.dumps({"action": action, "request_id": request_id}))

    # Block this thread until the Pi replies (or timeout)
    arrived = slot["event"].wait(timeout=timeout)

    with pi_lock:
        pending.pop(request_id, None)

    if not arrived or slot["data"] is None:
        print("Pi did not respond in time")
        return None

    return slot["data"]

def car_updater():
    time_wait = 60 * 10
    last_time = time.time() - time_wait + 10
    reconnection_delay = 10

    while True:
        if time.time() > last_time + time_wait:
            last_time = time.time()
            print("sending message")
            yolo_json: dict = send_message(pi_lock, "yolo_dict", 10)

            if yolo_json:
                db = get_db()
                spots_taken = yolo_json.get("car", 0)

                db.execute("INSERT INTO liveparkingdata (spots_left, spots_taken) VALUES (?, ?)",(30 - spots_taken, spots_taken))

                db.commit()
                db.close()
            else:
                with pi_lock:
                    ws = pi_ws
                if ws is None:
                    # No Pi connected og try again after reconnection delay
                    last_time = time.time() - time_wait + reconnection_delay

car_updater_thread = threading.Thread(target=car_updater)
car_updater_thread.start()
print("started car_updater thread")

