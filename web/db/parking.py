from . import db


class Parking(db.Model):
    __tablename__ = "parking"

    parking_id = db.Column(db.String(10), primary_key=True)
    username = db.Column(db.String(15), db.ForeignKey("users.username"), nullable=False)
    location_link = db.Column(db.String(100), nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False)

    available_from = db.Column(db.DateTime, nullable=False)
    available_till = db.Column(db.DateTime, nullable=False)

    image_url = db.Column(db.String(300), nullable=False)


def post_parking(parking: Parking) -> None:
    db.session.add(parking)
    db.session.commit()


def get_all_parking() -> list[Parking]:
    return Parking.query.filter_by().all()


def get_parking_by_owner(username: str) -> list[Parking]:
    return Parking.query.filter_by(username=username).all()


def get_parking_by_id(parking_id: str) -> Parking:
    return Parking.query.filter_by(parking_id=parking_id).first()


def get_username_by_parking_id(parking_id: str) -> str:
    parking = Parking.query.filter_by(parking_id=parking_id).first()
    if not parking:
        return None
    return parking.username
