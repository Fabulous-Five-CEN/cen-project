from flask import jsonify, request
import requests
from . import sets_bp
from app import db
from app.models import Card, User, SetTable
from datetime import datetime, timezone
import os


@sets_bp.route("/")
def sets_home():
    return jsonify({"page": "Sets"})


@sets_bp.route("/new", methods=["POST"])
def new_set():
    data = request.get_json() or {}

    name = data.get("name")
    description = data.get("description")
    user_id = data.get("user_id")

    if not name or not user_id:
        return jsonify({"error": "Missing one of these required fields: name, user_id"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": f"User with id {user_id} is not a registered user"}), 404

    new_set = SetTable(
        name=name,
        description=description,
        user_id=user_id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    try:
        db.session.add(new_set)
        db.session.commit()
        return jsonify({
            "message": "Set successfully created in database",
            "set": {
                "id": new_set.id,
                "name": new_set.name,
                "description": new_set.description,
                "user_id": new_set.user_id,
                "created_at": new_set.created_at.isoformat(),
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create set: {str(e)}"}), 500


@sets_bp.route("/edit/<int:set_id>", methods=["PUT"])
def edit_set(set_id):
    data = request.get_json() or {}

    set_obj = SetTable.query.get(set_id)
    if not set_obj:
        return jsonify({"error": f"No set exists in database with id {set_id}"}), 404

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
            "set": {
                "id": set_obj.id,
                "name": set_obj.name,
                "description": set_obj.description,
                "user_id": set_obj.user_id,
                "updated_at": set_obj.updated_at.isoformat(),
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update set: {str(e)}"}), 500


@sets_bp.route("/delete/<int:set_id>", methods=["DELETE"])
def delete_set(set_id):
    set_obj = SetTable.query.get(set_id)
    if not set_obj:
        return jsonify({"error": f"No set found with id {set_id}"}), 404

    try:
        db.session.delete(set_obj)
        db.session.commit()
        return jsonify({"message": f"Set with id {set_id} successfully deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete set: {str(e)}"}), 500


@sets_bp.route("/add_card/<int:set_id>", methods=["POST"])
def add_card_to_set(set_id):
    data = request.get_json() or {}
    card_ids = data.get("card_ids")

    if not card_ids:
        return jsonify({"error": "No card_ids provided"}), 400

    set_obj = SetTable.query.get(set_id)
    if not set_obj:
        return jsonify({"error": f"No set found with id {set_id}"}), 404

    # Ensure we can handle both single and multiple IDs
    if isinstance(card_ids, int):
        card_ids = [card_ids]

    cards = Card.query.filter(Card.id.in_(card_ids)).all()
    if not cards:
        return jsonify({"error": "No valid cards found for provided IDs"}), 404

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
def delete_card_from_set(set_id):
    data = request.get_json() or {}
    card_id = data.get("card_id")

    if not card_id:
        return jsonify({"error": "Missing required field: card_id"}), 400

    set_obj = SetTable.query.get(set_id)
    if not set_obj:
        return jsonify({"error": f"No set found with id {set_id}"}), 404

    card = Card.query.get(card_id)
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