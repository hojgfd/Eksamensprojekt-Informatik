from flask import Blueprint, render_template, request, redirect, session
from models import create_user, get_user

auth = Blueprint("auth", __name__)

@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        address = request.form["address"]

        create_user(username, password, address)
        return redirect("/login")

    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = get_user(username)

        if user and user["password"] == password:
            session["user_id"] = user["id"]
            return redirect("/reservation")

    return render_template("login.html")


@auth.route("/logout")
def logout():
    session.clear()
    return redirect("/login")