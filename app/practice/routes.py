from flask import jsonify, render_template
from . import practice_bp

@practice_bp.route("/")
def practice_home():
    return render_template("practice.html")
