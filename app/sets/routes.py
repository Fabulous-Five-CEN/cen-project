from flask import jsonify, request, abort, render_template
from . import sets_bp
from app.extensions import db
from app.models.orm_objects import Card, User, SetTable
from datetime import datetime, timezone
from flask_login import login_required, current_user

@login_required
@sets_bp.route("/")
def sets_home():
    user_id = current_user.id
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"Error" : f"User with id {user_id} is not a registered user"}), 404
    
    """Gets all sets associated with a specific user_id."""

    all_sets = SetTable.query.filter_by(user_id=user_id).order_by(SetTable.created_at.desc()).all()
    set_list = [serialize_set(s) for s in all_sets]
    
    return render_template("sets.html", user_sets=set_list)
def serialize_set(set_obj):
    """Converts a SetTable object into a JSON-friendly dictionary."""
    return {
        "id": set_obj.id,
        "name": set_obj.name,
        "description": set_obj.description,
        "user_id": set_obj.user_id,
        "card_count": len(set_obj.cards),
        "created_at": set_obj.created_at.isoformat(),
        "updated_at": set_obj.updated_at.isoformat()
    }

def get_set_or_404(set_id, description=None):
    set_obj = db.session.get(SetTable, set_id)
    if not set_obj:
        abort(404, description=description or f"Set with id {set_id} not found")
    return set_obj

# @login_required
# @sets_bp.route("/all", methods=["GET"])
# def get_all_sets():
#     # Check that user is in database
#     user_id = current_user.id
#     user = db.session.get(User, user_id)
#     if not user:
#         return jsonify({"Error" : f"User with id {user_id} is not a registered user"}), 404
    
#     """Gets all sets associated with a specific user_id."""

#     all_sets = SetTable.query.filter_by(user_id=user_id).order_by(SetTable.created_at.desc()).all()
#     set_list = [serialize_set(s) for s in all_sets]
    
#     return render_template("sets.html", set_list)

@login_required
@sets_bp.route("/<int:set_id>", methods=["GET"])
def get_set_details(set_id):
    """Gets details for a single set, including its cards."""

    user_id = current_user.id
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"Error" : f"User with id {user_id} is not a registered user"}), 404


    set_obj = get_set_or_404(set_id)
    set_data = serialize_set(set_obj)
    set_data['cards'] = [
        {"id": card.id, "english_text": card.english_text, "spanish_text": card.spanish_text}
        for card in set_obj.cards
    ]
    return jsonify(set_data), 200

@login_required
@sets_bp.route("/new", methods=["POST"])
def new_set():
    data = request.get_json() or {}
    name = data.get("name")
    description = data.get("description")

    if not name:
        return jsonify({"error": "Missing one of these required fields: name"}), 400

    user_id = current_user.id
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"Error" : f"User with id {user_id} is not a registered user"}), 404

    new_set_obj = SetTable(
        name=name,
        description=description,
        user_id=user_id
    )
    try:
        db.session.add(new_set_obj)
        db.session.commit()
        return jsonify({
            "message": "Set successfully created in database",
            "set": serialize_set(new_set_obj)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create set: {str(e)}"}), 500

@login_required
@sets_bp.route("/edit/<int:set_id>", methods=["PUT"])
def edit_set(set_id):

    user_id = current_user.id
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"Error" : f"User with id {user_id} is not a registered user"}), 404

    data = request.get_json() or {}
    set_obj = get_set_or_404(set_id)

    name = data.get("name")
    description = data.get("description")

    if name is not None:
        set_obj.name = name
    if description is not None:
        set_obj.description = description
    
    set_obj.updated_at = datetime.now(timezone.utc)
    try:
        db.session.commit()
        return jsonify({
            "message": "Set successfully updated",
            "set": serialize_set(set_obj)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update set: {str(e)}"}), 500

@login_required
@sets_bp.route("/delete/<int:set_id>", methods=["DELETE"])
def delete_set(set_id):

    user_id = current_user.id
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"Error" : f"User with id {user_id} is not a registered user"}), 404

    set_obj = get_set_or_404(set_id)
    try:
        db.session.delete(set_obj)
        db.session.commit()
        return jsonify({"message": f"Set with id {set_id} successfully deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete set: {str(e)}"}), 500

@login_required
@sets_bp.route("/add_card/<int:set_id>", methods=["POST"])
def add_card_to_set(set_id):

    user_id = current_user.id
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"Error" : f"User with id {user_id} is not a registered user"}), 404

    data = request.get_json() or {}
    card_ids = data.get("card_ids")
    if not card_ids:
        return jsonify({"error": "No card_ids provided"}), 400

    set_obj = get_set_or_404(set_id)
    
    if isinstance(card_ids, int):
        card_ids = [card_ids]

    cards = Card.query.filter(Card.id.in_(card_ids)).all()
    if len(cards) != len(set(card_ids)):
         return jsonify({"error": "One or more card IDs were not found"}), 404

    try:
        added_ids = []
        for card in cards:
            if card not in set_obj.cards:
                set_obj.cards.append(card)
                added_ids.append(card.id)
        db.session.commit()
        return jsonify({
            "message": f"{len(added_ids)} card(s) successfully added to set {set_id}",
            "added_card_ids": added_ids
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to add cards to set: {str(e)}"}), 500

@login_required
@sets_bp.route("/delete_card/<int:set_id>", methods=["POST"])
def delete_card_from_set(set_id):

    user_id = current_user.id
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"Error" : f"User with id {user_id} is not a registered user"}), 404

    data = request.get_json() or {}
    card_id = data.get("card_id")
    if not card_id:
        return jsonify({"error": "Missing required field: card_id"}), 400

    set_obj = get_set_or_404(set_id)
    card = db.session.get(Card, card_id)

    if not card or card not in set_obj.cards:
        return jsonify({"error": f"Card with id {card_id} not found in set {set_id}"}), 404

    try:
        set_obj.cards.remove(card)
        db.session.commit()
        return jsonify({
            "message": f"Card with id {card_id} successfully removed from set {set_id}"
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to remove card from set: {str(e)}"}), 500

@sets_bp.route("/view/<int:set_id>")
@login_required
def view_set(set_id):

    user_id = current_user.id
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"Error" : f"User with id {user_id} is not a registered user"}), 404


    set_obj = get_set_or_404(set_id)
    user_cards = [
        {
            "id": card.id,
            "spanish_text": card.spanish_text,
            "english_text": card.english_text,
            "notes": card.notes,
            "is_starred": card.is_starred,
            "set_ids": [s.id for s in card.sets],
        }
        for card in set_obj.cards
    ]
    return render_template(
        "view_set.html",
        set_name=set_obj.name,
        set_id=set_id,
        cards=user_cards
    )
