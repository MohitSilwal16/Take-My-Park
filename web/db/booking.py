from . import db


class Booking(db.Model):
    __tablename__ = "booking"

    booking_id = db.Column(db.String(10), primary_key=True)
    parking_id = db.Column(
        db.String(10), db.ForeignKey("parking.parking_id"), nullable=False
    )
    booker_name = db.Column(
        db.String(15), db.ForeignKey("users.username"), nullable=False
    )

    booked_from = db.Column(db.DateTime, nullable=False)
    booked_till = db.Column(db.DateTime, nullable=False)

    total_amount = db.Column(db.Float, nullable=False)


def add_booking(booking: Booking) -> None:
    db.session.add(booking)
    db.session.commit()


def get_bookings_by_parking_id(parking_id: str) -> list[Booking]:
    return Booking.query.filter_by(parking_id=parking_id).all()


def get_bookings_by_username(username: str) -> list[Booking]:
    return Booking.query.filter_by(booker_name=username).all()
