from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from functools import wraps
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(24)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(70), unique=True)
    password = db.Column(db.String(80))


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    auther = db.Column(db.String, nullable=False)
    tittle = db.Column(db.String(50), unique=True)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "x-access-token" in request.headers:
            auth_header = request.headers["x-access-token"]
            # if auth_header.startswith("Bearer "):
            #     token = auth_header.split(" ")[1]
            # else:
                # token = auth_header
            token = auth_header

        if not token:
            return jsonify({"message": "Token is missing !!"}), 401

        try:
            data = jwt.decode(token, app.config["SECRET_KEY"])
            current_user = User.query.filter_by(public_id=data["public_id"]).first()
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired !!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Token is invalid !!"}), 401

        return f(current_user, *args, **kwargs)

    return decorated


@app.route("/user", methods=["GET"])
@token_required
def get_all_users(current_user):
    users = User.query.all()
    output = []
    for user in users:
        output.append(
            {"public_id": user.public_id, "name": user.name, "email": user.email}
        )

    return jsonify({"users": output})


@app.route("/login", methods=["POST"])
def login():
    auth = request.form
    if not auth or not auth.get("email") or not auth.get("password"):
        return make_response(
            "Could not verify",
            401,
            {"WWW-Authenticate": 'Basic realm ="Login required !!"'},
        )

    user = User.query.filter_by(email=auth.get("email")).first()

    if not user:
        return make_response(
            "Could not verify",
            401,
            {"WWW-Authenticate": 'Basic realm ="User does not exist !!"'},
        )

    if check_password_hash(user.password, auth.get("password")):
        token = jwt.encode(
            {
                "public_id": user.public_id,
                "exp": datetime.utcnow() + timedelta(minutes=30),
            },
            app.config["SECRET_KEY"],
        )
        print(type(token))

        return make_response(jsonify({"token": token}), 201)
    return make_response(
        "Could not verify",
        403,
        {"WWW-Authenticate": 'Basic realm ="Wrong Password !!"'},
    )


@app.route("/signup", methods=["POST"])
def signup():
    data = request.form

    name, email = data.get("name"), data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(
            public_id=str(uuid.uuid4()),
            name=name,
            email=email,
            password=generate_password_hash(password),
        )

        token = jwt.encode(
            {
                "public_id": user.public_id,
                "exp": datetime.utcnow() + timedelta(minutes=30),
            },
            app.config["SECRET_KEY"],
        )

        db.session.add(user)
        db.session.commit()

        return make_response(
            jsonify(
                {"token": token.decode("UTF-8")},
                "success",
                "your successfully register",
            ),
            201,
        )
    else:
        return make_response("User already exists. Please Log in.", 202)


@app.route("/add", methods=["POST"])
def addBook():
    data = request.form

    if not data or not data.get("auther") or not data.get("tittle"):
        return jsonify({"error": "Both 'auther' and 'tittle' are required"}), 400

    new_Book = Book(auther=data.get("auther"), tittle=data.get("tittle"))
    db.session.add(new_Book)
    db.session.commit()

    return jsonify({"message": "Your Book is added"}), 201


@app.route("/delete", methods=["POST", "DELETE"])
def deleteBook():
    data = request.form
    if not data or data.get("tittle"):
        Book.query.filter_by(tittle=data.get("tittle")).delete()
        return jsonify({"this Book has been deleted"}, 200)
    else:
        return jsonify({"invalid Book name"})


@app.route("/allBooks", methods=["GET"])
def getBook():
    Books = Book.query.all()
    output = []
    for Books in Books:
        output.append({"Book_name": Books.tittle, "auther": Books.auther})

    return jsonify({"Books": output})


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
