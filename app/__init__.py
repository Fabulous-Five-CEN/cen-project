from flask import Flask, jsonify, redirect, request, url_for
from .extensions import db, login_manager
from .models import orm_objects
from .models.orm_objects import User

# Import blueprints
from .main import main_bp
from .auth import auth_bp
from .cards import cards_bp
from .sets import sets_bp
from .practice import practice_bp


def create_app(config_override=None):
    """
    Application factory that optionally accepts a dictionary of config overrides.
    Tests can inject in-memory databases without affecting the default config.
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object("config.Config")
    if config_override:
        app.config.update(config_override)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # Auto update changes
    app.config.setdefault("TEMPLATES_AUTO_RELOAD", True)
    app.config.setdefault("DEBUG", True)

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(cards_bp, url_prefix="/cards")
    app.register_blueprint(sets_bp, url_prefix="/sets")
    app.register_blueprint(practice_bp, url_prefix="/practice")

    return app


@login_manager.user_loader
def load_user(user_id):
    if not user_id:
        return None
    return db.session.get(User, int(user_id))


@login_manager.unauthorized_handler
def handle_unauthorized():
    login_url = url_for("auth.login", next=request.url)
    prefers_json = request.is_json or (
        request.accept_mimetypes["application/json"]
        >= request.accept_mimetypes["text/html"]
    )
    if prefers_json:
        return jsonify({"error": "Authentication required", "redirect": login_url}), 401
    return redirect(login_url)
