from flask import jsonify, render_template
from . import auth_bp

@auth_bp.route("/login")
def login():
    return jsonify({"page": "Login"})

@auth_bp.route("/signup")
def signup():
    return jsonify({"page": "Signup"})

@auth_bp.route("/account")
def account_home():
    return render_template("account.html")
