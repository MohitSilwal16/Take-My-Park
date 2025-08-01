from . import db
from sqlalchemy import or_


class Transactions(db.Model):
    __tablename__ = "transactions"

    transaction_id = db.Column(db.String(20), primary_key=True)
    from_user = db.Column(db.String(15), nullable=False)
    to_user = db.Column(db.String(15), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)


def add_transaction(transaction: Transactions) -> None:
    db.session.add(transaction)
    db.session.commit()


def get_transactions_by_username(username: str) -> list[Transactions]:
    return (
        Transactions.query.filter(
            or_(
                Transactions.from_user == username,
                Transactions.to_user == username,
            )
        )
        .order_by(Transactions.timestamp.desc())
        .all()
    )
