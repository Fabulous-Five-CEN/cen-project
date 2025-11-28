from flask import jsonify, request, abort, render_template
from . import sets_bp
from app.extensions import db
from app.models.orm_objects import Card, User, SetTable
from datetime import datetime, timezone
from flask_login import login_required, current_user

@sets_bp.route("/")
@login_required
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

@sets_bp.route("/all", methods=["GET"])
@login_required
def get_all_sets():
    user_id = current_user.id

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"Error": f"User with id {user_id} is not a registered user"}), 404

    sets = (
        SetTable.query
        .filter_by(user_id=user_id)
        .order_by(SetTable.created_at.desc())
        .all()
    )

    return jsonify([serialize_set(s) for s in sets]), 200


@sets_bp.route("/<int:set_id>", methods=["GET"])
@login_required
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

@sets_bp.route("/new", methods=["POST"])
@login_required
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

@sets_bp.route("/edit/<int:set_id>", methods=["PUT"])
@login_required
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

@sets_bp.route("/delete/<int:set_id>", methods=["DELETE"])
@login_required
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

@sets_bp.route("/add_card/<int:set_id>", methods=["POST"])
@login_required
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

@sets_bp.route("/delete_card/<int:set_id>", methods=["POST"])
@login_required
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


# new set for add card membership on frontend

@sets_bp.route("/update-membership/<int:card_id>", methods=["POST"])
@login_required
def update_card_sets(card_id):
    data = request.get_json() or {}
    set_ids = data.get("set_ids", [])

    if not isinstance(set_ids, list):
        return jsonify({"error": "set_ids must be a list"}), 400

    try:
        set_ids = set(int(sid) for sid in set_ids)
    except ValueError:
        return jsonify({"error": "set_ids must be integers"}), 400

    # Get the card
    card = db.session.get(Card, card_id)
    if not card or card.user_id != current_user.id:
        return jsonify({"error": f"No card found with id {card_id}"}), 404

    # All sets belong to the user
    user_sets = {s.id: s for s in SetTable.query.filter_by(user_id=current_user.id).all()}

    # Current set memberships
    current_ids = {s.id for s in card.sets}

    # Compute adds/removes
    to_add = set_ids - current_ids
    to_remove = current_ids - set_ids

    # Add
    for sid in to_add:
        s = user_sets.get(sid)
        if s:
            card.sets.append(s)

    # Remove
    for sid in to_remove:
        s = user_sets.get(sid)
        if s and s in card.sets:
            card.sets.remove(s)

    card.updated_at = datetime.now(timezone.utc)

    try:
        db.session.commit()
        return jsonify({
            "message": "Card set membership updated successfully",
            "card": {
                "id": card.id,
                "set_ids": [s.id for s in card.sets]
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update sets: {str(e)}"}), 500
