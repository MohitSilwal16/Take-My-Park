from . import transactions_bp
from flask import request, render_template, redirect, url_for
from db import users, transactions


@transactions_bp.route("/transactions", methods=["GET"])
def index():
    session_token = request.cookies.get("session-token")
    is_session_token_valid = users.is_session_token_valid(session_token)
    if not is_session_token_valid:
        return redirect(url_for("auth.login"))

    username = users.get_user_by_token(session_token)
    my_transactions = transactions.get_transactions_by_username(username)
    return render_template("transactions.html", transactions=my_transactions)
