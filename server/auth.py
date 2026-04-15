from flask import Blueprint, render_template, request, redirect, session
from models import create_user, get_user, update_user
from nominatim import distance_coord_to_string
auth = Blueprint("auth", __name__)

lat_skole = 56.156277
long_skole = 10.187640

@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        address = request.form["address"]
        distance = distance_coord_to_string(lat_skole, long_skole, address) # DEBUG
        plate = request.form["plate"]

        print(f"Distance fra addresse til skolen: {distance}")
        create_user(username, password, address, distance, plate)
        return redirect("/login")

    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = get_user(username)

        if user and user["password"] == password:
            session["user"] = {
                "id": user["id"],
                "username": user["username"],
                "address": user["address"]
            }
            return redirect("/reservation")

    return render_template("login.html")


@auth.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@auth.route("/profile", methods=["GET", "POST"])
def profile():
    if "user" not in session:
        return redirect("/login")

    user = session["user"]

    if request.method == "POST":
        address = request.form["address"]
        distance = distance_coord_to_string(lat_skole, long_skole, address)
        plate = request.form["plate"]

        print(f"Distance fra addresse til skolen: {distance}") # DEBUG

        update_user(user["id"], address, distance, plate)

        # reload bruger fra DB
        updated_user = get_user(user["username"])

        session["user"] = {
            "id": updated_user["id"],
            "username": updated_user["username"],
            "address": updated_user["address"],
            "plate": updated_user["plate"]
        }

        return redirect("/profile")

    return render_template("profile.html", user=user)