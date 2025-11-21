from flask import jsonify, render_template, request
from flask_login import login_user, logout_user, login_required, current_user

from app.models import User

from . import auth_bp


def _serialize_user(user: User):
    return {
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name,
    }


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return jsonify({"page": "Login"})

    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.verify_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    login_user(user)
    return jsonify({"message": "Login successful", "user": _serialize_user(user)}), 200


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout successful"}), 200


@auth_bp.route("/signup")
def signup():
    return jsonify({"page": "Signup"})

@auth_bp.route("/account")
@login_required
def account_home():
    return render_template("account.html", user=current_user)
