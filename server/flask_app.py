from flask import Flask, render_template, request, redirect, url_for
import os
from server.database import get_db, init_db

parking_spots = {i: None for i in range(1, 19)} # 12 spots
blocked_spots = {16, 17, 18} # Kan ikke reserveres
app = Flask(__name__)
@app.route('/update_server', methods=["GET", "POST"])
def update():
    os.system('cd /home/oscar1234/Eksamensprojekt-Informatik && git pull')
    # Til at reload app
    os.system("touch /var/www/oscar1234_pythonanywhere_com_wsgi.py")
    return 'Updated and reloaded'

@app.route('/')
def hello_world():
    return 'Hello from Flask!'

@app.route('/upload_form')
def upload_form():
    return render_template("upload_form.html")

# eksempel for curl:
# curl.exe -X POST http://127.0.0.1:5000/upload -F "image=@C:\Users\agc\Desktop\angry_bird_realistisk.jpg"
# curl.exe -X POST https://oscar1234.pythonanywhere.com/upload -F "image=@C:\Users\agc\Desktop\angry_bird_realistisk.jpg"
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return 'no image part'

    file = request.files['image']

    if file.filename == '':
        return 'no selected file'

    file.save(f'server/uploads/{file.filename}')

    return 'File uploaded successfully'





@app.route("/reservation", methods=["GET", "POST"])
def reservation():
    db = get_db()
    spots = db.execute("SELECT * FROM parking").fetchall()
    db.close()

    return render_template("reservation.html", spots=spots, blocked=blocked_spots)

@app.route("/reservation/reserver", methods=["POST"])
def reserve():
    plate = request.form.get("plade")

    db = get_db()

    # Find første ledige plads (ikke blokeret)
    spot = db.execute("""
        SELECT id FROM parking
        WHERE plate IS NULL
        AND id NOT IN ({})
        ORDER BY id ASC
        LIMIT 1
    """.format(",".join(map(str, blocked_spots)))).fetchone()

    if spot:
        db.execute(
            "UPDATE parking SET plate = ? WHERE id = ?",
            (plate, spot["id"])
        )
        db.commit()

    db.close()

    return redirect("/reservation")

@app.route('/get_schedule')
def get_schedule():

    return 'Skemamaxxing'