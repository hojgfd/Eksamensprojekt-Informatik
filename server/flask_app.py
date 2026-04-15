from flask import Flask, render_template, request, redirect, session, jsonify
import os, time
from datetime import date, timedelta
from database import get_db, init_db
from auth import auth
import random as rnd

parking_spots = {i: None for i in range(1, 19)}
blocked_spots = {16, 17, 18}

app = Flask(__name__)
app.secret_key = "minmegethemmeligenøgle"
app.register_blueprint(auth)

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

    row = db.execute(
        "SELECT spots_left, spots_taken FROM liveparkingdata WHERE id = ?",
        (0,)
    ).fetchone()

    db.close()

    return render_template(
        "livedata.html",
        spots_left=row["spots_left"],
        spots_taken=row["spots_taken"]
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

    if not spots_left and not spots_taken:
        return jsonify({"error": "Missing spots_left and/or spots_taken"}), 400

    init_db()
    db = get_db()

    db.execute("UPDATE liveparkingdata SET spots_left = ?, spots_taken = ? WHERE id = ?", (spots_left, spots_taken, 0))

    db.commit()
    db.close()

    return jsonify({"status": "ok"})



@app.route('/get_schedule')
def get_schedule():
    return 'Skemamaxxing'