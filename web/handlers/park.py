from . import park_bp
from flask import request, render_template, redirect, url_for
from db import parking, users, booking, transactions
from bot import bot
from utils.tokens import generate_random_tokens

from datetime import datetime
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
PARKING_BOOKING_ID_LENGTH = 5
PLATFORM_BOOKING_FEE = 10


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@park_bp.route("/", methods=["GET"])
def index():
    session_token = request.cookies.get("session-token")
    is_session_token_valid = users.is_session_token_valid(session_token)
    if not is_session_token_valid:
        return redirect(url_for("auth.login"))

    username = users.get_user_by_token(session_token)
    parkings = parking.get_all_parking()
    return render_template("home.html", username=username, parkings=parkings)


@park_bp.route("/parking", methods=["GET", "POST"])
def post_parking():
    session_token = request.cookies.get("session-token")
    is_session_token_valid = users.is_session_token_valid(session_token)
    if not is_session_token_valid:
        return redirect(url_for("auth.login"))

    if request.method == "GET":
        return render_template("post-parking.html")

    parking_id = "P" + generate_random_tokens(PARKING_BOOKING_ID_LENGTH)
    location_link = request.form["location_link"]
    price_per_hour = float(request.form["price_per_hour"])

    available_from = datetime.strptime(request.form["available_from"], "%Y-%m-%dT%H:%M")
    available_till = datetime.strptime(request.form["available_till"], "%Y-%m-%dT%H:%M")

    file = request.files["image"]

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = UPLOAD_FOLDER + "\\" + filename
        file.save(filepath)
        image_url = filepath.replace("\\", "/")  # Make it Browser-friendly

        username = users.get_user_by_token(session_token)
        park_post = parking.Parking(
            parking_id=parking_id,
            username=username,
            location_link=location_link,
            price_per_hour=price_per_hour,
            available_from=available_from,
            available_till=available_till,
            image_url=image_url,
        )
        parking.post_parking(park_post)
        return redirect(url_for("park.index"))
    return render_template("post-parking.html", error_msg="Invalid File Type")


@park_bp.route("/apply/<parking_id>", methods=["GET", "POST"])
def apply_parking(parking_id: str):
    session_token = request.cookies.get("session-token")
    is_session_token_valid = users.is_session_token_valid(session_token)
    if not is_session_token_valid:
        return redirect(url_for("auth.login"))

    parking_obj = parking.get_parking_by_id(parking_id)
    existing_bookings = booking.get_bookings_by_parking_id(parking_id)
    existing_bookings.sort(key=lambda x: x.booked_from)

    if request.method == "GET":
        return render_template(
            "apply-parking.html",
            parking=parking_obj,
            bookings=existing_bookings,
        )

    booked_from = datetime.strptime(request.form["booked_from"], "%Y-%m-%dT%H:%M")
    booked_till = datetime.strptime(request.form["booked_till"], "%Y-%m-%dT%H:%M")

    if booked_from >= booked_till:
        return render_template(
            "apply-parking.html",
            parking=parking_obj,
            bookings=existing_bookings,
            booked_from=booked_from,
            booked_till=booked_till,
            error_msg="Invalid Booking Time",
        )

    if (
        booked_from < parking_obj.available_from
        or booked_till > parking_obj.available_till
    ):
        return render_template(
            "apply-parking.html",
            parking=parking_obj,
            bookings=existing_bookings,
            booked_from=booked_from,
            booked_till=booked_till,
            error_msg="Selected Time is Out of Range",
        )

    for exst_book in existing_bookings:
        if (exst_book.booked_from <= booked_from <= exst_book.booked_till) or (
            booked_from <= exst_book.booked_from <= booked_till
        ):
            return render_template(
                "apply-parking.html",
                parking=parking_obj,
                bookings=existing_bookings,
                booked_from=booked_from,
                booked_till=booked_till,
                error_msg="Your Booking Time Clashes with Existing Booking",
            )

    booking_id = "B" + generate_random_tokens(PARKING_BOOKING_ID_LENGTH)
    username = users.get_user_by_token(session_token)
    duration = (booked_till - booked_from).total_seconds() / 3600
    total_amount = duration * parking_obj.price_per_hour + PLATFORM_BOOKING_FEE

    book = booking.Booking(
        booking_id=booking_id,
        parking_id=parking_id,
        booker_name=username,
        booked_from=booked_from,
        booked_till=booked_till,
        total_amount=total_amount,
    )

    parking_owner = parking.get_username_by_parking_id(parking_id)
    t = transactions.Transactions(
        transaction_id="T" + generate_random_tokens(PARKING_BOOKING_ID_LENGTH),
        from_user=username,
        to_user=parking_owner,
        amount=total_amount,
        timestamp=datetime.now(),
    )

    booking.add_booking(book)
    transactions.add_transaction(t)
    return redirect(url_for("park.index"))


@park_bp.route("/parking/my", methods=["GET"])
def my_parkings():
    session_token = request.cookies.get("session-token")
    is_session_token_valid = users.is_session_token_valid(session_token)
    if not is_session_token_valid:
        return redirect(url_for("auth.login"))

    username = users.get_user_by_token(session_token)
    parkings = parking.get_parking_by_owner(username)
    return render_template("my-parkings.html", parkings=parkings)


@park_bp.route("/parking/booked", methods=["GET"])
def my_booked_parkings():
    session_token = request.cookies.get("session-token")
    is_session_token_valid = users.is_session_token_valid(session_token)
    if not is_session_token_valid:
        return redirect(url_for("auth.login"))

    username = users.get_user_by_token(session_token)
    booked_parkings = booking.get_bookings_by_username(username)
    return render_template("my-booked-parkings.html", bookings=booked_parkings)


@park_bp.route("/parking/filter", methods=["POST"])
def filter_parkings():
    session_token = request.cookies.get("session-token")
    is_session_token_valid = users.is_session_token_valid(session_token)
    if not is_session_token_valid:
        return redirect(url_for("auth.login"))

    user_inp = request.form.get("user_inp")
    print(f"User Input: {user_inp}")
    username = users.get_user_by_token(session_token)
    filtered_parkings = bot.get_filtered_parkings(user_inp)
    return render_template("home.html", username=username, parkings=filtered_parkings)
