from . import db


class User(db.Model):
    __tablename__ = "users"

    username = db.Column(db.String(15), primary_key=True)
    password = db.Column(db.String(15), nullable=False)
    upi_id = db.Column(db.String(20), nullable=False)
    session_token = db.Column(db.String(4), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"


def create_user(username: str, password: str, upi_id: str, session_token: str) -> None:
    user = User(
        username=username, password=password, upi_id=upi_id, session_token=session_token
    )
    db.session.add(user)
    db.session.commit()


def verify_password(username: str, password: str) -> bool:
    return User.query.filter_by(username=username, password=password).first() != None


def get_user_by_token(session_token: str) -> str:
    return User.query.filter_by(session_token=session_token).first().username


def update_session_token(username: str, password: str, session_token: str) -> None:
    user = User.query.filter_by(username=username, password=password).first()
    if not user:
        return

    user.session_token = session_token
    db.session.commit()


def is_session_token_valid(session_token: str) -> bool:
    if session_token == "":
        return False
    return User.query.filter_by(session_token=session_token).first() != None


def is_username_already_taken(username: str) -> bool:
    return User.query.filter_by(username=username).first() != None


def revoke_session_token(session_token: str) -> None:
    user = User.query.filter_by(session_token=session_token).first()
    if not user:
        return
    user.session_token = ""
    db.session.commit()
