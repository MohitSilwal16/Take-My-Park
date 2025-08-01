from . import auth_bp
from flask import request, make_response, render_template, redirect, url_for
from utils.tokens import generate_random_tokens
from db import users

SESSION_TOKEN_LENGTH = 4


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    username = request.form.get("username")
    password = request.form.get("password")
    upi_id = request.form.get("upi-id")

    is_username_already_taken = users.is_username_already_taken(username)
    if is_username_already_taken:
        return render_template("register.html", error_msg="Username Already Exists")

    session_token = generate_random_tokens(SESSION_TOKEN_LENGTH)
    users.create_user(username, password, upi_id, session_token)

    res = make_response(redirect(url_for("park.index")))
    res.set_cookie("session-token", session_token)
    return res


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username")
    password = request.form.get("password")

    user_authenticated = users.verify_password(username, password)
    if not user_authenticated:
        return render_template("login.html", error_msg="Invalid Credentials")

    session_token = generate_random_tokens(SESSION_TOKEN_LENGTH)
    users.update_session_token(username, password, session_token)

    res = make_response(redirect(url_for("park.index")))
    res.set_cookie("session-token", session_token)
    return res


@auth_bp.route("/logout", methods=["GET"])
def logout():
    session_token = request.cookies.get("session-token")
    users.revoke_session_token(session_token)

    res = make_response(redirect(url_for("auth.login")))
    res.set_cookie("session-token", "")
    return res
