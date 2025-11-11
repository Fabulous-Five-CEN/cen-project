from flask import jsonify, render_template
from . import sets_bp

@sets_bp.route("/")
def sets_home():
    return render_template("sets.html")

@sets_bp.route("/new")
def new_set():
    return jsonify({"page": "New Set"})

@sets_bp.route("/edit")
def edit_set():
    return jsonify({"page": "Edit Set"})

@sets_bp.route("/delete")
def delete_set():
    return jsonify({"page": "Delete Set"})
