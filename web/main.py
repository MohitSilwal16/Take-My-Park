from flask import Flask
from db import db
from handlers.auth import auth_bp
from handlers.park import park_bp, UPLOAD_FOLDER
from handlers.transactions import transactions_bp

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///take-my-park.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

app.register_blueprint(auth_bp)
app.register_blueprint(park_bp)
app.register_blueprint(transactions_bp)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
