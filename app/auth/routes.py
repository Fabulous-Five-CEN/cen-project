from typing import Optional
from urllib.parse import urlparse

from flask import jsonify, render_template, request, redirect, url_for, current_app, session
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError
from app.services.seed_vocab import seed_essential_vocab_for_user

from datetime import datetime, timezone
from app.extensions import db
from app.models import User, Card, CardSet, SetTable, PracticeHistory

from . import auth_bp



def _serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name,
    }


def _safe_next_url(candidate: Optional[str]) -> Optional[str]:
    """Only allow relative next URLs so we do not redirect off-site."""
    if not candidate:
        return None
    parsed = urlparse(candidate)
    if parsed.netloc or parsed.scheme:
        return None
    return candidate


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if current_user.is_authenticated:
            target = _safe_next_url(request.args.get("next")) or url_for("main.dashboard")
            return redirect(target)
        return render_template("account.html")

    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")
    next_url = _safe_next_url(data.get("next") or request.args.get("next"))

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.verify_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    login_user(user)

    return (
        jsonify(
            {
                "user": _serialize_user(user),
                "redirect": next_url or url_for("main.dashboard"),
            }
        ),
        200,
    )


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        if current_user.is_authenticated:
            return redirect(url_for("auth.account_home"))
        return render_template("account.html")

    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")
    display_name = (data.get("display_name") or data.get("username") or "").strip()
    next_url = _safe_next_url(data.get("next") or request.args.get("next"))

    if not email or not password or not display_name:
        return jsonify({"error": "Email, display name, and password are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "An account with that email already exists"}), 400

    new_user = User(email=email, display_name=display_name)
    new_user.set_password(password)

    db.session.add(new_user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "An account with that email already exists"}), 400

    login_user(new_user)

    return (
        jsonify(
            {
                "user": _serialize_user(new_user),
                "redirect": next_url or url_for("main.dashboard"),
            }
        ),
        201,
    )


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout successful", "redirect": url_for("auth.login")}), 200


@auth_bp.route("/account")
@login_required
def account_home():
    return render_template("account.html", user=current_user)



# DEMO LOGIN MODE - ONLY ENABLED WHEN PROD ENV = DEMO


_last_demo_wipe = None

@auth_bp.route("/demo-login", methods=["POST"])
def demo_login():
  
    global _last_demo_wipe

    if not current_app.config.get("DEMO_MODE"):
        return redirect(url_for("auth.login"))

    demo_user = User.query.filter_by(email="demo@test.com").first()
    if not demo_user:
        return "Demo user not found", 404
    

    now = datetime.now(timezone.utc)
    if not _last_demo_wipe or now.hour != _last_demo_wipe.hour:
        _last_demo_wipe = now

       
        Card.query.filter_by(user_id=demo_user.id).delete()
        SetTable.query.filter_by(user_id=demo_user.id).delete()
        PracticeHistory.query.filter_by(user_id=demo_user.id).delete()
        seed_essential_vocab_for_user(demo_user)

        db.session.commit()

    login_user(demo_user, remember=False)  # do NOT persist login
    session.permanent = False  # ensures session expires after browser close or configured lifetime

    session["db"] = "demo"


    return redirect(url_for("main.dashboard"))
