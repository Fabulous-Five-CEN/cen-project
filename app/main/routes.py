from flask import render_template
from . import main_bp

@main_bp.route("/")
def dashboard():
    return render_template("dashboard.html")
